import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os
import json
import random
from datetime import date, datetime, timedelta
from yaml.loader import SafeLoader

# ---- Load Configuration ----
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# ---- Initialize Authenticator ----
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# ---- Login ----
auth_result = authenticator.login(location="main")

if auth_result is None:
    st.warning("Please enter your username and password.")
    st.stop()

if not auth_result["authenticated"]:
    st.error("Username or password is incorrect.")
    st.stop()

# ---- Extract Auth Info ----
name = auth_result["name"]
username = auth_result["username"]
authenticator.logout("Logout", location="sidebar")

# ---- Page Config ----
st.set_page_config(page_title="Salesmen Spartan Board", layout="centered")
st.title("Salesmen Spartan Board")
st.caption("St. Francis de Sales — PRAY FOR US 🙏")
st.success(f"Welcome, {name}!")

# ---- Setup Data File ----
today = date.today().isoformat()
DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        saved_data = json.load(f)
else:
    saved_data = {}

user_day_key = f"{username}_{today}"

# ---- Generate Daily Tasks ----
def generate_tasks():
    all_tasks = [
        "Cold call 10 people you've never talked to",
        "Read 10 pages of a non-fiction book",
        "Write down 3 things you’re grateful for",
        "Do 50 pushups (can be broken into sets)",
        "Take a cold shower",
        "Journal for 10 minutes",
        "Send a thoughtful message to someone you admire",
        "Walk 2 miles or more",
        "Pray or meditate for 10+ minutes",
        "Wake up before 6:00 AM",
        "No sugar all day",
        "Avoid social media all day"
    ]
    random.shuffle(all_tasks)
    return all_tasks[:5]

# ---- Load or Initialize Tasks ----
if user_day_key not in saved_data:
    saved_data[user_day_key] = {
        "tasks": generate_tasks(),
        "completed": [False] * 5
    }

task_set = saved_data[user_day_key]
st.markdown(f"### Tasks for {today}")

for i, task in enumerate(task_set["tasks"]):
    checked = st.checkbox(task, value=task_set["completed"][i], key=f"task_{i}")
    task_set["completed"][i] = checked

with open(DATA_FILE, "w") as f:
    json.dump(saved_data, f, indent=2)

# ---- Streak Logic ----
def calculate_streak(user_data):
    if not user_data:
        return 0
    sorted_dates = sorted(user_data.keys(), reverse=True)
    streak = 0
    today = datetime.today().date()
    for date_str in sorted_dates:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        expected_date = today - timedelta(days=streak)
        if day == expected_date and all(user_data[date_str]):
            streak += 1
        else:
            break
    return streak

user_history = {
    key.split("_")[1]: val["completed"]
    for key, val in saved_data.items()
    if key.startswith(f"{username}_")
}

streak = calculate_streak(user_history)
st.markdown(f"🔥 **Current Streak:** {streak} day{'s' if streak != 1 else ''}")
completed_count = sum(task_set["completed"])
st.write(f"✅ You’ve completed {completed_count}/5 tasks today.")

# ---- Leaderboard ----
st.subheader("🏆 Leaderboard")
def get_user_streaks(data):
    streaks = {}
    for key in data:
        if "_" not in key:
            continue
        user, date_str = key.rsplit("_", 1)
        if user not in streaks:
            user_data = {
                k.rsplit("_", 1)[1]: v["completed"]
                for k, v in data.items() if k.startswith(user + "_")
            }
            streaks[user] = calculate_streak(user_data)
    return streaks

user_streaks = get_user_streaks(saved_data)
sorted_streaks = sorted(user_streaks.items(), key=lambda x: x[1], reverse=True)
for rank, (user, s) in enumerate(sorted_streaks, start=1):
    st.write(f"{rank}. **{user.capitalize()}** — 🔥 {s} day{'s' if s != 1 else ''}")
