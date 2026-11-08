from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу и проверяет названия и типы её столбцов."""
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")

    table_columns = {"ID": "int"}
    seen_columns = set()

    if table_name in metadata:
        raise ValueError("Таблица с таким именем уже существует")

    for column in columns:
        if column.count(":") != 1:
            raise ValueError(f"Некорректный формат поля {column}")

        name, column_type = column.strip().split(":")
        name = name.strip()
        column_type = column_type.strip()

        if not name:
            raise ValueError(f"Пустое имя столбца: {column}")

        if not name.isidentifier():
            raise ValueError(f"Некорректное имя столбца: {name}")

        if column_type not in VALID_TYPES:
            raise ValueError(f"Некорректный тип поля {column_type}")

        if name == "ID" and column_type != "int":
            raise ValueError(f"Некорректный тип поля {column_type}")

        if name in seen_columns:
            raise ValueError(f"Дублируется поле {name}")

        seen_columns.add(name)
        table_columns[name] = column_type

    metadata[table_name] = table_columns
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных после подтверждения."""
    if table_name not in metadata:
        raise ValueError(f'Таблицы с именем "{table_name}" не существует')

    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """Возвращает список всех таблиц."""
    return list(metadata.keys())


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Проверяет значения и добавляет новую запись с уникальным ID."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = {
        name: dtype for name, dtype in metadata[table_name].items() if name != "ID"
    }

    if len(values) != len(columns):
        raise ValueError(f"Ожидалось {len(columns)} значений, получено {len(values)}.")

    type_map = {
        "int": int,
        "str": str,
        "bool": bool,
    }

    for (name, dtype), value in zip(columns.items(), values):
        if type(value) is not type_map[dtype]:
            raise ValueError(
                f'Столбец "{name}" ожидает тип {dtype}, получен {type(value).__name__}.'
            )

    table_data = load_table_data(table_name)

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    new_row = {"ID": new_id}
    new_row.update(zip(columns.keys(), values))

    table_data.append(new_row)

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или только подходящие под условие."""
    if where_clause is None:
        return table_data

    result = []

    for row in table_data:
        if all(row.get(name) == value for name, value in where_clause.items()):
            result.append(row)

    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Изменяет записи по условию и возвращает их ID."""
    if not where_clause:
        raise ValueError("Для обновления необходимо указать условие where")

    if not set_clause:
        raise ValueError("Для обновления необходимо указать значения set")

    updated_ids = []

    for row in table_data:
        if all(row.get(name) == value for name, value in where_clause.items()):
            for name, value in set_clause.items():
                row[name] = value

            updated_ids.append(row["ID"])

    return table_data, updated_ids


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Удаляет записи по условию после подтверждения."""
    if not where_clause:
        raise ValueError("Для удаления необходимо указать условие where")

    deleted_ids = []
    new_data = []

    for row in table_data:
        if all(row.get(name) == value for name, value in where_clause.items()):
            deleted_ids.append(row["ID"])
        else:
            new_data.append(row)

    return new_data, deleted_ids
