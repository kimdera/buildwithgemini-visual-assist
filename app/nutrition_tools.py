"""USDA FoodData Central lookup tool for VisualAssist."""

import os
import json
import urllib.parse
import urllib.request
from typing import Any, Dict


def lookup_food_nutrition_and_ingredients(food_query: str) -> Dict[str, Any]:
    """Look up nutrition details, ingredients list, and allergens from the USDA FoodData Central database.

    Helpful for low-vision users to read nutrition facts and ingredient labels on pantry foods.

    Args:
        food_query: Name of the food item or brand to search for (e.g., 'rolled oats', 'peanut butter', 'chamomile tea').

    Returns:
        Dictionary containing food description, brand name, ingredients, and key nutrient amounts.
    """
    api_key = os.getenv("USDA_FDC_API_KEY", "DEMO_KEY")
    encoded_query = urllib.parse.quote(food_query.strip())
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={encoded_query}&pageSize=1"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VisualAssist-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        foods = data.get("foods", [])
        if not foods:
            return {"status": "not_found", "message": f"No USDA food data found for '{food_query}'."}

        food = foods[0]
        nutrients = []
        for n in food.get("foodNutrients", []):
            name = n.get("nutrientName", "")
            amount = n.get("value")
            unit = n.get("unitName", "").lower()
            if any(k in name.lower() for k in ["energy", "protein", "carbohydrate", "total lipid", "fiber", "sugars", "sodium"]):
                nutrients.append(f"{name}: {amount} {unit}")

        return {
            "status": "success",
            "query": food_query,
            "description": food.get("description", "N/A"),
            "brand": food.get("brandName") or food.get("brandOwner") or "N/A",
            "ingredients": food.get("ingredients", "No ingredient list provided"),
            "category": food.get("foodCategory", "N/A"),
            "key_nutrients": nutrients[:6],
            "serving_size": f"{food.get('servingSize', 'N/A')} {food.get('servingSizeUnit', '')}".strip(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch food details for '{food_query}': {str(e)}"}
