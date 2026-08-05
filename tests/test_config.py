import json
import os
import tempfile
import unittest

from src.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def write_config(self, data):
        handle = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, handle)
        handle.close()
        self.addCleanup(lambda: os.unlink(handle.name))
        return handle.name

    def test_missing_required_key_is_rejected(self):
        path = self.write_config({'ymatrix': {}, 'mysql': {}, 'benchmark': {}})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_transport_is_rejected(self):
        data = {'ymatrix': {}, 'mysql': {'transport': 'udp'}, 'benchmark': {}}
        with self.assertRaises(ConfigError):
            load_config(self.write_config(data))

    def test_tcp_requires_host_and_port(self):
        data = {'ymatrix': {}, 'mysql': {'transport': 'tcp'}, 'benchmark': {}}
        with self.assertRaises(ConfigError):
            load_config(self.write_config(data))

    def test_mysql_database_is_required(self):
        data = {'ymatrix': {'psql_path': 'psql'}, 'mysql': {'transport': 'local_default'},
                'benchmark': {}}
        with self.assertRaises(ConfigError):
            load_config(self.write_config(data))

    def test_concurrency_must_be_one(self):
        data = {'ymatrix': {}, 'mysql': {}, 'benchmark': {'concurrency': 2}}
        with self.assertRaises(ConfigError):
            load_config(self.write_config(data))

    def test_v3_defaults_and_session_sql(self):
        data = {'ymatrix': {'psql_path': 'psql'}, 'mysql': {'transport': 'local_default',
                'database': 'benchmark_mvp'}, 'benchmark': {}, 'paths': {}}
        config = load_config(self.write_config(data))
        self.assertEqual(config['benchmark']['warmup_rounds'], 1)
        self.assertEqual(config['benchmark']['measurement_rounds'], 5)
        self.assertEqual(config['benchmark']['timeout_seconds'], 60)
        self.assertEqual(config['mysql']['session_sql'], [])
        self.assertEqual(config['paths']['mysql_sql_dir'], 'sql/mysql')


if __name__ == '__main__':
    unittest.main()
