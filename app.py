import streamlit as st
import os
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# File paths
USER_PROFILE_PATH = "user_profile.json"
WORKOUT_LOG_PATH = "workout_log.json"
PROGRESS_LOG_PATH = "progress_log.json"

# Load user profile
def load_user_profile():
    if os.path.exists(USER_PROFILE_PATH):
        with open(USER_PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

# Save user profile
def save_user_profile(profile):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

# Calculate macros
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

    tdee = bmr * 1.55  # Moderate activity

    if goal == "Fat Loss":
        calories = tdee - 500
    elif goal == "Muscle Gain":
        calories = tdee + 250
    else:
        calories = tdee

    protein = weight_kg * 2.2
    fat = calories * 0.25 / 9
    carbs = (calories - (protein * 4 + fat * 9)) / 4
    return round(protein), round(carbs), round(fat), round(calories)

# Generate weekly workout plan with detailed equipment-based options
def generate_weekly_workout(goal, equipment):
    # Equipment-based options
    options = {
        "None - Bodyweight Only": {
            "Push Day": [("Push-ups", 4, 12), ("Dips", 3, 10), ("Pike Push-ups", 3, 8), ("Wall Push-ups", 3, 15), ("Incline Push-ups", 3, 10)],
            "Pull Day": [("Superman Holds", 4, 20), ("Door Rows", 3, 12), ("Towel Curls", 3, 15), ("Face Pulls (band)", 3, 15)],
            "Leg Day": [("Air Squats", 4, 20), ("Wall Sits", 3, 30), ("Lunges", 3, 12), ("Step-Ups", 3, 12), ("Glute Bridges", 3, 15)],
            "Whole Body": [("Burpees", 3, 15), ("Mountain Climbers", 3, 20), ("Push-ups", 3, 12), ("Squats", 3, 15)],
            "Upper Body": [("Push-ups", 3, 12), ("Plank", 3, 30), ("Arm Circles", 3, 20)]
        },
        "Home - Dumbbells and Bands": {
            "Push Day": [("DB Chest Press", 4, 10), ("Overhead Press", 3, 8), ("Front Raise", 3, 12), ("Tricep Kickbacks", 3, 15), ("Push-ups", 3, 15)],
            "Pull Day": [("DB Rows", 4, 10), ("Band Pull-aparts", 3, 15), ("DB Curls", 3, 12), ("Reverse Flys", 3, 12)],
            "Leg Day": [("DB Goblet Squat", 4, 12), ("DB Lunges", 3, 12), ("Calf Raises", 3, 20), ("Glute Bridges", 3, 15), ("Step-ups", 3, 12)],
            "Whole Body": [("DB Snatch", 3, 8), ("Thrusters", 3, 10), ("Burpees", 3, 12), ("Squat Jumps", 3, 10)],
            "Upper Body": [("DB Chest Press", 3, 10), ("DB Curls", 3, 12), ("Band Pulls", 3, 15)]
        },
        "Home - Barbell, Bench, Squat Rack": {
            "Push Day": [("Barbell Bench Press", 4, 8), ("Overhead Press", 3, 8), ("Close-grip Bench", 3, 10), ("Incline Press", 3, 10), ("Dips", 3, 12)],
            "Pull Day": [("Barbell Rows", 4, 10), ("Barbell Curls", 3, 12), ("Face Pulls", 3, 15), ("Deadlifts", 3, 5)],
            "Leg Day": [("Back Squat", 4, 8), ("Front Squat", 3, 8), ("RDLs", 3, 10), ("Calf Raises", 3, 20), ("Step-ups", 3, 12)],
            "Whole Body": [("Power Clean", 3, 6), ("Thrusters", 3, 8), ("Burpees", 3, 15), ("Deadlifts", 3, 5)],
            "Upper Body": [("Overhead Press", 3, 8), ("Barbell Curls", 3, 10), ("Incline Press", 3, 10)]
        },
        "Full Commercial Gym": {
            "Push Day": [("Bench Press", 4, 8), ("Incline Press", 3, 10), ("Cable Flys", 3, 15), ("Shoulder Press", 3, 10), ("Tricep Pushdown", 3, 12)],
            "Pull Day": [("Lat Pulldown", 4, 10), ("Seated Row", 3, 12), ("Face Pulls", 3, 15), ("Cable Curls", 3, 12)],
            "Leg Day": [("Leg Press", 4, 12), ("Hack Squat", 3, 10), ("Walking Lunges", 3, 20), ("Leg Curl", 3, 15), ("Standing Calf Raise", 3, 20)],
            "Whole Body": [("Deadlift", 3, 5), ("Push Press", 3, 8), ("Clean to Press", 3, 6), ("Box Jumps", 3, 12)],
            "Upper Body": [("Pullups", 3, 8), ("Overhead Press", 3, 10), ("Incline Dumbbell Press", 3, 12)]
        }
    }

    plan = {}
    splits = ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body"]
    for split in splits:
        plan[split] = (options[equipment][split], "60–90 sec rest between sets")

    # Cardio days based on goal
    if goal == "Fat Loss":
        cardio_days = ["Cardio Day 1", "Cardio Day 2", "Cardio Day 3"]
    elif goal == "Muscle Gain":
        cardio_days = ["Cardio Day 1"]
    else:
        cardio_days = ["Cardio Day 1", "Cardio Day 2"]

    for i, name in enumerate(cardio_days, 1):
        plan[name] = ([("20–30 min Moderate-Intensity Cardio", 1, 1)], "As needed")

    return plan

# Log workout
def log_workout(date, day, exercises):
    logs = []
    if os.path.exists(WORKOUT_LOG_PATH):
        with open(WORKOUT_LOG_PATH, "r") as f:
            logs = json.load(f)
    logs.append({
        "date": str(date),
        "split": day,
        "exercises": exercises
    })
    with open(WORKOUT_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

# Log progress
def log_progress(date, weight, waist, notes):
    logs = []
    if os.path.exists(PROGRESS_LOG_PATH):
        with open(PROGRESS_LOG_PATH, "r") as f:
            logs = json.load(f)
    logs.append({
        "date": str(date),
        "weight": weight,
        "waist": waist,
        "notes": notes
    })
    with open(PROGRESS_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

# Main app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "Main Page",
        "User Intake Form",
        "Macro Calculator",
        "Workout Suggestions",
        "Log Workout",
        "Log Progress",
        "Workout History"
    ])

    # Main Page
    if page == "Main Page":
        st.title("🏋️ Online Personal Trainer")
        st.markdown("""
            Welcome to your personal fitness dashboard!  
            Use the sidebar to navigate between tools:
            - Fill out your **User Intake Form**
            - Generate a **Workout Plan**
            - Use the **Macro Calculator**
            - Log your **Workouts** and **Progress**
            - Review your **Workout History**

            👉 Start by completing the Intake Form so your plan and macros can be personalized!
        """)
        st.image(
            "https://raw.githubusercontent.com/StefP89/fitness-app/main/mascot.png",
            caption="**HYDRA FLEXCAVATOR**",
            use_container_width=True
        )

    # User Intake Form
    elif page == "User Intake Form":
        st.header("User Intake Form")
        if "user_profile" not in st.session_state:
            st.session_state.user_profile = load_user_profile()

        unit = st.radio("Preferred Units", ["Imperial (lbs, inches)", "Metric (kg, cm)"], index=0 if st.session_state.user_profile.get("unit") == "Imperial (lbs, inches)" else 1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to disclose"], index=["Male", "Female", "Other", "Prefer not to disclose"].index(st.session_state.user_profile.get("gender", "Male")))
        age = st.number_input("Age", 10, 100, step=1, value=st.session_state.user_profile.get("age", 25))
        weight = st.number_input("Weight", 0.0, value=st.session_state.user_profile.get("weight", 150.0))
        height = st.number_input("Height", 0.0, value=st.session_state.user_profile.get("height", 170.0))
        goal = st.selectbox("Primary Goal", ["Fat Loss", "Muscle Gain", "General Fitness"], index=["Fat Loss", "Muscle Gain", "General Fitness"].index(st.session_state.user_profile.get("goal", "Fat Loss")))
        equipment = st.selectbox("Available Equipment", [
            "None - Bodyweight Only",
            "Home - Dumbbells and Bands",
            "Home - Barbell, Bench, Squat Rack",
            "Full Commercial Gym"
        ], index=["None - Bodyweight Only", "Home - Dumbbells and Bands", "Home - Barbell, Bench, Squat Rack", "Full Commercial Gym"].index(st.session_state.user_profile.get("equipment", "None - Bodyweight Only")))

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

    # Macro Calculator
    elif page == "Macro Calculator":
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

    # Workout Suggestions
    elif page == "Workout Suggestions":
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

    # Log Workout
    elif page == "Log Workout":
        st.header("Log Today's Workout")
        date = st.date_input("Workout Date", value=datetime.date.today())
        day = st.selectbox("Workout Split", ["Push Day", "Pull Day", "Leg Day", "Whole Body", "Upper Body", "Cardio"])
        exercises = []
        for i in range(1, 7):
            ex = st.text_input(f"Exercise {i} Name", key=f"ex{i}")
            sets = st.number_input(f"Sets for {ex or f'Exercise {i}'}", 1, 10, step=1, key=f"sets{i}")
            reps = st.number_input(f"Reps per set for {ex or f'Exercise {i}'}", 1, 50, step=1, key=f"reps{i}")
            weight = st.number_input(f"Weight used (if any) for {ex or f'Exercise {i}'}", 0.0, step=0.5, key=f"weight{i}")
            if ex:
                exercises.append({"name": ex, "sets": sets, "reps": reps, "weight": weight})
        if st.button("Log Workout"):
            if exercises:
                log_workout(date, day, exercises)
                st.success("Workout logged!")
            else:
                st.error("Add at least one exercise.")

    # Log Progress
    elif page == "Log Progress":
        st.header("Log Body Measurements & Notes")
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Current Weight", 0.0, value=0.0)
        waist = st.number_input("Waist Measurement", 0.0, value=0.0)
        notes = st.text_area("Notes / Comments")
        if st.button("Log Progress"):
            log_progress(date, weight, waist, notes)
            st.success("Progress logged!")

    # Workout History
    elif page == "Workout History":
        st.header("Workout and Progress History")

        if os.path.exists(WORKOUT_LOG_PATH):
            with open(WORKOUT_LOG_PATH, "r") as f:
                logs = json.load(f)
            st.subheader("Workout Logs")
            df = pd.DataFrame(logs)
            if not df.empty:
                st.dataframe(df)
            else:
                st.write("No workouts logged yet.")
        else:
            st.write("No workouts logged yet.")

        if os.path.exists(PROGRESS_LOG_PATH):
            with open(PROGRESS_LOG_PATH, "r") as f:
                logs = json.load(f)
            st.subheader("Progress Logs")
            df = pd.DataFrame(logs)
            if not df.empty:
                st.dataframe(df)
                # Plot weight over time
                df['date'] = pd.to_datetime(df['date'])
                fig, ax = plt.subplots()
                ax.plot(df['date'], df['weight'], marker='o', label='Weight')
                ax.plot(df['date'], df['waist'], marker='o', label='Waist')
                ax.set_xlabel("Date")
                ax.set_ylabel("Measurement")
                ax.legend()
                st.pyplot(fig)
            else:
                st.write("No progress logged yet.")
        else:
            st.write("No progress logged yet.")

if __name__ == "__main__":
    main()
