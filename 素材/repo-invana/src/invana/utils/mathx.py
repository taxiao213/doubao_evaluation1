from decimal import Decimal


def mean(values):
    vals = list(values)
    if not vals:
        return Decimal(0)
    return sum(vals) / len(vals)


def growth(curr, prev):
    if not prev:
        return Decimal(0)
    return (Decimal(curr) - Decimal(prev)) / Decimal(prev)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))
