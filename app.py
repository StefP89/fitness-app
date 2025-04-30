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

# ------------------- Log Progress ------------------- #
if page == "Log Progress":
    st.title("Log Your Progress")

    if os.path.exists(USER_PROFILE_PATH):
        with st.form("progress_form"):
            date = st.date_input("Date", value=datetime.date.today())
            weight = st.number_input("Current Weight", min_value=20.0, max_value=300.0, step=0.1)
            waist = st.number_input("Waist (optional, cm/in)", min_value=0.0, step=0.1)
            hips = st.number_input("Hips (optional, cm/in)", min_value=0.0, step=0.1)
            chest = st.number_input("Chest (optional, cm/in)", min_value=0.0, step=0.1)
            submit_progress = st.form_submit_button("Save Progress")

        if submit_progress:
            progress_entry = {
                "date": str(date),
                "weight": weight,
                "waist": waist,
                "hips": hips,
                "chest": chest
            }

            if os.path.exists(PROGRESS_LOG_PATH):
                with open(PROGRESS_LOG_PATH, "r") as f:
                    progress_log = json.load(f)
            else:
                progress_log = []

            progress_log.append(progress_entry)

            with open(PROGRESS_LOG_PATH, "w") as f:
                json.dump(progress_log, f)

            st.success("Progress saved successfully!")

        # ---------------- Show Progress Table and Chart ---------------- #
        if os.path.exists(PROGRESS_LOG_PATH):
            with open(PROGRESS_LOG_PATH, "r") as f:
                progress_log = json.load(f)

            if progress_log:
                df = pd.DataFrame(progress_log)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(by='date')
                st.subheader("Progress Log")
                st.dataframe(df)

                st.subheader("Weight Over Time")
                fig, ax = plt.subplots()
                ax.plot(df['date'], df['weight'], marker='o')
                ax.set_xlabel("Date")
                ax.set_ylabel("Weight")
                ax.grid(True)
                st.pyplot(fig)
            else:
                st.info("No progress entries found yet.")
    else:
        st.warning("Please complete the intake form first.")
