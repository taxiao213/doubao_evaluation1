import pytest

from invana.exceptions import ValidationError
from invana.utils.validators import (
    require_decimal_string,
    require_non_empty,
    require_positive_int,
)


def test_require_non_empty_strips():
    assert require_non_empty("  abc ", "f") == "abc"


def test_require_non_empty_rejects_blank():
    with pytest.raises(ValidationError):
        require_non_empty("   ", "f")


def test_require_positive_int():
    assert require_positive_int("3", "q") == 3
    with pytest.raises(ValidationError):
        require_positive_int("-1", "q")


def test_require_decimal_string():
    assert require_decimal_string("12.5", "p") == "12.5"
    with pytest.raises(ValidationError):
        require_decimal_string("abc", "p")
