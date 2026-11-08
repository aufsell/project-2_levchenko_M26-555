import unittest

from primitive_db.parser import parse_insert, parse_set, parse_where


class TestParser(unittest.TestCase):
    def test_insert(self):
        command = 'insert into users values ("Ivan", 25, true)'
        table, values = parse_insert(command)

        self.assertEqual(table, "users")
        self.assertEqual(values, ["Ivan", 25, True])

    def test_insert_with_comma(self):
        command = 'insert into users values ("Ivan, Petr", 25)'
        table, values = parse_insert(command)

        self.assertEqual(table, "users")
        self.assertEqual(values, ["Ivan, Petr", 25])

    def test_insert_invalid_values(self):
        command = "insert into users values (Ivan, 25)"

        with self.assertRaises(ValueError):
            parse_insert(command)

    def test_where(self):
        result = parse_where('name = "Ivan"')
        self.assertEqual(result, {"name": "Ivan"})

    def test_where_with_equals(self):
        result = parse_where('name = "a=b"')
        self.assertEqual(result, {"name": "a=b"})

    def test_set(self):
        result = parse_set("age = 30")
        self.assertEqual(result, {"age": 30})


if __name__ == "__main__":
    unittest.main()
