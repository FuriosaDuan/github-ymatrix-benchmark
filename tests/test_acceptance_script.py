import os
import unittest


class AcceptanceScriptTests(unittest.TestCase):
    def test_linux_acceptance_is_fail_fast_and_runs_complete_order_twice(self):
        path = os.path.join('scripts', 'acceptance_linux.sh')
        self.assertTrue(os.path.isfile(path))
        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()
        self.assertIn('set -eu', content)
        commands = ['compileall', 'unittest', 'preflight', 'generate', 'load', 'validate']
        positions = [content.index(value) for value in commands]
        self.assertEqual(positions, sorted(positions))
        self.assertGreaterEqual(content.count('run.py benchmark'), 2)
        for filename in ('benchmark_detail.csv', 'benchmark_report.md',
                         'environment.md', 'benchmark.log'):
            self.assertIn(filename, content)
        upper = content.upper()
        for prohibited in ('DROP DATABASE', 'DROP SCHEMA', 'LOAD DATA LOCAL INFILE'):
            self.assertNotIn(prohibited, upper)
        self.assertNotIn('cat config.local.json', content)


if __name__ == '__main__':
    unittest.main()
