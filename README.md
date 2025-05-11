# 🌍 Earthquake Magnitude Predictor 🌐

A **Streamlit-powered web application** that predicts earthquake magnitudes in India & its surrounding territories, using a machine learning model trained on historical seismic data.  
Featuring an interactive, animated UI with user login, custom pages, and real-time predictions.

[![Streamlit App](https://img.shields.io/badge/Live%20App-Click%20Here-brightgreen)](https://earthquake-magnitude-predictor-io.streamlit.app/)

---

## 🚀 Key Features

- 🔒 **User Login & Signup** (Simple Auth)
- 📈 **Earthquake Prediction**: Input parameters like latitude, longitude, depth, and time — get instant magnitude prediction
- 🎨 **Interactive UI** with animated backgrounds and a stylish, responsive layout
- 📚 **Custom Pages**: About, Contact, and Model Explanation
- ⚡ **Real ML Model Integration** — trained using 9,000+ earthquake records
- ✅ **Responsive Design** powered by Streamlit + CSS

---

## 📊 Dataset & ML Model Pipeline

### 🔎 Dataset Info
- **Source**: Kaggle - *Earthquake Data (India & Surrounding Territories, 2010–2020)*
- **Records**: 9,000+
- **Features**:
  - Latitude, Longitude, Depth, Magnitude, Location, and Time
  - Engineered features like: year, month, day, region, time_of_day, and more!

### 🧑‍💻 Model Training Workflow
1. **Exploratory Data Analysis (EDA)**
   - Split location columns (`distance`, `direction`, `place`)
   - Created time & region-based features
2. **Feature Engineering**
   - Label encoding, date part extraction, categorical grouping
3. **Model Comparison**
   - Trained multiple models: 
     - Linear Regression
     - Random Forest
     - XGBoost
     - **Support Vector Regression (SVR) — Best Performer ✅**
4. **Model Saving**
   - Trained **SVR model** saved using `joblib` and integrated into the Streamlit app

#### 📈 Why SVR?
Among all tested models, **SVR** consistently delivered the best results with superior prediction accuracy, especially on unseen test data.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + HTML/CSS (custom styled)
- **Backend**: Python
- **ML Model**: Trained **Support Vector Regression (SVR)**
- **Libraries**: 
  - `streamlit`, `pandas`, `numpy`
  - `scikit-learn`, `joblib`, `matplotlib`

---

## 📦 Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/earthquake-app.git
    cd earthquake-app
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Streamlit app**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure

earthquake-app/
├── app.py # Streamlit main app
├── Earthquake_SVR.py # Model loading & prediction
├── pages/
│ ├── about.py
│ ├── contact.py
│ └── model_explanation.py
├── trained_svr_model.pkl # Best trained SVR model
├── requirements.txt
├── README.md


---

## 🚀 Streamlit App (Live)

Click below to try out the **live demo app**:

### 🌐 [Open Earthquake Magnitude Predictor App](https://earthquake-magnitude-predictor-io.streamlit.app/)

---

## 🎯 Future Enhancements
- Add real-time earthquake feed API for dynamic predictions 🌐
- Display earthquake hotspots on an interactive map (Folium/Plotly) 🗺️
- Predict depth & severity level along with magnitude 🚨

---

## ⚠️ License & Disclaimer

This project is for **educational/demo purposes** only.  
It is **not intended** for real-world disaster alert systems.  
Please ensure proper licensing when using images/assets for public deployment.

---

> Developed by Paarth Sahni | 2025  
> Powered by Machine Learning & Streamlit 🌊

