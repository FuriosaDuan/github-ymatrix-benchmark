import csv
import os

from .initializer import execute_sql


TABLES = {
    'customer': 'bench_customer',
    'part': 'bench_part',
    'orders': 'bench_orders',
    'lineitem': 'bench_lineitem'
}


def sql_literal(value):
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


def load_database(config, database, data_dir, schema_path, runner=None, batch_size=500):
    with open(schema_path, 'r') as schema_handle:
        schema_sql = schema_handle.read()
    execute_sql(config, database, schema_sql, runner=runner)
    counts = {}
    for name, table in TABLES.items():
        execute_sql(config, database, 'DELETE FROM {};'.format(table), runner=runner)
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
    return counts
