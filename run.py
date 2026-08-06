"""Command-line entry point for the complete dual-database benchmark workflow."""

import argparse
import os
import platform
import sys

from src.config import ConfigError, load_config
from src.generator import generate_data, sizes_for_scale
from src.initializer import preflight
from src.loader import load_database
from src.validator import validate_databases
from src.benchmark import run_benchmark_suite
from src.command import CommandError
from src.reporter import write_benchmark_detail, write_environment, write_markdown_report
from src.reporter import write_benchmark_log


def paths(config):
    """Return generated-data and result directories from normalized config."""
    configured = config.get('paths', {})
    return {'data': configured.get('data_dir', 'data'), 'results': configured.get('results_dir', 'results')}


def run_load(config, location):
    """Create, clear, and load all project tables in both databases."""
    results = {}
    for database, schema_path in (('ymatrix', 'schema/ymatrix.sql'), ('mysql', 'schema/mysql.sql')):
        results[database] = load_database(config, database, location['data'], schema_path)
        for table, count in sorted(results[database].items()):
            print('{} {} {}'.format(database, table, count))
    return results


def run_validate(config, location):
    """Validate local data and print comparable row counts from both databases."""
    rows = validate_databases(config, location['data'], raise_on_mismatch=True)
    print('table,expected,ymatrix,mysql,match')
    for row in rows:
        print('{table},{expected},{ymatrix},{mysql},{match}'.format(**row))
    return rows


def run_benchmark(config, location, preflight_info=None):
    """Execute both SQL suites and write detail, report, environment, and log files."""
    sql_dirs = {'ymatrix': config['paths']['ymatrix_sql_dir'],
                'mysql': config['paths']['mysql_sql_dir']}
    all_rows, all_summaries, correctness, comparisons = run_benchmark_suite(config, sql_dirs)
    write_benchmark_detail(os.path.join(location['results'], 'benchmark_detail.csv'), all_rows)
    scale_factor = config['benchmark'].get('scale_factor', 0.01)
    sizes = sizes_for_scale(scale_factor)
    size_text = ', '.join('{}={}'.format(name, sizes[name]) for name in
                          ('region', 'nation', 'supplier', 'customer', 'part',
                           'partsupp', 'orders', 'lineitem'))
    metadata = {'data_sizes': size_text + ', seed=2026',
                'scale_factor': scale_factor,
                'warmup_rounds': config['benchmark']['warmup_rounds'],
                'measurement_rounds': config['benchmark']['measurement_rounds'],
                'timeout_seconds': config['benchmark']['timeout_seconds'],
                'ymatrix_transport': 'tcp {}:{}'.format(config['ymatrix']['host'], config['ymatrix']['port']),
                'mysql_transport': config['mysql']['transport'],
                'indexes': ('nation(region), supplier(nation), customer(nation), orders(date/customer), '
                            'lineitem(order/part/supplier)')}
    if preflight_info:
        metadata['ymatrix_version'] = preflight_info.get('ymatrix_version', '')
        metadata['mysql_version'] = preflight_info.get('mysql_version', '')
    write_markdown_report(os.path.join(location['results'], 'benchmark_report.md'),
                          all_summaries, comparisons=comparisons,
                          correctness=correctness, metadata=metadata, detail_rows=all_rows)
    write_benchmark_log(os.path.join(location['results'], 'benchmark.log'), all_rows)
    write_environment(os.path.join(location['results'], 'environment.md'),
                      {'platform': platform.platform(), 'python': sys.version.split()[0],
                       'data_sizes': metadata['data_sizes'],
                       'scale_factor': metadata['scale_factor'],
                       'warmup_rounds': metadata['warmup_rounds'],
                       'measurement_rounds': metadata['measurement_rounds'],
                       'timeout_seconds': metadata['timeout_seconds'],
                       'ymatrix_transport': metadata['ymatrix_transport'],
                       'mysql_transport': metadata['mysql_transport'],
                       'indexes': metadata['indexes'],
                       'ymatrix_version': metadata.get('ymatrix_version', ''),
                       'mysql_version': metadata.get('mysql_version', '')})
    print('benchmark results written to ' + location['results'])
    if not all(item['match'] for item in correctness):
        raise ValueError('查询结果一致性校验失败')
    return all_summaries


def main(argv=None):
    """Parse one CLI command and return a process-compatible exit code."""
    parser = argparse.ArgumentParser(description='YMatrix/MySQL benchmark MVP')
    parser.add_argument('command', choices=['preflight', 'generate', 'load', 'validate', 'benchmark', 'all'])
    parser.add_argument('--config', default='config.local.json')
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        location = paths(config)
        if args.command == 'preflight':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 preflight；请在 Linux 集成环境运行。')
                return 2
            info = preflight(config)
            print(info['message'])
            print('YMatrix version: ' + info['ymatrix_version'])
            print('MySQL version: ' + info['mysql_version'])
        elif args.command == 'generate':
            generate_data(location['data'], scale_factor=config.get('benchmark', {}).get('scale_factor', 0.01))
            print('generated data in ' + location['data'])
        elif args.command == 'validate':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 validate；请在 Linux 集成环境运行。')
                return 2
            run_validate(config, location)
        elif args.command == 'load':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 load；请在 Linux 集成环境运行。')
                return 2
            run_load(config, location)
        elif args.command == 'benchmark':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 benchmark；请在 Linux 集成环境运行。')
                return 2
            run_benchmark(config, location, preflight_info=preflight(config))
        elif args.command == 'all':
            if platform.system() == 'Windows':
                print('Windows 仅支持 preflight/generate/validate；请在 Linux 集成环境运行 all。')
                return 2
            preflight_info = preflight(config)
            generate_data(location['data'], scale_factor=config.get('benchmark', {}).get('scale_factor', 0.01))
            run_load(config, location)
            run_validate(config, location)
            run_benchmark(config, location, preflight_info=preflight_info)
    except (ConfigError, CommandError, ValueError, OSError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
