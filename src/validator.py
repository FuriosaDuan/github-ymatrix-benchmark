import csv
import os

from .generator import SIZES


def validate_generated_data(output_dir):
    result = {}
    for name, expected in SIZES.items():
        path = os.path.join(output_dir, name + '.csv')
        if not os.path.exists(path):
            raise ValueError('缺少生成文件: ' + path)
        with open(path, 'r', newline='') as handle:
            count = max(0, sum(1 for _ in csv.reader(handle)) - 1)
        if count != expected:
            raise ValueError('{} 行数为 {}，期望 {}'.format(name, count, expected))
        result[name] = count
    return result
