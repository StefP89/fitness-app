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
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")

# ------------------------- Utility Functions --------------------------- #

# ... (rest of utility functions remain unchanged) ...

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

# ... (existing blocks like Intake Form, Macro Tracking, Meal Plan remain unchanged) ...

elif choice == "Set Macro Targets":
    st.header("\U0001F4C8 Set Your Macro Targets")
    profile = load_json(USER_PROFILE_PATH, {})
    weight_unit = profile.get("weight_unit", "kg")
    weight = st.number_input(f"Enter your weight ({weight_unit})", min_value=30.0, step=0.5)
    goal = profile.get("goal", "Weight Loss")
    activity = profile.get("activity_level", "Moderately Active")

    if weight_unit == "lb":
        weight_kg = weight * 0.453592
    else:
        weight_kg = weight

    activity_factors = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }

    base_calories = weight_kg * 22 * activity_factors.get(activity, 1.55)
    if goal == "Weight Loss":
        calories = base_calories - 500
    elif goal == "Muscle Gain":
        calories = base_calories + 300
    else:
        calories = base_calories

    protein = round(weight_kg * 2.2)
    fat = round((0.25 * calories) / 9)
    carbs = round((calories - (protein * 4 + fat * 9)) / 4)

    st.markdown(f"**Calories:** {int(calories)} kcal")
    st.markdown(f"**Protein:** {protein}g")
    st.markdown(f"**Carbs:** {carbs}g")
    st.markdown(f"**Fat:** {fat}g")

    save_json("data/macro_targets.json", {"calories": calories, "protein": protein, "carbs": carbs, "fat": fat})

elif choice == "Workout Program":
    st.header("\U0001F3CB\ufe0f Customized Workout Program")
    profile = load_json(USER_PROFILE_PATH, {})
    gym_access = profile.get("gym_access", "None")
    goal = profile.get("goal", "Muscle Gain")

    workout_plan = []

    if gym_access == "Gym Access":
        workout_plan = [
            "Day 1: Barbell Squats 4x8, Bench Press 4x8, Bent Over Rows 3x10",
            "Day 2: Deadlifts 3x5, Overhead Press 3x10, Lat Pulldowns 3x12",
            "Day 3: Leg Press 4x10, Dumbbell Flyes 3x12, Cable Rows 3x10"
        ]
    elif gym_access == "Home Equipment":
        workout_plan = [
            "Day 1: Goblet Squats 4x10, Push-Ups 4x15, Dumbbell Rows 3x12",
            "Day 2: Romanian Deadlifts 3x12, Shoulder Press 3x12, Banded Pull-Aparts 3x20",
            "Day 3: Step-Ups 3x15, Incline Push-Ups 3x15, Resistance Band Rows 3x15"
        ]
    else:
        workout_plan = [
            "Day 1: Air Squats 4x20, Push-Ups 4x15, Superman Holds 3x30s",
            "Day 2: Lunges 3x20, Pike Push-Ups 3x10, Planks 3x45s",
            "Day 3: Jump Squats 3x15, Wall Push-Ups 3x20, Glute Bridges 3x20"
        ]

    if goal == "Weight Loss":
        workout_plan.append("Add 20-30 min brisk walking or light jogging on off days.")
    elif goal == "Endurance":
        workout_plan.append("Include 3 days/week of 30-45 min cycling, swimming, or running.")
    else:
        workout_plan.append("Optional cardio: 15-20 min incline treadmill or cycling post workout.")

    for w in workout_plan:
        st.markdown(f"- {w}")
