import csv
import os

from .generator import SIZES
from .initializer import execute_sql
from .loader import TABLES


def validate_generated_data(output_dir, enforce_sizes=True):
    result = {}
    for name, expected in SIZES.items():
        path = os.path.join(output_dir, name + '.csv')
        if not os.path.exists(path):
            raise ValueError('缺少生成文件: ' + path)
        with open(path, 'r', newline='') as handle:
            count = max(0, sum(1 for _ in csv.reader(handle)) - 1)
        if enforce_sizes and count != expected:
            raise ValueError('{} 行数为 {}，期望 {}'.format(name, count, expected))
        result[name] = count
    return result


def _count(config, database, table, runner=None):
    output = execute_sql(config, database, 'SELECT COUNT(*) FROM {};'.format(table), runner=runner)
    for line in output.splitlines():
        if line.strip():
            return int(line.strip().split()[0])
    raise ValueError('COUNT 查询无结果: ' + table)


def validate_databases(config, data_dir, runner=None, raise_on_mismatch=False):
    expected = validate_generated_data(data_dir, enforce_sizes=False)
    rows = []
    for name, table in TABLES.items():
        ymatrix = _count(config, 'ymatrix', table, runner=runner)
        mysql = _count(config, 'mysql', table, runner=runner)
        match = expected[name] == ymatrix == mysql
        rows.append({'table': table, 'expected': expected[name], 'ymatrix': ymatrix,
                     'mysql': mysql, 'match': match})
    if raise_on_mismatch and not all(row['match'] for row in rows):
        raise ValueError('数据库行数校验失败')
    return rows
