def create_table(metadata, table_name, columns):
    table_columns = {"ID": "int"}
    seen_columns = set()

    if table_name in metadata:
        raise ValueError("Таблица с таким именем уже существует")

    allowed_types = {"int", "str", "bool"}
    for column in columns:
        if column.count(":") != 1:
            raise ValueError(f"Некорректный формат поля {column}")
        name, column_type = column.strip().split(":")
        name = name.strip()
        column_type = column_type.strip()
        if not name.strip():
            raise ValueError(f"Пустое имя столбца: {column}")
        if column_type not in allowed_types:
            raise ValueError(f"Некорректный тип поля {column_type}")
        if name == "ID" and column_type != "int":
            raise ValueError (f"Некорректный тип поля {column_type}")

        if name in seen_columns:
            raise ValueError(f"Дублируется поле {name}")
        seen_columns.add(name)
        
        table_columns[name] = column_type
        
    metadata[table_name] = table_columns
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблицы с именем "{table_name}" не существует')

    del metadata[table_name]
    return metadata

def list_tables(metadata):
    return list(metadata.keys())