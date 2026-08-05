SELECT p.p_partkey, p.p_name, SUM(l.l_extendedprice) AS sales
FROM bench_part p JOIN bench_lineitem l ON l.l_partkey = p.p_partkey
GROUP BY p.p_partkey, p.p_name ORDER BY sales DESC LIMIT 10;
