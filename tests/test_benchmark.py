import os
import tempfile
import unittest
from unittest import mock

from src.benchmark import benchmark_database, build_comparisons, compare_result_sets


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(lambda: [os.remove(os.path.join(self.directory, name))
                                 for name in os.listdir(self.directory)])
        for query_id in ('q01', 'q02', 'q03'):
            with open(os.path.join(self.directory, query_id + '.sql'), 'w') as handle:
                handle.write('SELECT 1')

    def test_warmup_not_recorded_and_timestamps_have_timezone(self):
        config = {'mysql': {'transport': 'local_default', 'user': 'root', 'database': 'benchmark_mvp'},
                  'benchmark': {'warmup_rounds': 1, 'measurement_rounds': 1, 'timeout_seconds': 0}}
        ticks = iter(range(100, 120))

        def runner(command, env, timeout):
            return 0, '', ''

        with mock.patch('src.benchmark.time.monotonic', side_effect=lambda: next(ticks)):
            rows, summaries = benchmark_database(config, 'mysql', self.directory, runner=runner)
        self.assertEqual(len(rows), 3)
        self.assertNotIn('warmup', rows[0])
        self.assertRegex(rows[0]['start_time'], r'[-+]\d\d:\d\d$')
        self.assertEqual(rows[0]['elapsed_ms'], 1000.0)

    def test_failed_elapsed_is_excluded_from_summary(self):
        config = {'mysql': {'transport': 'local_default', 'user': 'root', 'database': 'benchmark_mvp'},
                  'benchmark': {'warmup_rounds': 0, 'measurement_rounds': 2, 'timeout_seconds': 0}}
        def runner(command, env, timeout):
            if not hasattr(runner, 'calls'):
                runner.calls = 0
            runner.calls += 1
            return (1, '', 'failed') if runner.calls == 2 else (0, '', '')
        with mock.patch('src.benchmark.time.monotonic', side_effect=[1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13]):
            rows, summaries = benchmark_database(config, 'mysql', self.directory, runner=runner)
        self.assertFalse(rows[0]['success'])
        self.assertEqual(summaries['mysql']['q01']['avg'], 2000.0)

    def test_result_consistency_and_performance_comparison_are_explicit(self):
        results = {'ymatrix': {'q01': {'rows': [['1']], 'error_message': ''}},
                   'mysql': {'q01': {'rows': [['1.0']], 'error_message': ''}}}
        comparisons = compare_result_sets(results)
        self.assertTrue(comparisons[0]['match'])
        perf = build_comparisons({'ymatrix': {'q01': {'avg': 2, 'success_rate': 1}},
                                  'mysql': {'q01': {'avg': 4, 'success_rate': 1}}})
        self.assertEqual(perf[0]['faster_database'], 'ymatrix')
        self.assertEqual(perf[0]['faster_by_percent'], 100)
