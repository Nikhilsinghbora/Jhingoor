from __future__ import annotations

import logging

from api.services.food_provider_service import FoodItem, FoodProviderService


async def search_foods(
    query: str,
    *,
    service: FoodProviderService | None = None,
    limit: int = 5,
) -> list[FoodItem]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []
    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20.")

    provider = service or FoodProviderService()
    try:
        return await provider.search(cleaned_query, limit=limit)
    except Exception as exc:
        logging.exception("Food search failed for query '%s': %s", cleaned_query, exc)
        return []
