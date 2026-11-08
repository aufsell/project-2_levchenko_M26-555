import json
from pathlib import Path

from primitive_db.constants import DATA_DIR_NAME, VALID_TYPES

DATA_DIR = Path(DATA_DIR_NAME)


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        raise ValueError(f"Повреждён файл метаданных: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("Некорректный формат метаданных")

    for table_name, columns in data.items():
        if not table_name.isidentifier():
            raise ValueError(f"Некорректное имя таблицы: {table_name}")

        if not isinstance(columns, dict):
            raise ValueError(f'Некорректные столбцы таблицы "{table_name}"')

        if columns.get("ID") != "int":
            raise ValueError(f'Некорректный столбец ID таблицы "{table_name}"')

        for name, column_type in columns.items():
            if not name.isidentifier() or column_type not in VALID_TYPES:
                raise ValueError(f"Некорректный столбец: {name}")

    return data


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла."""
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")

    filepath = DATA_DIR / f"{table_name}.json"

    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(
            f'Не удалось прочитать данные таблицы "{table_name}": {error}'
        ) from error

    if not isinstance(data, list):
        raise ValueError(f'Некорректный формат данных таблицы "{table_name}"')

    for row in data:
        if not isinstance(row, dict):
            raise ValueError("Каждая запись таблицы должна быть словарём")

        if type(row.get("ID")) is not int or row["ID"] < 1:
            raise ValueError("Некорректный ID записи")

    return data


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл."""
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
