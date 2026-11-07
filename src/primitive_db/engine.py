import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


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
                print(f'Таблица "{table_name}" успешно удалена')
            else:
                raise ValueError(f"Функции {command} не существует. Попробуйте снова.")
        except ValueError as error:
            print(error)
        