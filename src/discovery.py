"""Discover non-recursive SQL files in deterministic filename order."""

import os


def discover_sql(directory):
    files = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if os.path.isfile(path) and name.endswith('.sql'):
            files.append((name[:-4], path))
    return files
