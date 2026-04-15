from __future__ import annotations


def calculate_macros(tdee: float, protein_ratio: float = 0.3, carb_ratio: float = 0.4) -> dict[str, int]:
    """Calculate daily macros in grams from TDEE (kcal/day)."""
    if tdee <= 0:
        raise ValueError("tdee must be greater than 0.")
    if not 0 <= protein_ratio <= 1:
        raise ValueError("protein_ratio must be between 0 and 1.")
    if not 0 <= carb_ratio <= 1:
        raise ValueError("carb_ratio must be between 0 and 1.")
    if protein_ratio + carb_ratio > 1:
        raise ValueError("protein_ratio + carb_ratio must be less than or equal to 1.")

    fat_ratio = 1.0 - (protein_ratio + carb_ratio)
    protein_cals = tdee * protein_ratio
    carb_cals = tdee * carb_ratio
    fat_cals = tdee * fat_ratio
    return {
        "calories": int(round(tdee)),
        "protein_g": int(round(protein_cals / 4)),
        "carbs_g": int(round(carb_cals / 4)),
        "fat_g": int(round(fat_cals / 9)),
    }
