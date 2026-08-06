"""Load the same generated CSV rows into both databases with safe batched INSERTs."""

import csv
import os
from collections import OrderedDict

from .initializer import execute_sql


TABLES = OrderedDict([
    ('region', 'tpch_region'), ('nation', 'tpch_nation'),
    ('supplier', 'tpch_supplier'), ('customer', 'tpch_customer'),
    ('part', 'tpch_part'), ('partsupp', 'tpch_partsupp'),
    ('orders', 'tpch_orders'), ('lineitem', 'tpch_lineitem')])

DELETE_ORDER = ('lineitem', 'orders', 'partsupp', 'part', 'customer', 'supplier', 'nation', 'region')

INDEXES = (
    ('idx_tpch_nation_regionkey', 'tpch_nation', 'n_regionkey'),
    ('idx_tpch_supplier_nationkey', 'tpch_supplier', 's_nationkey'),
    ('idx_tpch_customer_nationkey', 'tpch_customer', 'c_nationkey'),
    ('idx_tpch_orders_orderdate', 'tpch_orders', 'o_orderdate'),
    ('idx_tpch_orders_custkey', 'tpch_orders', 'o_custkey'),
    ('idx_tpch_lineitem_orderkey', 'tpch_lineitem', 'l_orderkey'),
    ('idx_tpch_lineitem_partkey', 'tpch_lineitem', 'l_partkey'),
    ('idx_tpch_lineitem_suppkey', 'tpch_lineitem', 'l_suppkey')
)


def sql_literal(value):
    """Return a safely quoted SQL string literal or NULL for an empty value."""
    if value is None or value == '':
        return 'NULL'
    text = str(value).replace('\\', '\\\\').replace("'", "''")
    return "'" + text + "'"


def _insert_sql(table, columns, rows):
    values = []
    for row in rows:
        values.append('(' + ', '.join(sql_literal(value) for value in row) + ')')
    return 'INSERT INTO {} ({}) VALUES {};'.format(table, ', '.join(columns), ', '.join(values))


def _batches(rows, size):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def ensure_indexes(config, database, runner=None):
    for name, table, column in INDEXES:
        if database == 'ymatrix':
            sql = 'CREATE INDEX IF NOT EXISTS {} ON {}({});'.format(name, table, column)
            execute_sql(config, database, sql, runner=runner)
            continue
        check = ("SELECT COUNT(*) FROM information_schema.statistics "
                 "WHERE table_schema = DATABASE() AND table_name = '{}' AND index_name = '{}';"
                 .format(table, name))
        output = execute_sql(config, database, check, runner=runner).strip()
        if not output or int(output.splitlines()[-1]) == 0:
            execute_sql(config, database,
                        'CREATE INDEX {} ON {}({});'.format(name, table, column), runner=runner)


def load_database(config, database, data_dir, schema_path, runner=None, batch_size=500):
    """Initialize, clear, batch-load, and index all project tables in one database."""
    with open(schema_path, 'r') as schema_handle:
        schema_sql = schema_handle.read()
    execute_sql(config, database, schema_sql, runner=runner)
    counts = {}
    for name in DELETE_ORDER:
        execute_sql(config, database, 'DELETE FROM {};'.format(TABLES[name]), runner=runner)
    for name, table in TABLES.items():
        path = os.path.join(data_dir, name + '.csv')
        if not os.path.exists(path):
            raise ValueError('缺少数据文件: ' + path)
        with open(path, 'r', newline='') as handle:
            reader = csv.reader(handle)
            columns = next(reader)
            rows = list(reader)
        for batch in _batches(rows, batch_size):
            execute_sql(config, database, _insert_sql(table, columns, batch), runner=runner)
        counts[name] = len(rows)
    ensure_indexes(config, database, runner=runner)
    return counts
