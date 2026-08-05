SELECT COUNT(*) AS order_count, SUM(li_count) AS detail_count, SUM(total_sales) AS total_sales
FROM (SELECT o.o_orderkey, COUNT(l.l_orderkey) AS li_count, o.o_totalprice AS total_sales
      FROM bench_orders o LEFT JOIN bench_lineitem l ON l.l_orderkey = o.o_orderkey
      GROUP BY o.o_orderkey, o.o_totalprice) x;
