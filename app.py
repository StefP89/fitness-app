# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os

# ------------------- Reset to Default Streamlit Theme ------------------- #
st.set_page_config(page_title="Fitness Macro Tracker", layout="wide")

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# ------------------------- Safe Session Reset --------------------------- #
if st.sidebar.button("Reset App"):
    st.session_state.clear()
    st.session_state["reset_triggered"] = True

if st.session_state.get("reset_triggered"):
    st.session_state.pop("reset_triggered")
    st.rerun()

# ------------------------- Sidebar Navigation --------------------------- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "User Intake Form",
    "Workout Suggestions",
    "Log Workout",
    "Macro Calculator",
    "Log Progress"
])

# ------------------------- File Paths --------------------------- #
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
WORKOUT_LOG_PATH = os.path.join("data", "workout_log.json")
PROGRESS_LOG_PATH = os.path.join("data", "progress_log.json")

# ------------------------- Macro Calculation Function --------------------------- #
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

# ------------------------- User Intake Form --------------------------- #
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

# ------------------------- Workout Suggestions --------------------------- #
if page == "Workout Suggestions":
    st.title("Workout Suggestions")

    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            profile = json.load(f)

        goal = profile.get("goal")
        equipment = profile.get("equipment")

        st.subheader(f"Workout Plan for Goal: {goal} with Equipment: {equipment}")

        def get_workout(goal, equipment):
            workouts = {
                "Fat Loss": {
                    "None - Bodyweight Only": [
                        ("Full Body Circuit", ["Push-ups", "Bodyweight Squats", "Lunges", "Plank"]),
                        ("Cardio", ["Jog in Place", "Jumping Jacks"])
                    ],
                    "Home - Dumbbells and Bands": [
                        ("Upper Body", ["DB Shoulder Press", "DB Rows", "Band Pull-aparts"]),
                        ("Lower Body + Cardio", ["DB Goblet Squats", "DB Deadlifts", "Jump Rope"])
                    ],
                    "Home - Barbell, Bench, Squat Rack": [
                        ("Strength + Cardio", ["Barbell Squats", "Bench Press", "Barbell Rows", "Rowing Machine"])
                    ],
                    "Full Commercial Gym": [
                        ("Full Split", ["Leg Press", "Lat Pulldown", "Incline Bench Press", "HIIT Treadmill"])
                    ]
                },
                "Muscle Gain": {
                    "None - Bodyweight Only": [
                        ("Bodyweight Strength", ["Elevated Push-ups", "Wall Sits", "Single Leg Glute Bridges"]),
                        ("Optional Cardio", ["Fast Walk"])
                    ],
                    "Home - Dumbbells and Bands": [
                        ("Push Day", ["DB Bench Press", "Overhead Press", "Tricep Kickbacks"]),
                        ("Pull Day", ["DB Rows", "Band Face Pulls", "Hammer Curls"])
                    ],
                    "Home - Barbell, Bench, Squat Rack": [
                        ("Strength Split", ["Barbell Squat", "Barbell Bench Press", "Barbell Deadlift"])
                    ],
                    "Full Commercial Gym": [
                        ("Push/Pull/Legs", ["Incline DB Press", "Cable Rows", "Leg Curl Machine"])
                    ]
                },
                "Maintenance": {
                    "None - Bodyweight Only": [
                        ("Balanced Bodyweight", ["Push-ups", "Squats", "Plank"])
                    ],
                    "Home - Dumbbells and Bands": [
                        ("Light Full Body", ["DB Curls", "DB Squats", "Band Pull-aparts"])
                    ],
                    "Home - Barbell, Bench, Squat Rack": [
                        ("Strength Maintenance", ["Barbell Press", "Barbell Squat"])
                    ],
                    "Full Commercial Gym": [
                        ("Circuit", ["Row", "Chest Press", "Lat Pulldown", "Leg Press"])
                    ]
                }
            }
            return workouts.get(goal, {}).get(equipment, [])

        plan = get_workout(goal, equipment)

        if plan:
            for workout_day in plan:
                if isinstance(workout_day, tuple) and len(workout_day) == 2:
                    day, routine = workout_day
                    st.markdown(f"### {day}")
                    for move in routine:
                        st.write(f"- {move}")
                else:
                    st.warning("Unexpected workout format.")
        else:
            st.warning("No workout plan found for your selected goal and equipment.")

    else:
        st.warning("Please fill out the intake form first.")
