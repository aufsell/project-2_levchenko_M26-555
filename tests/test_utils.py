"""Проверки чтения и сохранения JSON-файлов."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.patch_data = patch("primitive_db.utils.DATA_DIR", self.data_dir)
        self.patch_data.start()
        self.addCleanup(self.patch_data.stop)

    def test_missing_metadata_returns_empty_dict(self):
        self.assertEqual(load_metadata(self.root / "missing.json"), {})

    def test_metadata_round_trip(self):
        path = self.root / "db_meta.json"
        metadata = {"users": {"ID": "int", "name": "str"}}
        save_metadata(path, metadata)
        self.assertEqual(load_metadata(path), metadata)

    def test_missing_table_returns_empty_list(self):
        self.assertEqual(load_table_data("users"), [])

    def test_table_data_round_trip(self):
        rows = [{"ID": 1, "name": "Иван"}, {"ID": 2, "name": "Пётр"}]
        save_table_data("users", rows)
        self.assertEqual(load_table_data("users"), rows)
        self.assertTrue((self.data_dir / "users.json").exists())

    def test_broken_metadata_raises_value_error(self):
        path = self.root / "db_meta.json"
        path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_metadata(path)

    def test_broken_table_raises_value_error(self):
        self.data_dir.mkdir()
        (self.data_dir / "users.json").write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_table_data("users")

    def test_saved_json_is_valid(self):
        save_table_data("users", [{"ID": 1, "name": "Иван"}])
        with (self.data_dir / "users.json").open(encoding="utf-8") as file:
            self.assertEqual(json.load(file)[0]["name"], "Иван")

    def test_invalid_table_name_rejected(self):
        with self.assertRaises(ValueError):
            load_table_data("../outside")
        with self.assertRaises(ValueError):
            save_table_data("../outside", [])


if __name__ == "__main__":
    unittest.main()
