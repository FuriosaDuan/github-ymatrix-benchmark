import os
import tempfile
import unittest

from src.generator import SIZES, generate_data
from src.validator import validate_generated_data


class GeneratorTests(unittest.TestCase):
    def test_v3_scale_is_exact(self):
        self.assertEqual(SIZES, {'customer': 1000, 'part': 500, 'orders': 10000, 'lineitem': 30000})

    def test_same_seed_generates_same_files(self):
        first = tempfile.mkdtemp()
        second = tempfile.mkdtemp()
        generate_data(first, seed=2026)
        generate_data(second, seed=2026)
        self.assertEqual(validate_generated_data(first), validate_generated_data(second))
        for name in SIZES:
            with open(os.path.join(first, name + '.csv'), 'rb') as left:
                with open(os.path.join(second, name + '.csv'), 'rb') as right:
                    self.assertEqual(left.read(), right.read())


if __name__ == '__main__':
    unittest.main()
