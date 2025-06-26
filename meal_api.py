import requests

def fetch_meals_for_ingredient(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["meals"] if data["meals"] else []
    return []
