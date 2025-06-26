# app.py
import streamlit as st
import os
import pandas as pd
import base64
import matplotlib.pyplot as plt
from fpdf import FPDF
from ocr_utils import extract_ingredients_from_pdf, extract_ingredients_from_receipt
from meal_api import fetch_meals_for_ingredient
from nutrition_utils import get_nutrition_facts
import datetime

st.set_page_config(page_title="Diet Planner from Receipt", page_icon="🥗", layout="wide")

st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Navigation")
st.sidebar.info("Upload a grocery receipt to generate a weekly meal plan using OCR and MealDB API.")
st.sidebar.markdown("[Visit MealDB](https://www.themealdb.com/) for more recipes")

st.title("🥗 Diet Planner from Grocery Receipt")

uploaded = st.file_uploader("📄 Upload a grocery receipt (PDF or Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded:
    temp_path = "temp_receipt"
    with open(temp_path, "wb") as f:
        f.write(uploaded.read())

    with st.spinner("Processing receipt..."):
        if uploaded.type == "application/pdf":
            ingredients = extract_ingredients_from_pdf(temp_path)
        else:
            ingredients = extract_ingredients_from_receipt(temp_path)

    st.subheader("🍭 Extracted Items from Receipt:")
    st.write(ingredients)

    edited_text = st.text_area("💊 Review & Edit Extracted Items (one per line):", value="\n".join(ingredients))
    ingredients = [line.strip() for line in edited_text.splitlines() if line.strip() != ""]

    new_ingredient = st.text_input("➕ Add a missing food item manually:")
    if new_ingredient:
        ingredients.append(new_ingredient.strip())

    common_food_keywords = [
        "apple", "banana", "orange", "bread", "eggs", "milk", "rice", "butter", "chicken", "yogurt",
        "oats", "tomatoes", "onions", "potatoes", "spinach", "peanut butter", "coffee", "juice", "beans"
    ]

    filtered_ingredients = [
        item for item in ingredients
        if any(food in item.lower() for food in common_food_keywords)
    ]

    st.subheader("✅ Filtered Food Ingredients")
    daily_nutrition = []
    for item in filtered_ingredients:
        facts = get_nutrition_facts(item)
        st.markdown(f"**{item.title()}** — {facts.get('calories', '?')} kcal, {facts.get('protein', '?')}g protein, {facts.get('fat', '?')}g fat")
        daily_nutrition.append(facts)

    st.subheader("🗕️ Weekly Meal Plan")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    plan = []
    fallback = {
        "bread": "Grilled Cheese Sandwich",
        "canned beans": "Baked Beans on Toast",
        "orange juice": "Fruit Smoothie",
        "oats": "Oatmeal with Fruits"
    }

    veg_keywords = ["vegetable", "spinach", "tomato", "potato", "oats", "beans", "bread", "butter", "peanut butter", "coffee", "orange juice"]
    non_veg_keywords = ["chicken", "egg", "fish", "mutton", "beef", "meat", "prawns"]

    shopping_list = set()

    for day, ingredient in zip(days, filtered_ingredients):
        shopping_list.add(ingredient.lower())
        tag = st.radio(f"🌱 Choose meal type for {day}:", ["Vegetarian", "Non-Vegetarian"], key=f"tag_{day}", horizontal=True)
        prep_time = st.text_input(f"⏳ Estimated Prep Time for {day} (in minutes):", value="15", key=f"prep_{day}")

        if tag == "Vegetarian":
            matched_meals = [meal for meal in ["Veggie Stir Fry", "Grilled Veg Wrap", "Lentil Soup", "Paneer Tikka"] if any(kw in ingredient.lower() for kw in veg_keywords)]
            suggestions = matched_meals or ["Grilled Cheese", "Oatmeal", "Veggie Curry"]
        else:
            matched_meals = [meal for meal in ["Chicken Curry", "Fish Tacos", "Egg Bhurji", "Beef Stew"] if any(kw in ingredient.lower() for kw in non_veg_keywords)]
            suggestions = matched_meals or ["Omelette", "Chicken Wrap", "Fish Fry"]

        user_meal = st.selectbox(
            f"✏️ {day}: Select or enter meal for {ingredient.title()} ({tag})",
            suggestions + ["Custom Meal"],
            key=f"meal_{day}"
        )

        meal_name = user_meal if user_meal != "Custom Meal" else st.text_input(f"Enter custom meal for {day}", key=f"custom_{day}")

        st.markdown(f"**{day}** — {ingredient.title()} 🍲: {meal_name}")

        note = st.text_input(f"📝 Note for {day}:", value="", key=f"note_{day}")
        plan.append((day, ingredient.title(), meal_name, note, prep_time, tag))

    st.success("Meal plan generated!")

    st.subheader("📊 Nutrition Summary")
    if daily_nutrition:
        df_nutrition = pd.DataFrame(daily_nutrition)
        st.bar_chart(df_nutrition[['calories', 'protein', 'fat']])

    st.subheader("📄 Download Meal Plan")
    df = pd.DataFrame(plan, columns=["Day", "Ingredient", "Meal", "Note", "Prep Time (mins)", "Type"])
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="meal_plan.csv">😕 Download Meal Plan as CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

    df['Timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df.to_csv("meal_plan_history.csv", mode='a', header=not os.path.exists("meal_plan_history.csv"), index=False)

    if st.button("📄 Download as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Weekly Meal Plan", ln=True, align='C')
        pdf.ln(10)
        for day, ingredient, meal, note, prep, tag in plan:
            facts = get_nutrition_facts(ingredient)
            nutrition_summary = f"Calories: {facts.get('calories', '?')} kcal | Protein: {facts.get('protein', '?')}g | Fat: {facts.get('fat', '?')}g"
            pdf.multi_cell(0, 10, txt=f"{day} - {ingredient} → {meal} | Type: {tag} | Prep: {prep} mins\nNote: {note}\n{nutrition_summary}")
            pdf.ln(2)
        pdf.output("meal_plan.pdf")
        with open("meal_plan.pdf", "rb") as f:
            b64_pdf = base64.b64encode(f.read()).decode()
            href_pdf = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="meal_plan.pdf">🗕️ Download Meal Plan as PDF</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)

    st.subheader("🧕‍♂️ Auto-Generated Shopping List")
    for item in sorted(shopping_list):
        st.markdown(f"- {item.title()}")

    if st.button("📝 Download Shopping List"):
        shopping_text = "\n".join(sorted(shopping_list))
        with open("shopping_list.txt", "w") as f:
            f.write("Weekly Shopping List:\n\n" + shopping_text)
        with open("shopping_list.txt", "rb") as f:
            b64_txt = base64.b64encode(f.read()).decode()
            href_txt = f'<a href="data:text/plain;base64,{b64_txt}" download="shopping_list.txt">⬇️ Download Shopping List</a>'
            st.markdown(href_txt, unsafe_allow_html=True)

    if st.checkbox("📜 View Meal Plan History"):
        if os.path.exists("meal_plan_history.csv"):
            hist_df = pd.read_csv("meal_plan_history.csv")
            st.dataframe(hist_df.tail(10))

    avg_prices = {"eggs": 6, "bread": 30, "oats": 50, "butter": 40}
    total_cost = sum(avg_prices.get(i.lower(), 25) for i in filtered_ingredients)
    st.info(f"🛒 Estimated Total Grocery Cost: ₹{total_cost}")