"""Run real client preflight checks and execute schema initialization SQL."""

import os
import shutil

from .command import CommandError, build_mysql_command, build_psql_command, run_command
from .database import execute_query


def read_sql(path):
    with open(path, 'r') as handle:
        return handle.read()


def preflight(config, runner=None):
    """Verify both clients, connections, versions, and the MySQL target database."""
    psql_path = config['ymatrix']['psql_path']
    if not os.path.isfile(psql_path) or not os.access(psql_path, os.X_OK):
        raise ValueError('psql 不存在或不可执行: ' + psql_path)
    if not shutil.which('mysql'):
        raise ValueError('mysql 命令不在 PATH 中')
    ymatrix_output, _ = execute_query(config, 'ymatrix', 'SELECT version()', runner=runner)
    try:
        mysql_output, _ = execute_query(config, 'mysql', 'SELECT VERSION()', runner=runner)
    except CommandError:
        ensure_mysql_database(config, runner=runner)
        mysql_output, _ = execute_query(config, 'mysql', 'SELECT VERSION()', runner=runner)
    return {'status': 'ready',
            'message': 'YMatrix client/database ready; MySQL client/database ready',
            'ymatrix_version': ymatrix_output.strip(),
            'mysql_version': mysql_output.strip()}


def ensure_mysql_database(config, runner=None):
    """Create the configured project database if it does not already exist."""
    mysql = config['mysql']
    command, env = build_mysql_command(mysql, 'CREATE DATABASE IF NOT EXISTS {};'.format(mysql['database']),
                                       include_database=False)
    return run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 60), runner=runner)


def execute_sql(config, database, sql, runner=None):
    output, _ = execute_query(config, database, sql, runner=runner)
    return output


def load_schema(config, database, schema_path, runner=None):
    return execute_sql(config, database, read_sql(schema_path), runner=runner)
