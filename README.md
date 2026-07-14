# WhereVulniusAI

7-day weather forecast powered by LightGBM. The project collects historical weather from Open-Meteo, trains a single multi-output model, and serves predictions through a FastAPI backend with a bilingual web UI (Russian / English).

---

## Table of Contents

- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Machine Learning](#machine-learning)
- [API](#api)
- [Web UI](#web-ui)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## How It Works

```mermaid
flowchart LR
    A[Open-Meteo Archive API] -->|whether_collector.py| B[data/weather_data.xlsx]
    B -->|train.py| C[model/weather_model.joblib]
    B --> D[forecast_service.py]
    C --> D
    D -->|get_forecast| E[app.py FastAPI]
    E --> F[static/ Web UI]
```

1. **Collect** — `whether_collector.py` downloads hourly and daily weather history and saves a single Excel file.
2. **Train** — `train.py` builds lag/rolling features, trains one `MultiOutputRegressor(LGBMRegressor)`, and saves the bundle to `model/weather_model.joblib`.
3. **Predict** — on each API request, `get_forecast()` loads Excel + model, engineers features from the last 20 days, predicts 7 days ahead, and computes sunrise/sunset astronomically.
4. **Serve** — `app.py` exposes REST endpoints; the frontend renders the forecast with RU/EN localization.

---

## Project Structure

```
WhereVulniusAI/
├── app.py                  # FastAPI application (API + static files)
├── forecast_service.py     # Core logic: data, features, training, prediction, API response
├── train.py                # CLI: train model and print forecast report
├── whether_collector.py    # Download weather archive from Open-Meteo → Excel
├── requirements.txt        # Python dependencies
│
├── data/
│   └── weather_data.xlsx   # Single dataset (sheets: daily, hourly)
│
├── model/
│   └── weather_model.joblib # Saved model bundle (created by train.py)
│
├── static/
│   ├── index.html          # Forecast page
│   ├── app.js              # UI logic, API calls, rendering
│   ├── i18n.js             # Russian / English translations
│   └── styles.css          # Styles
│
└── .cache.sqlite           # HTTP cache for Open-Meteo (created by collector)
```

### File Roles

| File | Purpose |
|------|---------|
| `whether_collector.py` | Fetches archive data from [Open-Meteo Archive API](https://archive-api.open-meteo.com/v1/archive). Writes `data/weather_data.xlsx` with two sheets. |
| `forecast_service.py` | Shared module: merge daily/hourly data, feature engineering, training, inference, sun time calculation, JSON response builder. |
| `train.py` | Entry point for training. Saves model and prints a 7-day CLI report. |
| `app.py` | HTTP server: `/`, `/api/health`, `/api/forecast`. |
| `static/i18n.js` | All user-facing text (RU/EN). Backend code stays in English. |

---

## Data Pipeline

### Source: Open-Meteo

- **API:** `https://archive-api.open-meteo.com/v1/archive`
- **Location (default):** 52.52°N, 13.41°E (Berlin)
- **Date range:** configurable in `whether_collector.py` (`start_date` / `end_date`)

### Excel Format: `data/weather_data.xlsx`

| Sheet | Columns | Description |
|-------|---------|-------------|
| `daily` | 20 params + `date` | Daily targets (temperature, precipitation, wind, etc.) |
| `hourly` | 30 params + `date` | Hourly observations aggregated later as mean/max/min |

### Feature Merge (`load_merged_dataset`)

1. Read both sheets.
2. Aggregate hourly columns per day: `mean`, `max`, `min` → 90 extra columns (`hourly_*_mean`, etc.).
3. Merge with daily data on `date`.
4. **110 source columns** total for feature engineering.

---

## Machine Learning

### Model

- **Algorithm:** `MultiOutputRegressor` wrapping `LGBMRegressor`
- **Single file:** `model/weather_model.joblib`
- **Outputs:** 17 parameters × 7 days = **119 predictions**
- **Display:** 20 parameters × 7 days (sunrise, sunset, daylight are computed separately, not predicted)

### Targets (17 model outputs)

All daily columns **except** `sunrise`, `sunset`, `daylight_duration` (computed via the `astral` library).

### Features

For each of 110 source columns:

- Lags: 1–7 days
- Rolling: 7-day mean, 14-day mean, 7-day std (shifted by 1 day)
- Seasonality: `month_sin/cos`, `day_of_year_sin/cos`

### Inference Flow (`get_forecast`)

```
weather_data.xlsx
    → load_merged_dataset()
    → take last 20 days (HISTORY_DAYS)
    → create_features()
    → model.predict() → 119 values
    → predictions_to_forecast() → 7 rows
    → apply_computed_sun_times() → astronomical sunrise/sunset
    → build_forecast_response() → JSON for API/UI
```

### Model Bundle Contents

```python
{
    "model": MultiOutputRegressor,
    "feature_cols": [...],           # columns used for X
    "feature_source_cols": [...],    # columns for feature engineering
    "model_target_cols": [...],      # 17 trained targets
    "target_cols": [...],            # 20 display columns
    "forecast_days": 7,
    "history_days": 20,
}
```

---

## API

Base URL (local): `http://127.0.0.1:8000`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Forecast web page |
| `GET` | `/api/health` | Server status + model file check |
| `GET` | `/api/forecast` | 7-day forecast JSON |

### Example: `/api/health`

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": ".../model/weather_model.joblib"
}
```

### Example: `/api/forecast` (fragment)

```json
{
  "timezone": "Europe/Berlin",
  "last_known_date": "2026-07-12",
  "period_display": "13.07.2026 - 19.07.2026",
  "forecast_days": 7,
  "days": [
    {
      "date": "2026-07-13",
      "weekday": 0,
      "weather_code": 61,
      "weather_icon": "🌧️",
      "summary": {
        "temperature_mean": 18.5,
        "temperature_max": 22.0,
        "temperature_min": 14.0,
        "precipitation_sum": 2.1,
        "wind_speed_max": 15.0,
        "wind_direction": 180,
        "sunrise": 1752470400.0,
        "sunset": 1752520800.0
      },
      "details": [
        { "key": "temperature_2m_mean", "raw": 18.5 }
      ]
    }
  ]
}
```

Labels and units are formatted on the frontend via `static/i18n.js`.

---

## Web UI

- **Languages:** Russian / English (toggle in the top header)
- **Views:** week overview, 7 day tabs, detailed panel per day
- **Visuals:** weather icons (WMO codes), temperature gradient bar, grouped parameter details
- **Groups:** Temperature, Precipitation, Wind, Sun and light

---

## Requirements

- Python **3.10+**
- ~**2 GB RAM** recommended for inference (feature engineering on full Excel)
- Internet for initial data collection (`whether_collector.py`)

### Python Packages

See `requirements.txt`:

- **Serving:** `fastapi`, `uvicorn`, `pandas`, `numpy`, `lightgbm`, `scikit-learn`, `joblib`, `openpyxl`, `astral`
- **Data collection:** `openmeteo-requests`, `requests-cache`, `retry-requests`

---

## Installation

```bash
git clone <repository-url>
cd WhereVulniusAI

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

### Step 1 — Collect weather data

```bash
python whether_collector.py
```

Creates `data/weather_data.xlsx` (overwrites existing file).

### Step 2 — Train the model

```bash
python train.py
```

Creates `model/weather_model.joblib` (~2–3 minutes depending on hardware).

### Step 3 — Start the web server

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open: http://127.0.0.1:8000

### Serving without retraining

For serving without retraining you only need:

- `model/weather_model.joblib`
- `data/weather_data.xlsx` (must stay reasonably up to date)
- `app.py`, `forecast_service.py`, `static/`

Run `whether_collector.py` periodically to refresh data. Retraining is optional unless you change features or location.

---

## Configuration

### Change location

Edit `LOCATION` in `forecast_service.py` and coordinates in `whether_collector.py`, then:

1. Re-run `whether_collector.py`
2. Re-run `train.py`

### Key constants (`forecast_service.py`)

| Constant | Default | Meaning |
|----------|---------|---------|
| `FORECAST_DAYS` | 7 | Days to predict |
| `HISTORY_DAYS` | 20 | Days of history used for inference |
| `DATA_PATH` | `data/weather_data.xlsx` | Dataset path |
| `MODEL_PATH` | `model/weather_model.joblib` | Model path |

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Data file not found` | Missing Excel | Run `whether_collector.py` |
| `Model not found` | Missing model | Run `train.py` |
| `index 119 is out of bounds` | Model/API column mismatch | Retrain with `python train.py` |
