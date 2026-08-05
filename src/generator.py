import csv
import datetime
import os
import random
from decimal import Decimal


BASE_SF1 = {'region': 5, 'nation': 25, 'supplier': 10000, 'customer': 150000,
            'part': 200000, 'partsupp': 800000, 'orders': 1500000, 'lineitem': 6000000}


def sizes_for_scale(scale_factor):
    scale = Decimal(str(scale_factor))
    if scale <= 0:
        raise ValueError('scale_factor 必须大于 0')
    return {'region': 5, 'nation': 25,
            'supplier': max(1, int(Decimal(BASE_SF1['supplier']) * scale)),
            'customer': max(1, int(Decimal(BASE_SF1['customer']) * scale)),
            'part': max(1, int(Decimal(BASE_SF1['part']) * scale)),
            'partsupp': max(4, int(Decimal(BASE_SF1['partsupp']) * scale)),
            'orders': max(1, int(Decimal(BASE_SF1['orders']) * scale)),
            'lineitem': max(1, int(Decimal(BASE_SF1['lineitem']) * scale))}


SIZES = sizes_for_scale(0.01)
REGIONS = ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST']
NATIONS = ['ALGERIA', 'ARGENTINA', 'BRAZIL', 'CANADA', 'EGYPT', 'ETHIOPIA', 'FRANCE',
           'GERMANY', 'INDIA', 'INDONESIA', 'IRAN', 'IRAQ', 'JAPAN', 'JORDAN', 'KENYA',
           'MOROCCO', 'MOZAMBIQUE', 'PERU', 'CHINA', 'ROMANIA', 'SAUDI ARABIA', 'VIETNAM',
           'RUSSIA', 'UNITED KINGDOM', 'UNITED STATES']
SEGMENTS = ['AUTOMOBILE', 'BUILDING', 'FURNITURE', 'HOUSEHOLD', 'MACHINERY']
SHIP_MODES = ['AIR', 'FOB', 'MAIL', 'RAIL', 'REG AIR', 'SHIP', 'TRUCK']
CONTAINERS = ['SM BOX', 'SM CASE', 'MED BAG', 'MED BOX', 'LG CASE', 'LG PACK']


def _money(cents):
    return str((Decimal(cents) / Decimal('100')).quantize(Decimal('0.01')))


def _write(path, fields, rows):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)


def generate_data(output_dir, seed=2026, scale_factor=0.01):
    rng = random.Random(seed)
    sizes = sizes_for_scale(scale_factor)
    _write(os.path.join(output_dir, 'region.csv'), ['r_regionkey', 'r_name', 'r_comment'],
           [[key, name, 'Region {}'.format(name)] for key, name in enumerate(REGIONS)])
    _write(os.path.join(output_dir, 'nation.csv'),
           ['n_nationkey', 'n_name', 'n_regionkey', 'n_comment'],
           [[key, name, key % 5, 'Nation {}'.format(name)] for key, name in enumerate(NATIONS)])
    suppliers = []
    for key in range(1, sizes['supplier'] + 1):
        nation = (key * 7) % 25
        suppliers.append([key, 'Supplier#{:09d}'.format(key), 'Address {}'.format(key), nation,
                          '{:02d}-{:03d}-{:03d}-{:04d}'.format(10 + nation, key % 1000,
                                                               (key * 3) % 1000, (key * 17) % 10000),
                          _money(rng.randint(-99999, 999999)),
                          'Customer Complaints' if key % 37 == 0 else 'Reliable supplier'])
    _write(os.path.join(output_dir, 'supplier.csv'),
           ['s_suppkey', 's_name', 's_address', 's_nationkey', 's_phone', 's_acctbal', 's_comment'], suppliers)
    customers = []
    for key in range(1, sizes['customer'] + 1):
        nation = (key * 11) % 25
        customers.append([key, 'Customer#{:09d}'.format(key), 'Customer Address {}'.format(key), nation,
                          '{:02d}-{:03d}-{:03d}-{:04d}'.format(10 + nation, key % 1000,
                                                               (key * 5) % 1000, (key * 19) % 10000),
                          _money(rng.randint(-99999, 999999)), SEGMENTS[key % len(SEGMENTS)],
                          'Customer comment {}'.format(key)])
    _write(os.path.join(output_dir, 'customer.csv'),
           ['c_custkey', 'c_name', 'c_address', 'c_nationkey', 'c_phone', 'c_acctbal',
            'c_mktsegment', 'c_comment'], customers)
    parts = []
    for key in range(1, sizes['part'] + 1):
        part_type = ('PROMO ' if key % 10 == 0 else 'STANDARD ') + ('BRASS' if key % 7 == 0 else 'STEEL')
        parts.append([key, 'Part {} green blue'.format(key), 'Manufacturer#{}'.format(1 + key % 5),
                      'Brand#{:02d}'.format(10 + key % 45), part_type, 1 + key % 50,
                      CONTAINERS[key % len(CONTAINERS)], _money(90000 + key * 3), 'Part comment'])
    _write(os.path.join(output_dir, 'part.csv'),
           ['p_partkey', 'p_name', 'p_mfgr', 'p_brand', 'p_type', 'p_size', 'p_container',
            'p_retailprice', 'p_comment'], parts)
    supply_map = {}
    partsupp = []
    for partkey in range(1, sizes['part'] + 1):
        keys = []
        for offset in range(4):
            suppkey = ((partkey * 17 + offset * 23) % sizes['supplier']) + 1
            while suppkey in keys:
                suppkey = (suppkey % sizes['supplier']) + 1
            keys.append(suppkey)
            partsupp.append([partkey, suppkey, rng.randint(1, 9999), _money(rng.randint(100, 100000)),
                             'Supply relationship'])
        supply_map[partkey] = keys
    _write(os.path.join(output_dir, 'partsupp.csv'),
           ['ps_partkey', 'ps_suppkey', 'ps_availqty', 'ps_supplycost', 'ps_comment'], partsupp)
    start = datetime.date(1992, 1, 1)
    orders = []
    lineitems = []
    base_lines, extra_lines = divmod(sizes['lineitem'], sizes['orders'])
    for orderkey in range(1, sizes['orders'] + 1):
        orderdate = start + datetime.timedelta(days=rng.randint(0, 2400))
        line_count = base_lines + (1 if orderkey <= extra_lines else 0)
        total_cents = 0
        for line_number in range(1, line_count + 1):
            partkey = ((orderkey * 13 + line_number * 29) % sizes['part']) + 1
            suppkey = supply_map[partkey][(orderkey + line_number) % 4]
            quantity = rng.randint(1, 50)
            extended_cents = quantity * (9000 + partkey % 5000)
            discount = Decimal(rng.randint(0, 10)) / Decimal('100')
            tax = Decimal(rng.randint(0, 8)) / Decimal('100')
            total_cents += int(Decimal(extended_cents) * (1 - discount) * (1 + tax))
            shipdate = orderdate + datetime.timedelta(days=rng.randint(1, 90))
            commitdate = orderdate + datetime.timedelta(days=rng.randint(1, 60))
            receiptdate = shipdate + datetime.timedelta(days=rng.randint(1, 30))
            lineitems.append([orderkey, partkey, suppkey, line_number, quantity, _money(extended_cents),
                              str(discount.quantize(Decimal('0.00'))), str(tax.quantize(Decimal('0.00'))),
                              'R' if orderkey % 5 == 0 else 'N', 'F' if shipdate < datetime.date(1998, 1, 1) else 'O',
                              shipdate.isoformat(), commitdate.isoformat(), receiptdate.isoformat(),
                              'DELIVER IN PERSON', SHIP_MODES[(orderkey + line_number) % len(SHIP_MODES)],
                              'Lineitem comment'])
        orders.append([orderkey, ((orderkey * 31) % sizes['customer']) + 1,
                       'F' if orderdate < datetime.date(1997, 1, 1) else 'O', _money(total_cents),
                       orderdate.isoformat(), '{}-URGENT'.format(1 + orderkey % 5),
                       'Clerk#{:09d}'.format(1 + orderkey % 1000), 0, 'Order comment'])
    _write(os.path.join(output_dir, 'orders.csv'),
           ['o_orderkey', 'o_custkey', 'o_orderstatus', 'o_totalprice', 'o_orderdate',
            'o_orderpriority', 'o_clerk', 'o_shippriority', 'o_comment'], orders)
    _write(os.path.join(output_dir, 'lineitem.csv'),
           ['l_orderkey', 'l_partkey', 'l_suppkey', 'l_linenumber', 'l_quantity',
            'l_extendedprice', 'l_discount', 'l_tax', 'l_returnflag', 'l_linestatus',
            'l_shipdate', 'l_commitdate', 'l_receiptdate', 'l_shipinstruct', 'l_shipmode',
            'l_comment'], lineitems)
    return sizes
