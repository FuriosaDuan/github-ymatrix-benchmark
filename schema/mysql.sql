CREATE TABLE IF NOT EXISTS customer (c_custkey INT PRIMARY KEY, c_name VARCHAR(64), c_nation INT);
CREATE TABLE IF NOT EXISTS part (p_partkey INT PRIMARY KEY, p_name VARCHAR(64), p_retailprice DECIMAL(12,2));
CREATE TABLE IF NOT EXISTS orders (o_orderkey INT PRIMARY KEY, o_custkey INT, o_orderdate DATE, o_totalprice DECIMAL(14,2));
CREATE TABLE IF NOT EXISTS lineitem (l_orderkey INT, l_partkey INT, l_quantity INT, l_extendedprice DECIMAL(14,2));
