import csv
import os
import tempfile
import unittest

from src.generator import SIZES, generate_data, sizes_for_scale
from src.validator import validate_generated_data


class GeneratorTests(unittest.TestCase):
    def test_sf001_has_eight_expected_table_counts(self):
        self.assertEqual(SIZES, {'region': 5, 'nation': 25, 'supplier': 100,
                                 'customer': 1500, 'part': 2000, 'partsupp': 8000,
                                 'orders': 15000, 'lineitem': 60000})
        self.assertEqual(sizes_for_scale(0.01), SIZES)

    def test_same_seed_generates_same_files_and_valid_relationships(self):
        first = tempfile.mkdtemp()
        second = tempfile.mkdtemp()
        generate_data(first, seed=2026, scale_factor=0.01)
        generate_data(second, seed=2026, scale_factor=0.01)
        self.assertEqual(validate_generated_data(first), validate_generated_data(second))
        for name in SIZES:
            with open(os.path.join(first, name + '.csv'), 'rb') as left:
                with open(os.path.join(second, name + '.csv'), 'rb') as right:
                    self.assertEqual(left.read(), right.read())
        with open(os.path.join(first, 'partsupp.csv'), newline='') as handle:
            supplied = set((int(row['ps_partkey']), int(row['ps_suppkey']))
                           for row in csv.DictReader(handle))
        with open(os.path.join(first, 'lineitem.csv'), newline='') as handle:
            for row in csv.DictReader(handle):
                self.assertIn((int(row['l_partkey']), int(row['l_suppkey'])), supplied)


if __name__ == '__main__':
    unittest.main()
