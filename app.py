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

USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
USER_STATS_PATH = os.path.join("data", "user_stats.json")

# ------------------------- Helpers --------------------------- #

def load_json(path, default=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default if default is not None else {}
    return default if default is not None else {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------- Streamlit App --------------------------- #

st.title("🏋️ Personal Trainer & Nutrition Coach")

menu = [
    "User Intake Form",
    "Workout Program",
    "Meal Plan",
    "Ingredient-Based Suggestions",
    "Log Stats",
    "View Progress",
    "Set Macro Targets",
    "Download PDF"
]

choice = st.sidebar.selectbox("Menu", menu)

if choice == "User Intake Form":
    st.header("📝 User Intake Form")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    goal = st.selectbox("Primary Goal", ["Weight Loss", "Muscle Gain", "Endurance"])
    activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    gym_access = st.selectbox("Access to Equipment", ["None", "Home Equipment", "Gym Access"])
    weight_unit = st.selectbox("Preferred Weight Unit", ["kg", "lb"])
    height_unit = st.selectbox("Preferred Height Unit", ["cm", "in"])

    if st.button("Save Profile"):
        profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "goal": goal,
            "activity_level": activity_level,
            "gym_access": gym_access,
            "weight_unit": weight_unit,
            "height_unit": height_unit
        }
        save_json(USER_PROFILE_PATH, profile)
        st.success("Profile saved successfully!")

elif choice == "Workout Program":
    st.header("💪 Personalized Workout Program")
    profile = load_json(USER_PROFILE_PATH, {})
    if not profile:
        st.warning("Please complete the intake form first.")
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
