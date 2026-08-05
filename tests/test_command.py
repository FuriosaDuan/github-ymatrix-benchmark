import unittest

from src.command import CommandError, build_mysql_command, run_command


class CommandTests(unittest.TestCase):
    def test_local_default_does_not_add_connection_or_password_flags(self):
        command, env = build_mysql_command({'transport': 'local_default', 'user': 'root', 'password': ''}, 'select 1')
        self.assertNotIn('--host', command)
        self.assertNotIn('--port', command)
        self.assertNotIn('-p', command)
        self.assertNotIn('MYSQL_PWD', env)

    def test_tcp_password_is_only_in_environment(self):
        command, env = build_mysql_command({'transport': 'tcp', 'host': '127.0.0.1', 'port': 3306,
                                            'user': 'root', 'password': 'secret'}, 'select 1')
        self.assertNotIn('secret', ' '.join(command))
        self.assertEqual(env['MYSQL_PWD'], 'secret')

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


if __name__ == '__main__':
    unittest.main()
