import unittest
from unittest.mock import patch

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)


class TestCore(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "users": {
                "ID": "int",
                "name": "str",
                "age": "int",
            }
        }
        self.rows = [
            {"ID": 1, "name": "Ivan", "age": 25},
            {"ID": 2, "name": "Petr", "age": 30},
        ]

    def test_create_table(self):
        result = create_table({}, "products", ["title:str", "price:int"])

        self.assertEqual(
            result["products"],
            {"ID": "int", "title": "str", "price": "int"},
        )

    def test_duplicate_table(self):
        result = create_table(self.metadata, "users", ["name:str"])

        self.assertIsNone(result)

    def test_invalid_column_type(self):
        result = create_table({}, "products", ["price:float"])

        self.assertIsNone(result)

    def test_duplicate_columns(self):
        result = create_table({}, "products", ["name:str", "name:int"])

        self.assertIsNone(result)

    def test_list_tables(self):
        self.assertEqual(list_tables(self.metadata), ["users"])

    @patch("primitive_db.core.load_table_data", return_value=[])
    def test_insert(self, mock_load):
        result = insert(self.metadata, "users", ["Ivan", 25])

        self.assertEqual(
            result,
            [{"ID": 1, "name": "Ivan", "age": 25}],
        )
        mock_load.assert_called_once_with("users")

    def test_select(self):
        result = select(self.rows, {"age": 25})

        self.assertEqual(result, [self.rows[0]])

    def test_update(self):
        result, updated_ids = update(
            self.rows,
            {"age": 26},
            {"name": "Ivan"},
        )

        self.assertEqual(updated_ids, [1])
        self.assertEqual(result[0]["age"], 26)
        self.assertEqual(result[1]["age"], 30)

    @patch("builtins.input", return_value="n")
    def test_delete_cancel(self, mock_input):
        result = delete(self.rows, {"ID": 1})

        self.assertIsNone(result)
        self.assertEqual(len(self.rows), 2)
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="y")
    def test_delete_confirm(self, mock_input):
        result, deleted_ids = delete(self.rows, {"ID": 1})

        self.assertEqual(deleted_ids, [1])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ID"], 2)
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="y")
    def test_delete_without_where(self, mock_input):
        result = delete(self.rows, {})

        self.assertIsNone(result)
        self.assertEqual(len(self.rows), 2)
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="n")
    def test_drop_table_cancel(self, mock_input):
        result = drop_table(self.metadata, "users")

        self.assertIsNone(result)
        self.assertIn("users", self.metadata)
        mock_input.assert_called_once()

    def test_update_without_where(self):
        result = update(self.rows, {"age": 40}, {})

        self.assertIsNone(result)
        self.assertEqual(self.rows[0]["age"], 25)
        self.assertEqual(self.rows[1]["age"], 30)

    def test_update_without_set(self):
        result = update(self.rows, {}, {"ID": 1})

        self.assertIsNone(result)
        self.assertEqual(self.rows[0]["age"], 25)


if __name__ == "__main__":
    unittest.main()
