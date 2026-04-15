from __future__ import annotations


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Calculate BMR in kcal/day with Mifflin-St Jeor inputs."""
    normalized_sex = sex.strip().lower()
    if weight_kg <= 0:
        raise ValueError("weight_kg must be greater than 0.")
    if height_cm <= 0:
        raise ValueError("height_cm must be greater than 0.")
    if age <= 0 or age > 120:
        raise ValueError("age must be between 1 and 120.")
    if normalized_sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'.")

    if normalized_sex == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_multiplier: float) -> float:
    """Calculate TDEE in kcal/day rounded to 2 decimals."""
    if bmr <= 0:
        raise ValueError("bmr must be greater than 0.")
    if activity_multiplier < 1.1 or activity_multiplier > 2.5:
        raise ValueError("activity_multiplier must be between 1.1 and 2.5.")
    return round(bmr * activity_multiplier, 2)
