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

if st.session_state.get("show_reset_modal"):
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

# ------------------- Weekly Workout Generator ------------------- #
def generate_weekly_workout(goal, equipment):
    split = ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body"]
    plans = {
        "Push Day": [
            ("Incline Bench Press", 4, 10),
            ("Overhead DB Press", 3, 12),
            ("Tricep Dips", 3, 10)
        ],
        "Pull Day": [
            ("Pull-ups or Lat Pulldown", 4, 8),
            ("Barbell or DB Row", 4, 10),
            ("Face Pulls or Band Pull Aparts", 3, 15)
        ],
        "Leg Day": [
            ("Squats (BB or Goblet)", 4, 10),
            ("Lunges or Step-ups", 3, 12),
            ("Hamstring Curls or RDL", 3, 10)
        ],
        "Whole Body": [
            ("Clean & Press or Thrusters", 3, 10),
            ("Burpees", 3, 15),
            ("Kettlebell Swings or Jump Squats", 3, 15)
        ],
        "Upper Body": [
            ("Bench Press or Push-ups", 4, 10),
            ("Barbell Row or DB Row", 4, 10),
            ("Overhead Press or Pike Push-ups", 3, 12)
        ]
    }
    weekly = {}
    for day in split:
        exercises = plans[day]
        if goal == "Fat Loss":
            rest = "30-60 sec rest. Add 20 min cardio."
        elif goal == "Muscle Gain":
            rest = "60-90 sec rest. Cardio optional."
        else:
            rest = "60 sec rest. Moderate effort cardio 2x/week."
        weekly[day] = (exercises, rest)
    return weekly

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
            "age": int(age),
            "weight": float(weight),
            "height": float(height),
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
        weekly_plan = generate_weekly_workout(profile["goal"], profile["equipment"])
        for day, (exercises, rest) in weekly_plan.items():
            with st.expander(day):
                for name, sets, reps in exercises:
                    st.write(f"- {name}: {sets} sets x {reps} reps")
                st.caption(f"Rest: {rest}")
    else:
        st.warning("Please complete the intake form first.")

# ------------------- Log Workout ------------------- #
if page == "Log Workout":
    st.title("Log Workout")
    date = st.date_input("Workout Date", datetime.date.today())
    exercise = st.text_input("Exercise Name")
    sets = st.number_input("Number of Sets", min_value=1, max_value=10)

    log = []
    for i in range(int(sets)):
        cols = st.columns(2)
        with cols[0]:
            reps = st.number_input(f"Reps for Set {i+1}", key=f"reps_{i}")
        with cols[1]:
            weight = st.number_input(f"Weight for Set {i+1} (lbs or kg)", key=f"weight_{i}")
        log.append({"set": i+1, "reps": reps, "weight": weight})

    if st.button("Save Workout Log"):
        new_entry = {
            "date": str(date),
            "exercise": exercise,
            "sets": log
        }
        if os.path.exists(WORKOUT_LOG_PATH):
            with open(WORKOUT_LOG_PATH) as f:
                existing = json.load(f)
        else:
            existing = []
        existing.append(new_entry)
        with open(WORKOUT_LOG_PATH, "w") as f:
            json.dump(existing, f)
        st.success("Workout logged!")

# ------------------- Macro Calculator ------------------- #
if page == "Macro Calculator":
    st.title("Macro Calculator")
    profile = st.session_state.get("profile")
    if not profile and os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH) as f:
            profile = json.load(f)

    if profile:
        protein, carbs, fat, cal = calculate_macros(
            profile["weight"], profile["height"], profile["age"], profile["gender"], profile["goal"], profile["unit"])
        st.markdown(f"**Calories:** {cal} kcal")
        st.markdown(f"**Protein:** {protein} g")
        st.markdown(f"**Carbohydrates:** {carbs} g")
        st.markdown(f"**Fats:** {fat} g")
    else:
        st.warning("Please complete the intake form first.")

# ------------------- Log Progress ------------------- #
if page == "Log Progress":
    st.title("Progress Tracker")
    date = st.date_input("Measurement Date", datetime.date.today())
    weight = st.number_input("Current Weight")
    waist = st.number_input("Waist Circumference")
    hips = st.number_input("Hip Circumference")

    if st.button("Save Progress"):
        entry = {"date": str(date), "weight": weight, "waist": waist, "hips": hips}
        if os.path.exists(PROGRESS_LOG_PATH):
            with open(PROGRESS_LOG_PATH) as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(entry)
        with open(PROGRESS_LOG_PATH, "w") as f:
            json.dump(logs, f)
        st.success("Progress saved!")

    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH) as f:
            logs = json.load(f)
        df = pd.DataFrame(logs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        st.line_chart(df.set_index('date')[['weight', 'waist', 'hips']])

    # Visualize weight lifted over time
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH) as f:
            workout_data = json.load(f)
        df = pd.json_normalize(workout_data, record_path=['sets'], meta=['date', 'exercise'])
        if not df.empty:
            selected_exercise = st.selectbox("View progress for exercise:", df['exercise'].unique())
            filtered = df[df['exercise'] == selected_exercise]
            filtered['date'] = pd.to_datetime(filtered['date'])
            grouped = filtered.groupby('date')['weight'].max()
            st.line_chart(grouped)
