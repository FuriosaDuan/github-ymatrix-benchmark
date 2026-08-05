import os
import tempfile
import unittest

from src.discovery import discover_sql


class DiscoveryTests(unittest.TestCase):
    def test_discovers_only_non_recursive_sql_files_in_name_order(self):
        directory = tempfile.mkdtemp()
        with open(os.path.join(directory, 'q02.sql'), 'w') as handle:
            handle.write('SELECT 2')
        with open(os.path.join(directory, 'q01.sql'), 'w') as handle:
            handle.write('SELECT 1')
        os.mkdir(os.path.join(directory, 'nested'))
        with open(os.path.join(directory, 'nested', 'q00.sql'), 'w') as handle:
            handle.write('SELECT 0')
        with open(os.path.join(directory, 'notes.txt'), 'w') as handle:
            handle.write('ignore')
        self.assertEqual([item[0] for item in discover_sql(directory)], ['q01', 'q02'])


if __name__ == '__main__':
    unittest.main()
