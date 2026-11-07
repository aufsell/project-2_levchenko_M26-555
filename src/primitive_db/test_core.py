
from primitive_db.core import create_table


def expect_value_error(metadata, table_name, columns):
    try:
        create_table(metadata, table_name, columns)
    except ValueError:
        return

    raise AssertionError(
        f"Ожидался ValueError для таблицы {table_name!r}, "
        f"столбцы: {columns!r}"
    )


def test_create_table():
    metadata = {}

    # 1. Успешное создание таблицы
    result = create_table(metadata, "users", ["name:str", "age:int"])

    assert result == {
        "users": {
            "ID": "int",
            "name": "str",
            "age": "int",
        }
    }
    print("✅ Создание таблицы")

    # 2. Повторное создание существующей таблицы
    expect_value_error(metadata, "users", ["email:str"])
    print("✅ Проверка существующей таблицы")

    # 3. Недопустимый тип
    expect_value_error(metadata, "products", ["price:float"])
    print("✅ Проверка типа данных")

    # 4. Дублирование столбцов
    expect_value_error(metadata, "products", ["name:str", "name:int"])
    print("✅ Проверка дубликатов")

    # 5. Некорректный ID
    expect_value_error(metadata, "products", ["ID:str"])
    print("✅ Проверка типа ID")

    # 6. Некорректный формат
    expect_value_error(metadata, "products", ["name"])
    print("✅ Проверка формата")

    # 7. Пустое имя столбца
    expect_value_error(metadata, "products", [":int"])
    print("✅ Проверка пустого имени")

    # 8. Пользователь сам указал правильный ID
    result = create_table({}, "employees", ["ID:int", "salary:int"])
    assert result["employees"] == {"ID": "int", "salary": "int"}
    print("✅ Явное указание ID:int")

    # 9. При ошибках метаданные не должны измениться
    assert list(metadata) == ["users"]
    print("✅ Метаданные не изменились после ошибок")

    print("\n🎉 Все тесты пройдены!")


if __name__ == "__main__":
    test_create_table()
