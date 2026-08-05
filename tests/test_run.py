import unittest
from unittest import mock

import run


class RunTests(unittest.TestCase):
    def test_all_runs_strict_order(self):
        events = []
        config = {'paths': {'data_dir': 'data', 'results_dir': 'results'}}
        with mock.patch.object(run, 'load_config', return_value=config), \
             mock.patch.object(run.platform, 'system', return_value='Linux'), \
             mock.patch.object(run, 'preflight', side_effect=lambda c: events.append('preflight')), \
             mock.patch.object(run, 'generate_data', side_effect=lambda p: events.append('generate')), \
             mock.patch.object(run, 'run_load', side_effect=lambda *args: events.append('load')), \
             mock.patch.object(run, 'run_validate', side_effect=lambda *args: events.append('validate')), \
             mock.patch.object(run, 'run_benchmark', side_effect=lambda *args: events.append('benchmark')):
            self.assertEqual(run.main(['all', '--config', 'config.local.json']), 0)
        self.assertEqual(events, ['preflight', 'generate', 'load', 'validate', 'benchmark'])
