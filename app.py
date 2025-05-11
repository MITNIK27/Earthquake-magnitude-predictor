import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import requests
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Earthquake Dashboard")

# Custom CSS for sidebar + title alignment
st.markdown(
    """
    <style>
    /* Sidebar background color */
    [data-testid="stSidebar"] {
        background-color: #c89666;
    }

    /* Sidebar radio buttons - hover effect and rounded */
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }

    [data-testid="stSidebar"] .css-1d391kg:hover {
        color: #f0e6d2;
    }

    /* Radio buttons style */
    [role="radiogroup"] label {
        background-color: transparent;
        border-radius: 10px;
        padding: 8px 16px;
        margin: 5px 0;
        display: block;
    }

    [role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    /* Main title - remove extra top space */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Hide Streamlit default menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Function to get initials
def get_initials(name):
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0][0].upper()
    else:
        return ''.join([p[0].upper() for p in parts[:2]])

# User Badge Component
def user_badge(username):
    initials = get_initials(username)
    st.markdown(
        f"""
        <style>
        .user-badge {{
            position: fixed;
            top: 15px;
            right: 15px;
            background-color: #4CAF50;
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            cursor: pointer;
        }}
        .user-badge:hover::after {{
            content: '{username}';
            position: absolute;
            top: 60px;
            right: 0;
            background-color: #333;
            color: #fff;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
            white-space: nowrap;
        }}
        </style>
        <div class="user-badge">{initials}</div>
        """,
        unsafe_allow_html=True
    )


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
feature_cols = ['latitude', 'longitude', 'depth', 'direction_encoded', 'time_of_day_encoded', 'region_encoded', 'hour', 'month']

# Authentication Functions
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

# Background Setter
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

# Login/Signup Page
def login_signup_page():
    set_bg()
    st.title("🔒 Earthquake App - Login/Signup")

    page = st.selectbox("Choose Action", ["Login", "Signup"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if page == "Login":
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome back, {username} 👋")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "Dashboard"
            else:
                st.error("Invalid username or password ❌")
    elif page == "Signup":
        if st.button("Signup"):
            if signup_user(username, password):
                st.success("Signup successful! Please login now ✅")
            else:
                st.error("Username already exists ❌")

# Dashboard Page
def dashboard_page():
    set_bg()
    st.title("🌍 Earthquake Hotspots Dashboard")    # User badge top-right
    user_badge(st.session_state.username)

    st.markdown("""
        <style>
            body {
                background-color:  #12343b ;
            }
            .stApp {
                background-color:  #12343b ;      
            }
        </style>
    """, unsafe_allow_html=True)



    # Load data
    if os.path.exists('riseq.csv'):
        df = pd.read_csv('riseq.csv')
    else:
        st.warning("Dataset not found!")
        return


    # ---------- Extract Region from 'location' ----------
    df['region'] = df['location'].apply(lambda x: x.split(",")[-1].strip() if pd.notnull(x) else 'Unknown')

    # Group by region
    region_group = df.groupby('region').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'region': 'count'
    }).rename(columns={'region': 'count'}).reset_index()

    # Normalize radius
    max_count = region_group['count'].max()
    region_group['radius'] = region_group['count'].apply(lambda x: 10000 + (x / max_count) * 30000)

    # Map + Pie chart layout
    col1, col2 = st.columns(2)

    # 🌐 Map with Tooltip
    with col1:
        st.write("### 🌐 Earthquake Hotspots Map")
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            initial_view_state=pdk.ViewState(
                latitude=20,
                longitude=80,
                zoom=3.5,
                pitch=0,
            ),
            layers=[
                # Big transparent circle
                pdk.Layer(
                    'ScatterplotLayer',
                    data=region_group,
                    get_position='[longitude, latitude]',
                    get_color='[255, 0, 0, 200]',
                    get_radius='radius',
                    pickable=True,
                    stroked=False,
                    filled=True,
                    radius_min_pixels=10,
                    radius_max_pixels=50,
                    get_line_color=[0, 0, 0, 0],
                ),
                # Small red dot
                pdk.Layer(
                    'ScatterplotLayer',
                    data=region_group,
                    get_position='[longitude, latitude]',
                    get_color='[255, 0, 0, 255]',
                    get_radius=1000,
                    pickable=False,
                    stroked=False,
                    filled=True,
                    radius_min_pixels=2,
                    radius_max_pixels=5,
                ),
            ],
            tooltip={
                "html": "<b>Region:</b> {region}<br/><b>Count:</b> {count}",
                "style": {
                    "color": "black"
                }
            }
        ), use_container_width=True)  # ✅ Fills column width

    # 📊 Pie chart with "<2%" grouped as "Other"
    with col2:
        st.write("### 📊 Earthquake Counts by Region (Pie Chart)")

        total_counts = region_group['count'].sum()
        region_group['percent'] = region_group['count'] / total_counts * 100

        # Split regions
        major_regions = region_group[region_group['percent'] >= 2]
        minor_regions = region_group[region_group['percent'] < 2]

        # Combine minor regions into "Other"
        other_count = minor_regions['count'].sum()
        other_row = pd.DataFrame({
            'region': ['Other'],
            'count': [other_count]
        })

        pie_data = pd.concat([major_regions[['region', 'count']], other_row])

        # Plot pie chart
        fig, ax = plt.subplots(figsize=(6, 6))  # ✅ Bigger size to match map
        wedges, texts, autotexts = ax.pie(
            pie_data['count'],
            labels=pie_data['region'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},  # ✅ Better font size
        )
        ax.axis('equal')  # Circle pie chart

        # ✅ Optional: Add legend outside for clarity
        ax.legend(wedges, pie_data['region'],
                  title="Regions",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        st.pyplot(fig, use_container_width=True)  # ✅ Fills column width

    st.subheader("📅 Recent Earthquakes")
    st.dataframe(df.sort_values('orginal_time', ascending=False).head(5))
    df['magnitude'] = df['magnitude'].str.extract(r'(\d+\.\d+)').astype(float)

    st.subheader("🔢 Earthquake Counts")
    col1, col2 = st.columns(2)
    col1.metric("Total Earthquakes", len(df))
    col2.metric("Max Magnitude", df['magnitude'].max())

    st.subheader("📈 Earthquake Count by Magnitude")
    counts = df['magnitude'].round().value_counts().sort_index()
    st.bar_chart(counts)

    st.subheader("🔎 Explore Earthquakes by Magnitude Range")
    mag_range = st.slider("Select Magnitude Range", float(df['magnitude'].min()), float(df['magnitude'].max()), (4.0, 6.0))
    filtered_df = df[(df['magnitude'] >= mag_range[0]) & (df['magnitude'] <= mag_range[1])]
    st.map(filtered_df[['latitude', 'longitude']])

# Predictor Page
def prediction_page():
    set_bg()
    st.markdown("""
        <style>
            body {
                background-color:  #12343b ;
            }
            .stApp {
                background-color:  #12343b ;      
            }
        </style>
    """, unsafe_allow_html=True)
    st.title("🌍 Earthquake Magnitude Predictor")

    # User badge top-right
    user_badge(st.session_state.username)

    st.header("Enter Earthquake Details:")

    # Detect Location Button
    st.info("Click below to auto-detect your location 👇")
    if st.button("📍 Detect My Location"):
        try:
            response = requests.get('https://ipinfo.io/json')
            data = response.json()
            loc = data['loc'].split(',')
            lat_detected = float(loc[0])
            lon_detected = float(loc[1])

            st.session_state.latitude = lat_detected
            st.session_state.longitude = lon_detected
            st.success(f"Detected: Latitude {lat_detected}, Longitude {lon_detected}")

            st.map(pd.DataFrame({'lat': [lat_detected], 'lon': [lon_detected]}))
        except:
            st.error("Location detection failed.")

    latitude = st.number_input("Latitude", -90.0, 90.0, st.session_state.get('latitude', 20.0))
    longitude = st.number_input("Longitude", -180.0, 180.0, st.session_state.get('longitude', 80.0))
    depth = st.number_input("Depth (km)", 0.0, 700.0, 10.0)

    direction = st.selectbox("Direction", list(direction_mapping.keys()))
    time_of_day = st.selectbox("Time of Day", list(time_of_day_mapping.keys()))
    region = st.selectbox("Region", list(region_mapping.keys()))

    hour = st.slider("Hour (0-23)", 0, 23, 12)
    month = st.slider("Month (1-12)", 1, 12, 6)

    if st.button("Predict Magnitude"):
        direction_enc = direction_mapping[direction]
        time_of_day_enc = time_of_day_mapping[time_of_day]
        region_enc = region_mapping[region]

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

        prediction = model.predict(input_data)[0]
        st.success(f"🔮 Predicted Earthquake Magnitude: {round(prediction, 2)}")

        save_user_input(
            st.session_state.username,
            latitude, longitude, depth,
            direction, time_of_day, region,
            hour, month, prediction
        )

# Save Predictions
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
# Inject CSS for sidebar background
st.markdown(
    """
    <style>
    /* Sidebar background color */
    [data-testid="stSidebar"] {
        background-color: #c89666;
    }
    /* Sidebar text color for better contrast */
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# App Navigation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Login"

if not st.session_state.logged_in:
    login_signup_page()
else:
    # Sidebar Navigation
    st.sidebar.title(f"Hello, {st.session_state.username} 👋")
    page = st.sidebar.radio("Navigate", ["Dashboard", "Predictor", "Logout"])

    if page == "Dashboard":
        dashboard_page()
    elif page == "Predictor":
        prediction_page()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        st.rerun()
