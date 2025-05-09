import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# Load trained SVR model
model = joblib.load('svr_magnitude.pkl')

# Mappings
direction_mapping = {
    'N': 0, 'NE': 1, 'E': 2, 'SE': 3, 'S': 4, 'SW': 5, 'W': 6, 'NW': 7
}
time_of_day_mapping = {
    'Night': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3
}
region_mapping = {
    'India': 0, 'Nepal': 1, 'Pakistan': 2, 'Afghanistan': 3,
    'Bangladesh': 4, 'Myanmar': 5, 'Other': 6
}

# Feature columns (used during training)
feature_cols = ['latitude', 'longitude', 'depth', 'direction', 'time_of_day', 'region', 'hour', 'month']

# User authentication
def authenticate_user(username, password):
    if os.path.exists('users.xlsx'):
        users_df = pd.read_excel('users.xlsx', dtype=str)
        users_df['username'] = users_df['username'].astype(str).str.strip()
        users_df['password'] = users_df['password'].astype(str).str.strip()
        username = str(username).strip()
        password = str(password).strip()
        user_record = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        return not user_record.empty
    else:
        return False

def signup_user(username, password):
    username = str(username).strip()
    password = str(password).strip()
    if os.path.exists('users.xlsx'):
        users_df = pd.read_excel('users.xlsx', dtype=str)
        users_df['username'] = users_df['username'].astype(str).str.strip()
        if username in users_df['username'].values:
            return False
        else:
            new_user = pd.DataFrame({'username': [username], 'password': [password]})
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            users_df.to_excel('users.xlsx', index=False)
            return True
    else:
        new_user = pd.DataFrame({'username': [username], 'password': [password]})
        new_user.to_excel('users.xlsx', index=False)
        return True

# Background
def set_bg():
    background_image_url = "earthquake.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{background_image_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Login / Signup
def login_signup_page():
    set_bg()
    st.title("🔒 Earthquake Magnitude Prediction - Login")
    st.markdown(
        """
        <style>
        .centered-image {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=100)
    page = st.selectbox("Choose Action", ["Login", "Signup"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if page == "Login":
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome back, {username} 👋")
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Invalid username or password ❌")

    elif page == "Signup":
        if st.button("Signup"):
            if signup_user(username, password):
                st.success("Signup successful! Please login now ✅")
            else:
                st.error("Username already exists ❌")

# Main Prediction Page
def prediction_page():
    set_bg()
    st.title("🌍 Earthquake Magnitude Predictor")

    st.markdown(f"<h4 style='text-align: right;'>User: {st.session_state.username}</h4>", unsafe_allow_html=True)

    st.header("Enter Earthquake Details:")

    # Input Fields
    latitude = st.number_input("Latitude", -90.0, 90.0, 20.0)
    longitude = st.number_input("Longitude", -180.0, 180.0, 80.0)
    depth = st.number_input("Depth (km)", 0.0, 700.0, 10.0)

    direction = st.selectbox("Direction", list(direction_mapping.keys()))
    time_of_day = st.selectbox("Time of Day", list(time_of_day_mapping.keys()))
    region = st.selectbox("Region", list(region_mapping.keys()))

    hour = st.slider("Hour (0-23)", 0, 23, 12)
    month = st.slider("Month (1-12)", 1, 12, 6)

    if st.button("Predict Magnitude"):
        # Encode categorical fields
        direction_enc = direction_mapping[direction]
        time_of_day_enc = time_of_day_mapping[time_of_day]
        region_enc = region_mapping[region]

        # Prepare input DataFrame with correct column names matching training
        input_data = pd.DataFrame([{
            'latitude': latitude,
            'longitude': longitude,
            'depth': depth,
            'direction_encoded': direction_enc,
            'time_of_day_encoded': time_of_day_enc,
            'region_encoded': region_enc,
            'hour': hour,
            'month': month
        }])

        # Predict
        prediction = model.predict(input_data)[0]

        st.success(f"🔮 Predicted Earthquake Magnitude: {round(prediction, 2)}")

        # Save to Excel (user-specific log)
        save_user_input(
            st.session_state.username,
            latitude, longitude, depth,
            direction, time_of_day, region,
            hour, month, prediction
        )

# Save user inputs
def save_user_input(username, latitude, longitude, depth, direction, time_of_day, region, hour, month, prediction):
    record = {
        'username': username,
        'latitude': latitude,
        'longitude': longitude,
        'depth': depth,
        'direction': direction,
        'time_of_day': time_of_day,
        'region': region,
        'hour': hour,
        'month': month,
        'predicted_magnitude': round(prediction, 2)
    }
    df_new = pd.DataFrame([record])
    if os.path.exists('user_predictions.xlsx'):
        df_existing = pd.read_excel('user_predictions.xlsx')
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_excel('user_predictions.xlsx', index=False)
    st.info("✅ Your input and prediction has been saved!")

# App Flow
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_signup_page()
else:
    prediction_page()
