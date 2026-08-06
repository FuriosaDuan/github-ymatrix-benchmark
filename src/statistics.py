"""Calculate benchmark aggregates using nearest-rank percentile semantics."""

import math


def percentile_nearest_rank(values, percentile):
    if not values:
        return 0
    ordered = sorted(values)
    rank = int(math.ceil(percentile * len(ordered)))
    return ordered[max(0, rank - 1)]


def summarize(elapsed_values, successes):
    """Summarize successful timings while retaining all attempts in success rate."""
    values = list(elapsed_values)
    if not values:
        return {'avg': 0, 'min': 0, 'max': 0, 'p95': 0, 'success_rate': 0}
    return {'avg': sum(values) / float(len(values)), 'min': min(values), 'max': max(values),
            'p95': percentile_nearest_rank(values, 0.95),
            'success_rate': sum(1 for value in successes if value) / float(len(successes))}
