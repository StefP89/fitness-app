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
 
 @@ -28,65 +30,108 @@
     "banana": {"protein": 1, "carbs": 27, "fat": 0.3, "unit": "1 medium"}
 }
 
 WORKOUTS = {
     "Muscle Gain": {
         "Gym Access": [
             ("Day 1 - Push", ["Barbell Bench Press", "Overhead Dumbbell Press", "Cable Flys", "Tricep Pushdowns"]),
             ("Day 2 - Pull", ["Deadlift", "Lat Pulldown", "Barbell Rows", "Bicep Curls"]),
             ("Day 3 - Legs", ["Squats", "Leg Press", "Lunges", "Hamstring Curls"]),
         ],
         "Home Equipment": [
             ("Day 1 - Push", ["Push Ups", "Dumbbell Shoulder Press", "Dumbbell Flys", "Tricep Extensions"]),
             ("Day 2 - Pull", ["Bent Over Rows", "Resistance Band Pulldowns", "Hammer Curls"]),
             ("Day 3 - Legs", ["Goblet Squats", "Step-ups", "Glute Bridges"]),
         ],
         "None": [
             ("Day 1 - Push", ["Push Ups", "Wall Handstand Holds", "Chair Dips"]),
             ("Day 2 - Pull", ["Superman Holds", "Towel Rows", "Bicep Curls with Bottles"]),
             ("Day 3 - Legs", ["Air Squats", "Jump Squats", "Lunges"]),
         ]
     }
 }
 SEASONING_SUGGESTIONS = [
     "lemon pepper", "garlic and herb", "cumin and paprika", "soy sauce and ginger", "curry powder",
     "chili lime", "Italian seasoning", "rosemary and thyme"
 ]
 
 USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
 USER_STATS_PATH = os.path.join("data", "user_stats.json")
 USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
 MACRO_LOG_PATH = os.path.join("data", "macro_log.json")
 
 # ------------------------- Helpers --------------------------- #
 # ------------------------- Utility Functions --------------------------- #
 
 def load_json(path, default=None):
     os.makedirs(os.path.dirname(path), exist_ok=True)
 def load_json(path, default):
     if os.path.exists(path):
         with open(path, "r") as f:
             try:
                 return json.load(f)
             except json.JSONDecodeError:
                 return default if default is not None else {}
     return default if default is not None else {}
         with open(path, 'r') as f:
             return json.load(f)
     return default
 
 def save_json(path, data):
     os.makedirs(os.path.dirname(path), exist_ok=True)
     with open(path, "w") as f:
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
 
 st.title("🏋️ Personal Trainer & Nutrition Coach")
 st.title("\U0001F4AA Personal Trainer & Nutrition Coach")
 
 menu = [
     "User Intake Form",
     "Set Macro Targets",
     "Workout Program",
     "Meal Plan",
     "Ingredient-Based Suggestions",
     "Log Stats",
     "View Progress",
     "Set Macro Targets",
     "Macro Tracking",
     "Download PDF"
 ]
 
 choice = st.sidebar.selectbox("Menu", menu)
 
 if choice == "User Intake Form":
     st.header("📝 User Intake Form")
     st.header("\U0001F4DD User Intake Form")
     name = st.text_input("Name")
     age = st.number_input("Age", min_value=10, max_value=100)
     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
 @@ -95,6 +140,7 @@
     gym_access = st.selectbox("Access to Equipment", ["None", "Home Equipment", "Gym Access"])
     weight_unit = st.selectbox("Preferred Weight Unit", ["kg", "lb"])
     height_unit = st.selectbox("Preferred Height Unit", ["cm", "in"])
     available_foods = st.multiselect("Select Available Food Items", list(FOOD_DB.keys()))
 
     if st.button("Save Profile"):
         profile = {
 @@ -105,57 +151,63 @@
             "activity_level": activity_level,
             "gym_access": gym_access,
             "weight_unit": weight_unit,
             "height_unit": height_unit
             "height_unit": height_unit,
             "available_foods": available_foods
         }
         save_json(USER_PROFILE_PATH, profile)
         st.success("Profile saved successfully!")
 
 elif choice == "Workout Program":
     st.header("💪 Personalized Workout Program")
     profile = load_json(USER_PROFILE_PATH, {})
     if not profile:
         st.warning("Please complete the intake form first.")
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
         goal = profile.get("goal", "Muscle Gain")
         gym = profile.get("gym_access", "None")
         st.subheader(f"Goal: {goal}")
         st.subheader(f"Equipment: {gym}")
 
         if goal in WORKOUTS and gym in WORKOUTS[goal]:
             for day, exercises in WORKOUTS[goal][gym]:
                 st.markdown(f"### {day}")
                 for ex in exercises:
                     st.markdown(f"- {ex}")
         else:
             st.warning("Workout plan not found for this combination.")
         st.info("No macro data logged yet.")
 
 elif choice == "Meal Plan":
     st.header("🍱 Personalized Meal Plan")
     profile = load_json(USER_PROFILE_PATH, {})
     if not profile:
         st.warning("Please complete the intake form first.")
     else:
         st.write("Daily meal plan based on macro targets and user profile will go here.")
         st.markdown("**Example Meals**")
         st.markdown("**Meal 1**: Oats with whey protein and banana")
         st.markdown("**Meal 2**: Chicken breast, brown rice, broccoli")
         st.markdown("**Meal 3**: Egg and peanut butter sandwich")
         st.markdown("**Snack**: Almonds and olive oil on salad")
     st.header("\U0001F372 Meal Plan Suggestions")
     st.write("Here are some balanced and appetizing macro-conscious meals for today:")
     meals = suggest_balanced_meal()
     for meal in meals:
         st.markdown(meal)
 
 elif choice == "Ingredient-Based Suggestions":
     st.header("🥣 Ingredient-Based Meal Suggestions")
     available = st.text_area("Enter available foods (comma-separated)")
     if st.button("Suggest Meals"):
         available_list = [i.strip().lower() for i in available.split(",")]
         suggestions = [item for item in available_list if item in FOOD_DB]
         if suggestions:
             st.success("Based on your ingredients:")
             for food in suggestions:
                 info = FOOD_DB[food]
                 st.write(f"{food.title()} ({info['unit']}): {info['protein']}g protein, {info['carbs']}g carbs, {info['fat']}g fat")
         else:
             st.warning("No matching foods found in the database.")
 
 # Existing sections like Log Stats, View Progress, Set Macro Targets, Download PDF remain unchanged below
 
 # Existing Log Stats, View Progress, Set Macro Targets, Download PDF unchanged (see original implementation)
     st.header("\U0001F9C2 Customize Available Ingredients")
     available_foods = st.multiselect("Select Available Food Items", list(FOOD_DB.keys()))
     if st.button("Update Available Foods"):
         prefs = load_user_preferences()
         prefs["available_foods"] = available_foods
         save_user_preferences(prefs)
         st.success("Available foods updated!")
 
