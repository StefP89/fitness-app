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
    strength = {
        "None - Bodyweight Only": ["Push-ups", "Squats", "Lunges", "Plank"],
        "Home - Dumbbells and Bands": ["Dumbbell Press", "Goblet Squat", "Bent-over Rows", "Banded Pull Aparts"],
        "Home - Barbell, Bench, Squat Rack": ["Barbell Squats", "Bench Press", "Barbell Rows", "Overhead Press"],
        "Full Commercial Gym": ["Deadlifts", "Leg Press", "Lat Pulldown", "Incline Bench Press"]
    }
    cardio = ["Running", "Cycling", "Jump Rope", "Rowing Machine"]
    workout = strength.get(equipment, [])
    if goal == "Fat Loss":
        workout += cardio
    return workout

# ------------------- Main Page ------------------- #
if page == "Main Page":
    st.title("Welcome to Online Personal Trainer")
    st.write("This is your centralized dashboard for tracking workouts, calculating macros, and monitoring progress.")
    st.image("https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg", use_column_width=True)

# ------------------- User Intake Form ------------------- #
if page == "User Intake Form":
    st.title("User Intake Form")

    with st.form("intake_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=10, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"])

        unit_preference = st.radio("Preferred Units", ["Metric (kg, cm)", "Imperial (lbs, inches)"])

        if unit_preference == "Metric (kg, cm)":
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0)
        else:
            weight = st.number_input("Weight (lbs)", min_value=66.0, max_value=660.0, value=154.0)
            height = st.number_input("Height (inches)", min_value=39.0, max_value=98.0, value=69.0)

        goal = st.selectbox("What is your current fitness goal?", [
            "Fat Loss",
            "Muscle Gain",
            "Maintenance"
        ])

        equipment = st.selectbox("Available Equipment", [
            "None - Bodyweight Only",
            "Home - Dumbbells and Bands",
            "Home - Barbell, Bench, Squat Rack",
            "Full Commercial Gym"
        ])

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            user_profile = {
                "name": name,
                "age": age,
                "gender": gender,
                "unit_preference": unit_preference,
                "weight": weight,
                "height": height,
                "goal": goal,
                "equipment": equipment,
            }

            with open(USER_PROFILE_PATH, "w") as f:
                json.dump(user_profile, f)

            st.success("Profile saved successfully!")

# ------------------- Workout Suggestions ------------------- #
if page == "Workout Suggestions":
    st.title("Today's Workout Plan")

    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)

        exercises = get_workout(profile["goal"], profile["equipment"])

        st.subheader(f"Workout for {profile['goal']}")
        for ex in exercises:
            st.write(f"- {ex}")
    else:
        st.warning("Please complete the intake form first.")

# ------------------- Log Workout ------------------- #
if page == "Log Workout":
    st.title("Log Your Workout")

    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)

        exercises = get_workout(profile["goal"], profile["equipment"])

        workout_data = []

        with st.form("log_workout"):
            for ex in exercises:
                st.markdown(f"### {ex}")
                sets = st.number_input(f"Number of sets for {ex}", min_value=1, max_value=10, value=3)
                reps = []
                weights = []
                for i in range(sets):
                    col1, col2 = st.columns(2)
                    with col1:
                        reps.append(st.number_input(f"Reps - Set {i+1} ({ex})", key=f"reps_{ex}_{i}"))
                    with col2:
                        weights.append(st.number_input(f"Weight - Set {i+1} ({ex})", key=f"weight_{ex}_{i}"))
                workout_data.append({"exercise": ex, "sets": sets, "reps": reps, "weights": weights})

            submit_log = st.form_submit_button("Save Workout")

        if submit_log:
            log_entry = {
                "date": str(datetime.date.today()),
                "workout": workout_data
            }
            if os.path.exists(WORKOUT_LOG_PATH):
                with open(WORKOUT_LOG_PATH, "r") as f:
                    workout_log = json.load(f)
            else:
                workout_log = []
            workout_log.append(log_entry)
            with open(WORKOUT_LOG_PATH, "w") as f:
                json.dump(workout_log, f)
            st.success("Workout logged successfully!")
    else:
        st.warning("Please complete the intake form first.")


