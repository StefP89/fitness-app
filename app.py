# streamlit_app.py

import streamlit as st
import datetime
import json
import os
import pandas as pd

# ------------------- Setup ------------------- #
st.set_page_config(page_title="Online Personal Trainer", layout="wide")
if not os.path.exists("data"):
    os.makedirs("data")

USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
WORKOUT_LOG_PATH = os.path.join("data", "workout_log.json")
PROGRESS_LOG_PATH = os.path.join("data", "progress_log.json")

# ------------------- Sidebar ------------------- #
st.sidebar.title("Online Personal Trainer")
page = st.sidebar.radio("Navigation", [
    "Main Page", "User Intake Form", "Workout Suggestions",
    "Log Workout", "Macro Calculator", "Log Progress", "Workout History"
])

# ------------------- Utility Functions ------------------- #
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

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

    tdee = bmr * 1.55  # Moderate activity

    if goal == "Fat Loss":
        calories = tdee - 500
    elif goal == "Muscle Gain":
        calories = tdee + 250
    else:
        calories = tdee

    protein = weight_kg * 2.2
    fat = weight_kg * 1
    carbs = (calories - (protein * 4 + fat * 9)) / 4
    return round(protein), round(carbs), round(fat), round(calories)

def generate_weekly_workout(goal, equipment):
    exercises_dict = {
        "None - Bodyweight Only": {
            "Push": [("Push-ups", 3, 15), ("Dips (chair)", 3, 10)],
            "Pull": [("Door Rows", 3, 12), ("Superman", 3, 15)],
            "Legs": [("Bodyweight Squats", 4, 15), ("Lunges", 3, 12)],
            "Whole": [("Burpees", 3, 12), ("Plank", 3, "30s")],
            "Upper": [("Wall Push-ups", 3, 20), ("Shoulder Taps", 3, 20)]
        },
        "Home - Dumbbells and Bands": {
            "Push": [("Dumbbell Bench Press", 4, 10), ("Overhead Press", 3, 10)],
            "Pull": [("Dumbbell Row", 3, 10), ("Band Pull Apart", 3, 15)],
            "Legs": [("Dumbbell Squat", 4, 12), ("Glute Bridge", 3, 15)],
            "Whole": [("Thrusters", 3, 12), ("Mountain Climbers", 3, 30)],
            "Upper": [("Arnold Press", 3, 10), ("Curls", 3, 12)]
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Push": [("Barbell Bench Press", 4, 8), ("Overhead Press", 3, 10)],
            "Pull": [("Barbell Row", 4, 10), ("Band Pull Apart", 3, 15)],
            "Legs": [("Barbell Squat", 4, 8), ("Romanian Deadlift", 3, 10)],
            "Whole": [("Deadlift", 4, 6), ("Burpees", 3, 10)],
            "Upper": [("Incline Bench Press", 3, 10), ("Barbell Curl", 3, 12)]
        },
        "Full Commercial Gym": {
            "Push": [("Machine Chest Press", 4, 10), ("Dumbbell Overhead Press", 3, 12)],
            "Pull": [("Lat Pulldown", 4, 12), ("Seated Row", 3, 10)],
            "Legs": [("Leg Press", 4, 12), ("Hamstring Curl", 3, 12)],
            "Whole": [("Kettlebell Swings", 3, 15), ("Battle Ropes", 3, 30)],
            "Upper": [("Cable Flys", 3, 15), ("Face Pulls", 3, 15)]
        }
    }

    rest = "60-90 seconds between sets"
    week = ["Push", "Pull", "Legs", "Whole", "Upper"]
    plan = {}
    for day in week:
        plan[f"{day} Day"] = (exercises_dict[equipment][day], rest)
    return plan

def log_workout(date, day, exercises):
    logs = load_json(WORKOUT_LOG_PATH)
    logs.append({"date": str(date), "day": day, "exercises": exercises})
    save_json(WORKOUT_LOG_PATH, logs)

def log_progress(date, weight, waist, notes):
    logs = load_json(PROGRESS_LOG_PATH)
    logs.append({"date": str(date), "weight": weight, "waist": waist, "notes": notes})
    save_json(PROGRESS_LOG_PATH, logs)

# ------------------- Pages ------------------- #
if page == "Main Page":
    st.title("🏋️‍♀️ Online Personal Trainer")
    st.write("Welcome! Use the sidebar to navigate through the app.")

elif page == "User Intake Form":
    st.header("User Intake Form")
    unit = st.radio("Preferred Units", ["Imperial (lbs, inches)", "Metric (kg, cm)"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"])
    age = st.number_input("Age", 10, 100)
    weight = st.number_input("Weight", 0.0)
    height = st.number_input("Height", 0.0)
    goal = st.selectbox("Primary Goal", ["Fat Loss", "Muscle Gain", "General Fitness"])
    equipment = st.selectbox("Available Equipment", [
        "None - Bodyweight Only", "Home - Dumbbells and Bands",
        "Home - Barbell, Bench, Squat Rack", "Full Commercial Gym"
    ])
    if st.button("Save Profile"):
        profile = {
            "unit": unit, "gender": gender, "age": age,
            "weight": weight, "height": height, "goal": goal,
            "equipment": equipment
        }
        save_json(USER_PROFILE_PATH, profile)
        st.success("Profile saved!")

elif page == "Macro Calculator":
    st.header("Macro Calculator")
    profile = load_json(USER_PROFILE_PATH)
    if profile:
        p, c, f, cal = calculate_macros(
            profile["weight"], profile["height"], profile["age"],
            profile["gender"], profile["goal"], profile["unit"]
        )
        st.metric("Calories", f"{cal} kcal")
        st.metric("Protein", f"{p} g")
        st.metric("Carbs", f"{c} g")
        st.metric("Fat", f"{f} g")
    else:
        st.warning("Please complete the intake form.")

elif page == "Workout Suggestions":
    st.header("Weekly Workout Plan")
    profile = load_json(USER_PROFILE_PATH)
    if profile:
        plan = generate_weekly_workout(profile["goal"], profile["equipment"])
        for day, (exs, rest) in plan.items():
            with st.expander(day):
                for name, sets, reps in exs:
                    st.write(f"**{name}**: {sets} sets x {reps} reps")
                st.caption(rest)
    else:
        st.warning("Please complete the intake form.")

elif page == "Log Workout":
    st.header("Log Workout")
    date = st.date_input("Date", datetime.date.today())
    day = st.selectbox("Workout Type", ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body"])
    exercises = []
    for i in range(1, 6):
        name = st.text_input(f"Exercise {i} Name", key=f"ex{i}")
        sets = st.number_input("Sets", 1, 10, key=f"sets{i}")
        reps = st.number_input("Reps", 1, 30, key=f"reps{i}")
        weight = st.number_input("Weight Used", 0.0, 1000.0, key=f"wt{i}")
        if name:
            exercises.append({"name": name, "sets": sets, "reps": reps, "weight": weight})
    if st.button("Log Workout"):
        log_workout(date, day, exercises)
        st.success("Workout logged!")

elif page == "Log Progress":
    st.header("Log Body Progress")
    date = st.date_input("Date", datetime.date.today())
    weight = st.number_input("Weight", 0.0, 1000.0)
    waist = st.number_input("Waist Circumference", 0.0, 200.0)
    notes = st.text_area("Notes (optional)")
    if st.button("Log Progress"):
        log_progress(date, weight, waist, notes)
        st.success("Progress logged!")

elif page == "Workout History":
    st.header("Workout History")
    logs = load_json(WORKOUT_LOG_PATH)
    if logs:
        st.dataframe(pd.DataFrame(logs))
    else:
        st.info("No workout logs found.")
