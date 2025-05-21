import streamlit as st
import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Online Personal Trainer", layout="wide")

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

USER_PROFILE_PATH = "data/user_profile.json"
WORKOUT_LOG_PATH = "data/workout_log.json"
PROGRESS_LOG_PATH = "data/progress_log.json"

# ---------- Load & Save Helpers ----------
def save_user_profile(profile):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

def load_user_profile():
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

def log_workout(date, day, exercises):
    entry = {"date": str(date), "day": day, "exercises": exercises}
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(WORKOUT_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def log_progress(date, weight, waist, notes):
    entry = {"date": str(date), "weight": weight, "waist": waist, "notes": notes}
    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(PROGRESS_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

# ---------- Macro Calculator ----------
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

    tdee = bmr * 1.55  # moderate activity

    if goal == "Fat Loss":
        tdee -= 500
    elif goal == "Muscle Gain":
        tdee += 250

    protein = weight_kg * 2.2
    fat = weight_kg * 0.9
    carbs = (tdee - (protein * 4 + fat * 9)) / 4

    return round(protein), round(carbs), round(fat), round(tdee)

# ---------- Workout Generator ----------
def generate_weekly_workout(goal, equipment):
    options = {
        "None - Bodyweight Only": {
            "Push Day": [("Push-ups", 4, 12), ("Dips", 3, 10)],
            "Pull Day": [("Door Rows", 3, 12), ("Towel Curls", 3, 15)],
            "Leg Day": [("Air Squats", 4, 20), ("Lunges", 3, 12)],
            "Whole Body": [("Burpees", 3, 15), ("Mountain Climbers", 3, 20)],
            "Upper Body": [("Push-ups", 3, 12), ("Plank", 3, 30)],
        },
        "Home - Dumbbells and Bands": {
            "Push Day": [("DB Chest Press", 4, 10), ("Overhead Press", 3, 8)],
            "Pull Day": [("DB Rows", 4, 10), ("Band Pull-aparts", 3, 15)],
            "Leg Day": [("DB Goblet Squat", 4, 12), ("DB Lunges", 3, 12)],
            "Whole Body": [("DB Snatch", 3, 8), ("Thrusters", 3, 10)],
            "Upper Body": [("DB Chest Press", 3, 10), ("DB Curls", 3, 12)],
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Push Day": [("Barbell Bench Press", 4, 8), ("Overhead Press", 3, 8)],
            "Pull Day": [("Barbell Rows", 4, 10), ("Barbell Curls", 3, 12)],
            "Leg Day": [("Back Squat", 4, 8), ("RDLs", 3, 10)],
            "Whole Body": [("Power Clean", 3, 6), ("Deadlifts", 3, 5)],
            "Upper Body": [("Overhead Press", 3, 8), ("Barbell Curls", 3, 10)],
        },
        "Full Commercial Gym": {
            "Push Day": [("Bench Press", 4, 8), ("Incline Press", 3, 10)],
            "Pull Day": [("Lat Pulldown", 4, 10), ("Seated Row", 3, 12)],
            "Leg Day": [("Leg Press", 4, 12), ("Hack Squat", 3, 10)],
            "Whole Body": [("Deadlift", 3, 5), ("Push Press", 3, 8)],
            "Upper Body": [("Pullups", 3, 8), ("Overhead Press", 3, 10)],
        }
    }

    plan = {}
    splits = ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body"]
    for split in splits:
        plan[split] = (options[equipment][split], "60–90 sec rest between sets")

    if goal == "Fat Loss":
        cardio_days = ["Cardio Day 1", "Cardio Day 2", "Cardio Day 3"]
    elif goal == "Muscle Gain":
        cardio_days = ["Cardio Day 1"]
    else:
        cardio_days = ["Cardio Day 1", "Cardio Day 2"]

    for i, name in enumerate(cardio_days, 1):
        plan[name] = ([("20–30 min Moderate-Intensity Cardio", 1, 1)], "As needed")

    return plan

# ---------- Sidebar ----------
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

# ---------- Clear History Feature ----------
with st.sidebar.expander("⚠️ Danger Zone"):
    if st.button("Clear All Data"):
        for path in [USER_PROFILE_PATH, WORKOUT_LOG_PATH, PROGRESS_LOG_PATH]:
            if os.path.exists(path):
                os.remove(path)
        st.session_state.clear()
        st.success("All data cleared. Please refresh the app.")

# ---------- Main Page ----------
if page == "Main Page":
    st.title("🏋️ Online Personal Trainer")

    image_path = "data/ChatGPT Image May 21, 2025, 10_22_25 AM.png"
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.warning("Welcome image not found. Please ensure it's in the 'data' folder.")

    st.markdown("""
        ### Welcome to your personal fitness dashboard!  
        Use the sidebar to navigate between tools:
        - 📝 Fill out your **User Intake Form**
        - 🏋️ Generate a **Workout Plan**
        - 🍽️ Use the **Macro Calculator**
        - 📓 Log your **Workouts** and **Progress**
        - 📈 Review your **Workout History**

        👉 Start by completing the Intake Form so your plan and macros can be personalized!
    """)

# ---------- Intake Form ----------
if page == "User Intake Form":
    st.header("User Intake Form")
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = load_user_profile()

    profile = st.session_state.user_profile

    unit = st.radio("Preferred Units", ["Imperial (lbs, inches)", "Metric (kg, cm)"],
                    index=0 if profile.get("unit", "Imperial (lbs, inches)") == "Imperial (lbs, inches)" else 1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"],
                          index=["Male", "Female", "Other", "Prefer not to disclose"].index(profile.get("gender", "Male")))
    age = st.number_input("Age", 10, 100, step=1, value=profile.get("age", 25))
    weight = st.number_input("Weight", 0.0, value=profile.get("weight", 150.0))
    height = st.number_input("Height", 0.0, value=profile.get("height", 170.0))
    goal = st.selectbox("Primary Goal", ["Fat Loss", "Muscle Gain", "General Fitness"],
                        index=["Fat Loss", "Muscle Gain", "General Fitness"].index(profile.get("goal", "Fat Loss")))
    equipment = st.selectbox("Available Equipment", list(generate_weekly_workout("Fat Loss", "None - Bodyweight Only").keys())[0:5],
                             index=0)

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
        st.session_state.user_profile = profile
        save_user_profile(profile)
        st.success("Profile saved!")

# ---------- Macro Calculator ----------
if page == "Macro Calculator":
    st.header("Your Daily Macro Targets")
    profile = st.session_state.get("user_profile", load_user_profile())
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

# ---------- Workout Suggestions ----------
if page == "Workout Suggestions":
    st.header("Weekly Workout Plan")
    profile = st.session_state.get("user_profile", load_user_profile())
    if profile:
        plan = generate_weekly_workout(profile["goal"], profile["equipment"])
        for day, (exs, rest) in plan.items():
            with st.expander(day):
                for name, sets, reps in exs:
                    st.write(f"**{name}** - {sets} sets x {reps} reps")
                st.caption(f"_Rest: {rest}_")
    else:
        st.warning("Please fill out the intake form first.")

# ---------- Log Workout ----------
if page == "Log Workout":
    st.header("Log Today's Workout")
    date = st.date_input("Workout Date", value=datetime.date.today())
    day = st.selectbox("Workout Split", ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body", "Cardio"])
    exercises = []
    for i in range(1, 7):
        ex = st.text_input(f"Exercise {i} Name", key=f"ex{i}")
        sets = st.number_input(f"Sets for {ex or f'Exercise {i}'}", 1, 10, step=1, key=f"sets{i}")
        reps = st.number_input(f"Reps for {ex or f'Exercise {i}'}", 1, 50, step=1, key=f"reps{i}")
        weight = st.number_input(f"Weight used for {ex or f'Exercise {i}'}", 0.0, 1000.0, step=0.5, key=f"wt{i}")
        if ex:
            exercises.append({"name": ex, "sets": sets, "reps": reps, "weight": weight})
    if st.button("Log Workout"):
        log_workout(date, day, exercises)
        st.success("Workout logged successfully!")

# ---------- Log Progress ----------
if page == "Log Progress":
    st.header("Log Body Progress")
    date = st.date_input("Date", value=datetime.date.today(), key="prog_date")
    weight = st.number_input("Weight", 0.0, 600.0, step=0.1, key="prog_weight")
    waist = st.number_input("Waist Circumference", 0.0, 100.0, step=0.1, key="prog_waist")
    notes = st.text_area("Notes")
    if st.button("Log Progress"):
        log_progress(date, weight, waist, notes)
        st.success("Progress logged!")

    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH, "r") as f:
            logs = json.load(f)
        if logs:
            df = pd.DataFrame(logs)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            st.subheader("Progress Over Time")
            fig, ax = plt.subplots()
            ax.plot(df["date"], df["weight"], marker="o", label="Weight")
            ax.plot(df["date"], df["waist"], marker="s", label="Waist")
            ax.set_ylabel("Measurement")
            ax.set_xlabel("Date")
            ax.legend()
            st.pyplot(fig)

# ---------- Workout History ----------
if page == "Workout History":
    st.header("Workout History")
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            logs = json.load(f)
        if logs:
            for entry in logs[::-1]:
                with st.expander(f"{entry['date']} - {entry['day']}"):
                    for ex in entry["exercises"]:
                        st.markdown(f"- **{ex['name']}**: {ex['sets']} sets x {ex['reps']} reps @ {ex['weight']} lbs/kg")
        else:
            st.info("No workouts logged yet.")
    else:
        st.info("Workout log not found.")
