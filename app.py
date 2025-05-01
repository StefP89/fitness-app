# Streamlit Version of Online Personal Trainer

import streamlit as st
import datetime
import json
import os
import pandas as pd

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

if st.session_state.get("show_reset_modal"):
    with st.modal("⚠️ Confirm Reset"):
        st.write("This will clear all entered data. Are you sure you want to proceed?")
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

# ------------------- Workout Generator ------------------- #
def generate_workout(goal, equipment):
    workouts = {
        "None - Bodyweight Only": {
            "Fat Loss": [
                "Jumping Jacks - 3x30 sec", "Push-ups - 3x15", "Bodyweight Squats - 3x20",
                "Mountain Climbers - 3x30 sec", "Plank - 3x30 sec", "Cardio: 20-min brisk walk or jog"
            ],
            "Muscle Gain": [
                "Push-ups - 4x12", "Step-ups - 3x12 each leg", "Triceps Dips on Chair - 3x10",
                "Bodyweight Squats - 4x15", "Optional: Light Cardio 10 min"
            ],
            "Maintenance": [
                "Lunges - 3x12", "Plank - 3x30 sec", "Burpees - 3x10",
                "Jump Rope - 3x1 min", "Walk or Cycle - 15 min"
            ]
        },
        "Home - Dumbbells and Bands": {
            "Fat Loss": [
                "Dumbbell Thrusters - 3x15", "Band Rows - 3x15", "Dumbbell Lunges - 3x12",
                "Mountain Climbers - 3x30 sec", "Jump Rope - 5 min"
            ],
            "Muscle Gain": [
                "DB Bench Press - 4x10", "DB Deadlifts - 4x10", "DB Curls - 3x12",
                "Band Lateral Raises - 3x15", "Optional: Light Cardio 10 min"
            ],
            "Maintenance": [
                "Goblet Squat - 3x12", "Band Row - 3x15", "DB Shoulder Press - 3x12",
                "Cardio: Brisk Walk or Jog 15-20 min"
            ]
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Fat Loss": [
                "Barbell Squats - 4x10", "Barbell Rows - 4x10", "Push Press - 4x8",
                "HIIT Circuit: 15 min"
            ],
            "Muscle Gain": [
                "Bench Press - 4x8", "Barbell Squats - 4x10", "Romanian Deadlifts - 4x10",
                "Pull-ups - 3x max reps", "Optional: Light Treadmill Walk 10 min"
            ],
            "Maintenance": [
                "Front Squats - 3x10", "Overhead Press - 3x10", "Barbell Rows - 3x12",
                "Cardio: 20 min moderate effort"
            ]
        },
        "Full Commercial Gym": {
            "Fat Loss": [
                "Leg Press - 3x15", "Lat Pulldown - 3x12", "Treadmill Intervals - 20 min",
                "Cable Chest Fly - 3x12", "Battle Ropes - 3x30 sec"
            ],
            "Muscle Gain": [
                "Barbell Deadlift - 4x6", "Incline Press - 4x8", "Cable Row - 4x12",
                "Leg Extension - 4x15", "Optional Stairmaster 10 min"
            ],
            "Maintenance": [
                "Chest Press - 3x12", "Leg Curl - 3x15", "Lat Pulldown - 3x12",
                "Cardio: Elliptical 15-20 min"
            ]
        }
    }
    return workouts.get(equipment, {}).get(goal, ["No plan available. Please check inputs."])

# ------------------- Intake Form ------------------- #
if page == "User Intake Form":
    st.title("User Intake Form")
    unit = st.selectbox("Preferred Units", ["Metric (kg, cm)", "Imperial (lbs, inches)"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"])
    age = st.number_input("Age", min_value=10, max_value=100, step=1)

    if unit == "Imperial (lbs, inches)":
        weight = st.number_input("Weight (lbs)", min_value=50.0, max_value=500.0)
        height = st.number_input("Height (inches)", min_value=48.0, max_value=96.0)
    else:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=250.0)
        height = st.number_input("Height (cm)", min_value=120.0, max_value=240.0)

    goal = st.selectbox("Goal", ["Fat Loss", "Muscle Gain", "Maintenance"])
    equipment = st.selectbox("Available Equipment", [
        "None - Bodyweight Only",
        "Home - Dumbbells and Bands",
        "Home - Barbell, Bench, Squat Rack",
        "Full Commercial Gym"
    ])

    if st.button("Save Profile"):
        profile = {
            "unit": unit,
            "gender": gender,
            "age": age,
            "weight": weight,
            "height": height,
            "goal": goal,
            "equipment": equipment
        }
        with open(USER_PROFILE_PATH, "w") as f:
            json.dump(profile, f)
        st.session_state["profile"] = profile
        st.success("Profile saved!")

# ------------------- Main Page ------------------- #
if page == "Main Page":
    st.title("Welcome to Your Online Personal Trainer")
    st.markdown("Use the navigation menu to begin your fitness journey. Track workouts, calculate macros, and more.")

# ------------------- Workout Suggestions ------------------- #
if page == "Workout Suggestions":
    st.title("Workout Suggestions")
    profile = st.session_state.get("profile")
    if not profile and os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH) as f:
            profile = json.load(f)

    if profile:
        st.subheader(f"Goal: {profile['goal']}, Equipment: {profile['equipment']}")
        workout = generate_workout(profile["goal"], profile["equipment"])
        for ex in workout:
            st.write(f"- {ex}")
    else:
        st.warning("Please complete the intake form first.")

# ------------------- Log Workout ------------------- #
# [... unchanged ...]

# ------------------- Macro Calculator ------------------- #
# [... unchanged ...]

# ------------------- Log Progress ------------------- #
# [... unchanged ...]
