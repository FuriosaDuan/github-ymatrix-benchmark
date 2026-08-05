import json
import os


class ConfigError(Exception):
    pass


def load_config(path):
    if not os.path.exists(path):
        raise ConfigError('配置文件不存在: ' + path)
    with open(path, 'r') as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ConfigError('配置必须是 JSON 对象')
    for key in ('ymatrix', 'mysql', 'benchmark'):
        if key not in data:
            raise ConfigError('缺少配置项: ' + key)
    if not data['ymatrix'].get('psql_path'):
        raise ConfigError('缺少配置项: ymatrix.psql_path')
    mysql = data['mysql']
    if not mysql.get('database'):
        raise ConfigError('缺少配置项: mysql.database')
    transport = mysql.get('transport', 'local_default')
    if transport not in ('local_default', 'tcp'):
        raise ConfigError('mysql.transport 必须是 local_default 或 tcp')
    if transport == 'tcp' and (not mysql.get('host') or not mysql.get('port')):
        raise ConfigError('mysql.transport=tcp 时必须配置 host 和 port')
    benchmark = data['benchmark']
    if int(benchmark.get('concurrency', 1)) != 1:
        raise ConfigError('MVP 仅支持 concurrency=1')
    result = dict(data)
    result['mysql'] = dict(mysql)
    result['mysql'].setdefault('user', 'root')
    result['mysql'].setdefault('password', '')
    result['benchmark'] = dict(benchmark)
    result['benchmark'].setdefault('warmup_rounds', 1)
    result['benchmark'].setdefault('measurement_rounds', 3)
    result['benchmark'].setdefault('timeout_seconds', 0)
    result.setdefault('paths', {})
    return result
