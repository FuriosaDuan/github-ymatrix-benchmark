SELECT TO_CHAR(o_orderdate, 'YYYY-MM') AS order_month, COUNT(*) AS order_count, SUM(o_totalprice) AS sales
FROM bench_orders GROUP BY TO_CHAR(o_orderdate, 'YYYY-MM')
ORDER BY order_month;
