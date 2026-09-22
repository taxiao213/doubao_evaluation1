def pct(value, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def thousands(n) -> str:
    return f"{n:,}"


def table(rows, headers):
    """极简文本表格。"""
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)] if rows else [len(str(h)) for h in headers]
    head = " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    sep = "-+-".join("-" * w for w in widths)
    body = [" | ".join(str(c).ljust(w) for c, w in zip(r, widths)) for r in rows]
    return "\n".join([head, sep] + body)
