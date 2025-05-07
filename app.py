# Online Personal Trainer - Streamlit App (Single File)

import streamlit as st
import datetime
import json
import os
import pandas as pd

st.set_page_config(page_title="Online Personal Trainer", layout="wide")

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
WORKOUT_LOG_PATH = os.path.join("data", "workout_log.json")
PROGRESS_LOG_PATH = os.path.join("data", "progress_log.json")

# Sidebar Navigation
st.sidebar.title("Online Personal Trainer")
page = st.sidebar.radio("Navigation", [
    "Main Page",
    "User Intake Form",
    "Workout Suggestions",
    "Log Workout",
    "Macro Calculator",
    "Log Progress",
    "Workout History"
])

# Reset App Modal
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

# Utility Functions
def save_user_profile(profile):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profile, f)

def load_user_profile():
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

def log_workout(date, split, exercises):
    log = []
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            log = json.load(f)
    log.append({"date": str(date), "split": split, "exercises": exercises})
    with open(WORKOUT_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

def log_progress(date, weight, waist, notes):
    log = []
    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH, "r") as f:
            log = json.load(f)
    log.append({"date": str(date), "weight": weight, "waist": waist, "notes": notes})
    with open(PROGRESS_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
# ------------------- Intake Form ------------------- #
if page == "User Intake Form":
    st.header("User Intake Form")
    unit = st.radio("Preferred Units", ["Imperial (lbs, inches)", "Metric (kg, cm)"])
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"])
    age = st.number_input("Age", 10, 100, step=1)
    weight = st.number_input("Weight", 0.0)
    height = st.number_input("Height", 0.0)
    goal = st.selectbox("Primary Goal", ["Fat Loss", "Muscle Gain", "General Fitness"])
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
        save_user_profile(profile)
        st.success("Profile saved!")

# ------------------- Macro Calculator ------------------- #
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

    tdee = bmr * 1.5

    if goal == "Fat Loss":
        calories = tdee - 500
    elif goal == "Muscle Gain":
        calories = tdee + 250
    else:
        calories = tdee

    protein = int(weight_kg * 2.2)
    fat = int((0.25 * calories) / 9)
    carbs = int((calories - (protein * 4 + fat * 9)) / 4)

    return protein, carbs, fat, int(calories)

# ------------------- Workout Generator ------------------- #
def generate_weekly_workout(goal, equipment):
    base_plan = {
        "Push Day": [],
        "Pull Day": [],
        "Leg Day": [],
        "Whole Body": [],
        "Upper Body": []
    }

    exercise_library = {
        "None - Bodyweight Only": {
            "Push Day": [("Push-ups", 3, 12), ("Dips", 3, 10), ("Pike Push-ups", 3, 10)],
            "Pull Day": [("Superman Pulls", 3, 15), ("Inverted Rows (Table)", 3, 10)],
            "Leg Day": [("Bodyweight Squats", 4, 15), ("Lunges", 3, 12)],
            "Whole Body": [("Burpees", 3, 12), ("Mountain Climbers", 3, 20)],
            "Upper Body": [("Push-ups", 3, 12), ("Plank Ups", 3, 10)]
        },
        "Home - Dumbbells and Bands": {
            "Push Day": [("DB Bench Press", 3, 10), ("DB Shoulder Press", 3, 10)],
            "Pull Day": [("DB Rows", 3, 10), ("Resistance Band Pull-aparts", 3, 15)],
            "Leg Day": [("Goblet Squats", 4, 12), ("DB Lunges", 3, 10)],
            "Whole Body": [("Thrusters", 3, 10), ("DB Swings", 3, 12)],
            "Upper Body": [("DB Curls", 3, 12), ("Overhead Triceps", 3, 12)]
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Push Day": [("Barbell Bench Press", 4, 8), ("Overhead Press", 3, 10)],
            "Pull Day": [("Barbell Rows", 4, 8), ("Face Pulls (Bands)", 3, 12)],
            "Leg Day": [("Back Squat", 4, 8), ("RDLs", 3, 10)],
            "Whole Body": [("Power Cleans", 4, 5), ("Deadlifts", 3, 5)],
            "Upper Body": [("Incline Bench", 3, 10), ("Barbell Curls", 3, 12)]
        },
        "Full Commercial Gym": {
            "Push Day": [("Chest Press Machine", 3, 12), ("Shoulder Press Machine", 3, 12)],
            "Pull Day": [("Lat Pulldown", 3, 12), ("Seated Row", 3, 12)],
            "Leg Day": [("Leg Press", 4, 10), ("Hamstring Curl", 3, 12)],
            "Whole Body": [("Kettlebell Swings", 3, 15), ("Row Machine Sprints", 3, 30)],
            "Upper Body": [("Cable Fly", 3, 15), ("Preacher Curl", 3, 12)]
        }
    }

    rest_time = "Rest 60-90s between sets."

    for split in base_plan.keys():
        exercises = exercise_library.get(equipment, {}).get(split, [])
        base_plan[split] = (exercises, rest_time)

    # Add cardio based on goal
    cardio_day = ("Cardio", [("30 min steady-state cardio", 1, 1)], "Focus on endurance and fat burn.")
    weekly_plan = {}

    days = list(base_plan.items())
    for i, (day, content) in enumerate(days):
        weekly_plan[f"Day {i+1} - {day}"] = content

    if goal == "Fat Loss":
        for i in range(5, 8):
            weekly_plan[f"Day {i+1} - Cardio"] = ([("30 min brisk walk or jog", 1, 1)], "Keep heart rate elevated.")
    elif goal == "Muscle Gain":
        weekly_plan["Day 6 - Cardio"] = ([("20 min light cycling", 1, 1)], "Optional light recovery cardio.")
    else:  # General Fitness
        weekly_plan["Day 6 - Cardio"] = ([("25 min jog", 1, 1)], "Maintain aerobic base.")
        weekly_plan["Day 7 - Cardio"] = ([("Interval Training (HIIT)", 1, 1)], "Mix sprints and walks.")

    return weekly_plan
# ------------------- Workout Suggestions ------------------- #
if page == "Workout Suggestions":
    st.header("Weekly Workout Plan")
    profile = load_user_profile()
    if profile:
        plan = generate_weekly_workout(profile["goal"], profile["equipment"])
        for day, (exs, rest) in plan.items():
            with st.expander(day):
                for name, sets, reps in exs:
                    if sets == 1 and reps == 1:
                        st.write(f"**{name}**")
                    else:
                        st.write(f"**{name}** - {sets} sets x {reps} reps")
                st.caption(f"Rest guidance: {rest}")
    else:
        st.warning("Please fill out the intake form first.")

# ------------------- Log Workout ------------------- #
if page == "Log Workout":
    st.header("Log Today's Workout")
    date = st.date_input("Workout Date", value=datetime.date.today())
    day = st.selectbox("Workout Split", ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body", "Cardio"])
    exercises = []
    for i in range(1, 6):
        ex = st.text_input(f"Exercise {i} Name", key=f"ex{i}")
        sets = st.number_input(f"Sets for {ex or 'Exercise '+str(i)}", 1, 10, step=1, key=f"sets{i}")
        reps = st.number_input(f"Reps per set for {ex or 'Exercise '+str(i)}", 1, 30, step=1, key=f"reps{i}")
        weight = st.number_input(f"Weight used (if any) for {ex or 'Exercise '+str(i)}", 0.0, 1000.0, step=0.5, key=f"wt{i}")
        if ex:
            exercises.append({"name": ex, "sets": sets, "reps": reps, "weight": weight})
    if st.button("Log Workout"):
        log_workout(date, day, exercises)
        st.success("Workout logged successfully!")

# ------------------- Log Progress ------------------- #
if page == "Log Progress":
    st.header("Log Body Progress")
    date = st.date_input("Date", value=datetime.date.today(), key="prog_date")
    weight = st.number_input("Weight", 0.0, 600.0, step=0.1, key="prog_weight")
    waist = st.number_input("Waist Circumference (inches or cm)", 0.0, 100.0, step=0.1, key="prog_waist")
    notes = st.text_area("Notes")
    if st.button("Log Progress"):
        log_progress(date, weight, waist, notes)
        st.success("Progress logged!")

# ------------------- Macro Calculator ------------------- #
if page == "Macro Calculator":
    st.header("Your Daily Macro Targets")
    profile = load_user_profile()
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
        st.warning("Please complete the intake form to calculate macros.")

# ------------------- Workout History ------------------- #
if page == "Workout History":
    st.header("Workout History")
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            logs = json.load(f)
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df)
        else:
            st.info("No workouts logged yet.")
    else:
        st.info("Workout log not found.")

# ------------------- Main Page ------------------- #
if page == "Main Page":
    st.title("Welcome to Your Online Personal Trainer")
    st.write("📋 Start with the **User Intake Form** to get customized workout and macro plans.")
    st.write("💪 Log your workouts and track progress over time.")
    st.write("🔥 Adjust goals anytime and regenerate a new training plan.")

