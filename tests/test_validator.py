import tempfile
import unittest

from src.generator import SIZES, generate_data
from src.validator import validate_databases, validate_generated_data


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        generate_data(self.directory, seed=2026, scale_factor=0.01)

    def test_generated_data_validates_eight_counts_and_relationships(self):
        self.assertEqual(validate_generated_data(self.directory), SIZES)

    def test_validate_queries_both_databases_and_rejects_mismatch(self):
        calls = []

        def runner(command, env, timeout):
            calls.append(command)
            return 0, ('2\n' if '--database' in command else '1\n'), ''

        config = {'ymatrix': {'psql_path': 'psql', 'host': 'h', 'port': 1, 'user': 'u', 'database': 'd'},
                  'mysql': {'transport': 'local_default', 'user': 'root', 'database': 'benchmark_mvp'},
                  'benchmark': {'timeout_seconds': 60}}
        rows = validate_databases(config, self.directory, runner=runner)
        self.assertEqual(len(calls), 16)
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row['match'] is False for row in rows))
        with self.assertRaises(ValueError):
            validate_databases(config, self.directory, runner=runner, raise_on_mismatch=True)


if __name__ == '__main__':
    unittest.main()
