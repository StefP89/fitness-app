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
import math
import random

# ------------------------- Constants --------------------------- #

FOOD_DB = {
    # Proteins
    "chicken breast": {"protein": 31, "carbs": 0, "fat": 3.5, "unit": "100g"},
    "egg": {"protein": 6, "carbs": 1, "fat": 5, "unit": "1 large"},
    "whey protein": {"protein": 25, "carbs": 3, "fat": 2, "unit": "1 scoop"},
    "ground beef": {"protein": 26, "carbs": 0, "fat": 20, "unit": "100g"},
    "turkey breast": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
    "pork loin": {"protein": 24, "carbs": 0, "fat": 7, "unit": "100g"},
    "lamb chop": {"protein": 25, "carbs": 0, "fat": 21, "unit": "100g"},
    "duck breast": {"protein": 27, "carbs": 0, "fat": 12, "unit": "100g"},
    "ham": {"protein": 18, "carbs": 1, "fat": 6, "unit": "100g"},
    "salami": {"protein": 22, "carbs": 1, "fat": 17, "unit": "100g"},

    # Fish
    "salmon": {"protein": 25, "carbs": 0, "fat": 13, "unit": "100g"},
    "tuna": {"protein": 29, "carbs": 0, "fat": 1, "unit": "100g"},
    "cod": {"protein": 20, "carbs": 0, "fat": 1, "unit": "100g"},
    "tilapia": {"protein": 26, "carbs": 0, "fat": 3, "unit": "100g"},
    "sardines": {"protein": 25, "carbs": 0, "fat": 11, "unit": "100g"},

    # Carbs
    "brown rice": {"protein": 5, "carbs": 45, "fat": 1.5, "unit": "1 cup cooked"},
    "oats": {"protein": 5, "carbs": 27, "fat": 3, "unit": "1/2 cup"},
    "banana": {"protein": 1, "carbs": 27, "fat": 0.3, "unit": "1 medium"},
    "apple": {"protein": 0.5, "carbs": 25, "fat": 0.3, "unit": "1 medium"},
    "orange": {"protein": 1, "carbs": 20, "fat": 0.2, "unit": "1 medium"},
    "grapes": {"protein": 1, "carbs": 27, "fat": 0.2, "unit": "1 cup"},
    "strawberries": {"protein": 1, "carbs": 12, "fat": 0.2, "unit": "1 cup"},
    "blueberries": {"protein": 1, "carbs": 21, "fat": 0.5, "unit": "1 cup"},
    "pineapple": {"protein": 1, "carbs": 22, "fat": 0.2, "unit": "1 cup"},
    "watermelon": {"protein": 1, "carbs": 11, "fat": 0.2, "unit": "1 cup"},
    "peach": {"protein": 1, "carbs": 15, "fat": 0.2, "unit": "1 medium"},
    "mango": {"protein": 1, "carbs": 25, "fat": 0.6, "unit": "1 cup"},

    # Vegetables
    "broccoli": {"protein": 4, "carbs": 11, "fat": 0.5, "unit": "1 cup"},
    "carrots": {"protein": 1, "carbs": 12, "fat": 0.3, "unit": "1 cup sliced"},
    "spinach": {"protein": 1, "carbs": 1, "fat": 0.1, "unit": "1 cup raw"},
    "kale": {"protein": 2, "carbs": 7, "fat": 0.6, "unit": "1 cup"},
    "zucchini": {"protein": 1, "carbs": 4, "fat": 0.2, "unit": "1 cup sliced"},
    "bell pepper": {"protein": 1, "carbs": 9, "fat": 0.3, "unit": "1 medium"},
    "cauliflower": {"protein": 2, "carbs": 5, "fat": 0.3, "unit": "1 cup"},
    "onion": {"protein": 1, "carbs": 11, "fat": 0.1, "unit": "1 medium"},
    "tomato": {"protein": 1, "carbs": 5, "fat": 0.2, "unit": "1 medium"},
    "cucumber": {"protein": 1, "carbs": 4, "fat": 0.1, "unit": "1/2 cucumber"},

    # Dairy
    "milk (whole)": {"protein": 8, "carbs": 12, "fat": 8, "unit": "1 cup"},
    "milk (2%)": {"protein": 8, "carbs": 12, "fat": 5, "unit": "1 cup"},
    "milk (skim)": {"protein": 8, "carbs": 12, "fat": 0, "unit": "1 cup"},
    "greek yogurt": {"protein": 15, "carbs": 9, "fat": 0.5, "unit": "170g"},
    "cottage cheese": {"protein": 13, "carbs": 4, "fat": 5, "unit": "1/2 cup"},
    "cheddar cheese": {"protein": 7, "carbs": 1, "fat": 9, "unit": "28g"},
    "mozzarella cheese": {"protein": 7, "carbs": 1, "fat": 6, "unit": "28g"},
    "cream cheese": {"protein": 2, "carbs": 2, "fat": 10, "unit": "28g"},
    "butter": {"protein": 0, "carbs": 0, "fat": 11, "unit": "1 tbsp"},
    "yogurt (plain)": {"protein": 9, "carbs": 17, "fat": 3.5, "unit": "1 cup"},

    # Fats
    "almonds": {"protein": 6, "carbs": 6, "fat": 14, "unit": "28g"},
    "olive oil": {"protein": 0, "carbs": 0, "fat": 14, "unit": "1 tbsp"},
    "peanut butter": {"protein": 8, "carbs": 6, "fat": 16, "unit": "2 tbsp"},

    # Drinks
    "black coffee": {"protein": 0, "carbs": 0, "fat": 0, "unit": "1 cup"},
    "green tea": {"protein": 0, "carbs": 0, "fat": 0, "unit": "1 cup"},
    "orange juice": {"protein": 2, "carbs": 26, "fat": 0.5, "unit": "1 cup"},
    "soda": {"protein": 0, "carbs": 39, "fat": 0, "unit": "1 can (355ml)"},
    "beer": {"protein": 1, "carbs": 13, "fat": 0, "unit": "1 can (355ml)"},
    "wine (red)": {"protein": 0.1, "carbs": 4, "fat": 0, "unit": "5 oz"},
    "milkshake": {"protein": 8, "carbs": 50, "fat": 10, "unit": "1 cup"},
    "sports drink": {"protein": 0, "carbs": 21, "fat": 0, "unit": "1 bottle (500ml)"},
    "energy drink": {"protein": 1, "carbs": 27, "fat": 0, "unit": "1 can (250ml)"},
    "protein shake": {"protein": 20, "carbs": 5, "fat": 2, "unit": "1 scoop + water or milk"}
}

SEASONING_SUGGESTIONS = [
    "lemon pepper", "garlic and herb", "cumin and paprika", "soy sauce and ginger", "curry powder",
    "chili lime", "Italian seasoning", "rosemary and thyme"
]

USER_PREFS_PATH = os.path.join("data", "user_preferences.json")
MACRO_LOG_PATH = os.path.join("data", "macro_log.json")
USER_PROFILE_PATH = os.path.join("data", "user_profile.json")

# ------------------------- Utility Functions --------------------------- #

# ... (rest of utility functions remain unchanged) ...

# ------------------------- Streamlit App --------------------------- #

st.title("\U0001F4AA Personal Trainer & Nutrition Coach")

menu = [
    "User Intake Form",
    "Set Macro Targets",
    "Workout Program",
    "Meal Plan",
    "Ingredient-Based Suggestions",
    "Log Stats",
    "View Progress",
    "Macro Tracking",
    "Download PDF"
]

choice = st.sidebar.selectbox("Menu", menu)

# ... (existing blocks like Intake Form, Macro Tracking, Meal Plan remain unchanged) ...

# ... (unchanged sections of the app code) ...

