"""Проверки консольных команд и сохранения данных."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from primitive_db.engine import run


class TestEngineExtra(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
        self.addCleanup(os.chdir, self.old_cwd)

    def execute(self, commands, answers=()):
        output = io.StringIO()
        with (
            patch("primitive_db.engine.prompt.string", side_effect=commands),
            patch("builtins.input", side_effect=answers),
            redirect_stdout(output),
        ):
            run()
        return output.getvalue()

    def test_full_crud_and_files(self):
        output = self.execute(
            [
                "create_table users name:str age:int",
                'insert into users values ("Ivan", 25)',
                'insert into users values ("Petr", 30)',
                "select from users",
                'update users set age = 26 where name = "Ivan"',
                "select from users where age = 26",
                "delete from users where ID = 2",
                "info users",
                "exit",
            ],
            answers=["y"],
        )
        self.assertIn("Ivan", output)
        self.assertIn("Количество записей: 1", output)
        with Path("data/users.json").open(encoding="utf-8") as file:
            self.assertEqual(json.load(file), [{"ID": 1, "name": "Ivan", "age": 26}])
        with Path("db_meta.json").open(encoding="utf-8") as file:
            self.assertIn("users", json.load(file))

    def test_cancel_delete_keeps_data(self):
        output = self.execute(
            [
                "create_table users name:str",
                'insert into users values ("Ivan")',
                "delete from users where ID = 1",
                "drop_table users",
                "exit",
            ],
            answers=["n", "n"],
        )
        self.assertIn("Операция отменена", output)
        self.assertTrue(Path("data/users.json").exists())
        with Path("data/users.json").open(encoding="utf-8") as file:
            self.assertEqual(len(json.load(file)), 1)
        with Path("db_meta.json").open(encoding="utf-8") as file:
            self.assertIn("users", json.load(file))

    def test_confirm_drop_removes_table_file(self):
        self.execute(
            [
                "create_table users name:str",
                'insert into users values ("Ivan")',
                "drop_table users",
                "exit",
            ],
            answers=["y"],
        )
        self.assertFalse(Path("data/users.json").exists())
        with Path("db_meta.json").open(encoding="utf-8") as file:
            self.assertNotIn("users", json.load(file))

    def test_invalid_input_does_not_stop_cli(self):
        output = self.execute(
            [
                "create_table users name:str",
                'insert into users values ("Ivan", 25)',
                "list_tables",
                "exit",
            ]
        )
        self.assertIn("Ожидалось 1 значений", output)
        self.assertIn("- users", output)

    def test_select_cache_clears_after_insert(self):
        output = self.execute(
            [
                "create_table users name:str",
                'insert into users values ("Ivan")',
                "select from users",
                "select from users",
                'insert into users values ("Petr")',
                "select from users",
                "select from users",
                "exit",
            ]
        )
        self.assertEqual(output.count("Функция select выполнилась"), 2)
        self.assertIn("Petr", output)


if __name__ == "__main__":
    unittest.main()
