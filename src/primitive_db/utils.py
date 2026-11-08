import json
from pathlib import Path

from primitive_db.constants import DATA_DIR_NAME

DATA_DIR = Path(DATA_DIR_NAME)


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        raise ValueError(f"Повреждён файл метаданных: {error}") from error


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
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(
            f'Не удалось прочитать данные таблицы "{table_name}": {error}'
        ) from error


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл."""
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
