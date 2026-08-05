import csv
import os


DETAIL_FIELDS = ['database', 'query_id', 'round', 'start_time', 'end_time', 'elapsed_ms',
                 'success', 'error_message']


def write_benchmark_detail(path, rows):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict((field, row.get(field, '')) for field in DETAIL_FIELDS))


def write_markdown_report(path, summaries):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'w') as handle:
        handle.write('# Benchmark Report\n\n')
        handle.write('本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试。\n\n')
        handle.write('MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端启动和连接建立开销。\n\n')
        handle.write('| database | query | avg | min | max | p95 | success_rate |\n')
        handle.write('|---|---|---:|---:|---:|---:|---:|\n')
        for database in sorted(summaries):
            for query_id in sorted(summaries[database]):
                item = summaries[database][query_id]
                normalized = {'avg': 0, 'min': 0, 'max': 0, 'p95': 0, 'success_rate': 0}
                normalized.update(item)
                item = normalized
                handle.write('| {0} | {1} | {avg} | {min} | {max} | {p95} | {success_rate:.2%} |\n'.format(
                    database, query_id, **item))
        handle.write('\n本次结果来自单节点、小规模、低并发环境，不能代表生产集群性能。\n')


def write_environment(path, values):
    with open(path, 'w') as handle:
        for key in sorted(values):
            handle.write('{}: {}\n'.format(key, values[key]))
