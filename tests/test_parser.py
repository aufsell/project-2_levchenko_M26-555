import unittest

from primitive_db.parser import (
    parse_insert,
    parse_set,
    parse_where,
    split_outside_quotes,
)


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

    def test_split_where_inside_string(self):
        command = 'update users set name = "Ivan where Petr" where ID = 1'

        _, set_part = split_outside_quotes(command, " set ")
        set_part, where_part = split_outside_quotes(set_part, " where ")

        self.assertEqual(set_part, 'name = "Ivan where Petr"')
        self.assertEqual(where_part, "ID = 1")

    def test_split_escaped_quotes(self):
        command = 'update users set name = "Ivan \\"where\\" Petr" where ID = 1'

        _, set_part = split_outside_quotes(command, " set ")
        set_part, where_part = split_outside_quotes(set_part, " where ")

        self.assertEqual(set_part, 'name = "Ivan \\"where\\" Petr"')
        self.assertEqual(where_part, "ID = 1")

    def test_split_missing_separator(self):
        with self.assertRaises(ValueError):
            split_outside_quotes('name = "Ivan where Petr"', " where ")


if __name__ == "__main__":
    unittest.main()
