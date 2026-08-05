import csv
import os
import tempfile
import unittest

from src.reporter import write_benchmark_detail, write_benchmark_log, write_markdown_report


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

    def test_report_contains_comparison_slow_sql_failures_and_limitations(self):
        path = os.path.join(self.directory, 'report.md')
        write_markdown_report(path, {'ymatrix': {'q01': {'avg': 2, 'min': 1, 'max': 3, 'p95': 3,
                                                         'success_rate': 1}},
                                     'mysql': {'q01': {'avg': 4, 'min': 3, 'max': 5, 'p95': 5,
                                                       'success_rate': 1}}},
                             comparisons=[{'query_id': 'q01', 'faster_database': 'ymatrix',
                                           'faster_by_percent': 100, 'ymatrix_to_mysql_ratio': 0.5}],
                             correctness=[{'query_id': 'q01', 'match': True, 'summary': 'equal'}],
                             metadata={'data_sizes': {'part': 500}, 'measurement_rounds': 5})
        write_benchmark_log(os.path.join(self.directory, 'benchmark.log'), [{'query_id': 'q01',
                                                                               'database': 'mysql',
                                                                               'success': False,
                                                                               'error_message': 'timeout'}])
        with open(path, 'r') as handle:
            content = handle.read()
        self.assertIn('Top 慢 SQL', content)
        self.assertIn('失败 SQL 分类', content)
        self.assertIn('查询结果一致性', content)


if __name__ == '__main__':
    unittest.main()
