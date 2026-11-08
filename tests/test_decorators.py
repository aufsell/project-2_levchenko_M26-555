"""Проверки замыкания и декораторов."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)


class TestDecorators(unittest.TestCase):
    def test_cacher_avoids_repeating_calculation(self):
        cacher = create_cacher()
        calls = []

        def calculate():
            calls.append(1)
            return [1, 2]

        self.assertEqual(cacher("key", calculate), [1, 2])
        self.assertEqual(cacher("key", calculate), [1, 2])
        self.assertEqual(len(calls), 1)

    def test_cachers_are_independent(self):
        first = create_cacher()
        second = create_cacher()
        self.assertEqual(first("key", lambda: 1), 1)
        self.assertEqual(second("key", lambda: 2), 2)

    def test_error_decorator_returns_none(self):
        @handle_db_errors
        def failing():
            raise ValueError("wrong value")

        with redirect_stdout(io.StringIO()) as output:
            self.assertIsNone(failing())
        self.assertIn("wrong value", output.getvalue())

    def test_confirmation_cancels(self):
        @confirm_action("тест")
        def action():
            return 10

        with patch("builtins.input", return_value="n"):
            with redirect_stdout(io.StringIO()):
                self.assertIsNone(action())

    def test_confirmation_accepts(self):
        @confirm_action("тест")
        def action():
            return 10

        with patch("builtins.input", return_value="y"):
            self.assertEqual(action(), 10)

    def test_log_time_returns_result(self):
        @log_time
        def action():
            return 42

        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(action(), 42)
        self.assertIn("Функция action выполнилась за", output.getvalue())


if __name__ == "__main__":
    unittest.main()
