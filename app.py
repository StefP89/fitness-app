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

# ------------------- Safe Session Reset with Confirmation Modal ------------------- #
if st.sidebar.button("Reset App"):
    st.session_state["show_reset_modal"] = True

if st.session_state.get("show_reset_modal"):
    with st.modal("⚠️ Confirm Reset"):
        st.write("This will clear all entered data. Are you sure you want to proceed?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Reset"):
                st.session_state.clear()
                st.session_state["reset_triggered"] = True
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.pop("show_reset_modal", None)

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
        st.success("Profile saved!")

# ------------------- (remaining code unchanged) ------------------- #
