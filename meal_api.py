import os
import requests

# Get API key from environment variable
api_key = os.getenv("MEALDB_API_KEY", "1")  # Default to '1' for free tier

def search_meal(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/filter.php?i={ingredient}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("meals", [])
    else:
        return []
