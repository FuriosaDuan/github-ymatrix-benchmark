import csv
import datetime
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


def _timestamp():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def _command_for(config, database, sql):
    if database == 'mysql':
        return build_mysql_command(config['mysql'], sql)
    return build_psql_command(config['ymatrix'], sql)


def benchmark_mysql(config, sql_dir, rounds=None, runner=None):
    return benchmark_database(config, 'mysql', sql_dir, rounds=rounds, runner=runner)


def benchmark_database(config, database, sql_dir, rounds=None, runner=None):
    rounds = rounds or int(config['benchmark'].get('measurement_rounds', 3))
    warmups = int(config['benchmark'].get('warmup_rounds', 0))
    rows = []
    summaries = {}
    queries = load_queries(sql_dir)
    for query_id, sql in sorted(queries.items()):
        command, env = _command_for(config, database, sql)
        for _ in range(warmups):
            run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)
        elapsed = []
        successes = []
        for number in range(1, rounds + 1):
            start_time = _timestamp()
            start = time.monotonic()
            success = True
            error = ''
            try:
                run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 0), runner=runner)
            except Exception as exc:
                success = False
                error = str(exc)
            end = time.monotonic()
            end_time = _timestamp()
            elapsed_ms = (end - start) * 1000.0
            if success:
                elapsed.append(elapsed_ms)
            successes.append(success)
            rows.append({'database': database, 'query_id': query_id, 'round': number,
                         'start_time': start_time, 'end_time': end_time, 'elapsed_ms': elapsed_ms,
                         'success': success, 'error_message': error})
        summaries[query_id] = summarize(elapsed, successes)
    return rows, {database: summaries}
