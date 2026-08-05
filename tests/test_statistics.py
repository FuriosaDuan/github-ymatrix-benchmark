import unittest

from src.statistics import summarize, percentile_nearest_rank


class StatisticsTests(unittest.TestCase):
    def test_p95_uses_nearest_rank(self):
        self.assertEqual(percentile_nearest_rank([10, 20, 30, 40], 0.95), 40)

    def test_summary_contains_required_metrics(self):
        result = summarize([10, 20, 30], [True, True, False])
        self.assertEqual(result['avg'], 20)
        self.assertEqual(result['min'], 10)
        self.assertEqual(result['max'], 30)
        self.assertEqual(result['success_rate'], 2 / 3.0)


if __name__ == '__main__':
    unittest.main()
