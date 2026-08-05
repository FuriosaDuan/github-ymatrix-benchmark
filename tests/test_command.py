import unittest

from src.command import CommandError, build_mysql_command, run_command
from src.command import build_psql_command


class CommandTests(unittest.TestCase):
    def test_local_default_does_not_add_connection_or_password_flags(self):
        command, env = build_mysql_command({'transport': 'local_default', 'user': 'root', 'password': '',
                                            'database': 'benchmark_mvp'}, 'select 1')
        self.assertNotIn('--host', command)
        self.assertNotIn('--port', command)
        self.assertNotIn('-p', command)
        self.assertNotIn('MYSQL_PWD', env)
        self.assertIn('--database', command)
        self.assertIn('benchmark_mvp', command)

    def test_tcp_password_is_only_in_environment(self):
        command, env = build_mysql_command({'transport': 'tcp', 'host': '127.0.0.1', 'port': 3306,
                                            'user': 'root', 'password': 'secret', 'database': 'benchmark_mvp'}, 'select 1')
        self.assertNotIn('secret', ' '.join(command))
        self.assertEqual(env['MYSQL_PWD'], 'secret')
        self.assertIn('benchmark_mvp', command)

    def test_nonzero_subprocess_exit_is_reported(self):
        def runner(*args, **kwargs):
            return 2, '', 'bad query'
        with self.assertRaises(CommandError):
            run_command(['mysql'], runner=runner)

    def test_timeout_is_reported(self):
        def runner(*args, **kwargs):
            raise TimeoutError('timed out')
        with self.assertRaises(CommandError):
            run_command(['mysql'], runner=runner)

    def test_password_is_redacted_from_command_error(self):
        def runner(*args, **kwargs):
            return 1, '', 'password=secret'
        with self.assertRaises(CommandError) as context:
            run_command(['mysql'], env={'MYSQL_PWD': 'secret'}, runner=runner)
        self.assertNotIn('secret', str(context.exception))

    def test_v3_client_output_flags(self):
        mysql, _ = build_mysql_command({'transport': 'local_default', 'user': 'root',
                                        'password': '', 'database': 'benchmark_mvp'}, 'SELECT 1')
        psql, _ = build_psql_command({'psql_path': 'psql', 'host': 'h', 'port': 1,
                                      'user': 'u', 'database': 'd'}, 'SELECT 1')
        self.assertIn('--skip-column-names', mysql)
        for flag in ('-X', '--no-align', '--tuples-only'):
            self.assertIn(flag, psql)


if __name__ == '__main__':
    unittest.main()
