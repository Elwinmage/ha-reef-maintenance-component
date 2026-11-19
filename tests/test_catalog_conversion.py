"""Turning what a water test shows into a value (catalog_conversion.py)."""

from __future__ import annotations

from typing import Any

import pytest

from custom_components.reef_maintenance import catalog_conversion as cc

# Titration: the more reagent, the higher the value; points given out of order.
TABLE: dict[str, Any] = {
    "points": [
        {"amount": 2.0, "value": 10.0},
        {"amount": 0.0, "value": 0.0},
        {"amount": 1.0, "value": 4.0},
    ]
}
TITRATION: dict[str, Any] = {"method": "titration", "table": TABLE}


def test_table_bounds() -> None:
    """The bounds are the smallest and largest amounts of the table."""
    assert cc.table_bounds(TABLE) == (0.0, 2.0)


def test_reading_range() -> None:
    """A titration reads what its table covers; a direct test its stated range."""
    assert cc.reading_range(TITRATION) == (0.0, 10.0)
    assert cc.reading_range({"method": "direct", "range": {"min": 1, "max": 9}}) == (
        1,
        9,
    )
    assert cc.reading_range({"method": "direct"}) is None


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (0.0, 0.0),  # lower bound
        (0.5, 2.0),  # between the first two points
        (1.0, 4.0),  # on a point
        (1.5, 7.0),  # between the last two points
        (2.0, 10.0),  # upper bound
        (-0.1, None),  # outside: no extrapolation
        (2.1, None),
    ],
)
def test_to_value(amount: float, expected: float | None) -> None:
    """Values are interpolated linearly inside the table, never outside."""
    assert cc.to_value(TABLE, amount) == expected


def test_convert() -> None:
    """A direct test is read as it is; a titration goes through its table."""
    assert cc.convert({"method": "direct"}, 7.5) == 7.5
    assert cc.convert(TITRATION, 0.5) == 2.0
    assert cc.convert(TITRATION, 5.0) is None
