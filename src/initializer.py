import os
import shutil

from .command import build_mysql_command, build_psql_command, run_command


def read_sql(path):
    with open(path, 'r') as handle:
        return handle.read()


def preflight(config, runner=None):
    psql_path = config['ymatrix']['psql_path']
    if not os.path.isfile(psql_path) or not os.access(psql_path, os.X_OK):
        raise ValueError('psql 不存在或不可执行: ' + psql_path)
    if not shutil.which('mysql'):
        raise ValueError('mysql 命令不在 PATH 中')
    execute_sql(config, 'ymatrix', 'SELECT version();', runner=runner)
    execute_sql(config, 'mysql', 'SELECT VERSION();', runner=runner)
    return {'status': 'ready', 'message': 'YMatrix 和 MySQL preflight 连接成功'}


def execute_sql(config, database, sql, runner=None):
    if database == 'mysql':
        command, env = build_mysql_command(config['mysql'], sql)
    elif database == 'ymatrix':
        command, env = build_psql_command(config['ymatrix'], sql)
    else:
        raise ValueError('不支持的数据库: ' + database)
    return run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)


def load_schema(config, database, schema_path, runner=None):
    return execute_sql(config, database, read_sql(schema_path), runner=runner)
