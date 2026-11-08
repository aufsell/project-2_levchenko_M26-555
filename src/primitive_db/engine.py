import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import parse_insert, parse_set, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            print()


def run():
    print_help()

    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            parts = shlex.split(user_input)
            if not parts:
                continue
            command, *args = parts
            if command == "exit":
                if len(args) != 0:
                    raise ValueError("Для этой функции не требуются параметры")
                break
            elif command == "help":
                if len(args) != 0:
                    raise ValueError("Для этой функции не требуются параметры")
                print_help()
            elif command == "create_table":
                if len(args) < 2:
                    raise ValueError("Для этой функции требуются минимум 2 параметра")

                metadata = load_metadata("db_meta.json")
                table_name = args[0]
                columns = args[1:]
                new_metadata = create_table(metadata, table_name, columns)
                save_metadata("db_meta.json", new_metadata)

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

                metadata = load_metadata("db_meta.json")
                tables = list_tables(metadata)

                if not tables:
                    print("Таблиц пока нет.")
                else:
                    for table_name in tables:
                        print(f"- {table_name}")

            elif command == "drop_table":
                if len(args) != 1:
                    raise ValueError("Для этой функции требуется параметр с названием")
                metadata = load_metadata("db_meta.json")
                table_name = args[0]
                new_metadata = drop_table(metadata, table_name)
                save_metadata("db_meta.json", new_metadata)
                filepath = Path("data") / f"{table_name}.json"
                if filepath.exists():
                    filepath.unlink()
                print(f'Таблица "{table_name}" успешно удалена')

            elif command == "insert":
                table_name, values = parse_insert(user_input)

                metadata = load_metadata("db_meta.json")
                table_data = insert(metadata, table_name, values)

                save_table_data(table_name, table_data)

                print(
                    f"Запись с ID={table_data[-1]['ID']} "
                    f'успешно добавлена в таблицу "{table_name}".'
                )

            elif command == "select":
                if len(args) < 2 or args[0] != "from":
                    raise ValueError("Некорректный формат команды select")

                table_name = args[1]
                metadata = load_metadata("db_meta.json")

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                where_clause = None

                if len(args) > 2:
                    if args[2] != "where" or len(args) < 4:
                        raise ValueError("Некорректный формат команды select")

                    condition = user_input.split(" where ", maxsplit=1)[1]
                    where_clause = parse_where(condition)

                    column_name = next(iter(where_clause))

                    if column_name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{column_name}" не существует')

                table_data = load_table_data(table_name)
                result = select(table_data, where_clause)

                table = PrettyTable()
                table.field_names = list(metadata[table_name].keys())

                for row in result:
                    table.add_row([row[name] for name in table.field_names])

                print(table)

            elif command == "update":
                if " set " not in user_input or " where " not in user_input:
                    raise ValueError("Некорректный формат команды update")

                table_name = args[0]

                metadata = load_metadata("db_meta.json")

                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует')

                set_part = user_input.split(" set ", maxsplit=1)[1]
                set_part, where_part = set_part.split(" where ", maxsplit=1)

                set_clause = parse_set(set_part)
                where_clause = parse_where(where_part)

                for name, value in set_clause.items():
                    if name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{name}" не существует')

                    if name == "ID":
                        raise ValueError("Нельзя изменять ID записи")

                    column_type = metadata[table_name][name]

                    if type(value).__name__ != column_type:
                        raise ValueError(f"Некорректный тип значения для {name}")

                for name, value in where_clause.items():
                    if name not in metadata[table_name]:
                        raise ValueError(f'Столбец "{name}" не существует')

                    column_type = metadata[table_name][name]

                    if type(value).__name__ != column_type:
                        raise ValueError(f"Некорректный тип значения для {name}")

                table_data = load_table_data(table_name)
                new_data, updated_ids = update(table_data, set_clause, where_clause)

                save_table_data(table_name, new_data)

                if not updated_ids:
                    print("Подходящих записей не найдено")
                else:
                    for row_id in updated_ids:
                        print(
                            f'Запись с ID={row_id} в таблице "{table_name}" '
                            "успешно обновлена."
                        )

            elif command == "delete":
                if len(args) < 5 or args[0] != "from" or args[2] != "where":
                    raise ValueError("Некорректный формат команды delete")

                table_name = args[1]
                metadata = load_metadata("db_meta.json")

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
                new_data, deleted_ids = delete(table_data, where_clause)

                if not deleted_ids:
                    print("Подходящих записей не найдено")
                else:
                    save_table_data(table_name, new_data)

                    for row_id in deleted_ids:
                        print(
                            f"Запись с ID={row_id} успешно удалена "
                            f'из таблицы "{table_name}".'
                        )

            elif command == "info":
                if len(args) != 1:
                    raise ValueError("Для этой функции требуется название таблицы")

                table_name = args[0]
                metadata = load_metadata("db_meta.json")

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
