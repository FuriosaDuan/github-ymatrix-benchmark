SELECT DATE_FORMAT(o_orderdate, '%Y-%m') AS order_month, COUNT(*) AS order_count, SUM(o_totalprice) AS sales
FROM orders GROUP BY DATE_FORMAT(o_orderdate, '%Y-%m') ORDER BY order_month;
