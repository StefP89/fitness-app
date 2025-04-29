# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import re
import io
import base64
import csv
import math
import random

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    "chicken breast": {"protein": 31, "carbs": 0, "fat": 3.5, "unit": "100g"},
    "brown rice": {"protein": 5, "carbs": 45, "fat": 1.5, "unit": "1 cup cooked"},
    "egg": {"protein": 6, "carbs": 1, "fat": 5, "unit": "1 large"},
    "broccoli": {"protein": 4, "carbs": 11, "fat": 0.5, "unit": "1 cup"},
    "almonds": {"protein": 6, "carbs": 6, "fat": 14, "unit": "28g"},
    "oats": {"protein": 5, "carbs": 27, "fat": 3, "unit": "1/2 cup"},
    "whey protein": {"protein": 25, "carbs": 3, "fat": 2, "unit": "1 scoop"},
    "olive oil": {"protein": 0, "carbs": 0, "fat": 14, "unit": "1 tbsp"},
    "peanut butter": {"protein": 8, "carbs": 6, "fat": 16, "unit": "2 tbsp"},
    "banana": {"protein": 1, "carbs": 27, "fat": 0.3, "unit": "1 medium"}
}

SEASONING_SUGGESTIONS = [
    "lemon pepper", "garlic and herb", "cumin and paprika", "soy sauce and ginger", "curry powder",
    "chili lime", "Italian seasoning", "rosemary and thyme"
]

USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
MACRO_LOG_PATH = os.path.join("data", "macro_log.json")

# ------------------------- Utility Functions --------------------------- #

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_macro_log():
    return load_json(MACRO_LOG_PATH, default=[])

def save_macro_log(entries):
    save_json(MACRO_LOG_PATH, entries)

def log_macro_entry(date, food_name, servings):
    entry = {"date": date, "food": food_name, "servings": servings}
    entries = load_macro_log()
    entries.append(entry)
    save_macro_log(entries)

def summarize_macros(entries):
    daily_totals = {}
    for entry in entries:
        food = entry["food"]
        servings = float(entry["servings"])
        date = entry["date"]
        if food in FOOD_DB:
            macros = FOOD_DB[food]
            if date not in daily_totals:
                daily_totals[date] = {"protein": 0, "carbs": 0, "fat": 0}
            daily_totals[date]["protein"] += macros["protein"] * servings
            daily_totals[date]["carbs"] += macros["carbs"] * servings
            daily_totals[date]["fat"] += macros["fat"] * servings
    return daily_totals

def load_user_preferences():
    return load_json(USER_PREFS_PATH, default={})

def save_user_preferences(prefs):
    save_json(USER_PREFS_PATH, prefs)

def suggest_balanced_meal():
    prefs = load_user_preferences()
    available = prefs.get("available_foods", list(FOOD_DB.keys()))
    protein_sources = [f for f in available if FOOD_DB[f]["protein"] >= 10]
    carb_sources = [f for f in available if FOOD_DB[f]["carbs"] >= 10]
    fat_sources = [f for f in available if FOOD_DB[f]["fat"] >= 10]

    meals = []
    for i in range(3):
        if not (protein_sources and carb_sources and fat_sources):
            meals.append(f"**Meal {i+1}:** Not enough food options for a balanced meal.")
            continue
        protein = str(random.choice(protein_sources))
        carb = str(random.choice(carb_sources))
        fat = str(random.choice(fat_sources))
        season = str(random.choice(SEASONING_SUGGESTIONS))
        meal = f"**Meal {i+1}:** {protein.title()} ({FOOD_DB[protein]['unit']}), {carb} ({FOOD_DB[carb]['unit']}), and {fat} ({FOOD_DB[fat]['unit']}) - Season with {season}."
        meals.append(meal)

    if protein_sources and fat_sources:
        snack_protein = str(random.choice(protein_sources))
        snack_fat = str(random.choice(fat_sources))
        snack = f"**Snack:** {snack_protein.title()} ({FOOD_DB[snack_protein]['unit']}) and {snack_fat} ({FOOD_DB[snack_fat]['unit']}) with {str(random.choice(SEASONING_SUGGESTIONS))}."
    else:
        snack = "**Snack:** Not enough food options for a balanced snack."
    meals.append(snack)
    return meals

# ------------------------- Streamlit App --------------------------- #

st.title("\U0001F4AA Personal Trainer & Nutrition Coach")

menu = [
    "User Intake Form",
    "Set Macro Targets",
    "Workout Program",
    "Meal Plan",
    "Ingredient-Based Suggestions",
    "Log Stats",
    "View Progress",
    "Macro Tracking",
    "Download PDF"
]

choice = st.sidebar.selectbox("Menu", menu)

if choice == "User Intake Form":
    st.header("\U0001F4DD User Intake Form")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    goal = st.selectbox("Primary Goal", ["Weight Loss", "Muscle Gain", "Endurance"])
    activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    gym_access = st.selectbox("Access to Equipment", ["None", "Home Equipment", "Gym Access"])
    weight_unit = st.selectbox("Preferred Weight Unit", ["kg", "lb"])
    height_unit = st.selectbox("Preferred Height Unit", ["cm", "in"])
    available_foods = st.multiselect("Select Available Food Items", list(FOOD_DB.keys()))

    if st.button("Save Profile"):
        profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "goal": goal,
            "activity_level": activity_level,
            "gym_access": gym_access,
            "weight_unit": weight_unit,
            "height_unit": height_unit,
            "available_foods": available_foods
        }
        save_json("data/user_profile.json", profile)
        save_user_preferences({"available_foods": available_foods})
        st.success("Profile and preferences saved successfully!")

elif choice == "Macro Tracking":
    st.header("\U0001F95C Log and Track Your Macros")
    food = st.selectbox("Select Food", list(FOOD_DB.keys()))
    servings = st.number_input("Servings", min_value=0.1, step=0.1)
    if st.button("Log Entry"):
        today = datetime.date.today().isoformat()
        log_macro_entry(today, food, servings)
        st.success(f"Logged {servings} serving(s) of {food} for {today}.")

    entries = load_macro_log()
    if entries:
        st.subheader("Macro Summary by Day")
        summary = summarize_macros(entries)
        for date, macros in sorted(summary.items()):
            st.write(f"**{date}** - Protein: {macros['protein']:.1f}g, Carbs: {macros['carbs']:.1f}g, Fat: {macros['fat']:.1f}g")

        st.subheader("Macro Intake Graph")
        dates = list(summary.keys())
        protein = [summary[d]["protein"] for d in dates]
        carbs = [summary[d]["carbs"] for d in dates]
        fat = [summary[d]["fat"] for d in dates]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(dates, protein, label="Protein (g)", marker="o")
        ax.plot(dates, carbs, label="Carbs (g)", marker="s")
        ax.plot(dates, fat, label="Fat (g)", marker="^")
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.ylabel("Grams")
        plt.title("Daily Macro Intake")
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No macro data logged yet.")

elif choice == "Meal Plan":
    st.header("\U0001F372 Meal Plan Suggestions")
    st.write("Here are some balanced and appetizing macro-conscious meals for today:")
    meals = suggest_balanced_meal()
    for meal in meals:
        st.markdown(meal)

elif choice == "Ingredient-Based Suggestions":
    st.header("\U0001F9C2 Customize Available Ingredients")
    available_foods = st.multiselect("Select Available Food Items", list(FOOD_DB.keys()))
    if st.button("Update Available Foods"):
        prefs = load_user_preferences()
        prefs["available_foods"] = available_foods
        save_user_preferences(prefs)
        st.success("Available foods updated!")

