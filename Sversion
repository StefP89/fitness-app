# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import re
import io
import base64
import csv

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    "chicken breast": {"protein": 31, "carbs": 0, "fat": 3.5, "unit": "100g"},
    "brown rice": {"protein": 5, "carbs": 45, "fat": 1.5, "unit": "1 cup cooked"},
    "egg": {"protein": 6, "carbs": 1, "fat": 5, "unit": "1 large"},
    "broccoli": {"protein": 4, "carbs": 11, "fat": 0.5, "unit": "1 cup"},
    "almonds": {"protein": 6, "carbs": 6, "fat": 14, "unit": "28g"},
    "oats": {"protein": 5, "carbs": 27, "fat": 3, "unit": "1/2 cup"},
    "whey protein": {"protein": 25, "carbs": 3, "fat": 2, "unit": "1 scoop"},
    "olive oil": {"protein": 0, "carbs": 0, "fat": 14, "unit": "1 tbsp"},
    "peanut butter": {"protein": 8, "carbs": 6, "fat": 16, "unit": "2 tbsp"},
    "banana": {"protein": 1, "carbs": 27, "fat": 0.3, "unit": "1 medium"}
}

USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
USER_STATS_PATH = os.path.join("data", "user_stats.json")

# ------------------------- Helpers --------------------------- #

def load_json(path, default=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default or {}
    return default or {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------- Streamlit App --------------------------- #

st.title("🏋️ Personal Trainer & Nutrition Coach")

menu = ["Log Stats", "View Progress", "Set Macro Targets", "Download PDF"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Log Stats":
    st.header("📅 Log Today's Stats")
    date = st.date_input("Date", value=datetime.date.today())
    weight = st.text_input("Enter today's weight (kg)")
    note = st.text_area("Notes (optional)")

    if st.button("Log Entry"):
        cleaned_weight = re.sub(r"[^\d.-]", "", weight).strip()
        try:
            weight_val = float(cleaned_weight)
            new_entry = {"date": str(date), "weight": weight_val, "note": note}
            data = load_json(USER_STATS_PATH, [])
            data.append(new_entry)
            save_json(USER_STATS_PATH, data)
            st.success("Stats logged successfully!")

            # Export valid data to CSV
            valid_data = []
            for entry in data:
                try:
                    weight = float(entry["weight"])
                    entry["weight"] = weight
                    valid_data.append(entry)
                except (ValueError, TypeError):
                    st.warning(f"Skipping invalid entry: {entry}")

            csv_path = os.path.join("data", "user_stats.csv")
            with open(csv_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["date", "weight", "note"])
                writer.writeheader()
                writer.writerows(valid_data)

        except ValueError:
            st.error("Invalid weight input")

elif choice == "View Progress":
    st.header("📈 Weight Progress")
    data = load_json(USER_STATS_PATH, [])
    if not data:
        st.warning("No data to display")
    else:
        stats = [(datetime.datetime.fromisoformat(entry["date"]), entry["weight"]) for entry in data if "weight" in entry]
        dates, weights = zip(*stats)

        option = st.selectbox("Select time range", ["1 month", "3 months", "6 months", "1 year"])
        days = {"1 month": 30, "3 months": 90, "6 months": 180, "1 year": 365}[option]
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

        filtered = [(d, w) for d, w in stats if d >= cutoff]
        if not filtered:
            st.warning("No data in this time range")
        else:
            d, w = zip(*filtered)
            fig, ax = plt.subplots()
            ax.plot(d, w, marker='o')
            ax.set_title("Weight Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Weight (kg)")
            ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
            plt.xticks(rotation=45)
            st.pyplot(fig)

elif choice == "Set Macro Targets":
    st.header("🍽️ Macro Targets")
    profile = load_json(USER_PROFILE_PATH, {})
    p = st.number_input("% Protein", 0, 100, profile.get("protein", 30))
    c = st.number_input("% Carbs", 0, 100, profile.get("carbs", 40))
    f = st.number_input("% Fat", 0, 100, profile.get("fat", 30))

    if p + c + f != 100:
        st.error("The total must be 100%")
    else:
        if st.button("Save Targets"):
            profile.update({"protein": p, "carbs": c, "fat": f})
            save_json(USER_PROFILE_PATH, profile)
            st.success("Macro targets saved")

elif choice == "Download PDF":
    st.header("📄 Export PDF Report")
    stats = load_json(USER_STATS_PATH, [])
    if not stats:
        st.warning("No data to export")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Weight Progress Report", ln=True, align='C')
        for entry in stats:
            line = f"{entry['date']} - {entry['weight']}kg"
            if entry.get("note"):
                line += f" | Note: {entry['note']}"
            pdf.cell(200, 10, txt=line, ln=True)

        output_path = os.path.join("data", "weight_report.pdf")
        pdf.output(output_path)
        with open(output_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="weight_report.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
