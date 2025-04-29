# Streamlit Version of Personal Trainer & Nutrition Coach Program

import streamlit as st
import datetime
import json
import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import base64
from fpdf import FPDF

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

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    "Fruits": {
        "Apple": {"protein": 0.3, "carbs": 14, "fat": 0.2, "unit": "1 medium"},
        "Banana": {"protein": 1.3, "carbs": 27, "fat": 0.3, "unit": "1 medium"},
        "Orange": {"protein": 1.2, "carbs": 15.4, "fat": 0.2, "unit": "1 medium"},
        "Grapes": {"protein": 0.6, "carbs": 17, "fat": 0.2, "unit": "1 cup"},
        "Strawberries": {"protein": 1.0, "carbs": 11.7, "fat": 0.4, "unit": "1 cup"},
        "Blueberries": {"protein": 1.1, "carbs": 21, "fat": 0.5, "unit": "1 cup"},
        "Pineapple": {"protein": 0.9, "carbs": 21.6, "fat": 0.2, "unit": "1 cup"},
        "Watermelon": {"protein": 0.9, "carbs": 11.5, "fat": 0.2, "unit": "1 cup"},
        "Mango": {"protein": 0.8, "carbs": 25, "fat": 0.6, "unit": "1 fruit"},
        "Pear": {"protein": 0.6, "carbs": 22, "fat": 0.2, "unit": "1 medium"},
    },
    "Vegetables": {
        "Broccoli": {"protein": 2.6, "carbs": 6, "fat": 0.3, "unit": "1 cup chopped"},
        "Carrot": {"protein": 0.9, "carbs": 10, "fat": 0.2, "unit": "1 medium"},
        "Spinach": {"protein": 1.0, "carbs": 1.1, "fat": 0.4, "unit": "1 cup raw"},
        "Kale": {"protein": 2.2, "carbs": 6.7, "fat": 0.6, "unit": "1 cup"},
        "Zucchini": {"protein": 1.2, "carbs": 3.5, "fat": 0.3, "unit": "1 medium"},
        "Bell Pepper": {"protein": 1.0, "carbs": 9, "fat": 0.2, "unit": "1 medium"},
        "Cucumber": {"protein": 0.7, "carbs": 4, "fat": 0.1, "unit": "1 medium"},
        "Tomato": {"protein": 1.1, "carbs": 5, "fat": 0.2, "unit": "1 medium"},
        "Cauliflower": {"protein": 2.0, "carbs": 5, "fat": 0.3, "unit": "1 cup"},
        "Green Beans": {"protein": 2.4, "carbs": 7, "fat": 0.3, "unit": "1 cup"},
    },
    "Grains": {
        "Brown Rice": {"protein": 5, "carbs": 45, "fat": 1.8, "unit": "1 cup cooked"},
        "Quinoa": {"protein": 8, "carbs": 39, "fat": 3.6, "unit": "1 cup cooked"},
        "Oats": {"protein": 6, "carbs": 27, "fat": 3, "unit": "1/2 cup dry"},
        "Whole Wheat Bread": {"protein": 5, "carbs": 20, "fat": 1.5, "unit": "1 slice"},
        "White Rice": {"protein": 4, "carbs": 44, "fat": 0.4, "unit": "1 cup cooked"},
        "Pasta": {"protein": 7, "carbs": 43, "fat": 1.3, "unit": "1 cup cooked"},
        "Tortilla": {"protein": 4, "carbs": 20, "fat": 2, "unit": "1 medium"},
        "Bagel": {"protein": 9, "carbs": 48, "fat": 1.5, "unit": "1 medium"},
        "Cereal": {"protein": 2, "carbs": 22, "fat": 1, "unit": "1 cup"},
        "Granola": {"protein": 4, "carbs": 37, "fat": 10, "unit": "1/2 cup"},
    },
    "Dairy": {
        "Whole Milk": {"protein": 8, "carbs": 12, "fat": 8, "unit": "1 cup"},
        "Low-fat Milk": {"protein": 8, "carbs": 13, "fat": 2.5, "unit": "1 cup"},
        "Skim Milk": {"protein": 8, "carbs": 12, "fat": 0.2, "unit": "1 cup"},
        "Greek Yogurt": {"protein": 10, "carbs": 6, "fat": 0.7, "unit": "100g"},
        "Cheddar Cheese": {"protein": 7, "carbs": 0.4, "fat": 9, "unit": "1 oz"},
        "Cottage Cheese": {"protein": 11, "carbs": 3, "fat": 4, "unit": "1/2 cup"},
        "Cream Cheese": {"protein": 2, "carbs": 1, "fat": 10, "unit": "1 oz"},
        "Butter": {"protein": 0.1, "carbs": 0, "fat": 11, "unit": "1 tbsp"},
        "Yogurt (plain)": {"protein": 5, "carbs": 12, "fat": 3.5, "unit": "1 cup"},
        "Parmesan": {"protein": 10, "carbs": 1, "fat": 7, "unit": "1 oz"},
    },
    "Meats": {
        "Chicken Breast": {"protein": 31, "carbs": 0, "fat": 3.6, "unit": "100g"},
        "Ground Beef (80%)": {"protein": 26, "carbs": 0, "fat": 20, "unit": "100g"},
        "Pork Chop": {"protein": 22, "carbs": 0, "fat": 9, "unit": "100g"},
        "Turkey Breast": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
        "Lamb Chop": {"protein": 25, "carbs": 0, "fat": 20, "unit": "100g"},
        "Ham": {"protein": 18, "carbs": 1, "fat": 5, "unit": "100g"},
        "Bacon": {"protein": 12, "carbs": 1, "fat": 42, "unit": "100g"},
        "Sausage": {"protein": 18, "carbs": 2, "fat": 16, "unit": "100g"},
        "Roast Beef": {"protein": 28, "carbs": 0, "fat": 8, "unit": "100g"},
        "Beef Steak": {"protein": 27, "carbs": 0, "fat": 10, "unit": "100g"},
    },
    "Fish": {
        "Salmon": {"protein": 25, "carbs": 0, "fat": 14, "unit": "100g"},
        "Tuna": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
        "Tilapia": {"protein": 26, "carbs": 0, "fat": 2.3, "unit": "100g"},
        "Cod": {"protein": 20, "carbs": 0, "fat": 1.5, "unit": "100g"},
        "Sardines": {"protein": 25, "carbs": 0, "fat": 11, "unit": "100g"},
    }
}

USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
MACRO_LOG_PATH = os.path.join("data", "macro_log.json")
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")

# ... the rest of the app code remains unchanged

