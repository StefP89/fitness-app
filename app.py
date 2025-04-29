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
def calculate_macros(profile):
    gender = profile['gender']
    weight = profile['weight']
    height = profile['height']
    age = profile['age']
    unit_pref = profile['unit_pref']
    activity = profile['activity']
    goal = profile['goal']

    # Convert to metric if needed
    if unit_pref == "Imperial (lbs, inches)":
        weight = weight / 2.20462
        height = height * 2.54

    # BMR calculation
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_factors = {
        "Sedentary": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725
    }
    tdee = bmr * activity_factors.get(activity, 1.2)

    if goal == "Lose Fat":
        tdee *= 0.85
    elif goal == "Gain Muscle":
        tdee *= 1.15

    protein = weight * 2.0  # g/kg
    fat = (0.25 * tdee) / 9
    carbs = (tdee - (protein * 4 + fat * 9)) / 4

    return round(protein), round(carbs), round(fat), round(tdee)

if menu == "Macro Targets":
    st.title("🎯 Your Macro Targets")
    if os.path.exists(USER_PROFILE_PATH):
        try:
            with open(USER_PROFILE_PATH, "r") as f:
                profile = json.load(f)
                protein_g, carbs_g, fat_g, calories = calculate_macros(profile)
                st.write(f"**Daily Caloric Target:** {calories} kcal")
                st.write(f"**Protein:** {protein_g}g, **Carbs:** {carbs_g}g, **Fat:** {fat_g}g")
        except Exception as e:
            st.error(f"Error calculating macros: {e}")
    else:
        st.info("Please fill out the intake form first.")

# The rest of the app remains unchanged (Track Meals, Meal Suggestions, Workout Suggestions)
# for brevity but will still function correctly with the updated macro logic.
