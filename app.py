# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import base64

# ------------------- Reset to Default Streamlit Theme ------------------- #
st.set_page_config(page_title="Fitness Macro Tracker", layout="wide")

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# ------------------------- Safe Session Reset --------------------------- #
if "rerun_triggered" not in st.session_state:
    st.session_state["rerun_triggered"] = False

if st.sidebar.button("Reset App") and not st.session_state["rerun_triggered"]:
    st.session_state.clear()
    st.session_state["rerun_triggered"] = True
    st.experimental_rerun()

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    "Proteins": {
        "chicken breast": {"protein": 31, "carbs": 0, "fat": 3.5, "unit": "100g"},
        "egg": {"protein": 6, "carbs": 1, "fat": 5, "unit": "1 large"},
        "whey protein": {"protein": 25, "carbs": 3, "fat": 2, "unit": "1 scoop"},
        "ground beef": {"protein": 26, "carbs": 0, "fat": 20, "unit": "100g"},
        "turkey breast": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
        "pork loin": {"protein": 24, "carbs": 0, "fat": 7, "unit": "100g"},
        "lamb chop": {"protein": 25, "carbs": 0, "fat": 21, "unit": "100g"},
        "duck breast": {"protein": 27, "carbs": 0, "fat": 12, "unit": "100g"},
        "ham": {"protein": 18, "carbs": 1, "fat": 6, "unit": "100g"},
        "salami": {"protein": 22, "carbs": 1, "fat": 17, "unit": "100g"}
    },
    "Fish": {
        "salmon": {"protein": 25, "carbs": 0, "fat": 13, "unit": "100g"},
        "tuna": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
        "cod": {"protein": 20, "carbs": 0, "fat": 1, "unit": "100g"},
        "tilapia": {"protein": 26, "carbs": 0, "fat": 3, "unit": "100g"},
        "sardines": {"protein": 25, "carbs": 0, "fat": 11, "unit": "100g"}
    },
    "Carbs": {
        "brown rice": {"protein": 5, "carbs": 45, "fat": 1.5, "unit": "1 cup cooked"},
        "white rice": {"protein": 4, "carbs": 45, "fat": 0.4, "unit": "1 cup cooked"},
        "oats": {"protein": 5, "carbs": 27, "fat": 3, "unit": "1/2 cup"},
        "quinoa": {"protein": 8, "carbs": 39, "fat": 3.6, "unit": "1 cup cooked"},
        "whole wheat bread": {"protein": 5, "carbs": 20, "fat": 1.2, "unit": "1 slice"},
        "white bread": {"protein": 3, "carbs": 14, "fat": 1, "unit": "1 slice"},
        "pasta": {"protein": 8, "carbs": 43, "fat": 1.3, "unit": "1 cup cooked"},
        "couscous": {"protein": 6, "carbs": 36, "fat": 0.6, "unit": "1 cup cooked"},
        "barley": {"protein": 3.5, "carbs": 44, "fat": 0.5, "unit": "1 cup cooked"},
        "corn": {"protein": 3, "carbs": 27, "fat": 1, "unit": "1 cup"}
    },
    "Dairy": {
        "milk (whole)": {"protein": 8, "carbs": 12, "fat": 8, "unit": "1 cup"},
        "milk (2%)": {"protein": 8, "carbs": 12, "fat": 5, "unit": "1 cup"},
        "milk (skim)": {"protein": 8, "carbs": 12, "fat": 0, "unit": "1 cup"},
        "cheddar cheese": {"protein": 7, "carbs": 1, "fat": 9, "unit": "1 slice"},
        "cottage cheese": {"protein": 13, "carbs": 4, "fat": 2, "unit": "1/2 cup"},
        "greek yogurt": {"protein": 20, "carbs": 7, "fat": 0, "unit": "1 cup"},
        "mozzarella": {"protein": 6, "carbs": 1, "fat": 5, "unit": "1 oz"},
        "parmesan": {"protein": 10, "carbs": 1, "fat": 7, "unit": "1 oz"},
        "ricotta": {"protein": 7, "carbs": 3, "fat": 6, "unit": "1/4 cup"},
        "butter": {"protein": 0, "carbs": 0, "fat": 11, "unit": "1 tbsp"}
    },
    "Fruits": {
        "banana": {"protein": 1.3, "carbs": 27, "fat": 0.3, "unit": "1 medium"},
        "apple": {"protein": 0.5, "carbs": 25, "fat": 0.3, "unit": "1 medium"},
        "orange": {"protein": 1.2, "carbs": 15.4, "fat": 0.2, "unit": "1 medium"},
        "strawberry": {"protein": 1, "carbs": 12, "fat": 0.3, "unit": "1 cup"},
        "blueberry": {"protein": 1, "carbs": 21, "fat": 0.5, "unit": "1 cup"},
        "grapes": {"protein": 0.6, "carbs": 27, "fat": 0.3, "unit": "1 cup"},
        "kiwi": {"protein": 2, "carbs": 15, "fat": 0.9, "unit": "1 medium"},
        "pineapple": {"protein": 1, "carbs": 22, "fat": 0.2, "unit": "1 cup"},
        "mango": {"protein": 1, "carbs": 25, "fat": 0.6, "unit": "1 cup"},
        "peach": {"protein": 1, "carbs": 15, "fat": 0.4, "unit": "1 medium"}
    },
    "Vegetables": {
        "broccoli": {"protein": 2.5, "carbs": 6, "fat": 0.3, "unit": "1 cup chopped"},
        "spinach": {"protein": 3, "carbs": 4, "fat": 0.4, "unit": "1 cup cooked"},
        "carrot": {"protein": 1, "carbs": 12, "fat": 0.3, "unit": "1 cup sliced"},
        "cauliflower": {"protein": 2, "carbs": 5, "fat": 0.1, "unit": "1 cup chopped"},
        "zucchini": {"protein": 1.5, "carbs": 3.5, "fat": 0.3, "unit": "1 cup sliced"},
        "green beans": {"protein": 2, "carbs": 7, "fat": 0.3, "unit": "1 cup"},
        "asparagus": {"protein": 2.9, "carbs": 5.2, "fat": 0.2, "unit": "1 cup"},
        "bell pepper": {"protein": 1, "carbs": 9, "fat": 0.2, "unit": "1 cup chopped"},
        "kale": {"protein": 2.5, "carbs": 7, "fat": 0.5, "unit": "1 cup chopped"},
        "onion": {"protein": 1, "carbs": 11, "fat": 0.1, "unit": "1 cup chopped"}
    }
}

SEASONING_SUGGESTIONS = [
    "lemon pepper", "garlic and herb", "cumin and paprika", "soy sauce and ginger", "curry powder",
    "chili lime", "Italian seasoning", "rosemary and thyme"
]

USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
MACRO_LOG_PATH = os.path.join("data", "macro_log.json")
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")
