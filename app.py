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

# ------------------- Safe Session Reset ------------------- #
if st.sidebar.button("Reset App"):
    st.session_state.clear()
    st.session_state["reset_triggered"] = True

if st.session_state.get("reset_triggered"):
    st.session_state.pop("reset_triggered")
    st.rerun()

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

# ------------------- File Paths ------------------- #
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
WORKOUT_LOG_PATH = os.path.join("data", "workout_log.json")
PROGRESS_LOG_PATH = os.path.join("data", "progress_log.json")

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

    activity_factor = 1.55
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

# ------------------- Workout Plan Generator ------------------- #
def get_workout(goal, equipment):
    workouts = {
        "None - Bodyweight Only": [
            {"exercise": "Push-ups", "sets": 3, "reps": 15, "rest": "30s"},
            {"exercise": "Squats", "sets": 3, "reps": 20, "rest": "30s"},
            {"exercise": "Lunges", "sets": 3, "reps": 12, "rest": "30s"},
            {"exercise": "Plank", "sets": 3, "reps": "60s hold", "rest": "30s"}
        ],
        "Home - Dumbbells and Bands": [
            {"exercise": "Dumbbell Press", "sets": 3, "reps": 12, "rest": "60s"},
            {"exercise": "Goblet Squat", "sets": 3, "reps": 15, "rest": "60s"},
            {"exercise": "Bent-over Rows", "sets": 3, "reps": 12, "rest": "60s"},
            {"exercise": "Banded Pull Aparts", "sets": 3, "reps": 20, "rest": "45s"}
        ],
        "Home - Barbell, Bench, Squat Rack": [
            {"exercise": "Barbell Squats", "sets": 4, "reps": 8, "rest": "90s"},
            {"exercise": "Bench Press", "sets": 4, "reps": 8, "rest": "90s"},
            {"exercise": "Barbell Rows", "sets": 4, "reps": 10, "rest": "90s"},
            {"exercise": "Overhead Press", "sets": 3, "reps": 10, "rest": "60s"}
        ],
        "Full Commercial Gym": [
            {"exercise": "Deadlifts", "sets": 4, "reps": 5, "rest": "2 min"},
            {"exercise": "Leg Press", "sets": 4, "reps": 12, "rest": "90s"},
            {"exercise": "Lat Pulldown", "sets": 4, "reps": 12, "rest": "90s"},
            {"exercise": "Incline Bench Press", "sets": 3, "reps": 10, "rest": "90s"}
        ]
    }

    cardio_options = [
        {"exercise": "Running", "sets": 1, "reps": "20 min", "rest": ""},
        {"exercise": "Cycling", "sets": 1, "reps": "30 min", "rest": ""},
        {"exercise": "Jump Rope", "sets": 1, "reps": "15 min", "rest": ""}
    ]

    workout = workouts.get(equipment, [])
    if goal == "Fat Loss":
        workout += cardio_options
    return workout

# ------------------- Workout Logger ------------------- #
def log_workout(workout):
    st.title("Log Your Workout")
    today = str(datetime.date.today())
    log_entries = []

    for ex in workout:
        st.subheader(ex["exercise"])
        sets_data = []
        for s in range(1, ex["sets"] + 1):
            col1, col2 = st.columns(2)
            with col1:
                reps = st.number_input(f"Set {s} Reps - {ex['exercise']}", min_value=0, key=f"{ex['exercise']}_reps_{s}")
            with col2:
                weight = st.number_input(f"Set {s} Weight - {ex['exercise']}", min_value=0.0, key=f"{ex['exercise']}_wt_{s}")
            sets_data.append({"set": s, "reps": reps, "weight": weight})
        log_entries.append({"exercise": ex["exercise"], "sets": sets_data})

    if st.button("Save Workout Log"):
        if os.path.exists(WORKOUT_LOG_PATH):
            with open(WORKOUT_LOG_PATH, "r") as f:
                logs = json.load(f)
        else:
            logs = {}
        logs[today] = log_entries
        with open(WORKOUT_LOG_PATH, "w") as f:
            json.dump(logs, f)
        st.success("Workout logged!")

# ------------------- Log Workout Page ------------------- #
if page == "Log Workout":
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)
        exercises = get_workout(profile["goal"], profile["equipment"])
        log_workout(exercises)
    else:
        st.warning("Please complete the intake form first.")

# ------------------- Macro Calculator ------------------- #
if page == "Macro Calculator":
    st.title("Macro Calculator")
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)
        p, c, f, cal = calculate_macros(
            profile["weight"], profile["height"], profile["age"],
            profile["gender"], profile["goal"], profile["unit"])

        st.metric("Calories", cal)
        st.metric("Protein (g)", p)
        st.metric("Carbs (g)", c)
        st.metric("Fat (g)", f)
    else:
        st.warning("Please complete the intake form first.")


