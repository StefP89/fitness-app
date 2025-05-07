# Online Personal Trainer - Streamlit App

import streamlit as st
import json
import os
import datetime
import pandas as pd

# ------------------- Setup ------------------- #
st.set_page_config(page_title="Online Personal Trainer", layout="wide")

if not os.path.exists("data"):
    os.makedirs("data")

USER_PROFILE_PATH = "data/user_profile.json"
WORKOUT_LOG_PATH = "data/workout_log.json"
PROGRESS_LOG_PATH = "data/progress_log.json"

# ------------------- Sidebar ------------------- #
st.sidebar.title("Online Personal Trainer")
page = st.sidebar.radio("Navigation", [
    "Main Page", "User Intake Form", "Workout Suggestions",
    "Log Workout", "Macro Calculator", "Log Progress", "Workout History"
])

if st.sidebar.button("Reset App"):
    for path in [USER_PROFILE_PATH, WORKOUT_LOG_PATH, PROGRESS_LOG_PATH]:
        if os.path.exists(path):
            os.remove(path)
    st.success("App reset! Refresh the page.")
    st.stop()

# ------------------- Helpers ------------------- #
def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def calculate_macros(weight, height, age, gender, goal, unit):
    if unit == "Imperial (lbs, inches)":
        weight_kg = weight * 0.453592
        height_cm = height * 2.54
    else:
        weight_kg = weight
        height_cm = height

    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multiplier = 1.5
    tdee = bmr * activity_multiplier

    if goal == "Fat Loss":
        tdee -= 500
    elif goal == "Muscle Gain":
        tdee += 250

    protein = int(weight_kg * 2.2)
    fat = int((0.25 * tdee) / 9)
    carbs = int((tdee - (protein * 4 + fat * 9)) / 4)

    return protein, carbs, fat, int(tdee)

def log_workout(date, day, exercises):
    logs = load_json(WORKOUT_LOG_PATH)
    logs.append({"date": str(date), "day": day, "exercises": exercises})
    save_json(logs, WORKOUT_LOG_PATH)

def log_progress(date, weight, waist, notes):
    logs = load_json(PROGRESS_LOG_PATH)
    logs.append({"date": str(date), "weight": weight, "waist": waist, "notes": notes})
    save_json(logs, PROGRESS_LOG_PATH)

def generate_weekly_workout(goal, equipment):
    workouts = {
        "None - Bodyweight Only": {
            "Push": [("Push-ups", 3, 12), ("Dips (chair)", 3, 10), ("Wall Push-ups", 3, 15), ("Shoulder Taps", 3, 20), ("Incline Push-ups", 3, 10)],
            "Pull": [("Door Rows", 3, 10), ("Superman Hold", 3, 30), ("Towel Curls", 3, 12), ("Wall Slides", 3, 10), ("Back Extensions", 3, 12)],
            "Legs": [("Bodyweight Squats", 4, 15), ("Lunges", 3, 12), ("Wall Sit", 3, 30), ("Glute Bridges", 3, 15), ("Step-ups", 3, 12)],
            "Upper Body": [("Push-ups", 3, 12), ("Door Rows", 3, 10), ("Shoulder Taps", 3, 20), ("Towel Curls", 3, 12), ("Plank to Push-up", 3, 10)],
            "Whole Body": [("Burpees", 3, 10), ("Jumping Jacks", 3, 30), ("Lunges", 3, 12), ("Push-ups", 3, 12), ("Mountain Climbers", 3, 20)],
        },
        "Home - Dumbbells and Bands": {
            "Push": [("Dumbbell Shoulder Press", 3, 12), ("Dumbbell Chest Press", 3, 10), ("Band Front Raise", 3, 15), ("Overhead Triceps Ext", 3, 12), ("Incline DB Press", 3, 10)],
            "Pull": [("Dumbbell Rows", 3, 12), ("Band Face Pulls", 3, 15), ("Dumbbell Curls", 3, 12), ("Band Lat Pulldown", 3, 15), ("Reverse Flys", 3, 10)],
            "Legs": [("Dumbbell Squats", 3, 12), ("Lunges", 3, 12), ("Glute Bridge", 3, 15), ("Calf Raise", 3, 20), ("Goblet Squat", 3, 12)],
            "Upper Body": [("DB Shoulder Press", 3, 12), ("DB Rows", 3, 12), ("DB Chest Press", 3, 10), ("DB Curls", 3, 12), ("Band Pull-aparts", 3, 15)],
            "Whole Body": [("DB Squats", 3, 12), ("DB Clean & Press", 3, 10), ("Lunges", 3, 12), ("Push-ups", 3, 12), ("Mountain Climbers", 3, 20)],
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Push": [("Barbell Bench Press", 4, 10), ("Overhead Press", 4, 8), ("Incline Bench", 3, 10), ("Lateral Raise", 3, 15), ("Skullcrushers", 3, 12)],
            "Pull": [("Barbell Row", 4, 10), ("Chin-ups", 3, 8), ("Barbell Curls", 3, 12), ("Face Pulls", 3, 15), ("Reverse Flys", 3, 10)],
            "Legs": [("Barbell Squats", 4, 8), ("Deadlifts", 3, 5), ("Walking Lunges", 3, 12), ("Glute Bridge", 3, 15), ("Calf Raises", 3, 20)],
            "Upper Body": [("Bench Press", 4, 10), ("Rows", 3, 12), ("Shoulder Press", 3, 10), ("Curls", 3, 12), ("Push-ups", 3, 15)],
            "Whole Body": [("Deadlifts", 4, 5), ("Barbell Squats", 4, 8), ("Clean & Press", 3, 8), ("Push-ups", 3, 15), ("Plank", 3, 60)],
        },
        "Full Commercial Gym": {
            "Push": [("Bench Press", 4, 8), ("Incline DB Press", 3, 10), ("Shoulder Press", 3, 10), ("Triceps Pushdown", 3, 12), ("Lateral Raise", 3, 15)],
            "Pull": [("Lat Pulldown", 4, 10), ("Seated Row", 3, 10), ("Barbell Curl", 3, 12), ("Face Pull", 3, 15), ("Hammer Curl", 3, 12)],
            "Legs": [("Barbell Squat", 4, 8), ("Leg Press", 3, 10), ("Leg Curl", 3, 12), ("Lunges", 3, 12), ("Standing Calf Raise", 3, 20)],
            "Upper Body": [("DB Press", 3, 12), ("Lat Pulldown", 3, 10), ("Incline DB Press", 3, 10), ("Barbell Curl", 3, 12), ("Push-ups", 3, 15)],
            "Whole Body": [("Deadlifts", 3, 5), ("Clean and Press", 3, 8), ("Squats", 3, 10), ("Burpees", 3, 15), ("Plank", 3, 60)],
        }
    }

    plan = {}
    split = ["Push", "Pull", "Legs", "Whole Body", "Upper Body"]
    for day in split:
        exercises = workouts[equipment][day]
        rest = "60–90s between sets" if goal == "Muscle Gain" else "30–60s between sets"
        plan[f"{day} Day"] = (exercises, rest)

    # Cardio days
    if goal == "Fat Loss":
        cardio_days = 3
    elif goal == "Muscle Gain":
        cardio_days = 1
    else:
        cardio_days = 2

    for i in range(cardio_days):
        plan[f"Cardio Day {i+1}"] = ([("Moderate Jog or Cycling", 1, "20-30 min")], "Keep heart rate 60–75% max")

    return plan

# ------------------- Page Content ------------------- #
if page == "Main Page":
    st.title("Welcome to Your Online Personal Trainer")
    st.write("Use the sidebar to navigate through the features of your personal training dashboard.")

if page == "User Intake Form":
    st.header("User Intake Form")
    profile = load_json(USER_PROFILE_PATH)
    unit = st.radio("Preferred Units", ["Imperial (lbs, inches)", "Metric (kg, cm)"], index=0 if profile.get("unit") == "Imperial (lbs, inches)" else 1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"], index=profile.get("gender", "Male"))
    age = st.number_input("Age", 10, 100, value=profile.get("age", 25))
    weight = st.number_input("Weight", 0.0, 300.0, value=profile.get("weight", 150.0))
    height = st.number_input("Height", 0.0, 250.0, value=profile.get("height", 170.0))
    goal = st.selectbox("Primary Goal", ["Fat Loss", "Muscle Gain", "General Fitness"], index=["Fat Loss", "Muscle Gain", "General Fitness"].index(profile.get("goal", "Fat Loss")))
    equipment = st.selectbox("Available Equipment", [
        "None - Bodyweight Only", "Home - Dumbbells and Bands",
        "Home - Barbell, Bench, Squat Rack", "Full Commercial Gym"
    ], index=["None - Bodyweight Only", "Home - Dumbbells and Bands", "Home - Barbell, Bench, Squat Rack", "Full Commercial Gym"].index(profile.get("equipment", "None - Bodyweight Only")))
    if st.button("Save Profile"):
        new_profile = {
            "unit": unit, "gender": gender, "age": age,
            "weight": weight, "height": height,
            "goal": goal, "equipment": equipment
        }
        save_json(new_profile, USER_PROFILE_PATH)
        st.success("Profile saved!")

if page == "Workout Suggestions":
    st.header("Weekly Workout Plan")
    profile = load_json(USER_PROFILE_PATH)
    if profile:
        plan = generate_weekly_workout(profile["goal"], profile["equipment"])
        for day, (exs, rest) in plan.items():
            with st.expander(day):
                for name, sets, reps in exs:
                    st.write(f"**{name}** - {sets} sets x {reps} reps")
                st.caption(f"_Rest: {rest}_")
    else:
        st.warning("Please fill in the intake form first.")

if page == "Log Workout":
    st.header("Log Your Workout")
    date = st.date_input("Workout Date", value=datetime.date.today())
    day = st.selectbox("Workout Split", ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body", "Cardio"])
    exercises = []
    for i in range(1, 6):
        ex = st.text_input(f"Exercise {i} Name", key=f"ex{i}")
        sets = st.number_input(f"Sets for {ex}", 1, 10, value=3, key=f"sets{i}")
        reps = st.number_input(f"Reps per set for {ex}", 1, 30, value=10, key=f"reps{i}")
        weight = st.number_input(f"Weight used (if any) for {ex}", 0.0, 1000.0, value=0.0, key=f"wt{i}")
        if ex:
            exercises.append({"name": ex, "sets": sets, "reps": reps, "weight": weight})
    if st.button("Log Workout"):
        log_workout(date, day, exercises)
        st.success("Workout logged!")

if page == "Macro Calculator":
    st.header("Macro Calculator")
    profile = load_json(USER_PROFILE_PATH)
    if profile:
        protein, carbs, fat, calories = calculate_macros(
            profile["weight"], profile["height"], profile["age"],
            profile["gender"], profile["goal"], profile["unit"]
        )
        st.metric("Calories", f"{calories} kcal")
        st.metric("Protein", f"{protein} g")
        st.metric("Carbohydrates", f"{carbs} g")
        st.metric("Fat", f"{fat} g")
    else:
        st.warning("Please complete your intake form first.")

if page == "Log Progress":
    st.header("Log Your Body Progress")
    date = st.date_input("Date", value=datetime.date.today(), key="prog_date")
    weight = st.number_input("Weight", 0.0, 600.0, step=0.1, key="prog_weight")
    waist = st.number_input("Waist Circumference", 0.0, 100.0, step=0.1, key="prog_waist")
    notes = st.text_area("Notes")
    if st.button("Log Progress"):
        log_progress(date, weight, waist, notes)
        st.success("Progress logged!")

if page == "Workout History":
    st.header("Workout History")
    logs = load_json(WORKOUT_LOG_PATH)
    if logs:
        st.dataframe(pd.DataFrame(logs))
    else:
        st.info("No workouts logged yet.")
