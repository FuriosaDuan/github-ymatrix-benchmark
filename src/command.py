"""Build database client commands and execute them without exposing passwords."""

import os
import subprocess


class CommandError(Exception):
    pass


def build_mysql_command(mysql, sql, include_database=True):
    command = ['mysql', '--batch', '--raw', '--skip-column-names', '-u', str(mysql.get('user', 'root')),
               '-e', sql]
    if include_database:
        command[6:6] = ['--database', str(mysql['database'])]
    env = {}
    if mysql.get('transport') == 'tcp':
        command[1:1] = ['--host', str(mysql['host']), '--port', str(mysql['port'])]
        if mysql.get('password'):
            env['MYSQL_PWD'] = str(mysql['password'])
    return command, env


def build_psql_command(ymatrix, sql):
    command = [str(ymatrix.get('psql_path', 'psql')), '-X', '-v', 'ON_ERROR_STOP=1',
               '--no-align', '--tuples-only', '-F', '\t', '-P', 'null=NULL',
               '-h', str(ymatrix.get('host', '127.0.0.1')), '-p', str(ymatrix.get('port', 5432)),
               '-U', str(ymatrix.get('user', 'mxadmin')), '-d', str(ymatrix.get('database', 'postgres')), '-c', sql]
    env = {}
    if ymatrix.get('password'):
        env['PGPASSWORD'] = str(ymatrix['password'])
    return command, env


def _default_runner(command, env, timeout):
    merged = os.environ.copy()
    merged.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, env=merged)
    try:
        stdout, stderr = process.communicate(timeout=timeout or None)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise TimeoutError('命令执行超时')
    return process.returncode, stdout, stderr


def run_command(command, env=None, timeout=0, runner=None):
    """Run a client command, enforce timeout, redact secrets, and return stdout."""
    try:
        result = (runner or _default_runner)(command, env or {}, timeout)
    except (TimeoutError, subprocess.TimeoutExpired) as exc:
        raise CommandError(str(exc))
    except OSError as exc:
        raise CommandError('无法启动命令: ' + str(exc))
    code, stdout, stderr = result
    if code != 0:
        message = (stderr or stdout or '未知错误').strip()
        for secret in (env or {}).values():
            if secret:
                message = message.replace(str(secret), '[REDACTED]')
        raise CommandError('命令退出码 {}: {}'.format(code, message))
    return stdout
