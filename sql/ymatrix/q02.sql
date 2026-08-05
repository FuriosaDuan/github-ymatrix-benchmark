SELECT EXTRACT(YEAR FROM o_orderdate) AS order_year, EXTRACT(MONTH FROM o_orderdate) AS order_month,
       COUNT(*) AS order_count, SUM(o_totalprice) AS sales
FROM bench_orders GROUP BY EXTRACT(YEAR FROM o_orderdate), EXTRACT(MONTH FROM o_orderdate)
ORDER BY order_year, order_month;
