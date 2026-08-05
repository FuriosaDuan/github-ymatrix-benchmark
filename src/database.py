from decimal import Decimal, InvalidOperation

from .command import build_mysql_command, build_psql_command, run_command


def parse_rows(output):
    rows = []
    for line in output.splitlines():
        if line.strip():
            rows.append(line.rstrip('\r').split('\t'))
    return rows


def normalize_rows(rows):
    normalized = []
    for row in rows:
        values = []
        for value in row:
            try:
                number = Decimal(value)
                if number.as_tuple().exponent < -6:
                    number = number.quantize(Decimal('0.000001'))
                values.append(number)
            except (InvalidOperation, ValueError):
                values.append(value)
        normalized.append(values)
    return normalized


def execute_query(config, database, sql, session_sql=None, runner=None):
    statements = list(session_sql or [])
    statements.append(sql)
    combined_sql = '\n'.join(statement.rstrip(';') + ';' for statement in statements)
    if database == 'mysql':
        command, env = build_mysql_command(config['mysql'], combined_sql)
    elif database == 'ymatrix':
        command, env = build_psql_command(config['ymatrix'], combined_sql)
    else:
        raise ValueError('不支持的数据库: ' + database)
    output = run_command(command, env=env, timeout=config['benchmark'].get('timeout_seconds', 60), runner=runner)
    return output, parse_rows(output)
