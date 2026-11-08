import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает ошибки при выполнении операций базы данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Вызывает функцию и перехватывает возможные ошибки."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
            return None
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
            return None
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    """Создаёт декоратор для подтверждения опасных операций."""

    def decorator(func):
        """Принимает функцию, для которой нужно подтверждение."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Запрашивает подтверждение перед вызовом функции."""
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')

            if answer.lower().strip() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Вызывает функцию и выводит время её выполнения."""
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()

        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд")
        return result

    return wrapper


def create_cacher():
    """Создаёт независимый кэш для хранения результатов запросов."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его."""
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
