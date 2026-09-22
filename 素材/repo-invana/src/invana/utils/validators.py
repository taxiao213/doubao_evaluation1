from ..exceptions import ValidationError


def require_non_empty(value: str, field: str):
    if not value or not value.strip():
        raise ValidationError(f"{field} 不能为空")
    return value.strip()


def require_positive_int(value, field: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} 必须是整数")
    if n <= 0:
        raise ValidationError(f"{field} 必须为正数")
    return n


def require_decimal_string(value, field: str) -> str:
    from decimal import Decimal, InvalidOperation
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        raise ValidationError(f"{field} 必须是十进制数")
    if d < 0:
        raise ValidationError(f"{field} 不能为负")
    return str(d)
