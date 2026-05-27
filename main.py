from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import joblib
import os

# -----------------------------------
# LOAD MODEL + SCALER + ENCODERS
# -----------------------------------

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = joblib.load(os.path.join(base_dir, "models/isolation_forest_model.pkl"))
scaler = joblib.load(os.path.join(base_dir, "models/scaler.pkl"))
user_encoder = joblib.load(os.path.join(base_dir, "models/user_encoder.pkl"))
country_encoder = joblib.load(os.path.join(base_dir, "models/country_encoder.pkl"))
device_encoder = joblib.load(os.path.join(base_dir, "models/device_encoder.pkl"))
browser_encoder = joblib.load(os.path.join(base_dir, "models/browser_encoder.pkl"))
status_encoder = joblib.load(os.path.join(base_dir, "models/status_encoder.pkl"))

historical_data = pd.read_csv(os.path.join(base_dir, "data/behavior_feature_engineered_data (2).xls"))
historical_data['user_id'] = historical_data['user_id'].astype(str)

# -----------------------------------
# FASTAPI APP
# -----------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# INPUT SCHEMA
# -----------------------------------

class LoginData(BaseModel):
    user_id: str
    country: str
    device_type: str
    browser: str
    failed_attempts: int
    hour: int
    is_weekend: int

# -----------------------------------
# HOME ROUTE
# -----------------------------------

@app.get("/")
def home():
    return {"message": "Behavior-Based Login Anomaly Detection API Running"}


@app.post("/predict")
def predict(data: LoginData):
    # -----------------------------------
    # ENCODE INPUTS
    # -----------------------------------
    try:
        user_encoded = user_encoder.transform([data.user_id])[0]
    except:
        user_encoded = 0
    try:
        country_encoded = country_encoder.transform([data.country])[0]
    except:
        country_encoded = 0
    try:
        device_encoded = device_encoder.transform([data.device_type])[0]
    except:
        device_encoded = 0
    try:
        browser_encoded = browser_encoder.transform([data.browser])[0]
    except:
        browser_encoded = 0

    # -----------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------
    unusual_login_hour = int(data.hour <= 5 or data.hour >= 23)
    excessive_failed_attempts = int(data.failed_attempts >= 5)
    behavior_risk_score = unusual_login_hour * 50 + excessive_failed_attempts * 50
    high_risk_login = int(behavior_risk_score >= 80)
    
    # Retrieve user history
    user_hist = historical_data[historical_data['user_id'] == str(user_encoded)]
    if not user_hist.empty:
        max_normal_failed_attempts = int(user_hist['max_normal_failed_attempts'].iloc[0])
        usual_start_hour = int(user_hist['usual_start_hour'].iloc[0])
        usual_end_hour = int(user_hist['usual_end_hour'].iloc[0])
        
        is_new_country = int(str(country_encoded) not in user_hist['country'].values)
        is_new_device = int(str(device_encoded) not in user_hist['device_type'].values)
        is_new_browser = int(str(browser_encoded) not in user_hist['browser'].values)
    else:
        max_normal_failed_attempts = 3
        usual_start_hour = 8
        usual_end_hour = 20
        is_new_country = 1
        is_new_device = 1
        is_new_browser = 1
        
    day_of_week = 5 if data.is_weekend else 2
    login_status = status_encoder.transform(["Success"])[0] if data.failed_attempts == 0 else status_encoder.transform(["Failed"])[0]

    # -----------------------------------
    # CREATE INPUT DATAFRAME
    # -----------------------------------
    input_data = pd.DataFrame([{
        "user_id": user_encoded,
        "country": country_encoded,
        "device_type": device_encoded,
        "browser": browser_encoded,
        "failed_attempts": data.failed_attempts,
        "login_status": login_status,
        "hour": data.hour,
        "day_of_week": day_of_week,
        "is_weekend": data.is_weekend,
        "max_normal_failed_attempts": max_normal_failed_attempts,
        "usual_start_hour": usual_start_hour,
        "usual_end_hour": usual_end_hour,
        "is_new_country": is_new_country,
        "is_new_device": is_new_device,
        "is_new_browser": is_new_browser,
        "unusual_login_hour": unusual_login_hour,
        "excessive_failed_attempts": excessive_failed_attempts,
        "behavior_risk_score": behavior_risk_score,
        "high_risk_login": high_risk_login
    }])

    # -----------------------------------
    # SCALE INPUT
    # -----------------------------------
    input_scaled = scaler.transform(input_data)

    # -----------------------------------
    # PREDICT
    # -----------------------------------
    prediction = model.predict(input_scaled)[0]
    anomaly_score = model.decision_function(input_scaled)[0]

    # -----------------------------------
    # CONVERT PREDICTION
    # -----------------------------------
    if prediction == -1:
        prediction_value = 1
        status = "Suspicious Login"
    else:
        prediction_value = 0
        status = "Normal Login"

    # anomaly_score is positive for normal, negative for anomaly
    risk_score = max(0, min(int(50 - anomaly_score * 100), 100))
    if risk_score >= 80:
        risk_level = "Critical"
    elif risk_score >= 60:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "prediction": prediction_value,
        "status": status,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "behavior_risk_score": behavior_risk_score
    }

app.mount("/app", StaticFiles(directory=os.path.join(base_dir, "app"), html=True), name="app")