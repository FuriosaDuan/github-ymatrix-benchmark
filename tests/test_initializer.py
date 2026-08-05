import os
import tempfile
import unittest
from unittest import mock

from src.initializer import preflight


class InitializerTests(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.close()
        self.psql_path = handle.name
        self.addCleanup(lambda: os.unlink(self.psql_path))
        self.config = {
            'ymatrix': {'psql_path': self.psql_path, 'host': '127.0.0.1', 'port': 5432,
                        'user': 'mxadmin', 'database': 'postgres', 'password': ''},
            'mysql': {'transport': 'local_default', 'user': 'root', 'password': '',
                      'database': 'benchmark_mvp'},
            'benchmark': {'timeout_seconds': 0}
        }

    def test_preflight_executes_both_version_queries(self):
        calls = []

        def runner(command, env, timeout):
            calls.append((command, env))
            return 0, 'PostgreSQL version', ''

        with mock.patch('src.initializer.shutil.which', return_value='mysql'), \
             mock.patch('src.initializer.os.access', return_value=True):
            result = preflight(self.config, runner=runner)
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(len(calls), 2)
        self.assertIn('SELECT version()', ' '.join(calls[0][0]))
        self.assertIn('SELECT VERSION()', ' '.join(calls[1][0]))

    def test_preflight_rejects_missing_mysql(self):
        with mock.patch('src.initializer.shutil.which', return_value=None), \
             mock.patch('src.initializer.os.access', return_value=True):
            with self.assertRaises(Exception):
                preflight(self.config, runner=lambda *args: (0, '', ''))
