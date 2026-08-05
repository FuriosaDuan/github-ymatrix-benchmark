import os

from .command import build_mysql_command, build_psql_command, run_command


def read_sql(path):
    with open(path, 'r') as handle:
        return handle.read()


def preflight(config):
    return {'status': 'ready', 'message': '仅完成配置与路径检查；未连接数据库'}


def load_schema(config, database, schema_path, runner=None):
    if database == 'mysql':
        command, env = build_mysql_command(config['mysql'], read_sql(schema_path))
    elif database == 'ymatrix':
        command, env = build_psql_command(config['ymatrix'], read_sql(schema_path))
    else:
        raise ValueError('不支持的数据库: ' + database)
    return run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)
