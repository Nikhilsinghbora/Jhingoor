from __future__ import annotations

from datetime import date


def infer_cycle_phase(period_start: date, cycle_length: int | None, on_date: date | None = None) -> str:
    """Infer menstrual cycle phase from period start and cycle length."""
    if on_date is None:
        on_date = date.today()
    length = 28 if cycle_length is None else cycle_length
    if length < 15 or length > 60:
        raise ValueError("cycle_length must be between 15 and 60 days.")
    if on_date < period_start:
        raise ValueError("on_date must be on or after period_start.")

    day = ((on_date - period_start).days % length) + 1
    if day <= 5:
        return "menstrual"
    if day <= 13:
        return "follicular"
    if day <= 16:
        return "ovulation"
    return "luteal"
