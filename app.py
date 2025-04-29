# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import base64
from fpdf import FPDF

# ------------------- Reset to Default Streamlit Theme ------------------- #
st.set_page_config(page_title="Fitness Macro Tracker", layout="wide")

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# ------------------------- Safe Session Reset --------------------------- #
if st.sidebar.button("Reset App"):
    st.session_state.clear()
    st.session_state["reset_triggered"] = True

if st.session_state.get("reset_triggered"):
    st.session_state.pop("reset_triggered")
    st.rerun()

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    "Fruits": {
        "Apple": {"protein": 0.3, "carbs": 14, "fat": 0.2, "unit": "1 medium"},
        "Banana": {"protein": 1.3, "carbs": 27, "fat": 0.3, "unit": "1 medium"},
    },
    "Vegetables": {
        "Broccoli": {"protein": 2.6, "carbs": 6, "fat": 0.3, "unit": "1 cup chopped"},
    }
}

USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
MACRO_LOG_PATH = os.path.join("data", "macro_log.json")
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")

# ------------------------- Sidebar Navigation --------------------------- #
menu = st.sidebar.radio("Select Section", [
    "Intake Form",
    "Macro Targets",
    "Track Meals",
    "Meal Suggestions",
    "Workout Suggestions"
])

# ------------------------- Intake Form --------------------------- #
if menu == "Intake Form":
    st.title("🏋️ Fitness & Nutrition Planner - Intake Form")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    unit_pref = st.radio("Preferred Units", ["Metric (kg, cm)", "Imperial (lbs, inches)"])
    if unit_pref == "Metric (kg, cm)":
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=250, value=70)
    else:
        height = st.number_input("Height (inches)", min_value=40, max_value=100, value=67)
        weight = st.number_input("Weight (lbs)", min_value=66, max_value=550, value=154)

    goal = st.selectbox("Fitness Goal", ["Lose Fat", "Gain Muscle", "Maintain Weight"])
    activity = st.selectbox("Activity Level", ["Sedentary", "Lightly active", "Moderately active", "Very active"])
    equipment = st.multiselect("Available Equipment", ["Dumbbells", "Barbell", "Kettlebell", "Resistance Bands", "Bodyweight only", "Full Commercial Gym"])

    pantry = st.text_area("List food items available in your pantry (comma-separated)")

    if st.button("Save Intake Info"):
        with open(USER_PROFILE_PATH, "w") as f:
            json.dump({
                "name": name,
                "age": age,
                "gender": gender,
                "unit_pref": unit_pref,
                "height": height,
                "weight": weight,
                "goal": goal,
                "activity": activity,
                "equipment": equipment,
                "pantry": pantry.split(",")
            }, f)
        st.success("User intake saved!")

# ------------------------- Macro Target Calculator --------------------------- #
def calculate_macros(weight, goal):
    weight_lb = weight * 2.2
    if goal == "Lose Fat":
        calories = weight_lb * 12
    elif goal == "Gain Muscle":
        calories = weight_lb * 18
    else:
        calories = weight_lb * 15

    protein = weight_lb * 1
    fat = weight_lb * 0.4
    carbs = (calories - (protein * 4 + fat * 9)) / 4
    return round(protein), round(carbs), round(fat), round(calories)

if menu == "Macro Targets":
    st.title("🎯 Your Macro Targets")
    if os.path.exists(USER_PROFILE_PATH):
        try:
            with open(USER_PROFILE_PATH, "r") as f:
                profile = json.load(f)
                weight = profile.get('weight')
                goal = profile.get('goal')
                if weight and goal:
                    protein_g, carbs_g, fat_g, calories = calculate_macros(weight, goal)
                    st.write(f"**Daily Caloric Target:** {calories} kcal")
                    st.write(f"**Protein:** {protein_g}g, **Carbs:** {carbs_g}g, **Fat:** {fat_g}g")
                else:
                    st.warning("Weight or goal missing from profile. Please complete the intake form.")
        except Exception as e:
            st.error(f"Error reading user profile: {e}")
    else:
        st.info("Please fill out the intake form first.")

# ------------------------- Log Macros --------------------------- #
if menu == "Track Meals":
    st.title("🍽️ Track Your Meals")
    log_date = st.date_input("Log Date", value=datetime.date.today())
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    food_group = st.selectbox("Food Group", list(FOOD_DB.keys()))
    food_item = st.selectbox("Food Item", list(FOOD_DB[food_group].keys()))
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)

    if st.button("Add to Log"):
        entry = FOOD_DB[food_group][food_item]
        new_entry = {
            "date": log_date.strftime("%Y-%m-%d"),
            "meal": meal_type,
            "item": food_item,
            "group": food_group,
            "quantity": quantity,
            "protein": round(entry['protein'] * quantity, 2),
            "carbs": round(entry['carbs'] * quantity, 2),
            "fat": round(entry['fat'] * quantity, 2)
        }
        if os.path.exists(MACRO_LOG_PATH):
            with open(MACRO_LOG_PATH, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(new_entry)
        with open(MACRO_LOG_PATH, "w") as f:
            json.dump(data, f)
        st.success("Entry added!")

    if os.path.exists(MACRO_LOG_PATH):
        with open(MACRO_LOG_PATH, "r") as f:
            log_data = json.load(f)
        df = pd.DataFrame(log_data)
        df['date'] = pd.to_datetime(df['date'])
        st.line_chart(df.groupby('date')[['protein', 'carbs', 'fat']].sum())

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Log as CSV", data=csv, file_name="macro_log.csv")

# ------------------------- Meal Suggestions --------------------------- #
if menu == "Meal Suggestions":
    st.title("🍳 Meal Suggestions")
    selected_group = st.selectbox("Choose a food group for suggestions", list(FOOD_DB.keys()))
    if selected_group:
        items = list(FOOD_DB[selected_group].keys())
        for i in range(3):
            item = items[i % len(items)]
            suggestion = FOOD_DB[selected_group][item]
            st.write(f"- **{item.title()}** ({suggestion['unit']}): {suggestion['protein']}g P / {suggestion['carbs']}g C / {suggestion['fat']}g F")

# ------------------------- Workout Generator --------------------------- #
if menu == "Workout Suggestions":
    st.title("💪 Workout Suggestions")
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)
        equipment = profile.get("equipment", [])
        goal = profile.get("goal", "Maintain Weight")
        workouts = []
        if "Bodyweight only" in equipment:
            workouts += ["Push-ups - 3x12", "Air Squats - 3x15", "Plank - 3x60s"]
        if "Dumbbells" in equipment:
            workouts += ["Dumbbell Rows - 3x10", "Dumbbell Shoulder Press - 3x12"]
        if goal == "Lose Fat":
            workouts.append("Cardio (Jogging or Cycling) - 30 min")
        elif goal == "Gain Muscle":
            workouts.append("HIIT - 20 min")
        for w in workouts:
            st.write(f"- {w}")
    else:
        st.info("Please complete intake form to get customized workouts.")

