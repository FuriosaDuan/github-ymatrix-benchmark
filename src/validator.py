"""Validate generated relationships and reconcile CSV and database row counts."""

import csv
import os

from .generator import SIZES
from .initializer import execute_sql
from .loader import TABLES


def _rows(output_dir, name):
    path = os.path.join(output_dir, name + '.csv')
    if not os.path.exists(path):
        raise ValueError('缺少生成文件: ' + path)
    with open(path, 'r', newline='', encoding='utf-8') as handle:
        for row in csv.DictReader(handle):
            yield row


def validate_relationships(output_dir):
    """Reject generated data whose supply-chain foreign-key relationships break."""
    regions = set(int(row['r_regionkey']) for row in _rows(output_dir, 'region'))
    nations = set()
    for row in _rows(output_dir, 'nation'):
        if int(row['n_regionkey']) not in regions:
            raise ValueError('nation 引用了不存在的 region')
        nations.add(int(row['n_nationkey']))
    suppliers = set()
    for row in _rows(output_dir, 'supplier'):
        if int(row['s_nationkey']) not in nations:
            raise ValueError('supplier 引用了不存在的 nation')
        suppliers.add(int(row['s_suppkey']))
    customers = set()
    for row in _rows(output_dir, 'customer'):
        if int(row['c_nationkey']) not in nations:
            raise ValueError('customer 引用了不存在的 nation')
        customers.add(int(row['c_custkey']))
    parts = set(int(row['p_partkey']) for row in _rows(output_dir, 'part'))
    supplied = set()
    for row in _rows(output_dir, 'partsupp'):
        pair = (int(row['ps_partkey']), int(row['ps_suppkey']))
        if pair[0] not in parts or pair[1] not in suppliers:
            raise ValueError('partsupp 引用了不存在的 part 或 supplier')
        supplied.add(pair)
    orders = set()
    for row in _rows(output_dir, 'orders'):
        if int(row['o_custkey']) not in customers:
            raise ValueError('orders 引用了不存在的 customer')
        orders.add(int(row['o_orderkey']))
    for row in _rows(output_dir, 'lineitem'):
        if int(row['l_orderkey']) not in orders:
            raise ValueError('lineitem 引用了不存在的 orders')
        if (int(row['l_partkey']), int(row['l_suppkey'])) not in supplied:
            raise ValueError('lineitem 的商品与供应商不存在供货关系')
    return True


def validate_generated_data(output_dir, enforce_sizes=True, expected_sizes=None,
                            enforce_relationships=True):
    """Return CSV row counts after relationship and optional scale checks."""
    expected_sizes = expected_sizes or SIZES
    result = {}
    for name, expected in expected_sizes.items():
        path = os.path.join(output_dir, name + '.csv')
        if not os.path.exists(path):
            raise ValueError('缺少生成文件: ' + path)
        with open(path, 'r', newline='', encoding='utf-8') as handle:
            count = max(0, sum(1 for _ in csv.reader(handle)) - 1)
        if enforce_sizes and count != expected:
            raise ValueError('{} 行数为 {}，期望 {}'.format(name, count, expected))
        result[name] = count
    if enforce_relationships:
        validate_relationships(output_dir)
    return result


def _count(config, database, table, runner=None):
    output = execute_sql(config, database, 'SELECT COUNT(*) FROM {};'.format(table), runner=runner)
    for line in output.splitlines():
        if line.strip():
            return int(line.strip().split()[0])
    raise ValueError('COUNT 查询无结果: ' + table)


def validate_databases(config, data_dir, runner=None, raise_on_mismatch=False):
    """Compare expected CSV counts with YMatrix and MySQL COUNT(*) results."""
    expected = validate_generated_data(data_dir, enforce_sizes=False, enforce_relationships=True)
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
