import csv
import os
import tempfile
import unittest

from src.generator import SIZES
from src.loader import load_database


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.directory, name))
                                 for name in os.listdir(self.directory)])
        for name, size in SIZES.items():
            path = os.path.join(self.directory, name + '.csv')
            with open(path, 'w', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(['a', 'b', 'c', 'd'])
                for index in range(1001 if name == 'customer' else 2):
                    writer.writerow([index, "O'Reilly", 1, '1.00'])

    def test_load_reads_all_tables_and_limits_insert_batches(self):
        statements = []

        def runner(command, env, timeout):
            statements.append(command[-1])
            return 0, '', ''

        counts = load_database({'mysql': {'transport': 'local_default', 'user': 'root',
                                          'password': '', 'database': 'benchmark_mvp'},
                                'benchmark': {'timeout_seconds': 0}},
                               'mysql', self.directory, 'schema/mysql.sql', runner=runner)
        self.assertEqual(set(counts), set(SIZES))
        inserts = [sql for sql in statements if sql.startswith('INSERT INTO')]
        self.assertGreater(len(inserts), 0)
        self.assertTrue(all(sql.count('),') < 500 for sql in inserts))
        joined = '\n'.join(statements)
        self.assertIn('tpch_customer', joined)
        self.assertNotIn('COPY', joined.upper())
        self.assertNotIn('LOAD DATA', joined.upper())
        self.assertNotIn("['", joined)

    def test_load_ensures_same_three_logical_indexes(self):
        statements = []

        def runner(command, env, timeout):
            statements.append(command[-1])
            return 0, '0\n', ''

        config = {'mysql': {'transport': 'local_default', 'user': 'root', 'password': '',
                            'database': 'benchmark_mvp'},
                  'benchmark': {'timeout_seconds': 60}}
        load_database(config, 'mysql', self.directory, 'schema/mysql.sql', runner=runner)
        joined = '\n'.join(statements)
        self.assertIn('idx_tpch_orders_orderdate', joined)
        self.assertIn('idx_tpch_lineitem_orderkey', joined)
        self.assertIn('idx_tpch_lineitem_partkey', joined)
        self.assertEqual(joined.count('CREATE INDEX idx_tpch_'), 8)
