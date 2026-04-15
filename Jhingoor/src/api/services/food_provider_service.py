from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

import httpx


@dataclass(slots=True)
class FoodItem:
    name: str
    calories: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    source: str


class FoodProviderService:
    def __init__(self, timeout_seconds: float = 8.0, retries: int = 2) -> None:
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.usda_api_key = os.getenv("USDA_API_KEY", "").strip()

    async def search(self, query: str, limit: int = 5) -> list[FoodItem]:
        q = query.strip()
        if not q:
            return []

        usda_items = await self._search_usda(q, limit=limit) if self.usda_api_key else []
        if usda_items:
            return usda_items
        return await self._search_open_food_facts(q, limit=limit)

    async def _search_usda(self, query: str, limit: int) -> list[FoodItem]:
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {"api_key": self.usda_api_key}
        payload = {"query": query, "pageSize": limit}

        data = await self._request_json("POST", url, params=params, json=payload)
        foods = data.get("foods") or []
        normalized: list[FoodItem] = []
        for item in foods:
            nutrients = self._extract_usda_nutrients(item.get("foodNutrients") or [])
            normalized.append(
                FoodItem(
                    name=item.get("description", "Unknown food"),
                    calories=nutrients.get("calories"),
                    protein_g=nutrients.get("protein"),
                    carbs_g=nutrients.get("carbs"),
                    fat_g=nutrients.get("fat"),
                    source="usda",
                )
            )
        return normalized

    async def _search_open_food_facts(self, query: str, limit: int) -> list[FoodItem]:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": limit,
        }
        data = await self._request_json("GET", url, params=params)
        products = data.get("products") or []
        normalized: list[FoodItem] = []
        for product in products:
            nutriments = product.get("nutriments") or {}
            normalized.append(
                FoodItem(
                    name=product.get("product_name") or product.get("generic_name") or "Unknown food",
                    calories=self._float_or_none(nutriments.get("energy-kcal_100g")),
                    protein_g=self._float_or_none(nutriments.get("proteins_100g")),
                    carbs_g=self._float_or_none(nutriments.get("carbohydrates_100g")),
                    fat_g=self._float_or_none(nutriments.get("fat_100g")),
                    source="openfoodfacts",
                )
            )
        return normalized

    async def _request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        timeout = httpx.Timeout(self.timeout_seconds)
        last_error: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(method, url, params=params, json=json)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    return payload
                return {}
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    await asyncio.sleep(0.25 * (2**attempt))
                continue

        if last_error:
            raise RuntimeError(f"Food provider request failed: {last_error}") from last_error
        raise RuntimeError("Food provider request failed with unknown error")

    @staticmethod
    def _extract_usda_nutrients(nutrients: list[dict]) -> dict[str, float | None]:
        result = {"calories": None, "protein": None, "carbs": None, "fat": None}
        for nutrient in nutrients:
            name = (nutrient.get("nutrientName") or "").lower()
            value = FoodProviderService._float_or_none(nutrient.get("value"))
            if "energy" in name and result["calories"] is None:
                result["calories"] = value
            elif "protein" in name:
                result["protein"] = value
            elif "carbohydrate" in name:
                result["carbs"] = value
            elif "total lipid" in name or name == "fat":
                result["fat"] = value
        return result

    @staticmethod
    def _float_or_none(value: object) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
