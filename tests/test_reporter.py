import csv
import os
import tempfile
import unittest

from src.reporter import write_benchmark_detail, write_markdown_report


class ReporterTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.directory, name)) for name in os.listdir(self.directory)])

    def test_csv_header_has_stable_order(self):
        path = os.path.join(self.directory, 'detail.csv')
        write_benchmark_detail(path, [{'database': 'mysql', 'query_id': 'q01', 'round': 1,
                                       'start_time': 'a', 'end_time': 'b', 'elapsed_ms': 1,
                                       'success': True, 'error_message': ''}])
        with open(path, 'r', newline='') as handle:
            self.assertEqual(next(csv.reader(handle)), ['database', 'query_id', 'round', 'start_time',
                                                         'end_time', 'elapsed_ms', 'success', 'error_message'])

    def test_markdown_report_contains_scope_disclaimer(self):
        path = os.path.join(self.directory, 'report.md')
        write_markdown_report(path, {'mysql': {'q01': {'avg': 1}}})
        with open(path, 'r') as handle:
            content = handle.read()
        self.assertIn('不属于标准 TPC-H 测试', content)


if __name__ == '__main__':
    unittest.main()
