# Streamlit Version of Online Personal Trainer

import streamlit as st
import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# ------------------- Streamlit Setup ------------------- #
st.set_page_config(page_title="Online Personal Trainer", layout="wide")

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# ------------------- File Paths ------------------- #
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
WORKOUT_LOG_PATH = os.path.join("data", "workout_log.json")
PROGRESS_LOG_PATH = os.path.join("data", "progress_log.json")

# ------------------- Sidebar Navigation ------------------- #
st.sidebar.title("Online Personal Trainer")
page = st.sidebar.radio("Navigation", [
    "Main Page",
    "User Intake Form",
    "Workout Suggestions",
    "Log Workout",
    "Macro Calculator",
    "Log Progress"
])

# ------------------- Reset App Modal ------------------- #
if st.sidebar.button("Reset App"):
    st.session_state["show_reset_modal"] = True
    st.experimental_rerun()

if st.session_state.get("show_reset_modal", False):
    st.warning("⚠️ This will clear all entered data. Are you sure you want to proceed?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Reset"):
            st.session_state.clear()
            for path in [USER_PROFILE_PATH, WORKOUT_LOG_PATH, PROGRESS_LOG_PATH]:
                if os.path.exists(path):
                    os.remove(path)
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.pop("show_reset_modal", None)

# ------------------- Macro Calculation Function ------------------- #
def calculate_macros(weight, height, age, gender, goal, unit):
    if unit == "Imperial (lbs, inches)":
        weight_kg = weight * 0.453592
        height_cm = height * 2.54
    else:
        weight_kg = weight
        height_cm = height

    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender == "Female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age

    activity_factor = 1.55  # Moderately active by default
    tdee = bmr * activity_factor

    if goal == "Fat Loss":
        calories = tdee - 500
    elif goal == "Muscle Gain":
        calories = tdee + 300
    else:
        calories = tdee

    protein = weight_kg * 2.2
    fat = weight_kg * 1
    carbs = (calories - (protein * 4 + fat * 9)) / 4

    return round(protein), round(carbs), round(fat), round(calories)

# ------------------- Weekly Workout Generator ------------------- #
def generate_weekly_workout(goal, equipment):
    def include_ex(equip, opts):
        if equip == "None - Bodyweight Only":
            return opts.get("bodyweight", [])
        elif equip == "Home - Dumbbells and Bands":
            return opts.get("dumbbells", [])
        elif equip == "Home - Barbell, Bench, Squat Rack":
            return opts.get("barbell", [])
        else:
            return opts.get("gym", [])

    weekly = {}
    workout_split = ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body"]

    exercises = {
        "Push Day": {
            "bodyweight": [("Push-ups", 4, 15), ("Dips on chair", 3, 12), ("Pike Push-ups", 3, 10)],
            "dumbbells": [("DB Bench Press", 4, 10), ("DB Overhead Press", 3, 12), ("DB Tricep Kickbacks", 3, 12)],
            "barbell": [("Barbell Bench Press", 4, 8), ("Overhead Press", 4, 10), ("Close Grip Press", 3, 10)],
            "gym": [("Incline Bench Press", 4, 8), ("Seated Shoulder Press Machine", 3, 12), ("Tricep Pushdown", 3, 12)]
        },
        "Pull Day": {
            "bodyweight": [("Inverted Rows", 4, 12), ("Superman Holds", 3, 30), ("Bodyweight Bicep Curls", 3, 15)],
            "dumbbells": [("DB Rows", 4, 10), ("DB Bicep Curls", 3, 12), ("Band Face Pulls", 3, 15)],
            "barbell": [("Barbell Row", 4, 10), ("EZ Bar Curl", 3, 12), ("Lat Pulldown (if available)", 3, 10)],
            "gym": [("Lat Pulldown", 4, 10), ("Cable Row", 3, 12), ("Barbell Curl", 3, 12)]
        },
        "Leg Day": {
            "bodyweight": [("Bodyweight Squats", 4, 20), ("Lunges", 3, 15), ("Wall Sit", 3, 30)],
            "dumbbells": [("Goblet Squat", 4, 12), ("DB Lunges", 3, 10), ("Romanian Deadlift", 3, 12)],
            "barbell": [("Back Squat", 4, 8), ("Barbell Lunge", 3, 10), ("Barbell RDL", 3, 10)],
            "gym": [("Leg Press", 4, 10), ("Leg Curl Machine", 3, 12), ("Smith Squat", 3, 10)]
        },
        "Whole Body": {
            "bodyweight": [("Burpees", 3, 15), ("Jump Squats", 3, 12), ("Mountain Climbers", 3, 30)],
            "dumbbells": [("DB Snatch", 3, 10), ("Thrusters", 3, 12), ("KB Swing", 3, 15)],
            "barbell": [("Clean & Press", 3, 8), ("Thrusters", 3, 10), ("Deadlifts", 3, 10)],
            "gym": [("Battle Ropes", 3, 30), ("Clean & Press", 3, 8), ("Jump Rope", 3, 60)]
        },
        "Upper Body": {
            "bodyweight": [("Push-ups", 4, 15), ("Inverted Rows", 4, 12), ("Pike Push-ups", 3, 10)],
            "dumbbells": [("DB Bench Press", 4, 10), ("DB Row", 4, 10), ("DB Overhead Press", 3, 12)],
            "barbell": [("Bench Press", 4, 8), ("Barbell Row", 4, 10), ("Overhead Press", 3, 10)],
            "gym": [("Chest Press", 4, 10), ("Lat Pulldown", 4, 10), ("Shoulder Press", 3, 12)]
        }
    }

    for day in workout_split:
        workout = include_ex(equipment, exercises[day])
        if goal == "Fat Loss":
            rest = "30-60 sec rest. Add 20-30 min cardio."
        elif goal == "Muscle Gain":
            rest = "60-90 sec rest. Cardio optional."
        else:
            rest = "60 sec rest. Moderate cardio 2x/week."
        weekly[day] = (workout, rest)
    return weekly

# ------------------- Workout Logging ------------------- #
def log_workout(date, day, exercises):
    entry = {
        "date": str(date),
        "day": day,
        "exercises": exercises
    }
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(entry)
    with open(WORKOUT_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

# ------------------- Progress Logging ------------------- #
def log_progress(date, weight, waist, notes):
    entry = {
        "date": str(date),
        "weight": weight,
        "waist": waist,
        "notes": notes
    }
    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(entry)
    with open(PROGRESS_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)
