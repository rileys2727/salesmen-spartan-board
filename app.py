import streamlit as st
import streamlit_authenticator as stauth
import yaml
import json
import os
import random
from datetime import date, datetime, timedelta
from yaml.loader import SafeLoader

# --- Load credentials from YAML ---
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"]
)

# --- User Login ---
name, authentication_status, username = authenticator.login(location="main")

if authentication_status is False:
    st.error("Username/password is incorrect")
    st.stop()
elif authentication_status is None:
    st.warning("Please enter your username and password")
    st.stop()

authenticator.logout("Logout", location="sidebar")
st.set_page_config(page_title="Salesmen Spartan Board", layout="centered")

# --- App Title ---
st.title("Salesmen Spartan Board")
st.caption("St. Francis de Sales — PRAY FOR US 🙏")

# --- Date ---
today = date.today().isoformat()
st.markdown(f"**Tasks for: {today}**")

# --- File path ---
DATA_FILE = "data.json"

# --- Load saved data ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        saved_data = json.load(f)
else:
    saved_data = {}

user_day_key = f"{username}_{today}"

# --- Task generator ---
def generate_tasks():
    all_tasks = [
        "Cold call 10 people you've never talked to",
        "Read 10 pages of a non-fictio
