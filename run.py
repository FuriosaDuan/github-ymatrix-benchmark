import argparse
import os
import platform
import sys

from src.config import ConfigError, load_config
from src.generator import generate_data
from src.validator import validate_generated_data
from src.initializer import load_schema, preflight
from src.benchmark import benchmark_database
from src.reporter import write_benchmark_detail, write_environment, write_markdown_report


def paths(config):
    configured = config.get('paths', {})
    return {'data': configured.get('data_dir', 'data'), 'results': configured.get('results_dir', 'results')}


def main(argv=None):
    parser = argparse.ArgumentParser(description='YMatrix/MySQL benchmark MVP')
    parser.add_argument('command', choices=['preflight', 'generate', 'load', 'validate', 'benchmark', 'all'])
    parser.add_argument('--config', default='config.local.json')
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        location = paths(config)
        if args.command == 'preflight':
            print(preflight(config)['message'])
        elif args.command == 'generate':
            generate_data(location['data'])
            print('generated data in ' + location['data'])
        elif args.command == 'validate':
            print(validate_generated_data(location['data']))
        elif args.command == 'load':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 load；请在 Linux 集成环境运行。')
                return 2
            load_schema(config, 'ymatrix', 'schema/ymatrix.sql')
            load_schema(config, 'mysql', 'schema/mysql.sql')
            print('schemas loaded')
        elif args.command == 'benchmark':
            if platform.system() == 'Windows':
                print('Windows 不执行真实数据库 benchmark；请在 Linux 集成环境运行。')
                return 2
            all_rows = []
            all_summaries = {}
            for database, sql_dir in (('ymatrix', 'sql/ymatrix'), ('mysql', 'sql/mysql')):
                rows, summaries = benchmark_database(config, database, sql_dir)
                all_rows.extend(rows)
                all_summaries.update(summaries)
            write_benchmark_detail(os.path.join(location['results'], 'benchmark_detail.csv'), all_rows)
            write_markdown_report(os.path.join(location['results'], 'benchmark_report.md'), all_summaries)
            write_environment(os.path.join(location['results'], 'environment.md'),
                              {'platform': platform.platform(), 'python': sys.version.split()[0]})
            print('benchmark results written to ' + location['results'])
        elif args.command == 'all':
            if platform.system() == 'Windows':
                print('Windows 仅支持 preflight/generate/validate；请在 Linux 集成环境运行 all。')
                return 2
            generate_data(location['data'])
            validate_generated_data(location['data'])
            load_schema(config, 'ymatrix', 'schema/ymatrix.sql')
            load_schema(config, 'mysql', 'schema/mysql.sql')
            return main(['benchmark', '--config', args.config])
    except (ConfigError, ValueError, OSError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
