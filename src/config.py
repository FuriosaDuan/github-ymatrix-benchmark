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
    result['mysql'].setdefault('database', 'benchmark_mvp')
    result['mysql'].setdefault('user', 'root')
    result['mysql'].setdefault('password', '')
    result['benchmark'] = dict(benchmark)
    result['benchmark'].setdefault('warmup_rounds', 1)
    result['benchmark'].setdefault('scale_factor', 0.01)
    result['benchmark'].setdefault('measurement_rounds', 5)
    result['benchmark'].setdefault('timeout_seconds', 60)
    if float(result['benchmark']['scale_factor']) <= 0:
        raise ConfigError('benchmark.scale_factor 必须大于 0')
    if int(result['benchmark']['warmup_rounds']) < 0 or int(result['benchmark']['measurement_rounds']) <= 0:
        raise ConfigError('warmup_rounds 必须 >= 0，measurement_rounds 必须 > 0')
    result['ymatrix'] = dict(data['ymatrix'])
    result['ymatrix'].setdefault('session_sql', [])
    result['mysql'].setdefault('session_sql', [])
    result.setdefault('paths', {})
    result['paths'] = dict(result['paths'])
    result['paths'].setdefault('mysql_sql_dir', 'sql/mysql')
    result['paths'].setdefault('ymatrix_sql_dir', 'sql/ymatrix')
    result['paths'].setdefault('data_dir', 'data')
    result['paths'].setdefault('results_dir', 'results')
    return result
