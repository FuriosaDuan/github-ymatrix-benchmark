import csv
import os


DETAIL_FIELDS = ['database', 'query_id', 'round', 'start_time', 'end_time', 'elapsed_ms',
                 'success', 'error_message']


def _ensure_parent(path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def write_benchmark_detail(path, rows):
    _ensure_parent(path)
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict((field, row.get(field, '')) for field in DETAIL_FIELDS))


def _metric(item, name):
    return item.get(name, 0)


def write_markdown_report(path, summaries, comparisons=None, correctness=None, metadata=None,
                          detail_rows=None):
    _ensure_parent(path)
    comparisons = comparisons or []
    correctness = correctness or []
    metadata = metadata or {}
    with open(path, 'w') as handle:
        handle.write('# YMatrix 与 MySQL SQL Benchmark 报告\n\n')
        handle.write('## 1. 项目目标\n\n比较 YMatrix 与 MySQL 在相同简化 TPC-H 风格查询和数据上的端到端客户端耗时。\n\n')
        handle.write('## 2. 测试环境\n\n')
        for key in sorted(metadata):
            handle.write('- {}: {}\n'.format(key, metadata[key]))
        handle.write('\n## 3. 数据模型与规模\n\n')
        handle.write('{}\n\n'.format(metadata.get('data_sizes', 'customer=1000, part=500, orders=10000, lineitem=30000, seed=2026')))
        handle.write('## 4. 测试方法\n\n')
        handle.write('warmup_rounds={}，measurement_rounds={}，concurrency=1，timeout_seconds={}。\n\n'.format(
            metadata.get('warmup_rounds', 1), metadata.get('measurement_rounds', 5),
            metadata.get('timeout_seconds', 60)))
        handle.write('## 5. 查询说明\n\nQ01 为订单/明细/销售额聚合；Q02 为按月份聚合；Q03 为销售额 Top-N。\n\n')
        handle.write('## 6. 查询结果一致性\n\n| query_id | match | summary |\n|---|---|---|\n')
        for item in correctness:
            handle.write('| {query_id} | {match} | {summary} |\n'.format(**item))
        if not correctness:
            handle.write('| - | - | 未提供结果摘要 |\n')
        handle.write('\n## 7. Benchmark 统计结果\n\n')
        handle.write('| database | query_id | avg | min | max | p95 | success_rate |\n|---|---|---:|---:|---:|---:|---:|\n')
        for database in sorted(summaries):
            for query_id in sorted(summaries[database]):
                item = summaries[database][query_id]
                handle.write('| {} | {} | {} | {} | {} | {} | {:.2%} |\n'.format(
                    database, query_id, _metric(item, 'avg'), _metric(item, 'min'),
                    _metric(item, 'max'), _metric(item, 'p95'), _metric(item, 'success_rate')))
        handle.write('\n## 8. YMatrix 与 MySQL 对比\n\n')
        handle.write('| query_id | ymatrix_avg_ms | mysql_avg_ms | faster_database | faster_by_percent | ymatrix_to_mysql_ratio |\n|---|---:|---:|---|---:|---:|\n')
        for item in comparisons:
            normalized = {'ymatrix_avg_ms': 0, 'mysql_avg_ms': 0, 'faster_database': 'N/A',
                          'faster_by_percent': 0, 'ymatrix_to_mysql_ratio': 0}
            normalized.update(item)
            handle.write('| {query_id} | {ymatrix_avg_ms} | {mysql_avg_ms} | {faster_database} | {faster_by_percent:.2f}% | {ymatrix_to_mysql_ratio:.4f} |\n'.format(**normalized))
        if not comparisons:
            handle.write('| - | - | - | N/A | 0 | 0 |\n')
        handle.write('\n## 9. Top 慢 SQL\n\n')
        slow = []
        for database in summaries:
            for query_id, item in summaries[database].items():
                slow.append((item.get('avg', 0), database, query_id))
        for avg, database, query_id in sorted(slow, reverse=True)[:5]:
            handle.write('- {} {} avg={} ms\n'.format(database, query_id, avg))
        handle.write('\n## 10. 失败 SQL 分类\n\n')
        failures = {}
        for database in summaries:
            for item in summaries[database].values():
                for category, count in item.get('failure_categories', {}).items():
                    failures[category] = failures.get(category, 0) + count
        for category in sorted(failures):
            handle.write('- {}: {}\n'.format(category, failures[category]))
        if not failures:
            handle.write('- none\n')
        handle.write('\n## 11. 执行计划与性能分析\n\n本版本保留客户端端到端计时；短 SQL 的结果会受到客户端启动和连接建立开销影响。\n\n')
        handle.write('## 12. 项目结论\n\n结论应基于真实报告中的逐查询结果、成功率、波动和结果一致性，不预设某一数据库获胜。\n\n')
        handle.write('## 13. 测试限制\n\n')
        handle.write('本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试。\n\n')
        handle.write('MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。\n\n')
        handle.write('本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。\n\n')
        handle.write('YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。\n')


def write_benchmark_log(path, rows):
    _ensure_parent(path)
    with open(path, 'w') as handle:
        for row in rows:
            handle.write('{} {} q={} round={} success={} elapsed_ms={} category={} error={}\n'.format(
                row.get('database'), row.get('query_id'), row.get('query_id'), row.get('round'),
                row.get('success'), row.get('elapsed_ms'), row.get('error_category', ''),
                row.get('error_message', '')))


def write_environment(path, values):
    _ensure_parent(path)
    with open(path, 'w') as handle:
        for key in sorted(values):
            handle.write('{}: {}\n'.format(key, values[key]))
