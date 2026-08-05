import csv
import os
import tempfile
import unittest

from src.generator import SIZES
from src.validator import validate_databases


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.directory, name))
                                 for name in os.listdir(self.directory)])
        for name in SIZES:
            with open(os.path.join(self.directory, name + '.csv'), 'w', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(['id'])
                writer.writerow([1])

    def test_validate_queries_both_databases_and_rejects_mismatch(self):
        calls = []

        def runner(command, env, timeout):
            calls.append(command)
            return 0, ('2\n' if '--database' in command else '1\n'), ''

        config = {'ymatrix': {'psql_path': 'psql', 'host': 'h', 'port': 1, 'user': 'u', 'database': 'd'},
                  'mysql': {'transport': 'local_default', 'user': 'root', 'database': 'benchmark_mvp'},
                  'benchmark': {'timeout_seconds': 0}}
        rows = validate_databases(config, self.directory, runner=runner)
        self.assertEqual(len(calls), 8)
        self.assertTrue(all(row['match'] is False for row in rows))
        with self.assertRaises(ValueError):
            validate_databases(config, self.directory, runner=runner, raise_on_mismatch=True)
