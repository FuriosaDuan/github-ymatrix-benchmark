import csv
import os
import time

from .command import build_mysql_command, build_psql_command, run_command
from .statistics import summarize


def load_queries(directory):
    result = {}
    for query_id in ('q01', 'q02', 'q03'):
        path = os.path.join(directory, query_id + '.sql')
        with open(path, 'r') as handle:
            result[query_id] = handle.read()
    return result


def benchmark_mysql(config, sql_dir, rounds=None, runner=None):
    rounds = rounds or int(config['benchmark'].get('measurement_rounds', 3))
    rows = []
    summaries = {}
    for query_id, sql in sorted(load_queries(sql_dir).items()):
        elapsed = []
        successes = []
        for number in range(1, rounds + 1):
            start = time.time()
            error = ''
            success = True
            try:
                command, env = build_mysql_command(config['mysql'], sql)
                run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)
            except Exception as exc:
                success = False
                error = str(exc)
            end = time.time()
            elapsed_ms = (end - start) * 1000.0
            elapsed.append(elapsed_ms)
            successes.append(success)
            rows.append({'database': 'mysql', 'query_id': query_id, 'round': number,
                         'start_time': str(start), 'end_time': str(end), 'elapsed_ms': elapsed_ms,
                         'success': success, 'error_message': error})
        summaries[query_id] = summarize(elapsed, successes)
    return rows, {'mysql': summaries}


def benchmark_database(config, database, sql_dir, rounds=None, runner=None):
    rounds = rounds or int(config['benchmark'].get('measurement_rounds', 3))
    rows = []
    summaries = {}
    queries = load_queries(sql_dir)
    for query_id, sql in sorted(queries.items()):
        elapsed = []
        successes = []
        for number in range(1, rounds + 1):
            start = time.time()
            success = True
            error = ''
            try:
                if database == 'mysql':
                    command, env = build_mysql_command(config['mysql'], sql)
                else:
                    command, env = build_psql_command(config['ymatrix'], sql)
                run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)
            except Exception as exc:
                success = False
                error = str(exc)
            end = time.time()
            elapsed_ms = (end - start) * 1000.0
            elapsed.append(elapsed_ms)
            successes.append(success)
            rows.append({'database': database, 'query_id': query_id, 'round': number,
                         'start_time': str(start), 'end_time': str(end), 'elapsed_ms': elapsed_ms,
                         'success': success, 'error_message': error})
        summaries[query_id] = summarize(elapsed, successes)
    return rows, {database: summaries}
