
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



## CRUD-операции

Primitive DB поддерживает добавление, просмотр, изменение и удаление записей.

Данные каждой таблицы сохраняются в отдельном JSON-файле в директории `data/`.

### Доступные команды

| Команда | Описание |
|---|---|
| `insert into <таблица> values (...)` | Добавить запись |
| `select from <таблица>` | Показать все записи |
| `select from <таблица> where <поле> = <значение>` | Найти записи |
| `update <таблица> set <поле> = <значение> where <условие>` | Изменить записи |
| `delete from <таблица> where <поле> = <значение>` | Удалить записи |
| `info <таблица>` | Информация о таблице |

Значения строк указываются в двойных кавычках. Поддерживаются типы `int`, `str`, `bool`.

Столбец `ID` создаётся автоматически.

### Пример работы

```text
create_table users name:str age:int is_active:bool
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
update users set age = 29 where name = "Sergei"
select from users
delete from users where ID = 1
info users
```

### Демонстрация CRUD-операций

[![Демонстрация CRUD](https://asciinema.org/a/w1oqAZtptDuuQRBW.svg)](https://asciinema.org/a/w1oqAZtptDuuQRBW)
