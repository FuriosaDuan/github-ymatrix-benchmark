# TPC-H 兼容 SF=0.01 双数据库 Benchmark 设计

## 定位

项目实现纯 Python 3.6.8 标准库的 TPC-H 兼容工作负载，不依赖 dbgen/qgen，不声称通过 TPC 官方审计。默认 `scale_factor=0.01`，可配置扩大；正式报告必须记录生成器、规模和限制。

## 八表供应链雪花模型

`region → nation → {supplier, customer}`；`part ↔ supplier` 通过 `partsupp` 建立供货关系；`customer → orders → lineitem` 表示采购交易；每条 lineitem 的 `(partkey,suppkey)` 必须存在于 partsupp。

默认行数：region=5、nation=25、supplier=100、customer=1500、part=2000、partsupp=8000、orders=15000、lineitem 约 60000。除 lineitem 外按标准 SF1 基数乘 0.01；lineitem 每订单确定性生成 1–7 行。

## 生成与装载

固定 seed 生成八个带标准 TPC-H 风格列名的 CSV，金额使用 Decimal/整数分单位逻辑。两数据库使用同一 CSV，建表、按依赖逆序清空、最多 500 行多行 INSERT、创建公平索引。禁止 COPY 和 LOAD DATA。

## 查询

YMatrix 与 MySQL 各提供 q01.sql–q22.sql。查询覆盖 TPC-H 22 类分析场景，使用固定参数和确定性排序；日期、interval、substring、limit 等按 PostgreSQL 12 与 MySQL 5.7 分别适配。查询发现仍按目录中全部 `.sql` 文件动态执行。

## 校验和报告

validate 校验八个 CSV 行数、主外键/partsupp 供货关系，并比较两库八表 COUNT。benchmark 首次捕获两库结果并规范化 Decimal/NULL 后比较，随后执行 warmup=1 和 measurement=5。输出 CSV 明细、UTF-8 Markdown 报告、环境说明、日志、22 查询一致性、统计、逐查询差异、慢 SQL、失败分类和限制。

## 验收

一键 Linux 脚本执行 compileall、unittest、preflight、generate、load、validate 和两次 benchmark，逐次保存四个结果文件。人工文档说明 Git push/pull、数据库初始化、预期八表行数、22 查询检查和 SCP 回收。
