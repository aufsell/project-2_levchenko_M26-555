import json


def parse_insert(user_input):
    """Разбирает команду insert и возвращает имя таблицы и значения."""
    parts = user_input.split(maxsplit=4)

    if len(parts) != 5 or parts[0] != "insert" or parts[1] != "into":
        raise ValueError("Некорректный формат команды insert")

    table_name = parts[2]

    if parts[3] != "values":
        raise ValueError("Ожидалось ключевое слово values")

    values_str = parts[4].strip()

    if not values_str.startswith("(") or not values_str.endswith(")"):
        raise ValueError("Значения должны быть указаны в скобках")

    values_str = values_str[1:-1]

    try:
        values = json.loads(f"[{values_str}]")
    except json.JSONDecodeError:
        raise ValueError("Некорректные значения") from None

    if not isinstance(values, list):
        raise ValueError("Некорректный список значений")

    return table_name, values


def parse_where(condition):
    """Разбирает условие where и возвращает столбец и значение."""
    parts = condition.split("=", maxsplit=1)

    if len(parts) != 2:
        raise ValueError("Некорректное условие where")

    name = parts[0].strip()
    value = parts[1].strip()

    if not name or not value:
        raise ValueError("Некорректное условие where")

    try:
        value = json.loads(value)
    except json.JSONDecodeError:
        raise ValueError("Некорректное значение в where") from None

    if type(value) not in (int, str, bool):
        raise ValueError("Недопустимый тип значения в where")

    return {name: value}


def parse_set(condition):
    """Разбирает выражение set для обновления записи."""
    return parse_where(condition)


def split_outside_quotes(text, separator):
    """Разделяет строку по первому разделителю вне кавычек."""
    in_quotes = False
    escaped = False

    for i, char in enumerate(text):
        if escaped:
            escaped = False
            continue

        if char == "\\" and in_quotes:
            escaped = True
            continue

        if char == '"':
            in_quotes = not in_quotes
            continue

        if not in_quotes and text.startswith(separator, i):
            left = text[:i]
            right = text[i + len(separator) :]
            return left, right

    raise ValueError(f"Не найден разделитель {separator.strip()}")
