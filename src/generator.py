import csv
import os
import random
from decimal import Decimal


SIZES = {'customer': 1000, 'part': 1000, 'orders': 10000, 'lineitem': 30000}


def _write(path, fields, rows):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)


def generate_data(output_dir, seed=2026):
    random.seed(seed)
    _write(os.path.join(output_dir, 'customer.csv'), ['c_custkey', 'c_name', 'c_nation'],
           [[i, 'Customer{}'.format(i), random.randint(1, 25)] for i in range(1, SIZES['customer'] + 1)])
    _write(os.path.join(output_dir, 'part.csv'), ['p_partkey', 'p_name', 'p_retailprice'],
           [[i, 'Part{}'.format(i), str(Decimal(random.randint(100, 100000)) / Decimal('100'))]
            for i in range(1, SIZES['part'] + 1)])
    _write(os.path.join(output_dir, 'orders.csv'), ['o_orderkey', 'o_custkey', 'o_orderdate', 'o_totalprice'],
           [[i, random.randint(1, SIZES['customer']), '2026-{0:02d}-{1:02d}'.format(random.randint(1, 12), random.randint(1, 28)),
             str(Decimal(random.randint(100, 1000000)) / Decimal('100'))]
            for i in range(1, SIZES['orders'] + 1)])
    _write(os.path.join(output_dir, 'lineitem.csv'), ['l_orderkey', 'l_partkey', 'l_quantity', 'l_extendedprice'],
           [[random.randint(1, SIZES['orders']), random.randint(1, SIZES['part']), random.randint(1, 50),
             str(Decimal(random.randint(100, 100000)) / Decimal('100'))]
            for _ in range(SIZES['lineitem'])])
