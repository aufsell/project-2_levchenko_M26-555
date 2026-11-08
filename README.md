# Primitive DB

Primitive DB — простая консольная база данных на Python 3.12. Позволяет создавать таблицы, добавлять, искать, изменять и удалять записи.

Метаданные таблиц хранятся в `db_meta.json`, а сами записи — в отдельных JSON-файлах в папке `data/`.

## Установка и запуск

Для работы нужен Python 3.12 и `uv`.

```bash
uv sync
uv run database
```

Для сборки пакета:

```bash
uv build
```

## Команды

### Работа с таблицами

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | Создать таблицу |
| `list_tables` | Показать список таблиц |
| `drop_table <имя>` | Удалить таблицу |
| `info <имя>` | Показать столбцы и количество записей |

При создании таблицы автоматически добавляется столбец `ID:int`. Поддерживаются типы `int`, `str` и `bool`.

### Работа с записями

| Команда | Описание |
|---|---|
| `insert into <таблица> values (...)` | Добавить запись |
| `select from <таблица>` | Вывести все записи |
| `select from <таблица> where <условие>` | Найти записи по условию |
| `update <таблица> set <поле> = <значение> where <условие>` | Изменить записи |
| `delete from <таблица> where <условие>` | Удалить записи |

Также есть команды `help` и `exit`.

Строки нужно писать в двойных кавычках, логические значения — `true` и `false`.

## Пример использования

```text
create_table users name:str age:int is_active:bool

insert into users values ("Ivan", 25, true)
insert into users values ("Petr", 30, false)

select from users
select from users where age = 25

update users set age = 26 where name = "Ivan"

delete from users where ID = 2

info users
```

Результаты `select` выводятся в виде таблицы с помощью `PrettyTable`.

## Декораторы и кэширование

Для обработки ошибок, подтверждения удаления и замера времени используются декораторы из `decorators.py`.

- `handle_db_errors` — обрабатывает `ValueError`, `KeyError` и `FileNotFoundError`.
- `confirm_action` — запрашивает подтверждение перед удалением таблицы или записей.
- `log_time` — показывает время выполнения `insert` и `select`.

Например, при удалении таблицы появляется запрос:

```text
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]:
```

При ответе `y` операция выполняется, при любом другом — отменяется.

Для кэширования результатов `select` используется замыкание `create_cacher()` из `utils.py`. Если запрос повторяется, результат берётся из кэша. После изменения данных кэш сбрасывается, чтобы не возвращать старые записи.

## Проверка кода

Для проверки и форматирования используется Ruff:

```bash
uv run ruff check .
uv run ruff format .
```

Проверка собранного пакета:

```bash
uv build
uvx twine check dist/*
```

## Демонстрации

### Управление таблицами

Создание таблицы, просмотр списка и удаление.

[![Управление таблицами](https://asciinema.org/a/RZCmZDqD0qa7IcFj.svg)](https://asciinema.org/a/RZCmZDqD0qa7IcFj)

### CRUD-операции

Добавление, поиск, изменение и удаление записей.

[![CRUD-операции](https://asciinema.org/a/w1oqAZtptDuuQRBW.svg)](https://asciinema.org/a/w1oqAZtptDuuQRBW)

### Декораторы и замыкания

Обработка ошибок, подтверждение удаления, замер времени и кэширование запросов.

[![Декораторы и замыкания](https://asciinema.org/a/F0qD44A6f7CEFoo9.svg)](https://asciinema.org/a/F0qD44A6f7CEFoo9)