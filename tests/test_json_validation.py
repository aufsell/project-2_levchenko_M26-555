import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from primitive_db.utils import load_metadata, load_table_data


class TestJsonValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_invalid_metadata_format(self):
        filepath = self.path / "db_meta.json"
        filepath.write_text('["users"]', encoding="utf-8")

        with self.assertRaises(ValueError):
            load_metadata(filepath)

    def test_invalid_table_columns(self):
        filepath = self.path / "db_meta.json"
        filepath.write_text(
            json.dumps({"users": {"name": "str"}}),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_metadata(filepath)

    def test_invalid_table_data_format(self):
        filepath = self.path / "users.json"
        filepath.write_text('{"name": "Ivan"}', encoding="utf-8")

        with patch("primitive_db.utils.DATA_DIR", self.path):
            with self.assertRaises(ValueError):
                load_table_data("users")

    def test_invalid_row_format(self):
        filepath = self.path / "users.json"
        filepath.write_text('["Ivan", "Petr"]', encoding="utf-8")

        with patch("primitive_db.utils.DATA_DIR", self.path):
            with self.assertRaises(ValueError):
                load_table_data("users")

    def test_invalid_row_id(self):
        filepath = self.path / "users.json"
        filepath.write_text(
            '[{"ID": "abc", "name": "Ivan"}]',
            encoding="utf-8",
        )

        with patch("primitive_db.utils.DATA_DIR", self.path):
            with self.assertRaises(ValueError):
                load_table_data("users")

    def test_valid_table_data(self):
        filepath = self.path / "users.json"
        rows = [{"ID": 1, "name": "Ivan"}]
        filepath.write_text(json.dumps(rows), encoding="utf-8")

        with patch("primitive_db.utils.DATA_DIR", self.path):
            result = load_table_data("users")

        self.assertEqual(result, rows)


if __name__ == "__main__":
    unittest.main()
