from __future__ import annotations


def calculate_sleep_score(hours: float, quality: int) -> float:
    """Calculate sleep score (0-100) from sleep duration and quality."""
    if hours < 0 or hours > 24:
        raise ValueError("hours must be between 0 and 24.")
    if quality < 1 or quality > 10:
        raise ValueError("quality must be between 1 and 10.")

    target_hours = 8.0
    hours_score = max(0.0, min(70.0, (hours / target_hours) * 70.0))
    quality_score = (quality / 10.0) * 30.0
    return round(hours_score + quality_score, 2)
