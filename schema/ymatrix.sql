CREATE TABLE IF NOT EXISTS bench_customer (c_custkey INTEGER PRIMARY KEY, c_name TEXT, c_nation INTEGER);
CREATE TABLE IF NOT EXISTS bench_part (p_partkey INTEGER PRIMARY KEY, p_name TEXT, p_retailprice NUMERIC(12,2));
CREATE TABLE IF NOT EXISTS bench_orders (o_orderkey INTEGER PRIMARY KEY, o_custkey INTEGER, o_orderdate DATE, o_totalprice NUMERIC(14,2));
CREATE TABLE IF NOT EXISTS bench_lineitem (l_orderkey INTEGER, l_partkey INTEGER, l_quantity INTEGER, l_extendedprice NUMERIC(14,2));
