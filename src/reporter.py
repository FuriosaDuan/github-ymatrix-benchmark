"""Render benchmark detail, comparison reports, environment metadata, and logs."""

import csv
import os


DETAIL_FIELDS = ['database', 'query_id', 'round', 'start_time', 'end_time', 'elapsed_ms',
                 'success', 'error_message']


def _ensure_parent(path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def write_benchmark_detail(path, rows):
    """Write formal measurement rows to the required detail CSV schema."""
    _ensure_parent(path)
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict((field, row.get(field, '')) for field in DETAIL_FIELDS))


def _metric(item, name):
    return item.get(name, 0)


def _conclusion(comparisons, correctness):
    mismatches = [item['query_id'] for item in correctness if not item.get('match')]
    if mismatches:
        return '查询结果存在不一致（{}），本次 Benchmark 不能判定为完全成功。'.format(', '.join(mismatches))
    parts = []
    for item in comparisons:
        faster = item.get('faster_database', 'N/A')
        query_id = item.get('query_id', '')
        if faster == 'ymatrix':
            parts.append('YMatrix 在 {} 的平均端到端耗时更低'.format(query_id))
        elif faster == 'mysql':
            parts.append('MySQL 在 {} 的平均端到端耗时更低'.format(query_id))
        elif faster == 'tie':
            parts.append('{} 平均耗时持平'.format(query_id))
        else:
            parts.append('{} 缺少可比较的成功轮次'.format(query_id))
    if not parts:
        return '当前没有足够的正式明细用于数据库性能结论。'
    return '；'.join(parts) + '。结论仅适用于本报告记录的环境与数据规模。'


def write_markdown_report(path, summaries, comparisons=None, correctness=None, metadata=None,
                          detail_rows=None):
    """Write the complete human-readable benchmark report from measured rows."""
    _ensure_parent(path)
    comparisons = comparisons or []
    correctness = correctness or []
    metadata = metadata or {}
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        handle.write('# YMatrix 与 MySQL SQL Benchmark 报告\n\n')
        handle.write('## 1. 项目目标\n\n')
        handle.write('比较 YMatrix 与 MySQL 在相同简化 TPC-H 风格数据和查询上的命令行客户端端到端耗时。\n\n')
        handle.write('## 2. 测试环境\n\n')
        for key in sorted(metadata):
            handle.write('- {}: {}\n'.format(key, metadata[key]))
        handle.write('\n## 3. 数据模型与规模\n\n{}\n\n'.format(
            metadata.get('data_sizes', 'scale_factor=0.01')))
        handle.write('使用 region、nation、supplier、customer、part、partsupp、orders、lineitem 八张供应链关联表。\n\n')
        handle.write('## 4. 测试方法\n\n')
        handle.write('warmup_rounds={}，measurement_rounds={}，concurrency=1，timeout_seconds={}。预热不进入正式明细；正式耗时使用 monotonic 计时。\n\n'.format(
            metadata.get('warmup_rounds', 1), metadata.get('measurement_rounds', 5),
            metadata.get('timeout_seconds', 60)))
        handle.write('## 5. 查询说明\n\n')
        handle.write('Q01–Q22 依次覆盖定价汇总、最低成本供应商、运输优先级、订单优先级、区域收入、预测收入、跨国运输、市场份额、商品利润、退货客户、重要库存、运输模式、客户订单分布、促销收入、头部供应商、供货关系、平均年度收入、大订单客户、折扣收入、潜在促销供应商、供应商等待和全球销售机会。\n\n')
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
                handle.write('| {} | {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.2%} |\n'.format(
                    database, query_id, _metric(item, 'avg'), _metric(item, 'min'),
                    _metric(item, 'max'), _metric(item, 'p95'), _metric(item, 'success_rate')))
        handle.write('\n## 8. YMatrix 与 MySQL 对比\n\n')
        handle.write('| query_id | ymatrix_avg_ms | mysql_avg_ms | faster_database | faster_by_percent | ymatrix_to_mysql_ratio |\n|---|---:|---:|---|---:|---:|\n')
        for item in comparisons:
            values = {'ymatrix_avg_ms': 0, 'mysql_avg_ms': 0, 'faster_database': 'N/A',
                      'faster_by_percent': 0, 'ymatrix_to_mysql_ratio': 0}
            values.update(item)
            handle.write('| {query_id} | {ymatrix_avg_ms:.3f} | {mysql_avg_ms:.3f} | {faster_database} | {faster_by_percent:.2f}% | {ymatrix_to_mysql_ratio:.4f} |\n'.format(**values))
        if not comparisons:
            handle.write('| - | 0 | 0 | N/A | 0 | 0 |\n')
        handle.write('\n## 9. Top 慢 SQL\n\n')
        slow = [(item.get('avg', 0), database, query_id)
                for database in summaries for query_id, item in summaries[database].items()]
        for avg, database, query_id in sorted(slow, reverse=True)[:5]:
            handle.write('- {} {} avg={:.3f} ms\n'.format(database, query_id, avg))
        handle.write('\n## 10. 失败 SQL 分类\n\n')
        failures = {}
        for database in summaries:
            for item in summaries[database].values():
                for category, count in item.get('failure_categories', {}).items():
                    failures[category] = failures.get(category, 0) + count
        if failures:
            for category in sorted(failures):
                handle.write('- {}: {}\n'.format(category, failures[category]))
        else:
            handle.write('- none\n')
        handle.write('\n## 11. 执行计划与性能分析\n\n')
        handle.write('公平索引：{}。短 SQL 容易受到客户端进程启动和连接建立开销影响。\n\n'.format(
            metadata.get('indexes', '未记录')))
        handle.write('## 12. 项目结论\n\n{}\n\n'.format(_conclusion(comparisons, correctness)))
        handle.write('## 13. 测试限制\n\n')
        handle.write('本项目使用纯 Python 标准库生成 TPC-H 兼容数据和 22 类分析查询，不属于标准或经审计的 TPC-H 测试。\n\n')
        handle.write('TPC-C 当前作为扩展说明，尚未实现标准事务负载执行器。\n\n')
        handle.write('MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。\n\n')
        handle.write('本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。\n\n')
        handle.write('YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。\n')


def write_benchmark_log(path, rows):
    """Write one auditable log line for every formal benchmark execution."""
    _ensure_parent(path)
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        for row in rows:
            handle.write('{} {} q={} round={} success={} elapsed_ms={} category={} error={}\n'.format(
                row.get('database'), row.get('query_id'), row.get('query_id'), row.get('round'),
                row.get('success'), row.get('elapsed_ms'), row.get('error_category', ''),
                row.get('error_message', '')))


def write_environment(path, values):
    """Write database versions, runtime parameters, data scale, and limitations."""
    _ensure_parent(path)
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        for key in sorted(values):
            handle.write('{}: {}\n'.format(key, values[key]))
