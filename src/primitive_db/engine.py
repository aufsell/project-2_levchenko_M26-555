import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import (
    parse_insert,
    parse_set,
    parse_where,
    split_outside_quotes,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по доступным командам базы данных."""
    print("\n***База данных***")
    print("Функции:")
    print("<command> create_table <имя> <столбец:тип> ... - создать таблицу")
    print("<command> list_tables - показать список таблиц")
    print("<command> drop_table <имя> - удалить таблицу")
    print("<command> insert into <имя> values (...) - добавить запись")
    print("<command> select from <имя> [where <поле> = <значение>] - найти записи")
    print("<command> update <имя> set <поле> = <значение> where ... - обновить")
    print("<command> delete from <имя> where <поле> = <значение> - удалить запись")
    print("<command> info <имя> - информация о таблице")
    print("<command> exit - выйти")
    print("<command> help - справка\n")


def run():
    """Читает команды пользователя и выполняет операции с базой данных."""
    print_help()
    cacher = create_cacher()

    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            parts = shlex.split(user_input)

            if not parts:
                continue

            command, *args = parts

            if command == "exit":
                if args:
                    raise ValueError("Для этой функции не требуются параметры")
                break

            elif command == "help":
                if args:
                    raise ValueError("Для этой функции не требуются параметры")
                print_help()

            elif command == "create_table":
                if len(args) < 2:
                    raise ValueError("Для этой функции требуются минимум 2 параметра")

                metadata = load_metadata(META_FILE)
                table_name = args[0]
                columns = args[1:]
                new_metadata = create_table(metadata, table_name, columns)

                if new_metadata is None:
                    continue

                save_metadata(META_FILE, new_metadata)
                cacher = create_cacher()
                columns_str = ", ".join(
                    f"{name}:{dtype}"
                    for name, dtype in new_metadata[table_name].items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {columns_str}"
                )

            elif command == "list_tables":
                if args:
                    raise ValueError("Для этой функции не требуются параметры")

                metadata = load_metadata(META_FILE)
                tables = list_tables(metadata)

                if tables is None:
                    continue

                if not tables:
                    print("Таблиц пока нет.")
                else:
                    for table_name in tables:
                        print(f"- {table_name}")

            elif command == "drop_table":
                if len(args) != 1:
                    raise ValueError("Для этой функции требуется название таблицы")

                metadata = load_metadata(META_FILE)
                table_name = args[0]
                new_metadata = drop_table(metadata, table_name)

                if new_metadata is None:
                    continue

                save_metadata(META_FILE, new_metadata)
                cacher = create_cacher()
                filepath = Path("data") / f"{table_name}.json"

                try:
                    if filepath.exists():
                        filepath.unlink()
                except OSError as error:
                    print(f"Ошибка при удалении файла таблицы: {error}")

                print(f'Таблица "{table_name}" успешно удалена')

            elif command == "insert":
                table_name, values = parse_insert(user_input)
                metadata = load_metadata(META_FILE)
                table_data = insert(metadata, table_name, values)

                if table_data is None:
                    continue

                save_table_data(table_name, table_data)
                cacher = create_cacher()
                print(
                    f"Запись с ID={table_data[-1]['ID']} "
                    f'успешно добавлена в таблицу "{table_name}".'
                )

            elif command == "select":
                if len(args) < 2 or args[0] != "from":
                    raise ValueError("Некорректный формат команды select")

                table_name = args[1]
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                where_clause = None

                if len(args) > 2:
                    if len(args) < 4 or args[2] != "where":
                        raise ValueError("Некорректный формат команды select")

                    condition = user_input.split(" where ", maxsplit=1)[1]
                    where_clause = parse_where(condition)

                    for name, value in where_clause.items():
                        if name not in metadata[table_name]:
                            raise ValueError(f'Столбец "{name}" не существует')
                        if type(value).__name__ != metadata[table_name][name]:
                            raise ValueError(f"Некорректный тип значения для {name}")

                table_data = load_table_data(table_name)

                cache_key = (
                    table_name,
                    tuple(sorted(where_clause.items())) if where_clause else None,
                )

                result = cacher(
                    cache_key,
                    lambda: select(table_data, where_clause),
                )

                if result is None:
                    continue

                table = PrettyTable()
                table.field_names = list(metadata[table_name].keys())

                for row in result:
                    table.add_row([row[name] for name in table.field_names])

                print(table)

            elif command == "update":
                if len(args) < 2 or " set " not in user_input:
                    raise ValueError("Некорректный формат команды update")
                if " where " not in user_input:
                    raise ValueError("Некорректный формат команды update")

                table_name = args[0]
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                _, set_part = split_outside_quotes(user_input, " set ")
                set_part, where_part = split_outside_quotes(set_part, " where ")
                set_clause = parse_set(set_part)
                where_clause = parse_where(where_part)

                for name, value in set_clause.items():
                    if name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{name}" не существует')
                    if name == "ID":
                        raise ValueError("Нельзя изменять ID записи")
                    if type(value).__name__ != metadata[table_name][name]:
                        raise ValueError(f"Некорректный тип значения для {name}")

                for name, value in where_clause.items():
                    if name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{name}" не существует')
                    if type(value).__name__ != metadata[table_name][name]:
                        raise ValueError(f"Некорректный тип значения для {name}")

                table_data = load_table_data(table_name)
                result = update(table_data, set_clause, where_clause)

                if result is None:
                    continue

                new_data, updated_ids = result

                if not updated_ids:
                    print("Подходящих записей не найдено")
                else:
                    save_table_data(table_name, new_data)
                    cacher = create_cacher()
                    for row_id in updated_ids:
                        print(
                            f'Запись с ID={row_id} в таблице "{table_name}" '
                            "успешно обновлена."
                        )

            elif command == "delete":
                if len(args) < 4 or args[0] != "from" or args[2] != "where":
                    raise ValueError("Некорректный формат команды delete")

                table_name = args[1]
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                where_part = user_input.split(" where ", maxsplit=1)[1]
                where_clause = parse_where(where_part)

                for name, value in where_clause.items():
                    if name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{name}" не существует')
                    if type(value).__name__ != metadata[table_name][name]:
                        raise ValueError(f"Некорректный тип значения для {name}")

                table_data = load_table_data(table_name)
                result = delete(table_data, where_clause)

                if result is None:
                    continue

                new_data, deleted_ids = result

                if not deleted_ids:
                    print("Подходящих записей не найдено")
                else:
                    save_table_data(table_name, new_data)
                    cacher = create_cacher()
                    for row_id in deleted_ids:
                        print(
                            f"Запись с ID={row_id} успешно удалена "
                            f'из таблицы "{table_name}".'
                        )

            elif command == "info":
                if len(args) != 1:
                    raise ValueError("Для этой функции требуется название таблицы")

                table_name = args[0]
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                table_data = load_table_data(table_name)
                columns = metadata[table_name]
                columns_str = ", ".join(
                    f"{name}:{dtype}" for name, dtype in columns.items()
                )

                print(f"Таблица: {table_name}")
                print(f"Столбцы: {columns_str}")
                print(f"Количество записей: {len(table_data)}")

            else:
                raise ValueError(f"Функции {command} не существует. Попробуйте снова.")

        except ValueError as error:
            print(error)
