# nutrition_utils.py

def get_nutrition_facts(ingredient):
    nutrition_data = {
        "eggs": {"calories": 155, "protein": 13, "fat": 11},
        "bread": {"calories": 265, "protein": 9, "fat": 3.2},
        "butter": {"calories": 717, "protein": 0.9, "fat": 81},
        "oats": {"calories": 389, "protein": 17, "fat": 7},
        "orange juice": {"calories": 45, "protein": 0.7, "fat": 0.2},
        "peanut butter": {"calories": 588, "protein": 25, "fat": 50},
        "canned beans": {"calories": 155, "protein": 10, "fat": 1},
        "coffee": {"calories": 2, "protein": 0.3, "fat": 0}
    }

    return nutrition_data.get(ingredient.lower(), {"calories": "?", "protein": "?", "fat": "?"})
