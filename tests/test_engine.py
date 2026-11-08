import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from primitive_db.engine import run


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    @patch("builtins.input", return_value="y")
    @patch("primitive_db.engine.prompt.string")
    def test_full_crud(self, mock_prompt, mock_input):
        mock_prompt.side_effect = [
            "create_table users name:str age:int",
            'insert into users values ("Ivan", 25)',
            "select from users",
            'update users set age = 26 where name = "Ivan"',
            "select from users where age = 26",
            "delete from users where ID = 1",
            "drop_table users",
            "exit",
        ]

        run()

        self.assertFalse(Path("data/users.json").exists())
        mock_input.assert_called()
