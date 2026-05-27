# login-anomally-detection

# Login Anomaly Detector

A behavior-based login anomaly detection system that uses machine learning to identify suspicious login activity in real time. The system analyzes user behavior patterns — including login timing, device, location, browser, and failed attempts — to flag potential security threats.

---

## How It Works

The system is built around a trained **Isolation Forest** model, an unsupervised anomaly detection algorithm well-suited for identifying rare, unusual events in high-dimensional data. When a login event is submitted, the API:

1. Encodes categorical inputs (user, country, device, browser) using pre-fitted label encoders
2. Performs feature engineering to derive risk indicators (unusual login hours, excessive failed attempts, new device/country/browser flags)
3. Looks up the user's historical behavior baseline from the feature-engineered dataset
4. Scales the full feature vector and runs it through the Isolation Forest model
5. Returns a prediction (`Normal` / `Suspicious`), a risk score (0–100), and a risk level (`Low`, `Medium`, `High`, or `Critical`)

---

## Project Structure

```
login-anomally-detector/
├── api/
│   └── main.py               # FastAPI backend — prediction endpoint
├── app/
│   ├── index.html            # Frontend UI
│   ├── script.js             # Form handling & API calls
│   └── style.css             # Styling
├── data/
│   ├── login_behavior_dataset.xls
│   ├── behavior_preprocessed_data.xls
│   └── behavior_feature_engineered_data.xls
├── models/
│   ├── isolation_forest_model.pkl
│   ├── scaler.pkl
│   ├── feature_columns.pkl
│   ├── user_encoder.pkl
│   ├── country_encoder.pkl
│   ├── device_encoder.pkl
│   ├── browser_encoder.pkl
│   └── status_encoder.pkl
├── notebooks/
│   ├── dataset-generation.ipynb
│   ├── preprocessed-data.ipynb
│   ├── feature-selection.ipynb
│   ├── isolation-forest.ipynb
│   └── model-training.ipynb
└── results/
    └── isolation_forest_results.xls
```

---

## API

### `GET /`
Health check — returns a status message confirming the API is running.

### `POST /predict`

Accepts a JSON body with the following fields:

| Field             | Type    | Description                          |
|------------------|---------|--------------------------------------|
| `user_id`        | string  | User identifier (e.g. `"user_42"`)  |
| `country`        | string  | Login country (e.g. `"India"`)      |
| `device_type`    | string  | Device OS (e.g. `"Windows"`)        |
| `browser`        | string  | Browser used (e.g. `"Chrome"`)      |
| `failed_attempts`| integer | Number of failed login attempts     |
| `hour`           | integer | Hour of login (0–23, 24h format)    |
| `is_weekend`     | integer | `1` if weekend, `0` if weekday      |

**Example request:**
```json
{
  "user_id": "user_42",
  "country": "India",
  "device_type": "Windows",
  "browser": "Chrome",
  "failed_attempts": 0,
  "hour": 10,
  "is_weekend": 0
}
```

**Example response:**
```json
{
  "prediction": 0,
  "status": "Normal Login",
  "risk_score": 22,
  "risk_level": "Low",
  "behavior_risk_score": 0
}
```

---

## Tech Stack

- **Backend:** Python, FastAPI
- **ML Model:** Scikit-learn Isolation Forest (`contamination=0.05`)
- **Preprocessing:** StandardScaler, LabelEncoders (via joblib)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Data:** Behavior-engineered login dataset (~100 users)

---

## Setup & Running

### Prerequisites

- Python 3.9+

### Install dependencies

```bash
pip install fastapi uvicorn scikit-learn pandas joblib
```

### Run the API

```bash
cd api
uvicorn main:app --reload
```

The app and UI will be served at:
- API: `http://localhost:8000`
- Frontend: `http://localhost:8000/app`

---

## Model Details

The Isolation Forest was trained on feature-engineered login behavior data with the following key features:

- User identity, country, device type, browser (label-encoded)
- Login hour, day of week, weekend flag
- Failed attempts and login status
- Derived features: `unusual_login_hour`, `excessive_failed_attempts`, `behavior_risk_score`, `high_risk_login`
- User-baseline features: `usual_start_hour`, `usual_end_hour`, `max_normal_failed_attempts`
- Novelty flags: `is_new_country`, `is_new_device`, `is_new_browser`

The model was trained with an 80/20 train-test split using `stratify=y` and `random_state=42` for reproducibility. See the `notebooks/` directory for the full training pipeline.

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `dataset-generation.ipynb` | Synthetic login dataset creation |
| `preprocessed-data.ipynb` | Data cleaning and preprocessing |
| `feature-selection.ipynb` | Feature engineering and selection |
| `isolation-forest.ipynb` | Model exploration and evaluation |
| `model-training.ipynb` | Final model training and export |
