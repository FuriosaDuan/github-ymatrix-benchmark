"""Repository-level tests for files that must stay outside version control."""

import os
import subprocess
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RepositoryHygieneTests(unittest.TestCase):
    def test_private_and_generated_paths_are_ignored(self):
        """Git must ignore credentials, generated output, and private notes."""
        paths = (
            'config.local.json',
            'data/generated.csv',
            'results/benchmark_report.md',
            'acceptance-results/example/run1/benchmark.log',
            'docs/interview_demo.md',
            'docs/project_demo.md',
        )
        process = subprocess.Popen(
            ['git', 'check-ignore', '-z', '--stdin'],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        payload = ('\0'.join(paths) + '\0').encode('utf-8')
        stdout, stderr = process.communicate(payload)
        ignored = [item.decode('utf-8') for item in stdout.split(b'\0') if item]

        self.assertEqual(0, process.returncode, stderr.decode('utf-8'))
        self.assertEqual(list(paths), ignored)


if __name__ == '__main__':
    unittest.main()
