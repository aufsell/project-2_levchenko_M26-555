
## Управление таблицами

Primitive DB — консольная база данных на Python 3.12 с хранением метаданных таблиц в JSON.

### Установка и запуск

```bash
uv sync
uv run database
```

### Доступные команды

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | Создать таблицу |
| `list_tables` | Показать все таблицы |
| `drop_table <имя>` | Удалить таблицу |
| `help` | Показать справку |
| `exit` | Выйти из программы |

Поддерживаемые типы данных: `int`, `str`, `bool`.

При создании таблицы автоматически добавляется столбец `ID:int`, если он не задан пользователем.

### Пример использования

```text
Введите команду: create_table users name:str age:int
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int

Введите команду: list_tables
- users

Введите команду: drop_table users
Таблица "users" успешно удалена.
```

Метаданные таблиц сохраняются в файле `db_meta.json`.

## Демонстрация работы

[![Демонстрация Primitive DB](https://asciinema.org/a/RZCmZDqD0qa7IcFj.svg)](https://asciinema.org/a/RZCmZDqD0qa7IcFj)