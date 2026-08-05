import datetime
import os
import time

from .database import execute_query, normalize_rows
from .discovery import discover_sql
from .statistics import summarize


def load_queries(directory):
    result = []
    for query_id, path in discover_sql(directory):
        with open(path, 'r') as handle:
            result.append((query_id, handle.read()))
    return result


def _timestamp():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def classify_error(message):
    text = (message or '').lower()
    if 'timeout' in text or '超时' in text:
        return 'timeout'
    if 'connect' in text or 'connection' in text or '连接' in text:
        return 'connection'
    if 'syntax' in text or 'sql' in text or 'query' in text:
        return 'sql'
    if 'command' in text or '命令' in text:
        return 'command'
    return 'other'


def benchmark_database(config, database, sql_dir, rounds=None, runner=None, result_store=None):
    rounds = rounds or int(config['benchmark'].get('measurement_rounds', 5))
    warmups = int(config['benchmark'].get('warmup_rounds', 1))
    session_sql = config.get(database, {}).get('session_sql', [])
    rows = []
    summaries = {}
    if result_store is not None:
        result_store.setdefault(database, {})
    for query_id, sql in load_queries(sql_dir):
        capture_error = ''
        try:
            capture_output, capture_rows = execute_query(config, database, sql,
                                                        session_sql=session_sql, runner=runner)
            if result_store is not None:
                result_store[database][query_id] = {
                    'rows': normalize_rows(capture_rows), 'error_message': ''}
        except Exception as exc:
            capture_error = str(exc)
            capture_rows = []
            if result_store is not None:
                result_store[database][query_id] = {
                    'rows': [], 'error_message': capture_error}
        if capture_error:
            summaries[query_id] = {'avg': 0, 'min': 0, 'max': 0, 'p95': 0,
                                   'success_rate': 0, 'failure_count': rounds,
                                   'failure_categories': {classify_error(capture_error): rounds}}
            for number in range(1, rounds + 1):
                rows.append({'database': database, 'query_id': query_id, 'round': number,
                             'start_time': _timestamp(), 'end_time': _timestamp(),
                             'elapsed_ms': 0, 'success': False,
                             'error_message': capture_error,
                             'error_category': classify_error(capture_error)})
            continue
        for _ in range(warmups):
            execute_query(config, database, sql, session_sql=session_sql, runner=runner)
        elapsed = []
        successes = []
        failures = {}
        for number in range(1, rounds + 1):
            start_time = _timestamp()
            start = time.monotonic()
            success = True
            error = ''
            try:
                execute_query(config, database, sql, session_sql=session_sql, runner=runner)
            except Exception as exc:
                success = False
                error = str(exc)
                category = classify_error(error)
                failures[category] = failures.get(category, 0) + 1
            end = time.monotonic()
            end_time = _timestamp()
            elapsed_ms = (end - start) * 1000.0
            if success:
                elapsed.append(elapsed_ms)
            successes.append(success)
            rows.append({'database': database, 'query_id': query_id, 'round': number,
                         'start_time': start_time, 'end_time': end_time,
                         'elapsed_ms': elapsed_ms, 'success': success,
                         'error_message': error,
                         'error_category': '' if success else category})
        summary = summarize(elapsed, successes)
        summary['failure_count'] = len(successes) - sum(1 for value in successes if value)
        summary['failure_categories'] = failures
        summaries[query_id] = summary
    return rows, {database: summaries}


def compare_result_sets(result_store):
    query_ids = sorted(set(result_store.get('ymatrix', {})) |
                       set(result_store.get('mysql', {})))
    comparisons = []
    for query_id in query_ids:
        left = result_store.get('ymatrix', {}).get(query_id, {})
        right = result_store.get('mysql', {}).get(query_id, {})
        if left.get('error_message') or right.get('error_message'):
            comparisons.append({'query_id': query_id, 'match': False,
                                'summary': 'capture failed: {} {}'.format(
                                    left.get('error_message', ''), right.get('error_message', ''))})
        else:
            match = normalize_rows(left.get('rows', [])) == normalize_rows(right.get('rows', []))
            summary = 'equal' if match else 'row/value difference'
            comparisons.append({'query_id': query_id, 'match': match, 'summary': summary})
    return comparisons


def build_comparisons(summaries):
    query_ids = sorted(set(summaries.get('ymatrix', {})) |
                       set(summaries.get('mysql', {})))
    result = []
    for query_id in query_ids:
        y = summaries.get('ymatrix', {}).get(query_id, {})
        m = summaries.get('mysql', {}).get(query_id, {})
        ya = y.get('avg', 0)
        ma = m.get('avg', 0)
        if not ya or not ma or not y.get('success_rate') or not m.get('success_rate'):
            faster = 'N/A'
            percent = 0
            ratio = 0
        elif ya == ma:
            faster = 'tie'
            percent = 0
            ratio = 1
        elif ya < ma:
            faster = 'ymatrix'
            percent = (ma / ya - 1) * 100
            ratio = ya / ma
        else:
            faster = 'mysql'
            percent = (ya / ma - 1) * 100
            ratio = ya / ma
        result.append({'query_id': query_id, 'ymatrix_avg_ms': ya, 'mysql_avg_ms': ma,
                       'faster_database': faster, 'faster_by_percent': percent,
                       'ymatrix_to_mysql_ratio': ratio})
    return result


def run_benchmark_suite(config, sql_dirs, runner=None):
    all_rows = []
    summaries = {}
    result_store = {}
    for database in ('ymatrix', 'mysql'):
        rows, database_summaries = benchmark_database(
            config, database, sql_dirs[database], runner=runner, result_store=result_store)
        all_rows.extend(rows)
        summaries.update(database_summaries)
    return all_rows, summaries, compare_result_sets(result_store), build_comparisons(summaries)
