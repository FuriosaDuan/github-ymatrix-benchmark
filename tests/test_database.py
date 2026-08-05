import unittest

from src.database import normalize_rows, parse_rows


class DatabaseTests(unittest.TestCase):
    def test_parses_headerless_tabular_output_and_normalizes_decimal(self):
        parsed = parse_rows('2026-01\t10\t12.5000\n')
        self.assertEqual(parsed, [['2026-01', '10', '12.5000']])
        rows = normalize_rows(parsed)
        self.assertEqual(str(rows[0][1]), '10')

    def test_decimal_values_compare_by_value(self):
        self.assertEqual(normalize_rows([['1.0']]), normalize_rows([['1.00']]))


if __name__ == '__main__':
    unittest.main()
