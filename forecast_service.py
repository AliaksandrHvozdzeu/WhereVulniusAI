from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from astral import LocationInfo
from astral.sun import sun
from lightgbm import LGBMRegressor
from sklearn.multioutput import MultiOutputRegressor

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "weather_data.xlsx"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "weather_model.joblib"
FORECAST_DAYS = 7
HISTORY_DAYS = 20

LOCATION = {
    "name": "Berlin",
    "region": "Germany",
    "timezone": "Europe/Berlin",
    "latitude": 52.52,
    "longitude": 13.41,
}

COMPUTED_SUN_COLUMNS = {"sunrise", "sunset", "daylight_duration"}

NON_NEGATIVE_KEYWORDS = (
    "precipitation",
    "rain",
    "snowfall",
    "wind_speed",
    "wind_gusts",
    "sunshine",
    "radiation",
    "daylight",
    "et0",
)

PARAM_LABELS = {
    "weather_code": "Weather code",
    "temperature_2m_mean": "Mean temperature, C",
    "temperature_2m_max": "Max temperature, C",
    "temperature_2m_min": "Min temperature, C",
    "apparent_temperature_mean": "Feels like mean, C",
    "apparent_temperature_max": "Feels like max, C",
    "apparent_temperature_min": "Feels like min, C",
    "sunrise": "Sunrise",
    "sunset": "Sunset",
    "daylight_duration": "Daylight duration",
    "sunshine_duration": "Sunshine duration",
    "precipitation_sum": "Precipitation, mm",
    "rain_sum": "Rain, mm",
    "snowfall_sum": "Snowfall, cm",
    "precipitation_hours": "Precipitation hours",
    "wind_speed_10m_max": "Max wind speed, km/h",
    "wind_gusts_10m_max": "Wind gusts, km/h",
    "wind_direction_10m_dominant": "Wind direction",
    "shortwave_radiation_sum": "Shortwave radiation, MJ/m2",
    "et0_fao_evapotranspiration": "ET0 evapotranspiration, mm",
}

WEEKDAY_LABELS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def get_model_target_cols(target_cols: list[str]) -> list[str]:
    return [column for column in target_cols if column not in COMPUTED_SUN_COLUMNS]


def compute_sun_times(day: pd.Timestamp) -> tuple[float, float, float]:
    location = LocationInfo(
        LOCATION["name"],
        LOCATION["region"],
        LOCATION["timezone"],
        LOCATION["latitude"],
        LOCATION["longitude"],
    )
    sun_times = sun(location.observer, date=day.date(), tzinfo=location.timezone)
    daylight_duration = (sun_times["sunset"] - sun_times["sunrise"]).total_seconds()
    return (
        float(sun_times["sunrise"].timestamp()),
        float(sun_times["sunset"].timestamp()),
        float(daylight_duration),
    )


def apply_computed_sun_times(
    forecast_df: pd.DataFrame,
    forecast_start: pd.Timestamp,
) -> pd.DataFrame:
    result = forecast_df.copy()

    for column in COMPUTED_SUN_COLUMNS:
        if column not in result.columns:
            result[column] = np.nan

    for day_index in range(len(result)):
        day = forecast_start + pd.Timedelta(days=day_index)
        sunrise, sunset, daylight_duration = compute_sun_times(day)
        result.at[result.index[day_index], "sunrise"] = sunrise
        result.at[result.index[day_index], "sunset"] = sunset
        result.at[result.index[day_index], "daylight_duration"] = daylight_duration

    return result


def load_merged_dataset(data_path: Path = DATA_PATH) -> tuple[pd.DataFrame, list[str], list[str]]:
    daily = pd.read_excel(data_path, sheet_name="daily", engine="openpyxl")
    hourly = pd.read_excel(data_path, sheet_name="hourly", engine="openpyxl")

    daily["date"] = pd.to_datetime(daily["date"]).dt.normalize()
    hourly["date"] = pd.to_datetime(hourly["date"]).dt.normalize()

    hourly_cols = [col for col in hourly.columns if col != "date"]
    hourly_daily = hourly.groupby("date")[hourly_cols].agg(["mean", "max", "min"])
    hourly_daily.columns = [f"hourly_{col}_{stat}" for col, stat in hourly_daily.columns]
    hourly_daily = hourly_daily.reset_index()

    df = daily.merge(hourly_daily, on="date", how="left")
    df = df.sort_values("date").reset_index(drop=True)

    target_cols = [col for col in daily.columns if col != "date"]
    hourly_feature_cols = [col for col in hourly_daily.columns if col != "date"]
    feature_source_cols = target_cols + hourly_feature_cols

    return df, target_cols, feature_source_cols


def create_features(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    base = data.copy()
    new_features: dict[str, pd.Series] = {
        "month_sin": np.sin(2 * np.pi * base["date"].dt.month / 12.0),
        "month_cos": np.cos(2 * np.pi * base["date"].dt.month / 12.0),
        "day_of_year_sin": np.sin(2 * np.pi * base["date"].dt.dayofyear / 365.25),
        "day_of_year_cos": np.cos(2 * np.pi * base["date"].dt.dayofyear / 365.25),
    }

    for col in columns:
        shifted = base[col].shift(1)
        for lag in range(1, 8):
            new_features[f"{col}_lag_{lag}"] = base[col].shift(lag)

        new_features[f"{col}_roll_mean_7"] = shifted.rolling(window=7).mean()
        new_features[f"{col}_roll_mean_14"] = shifted.rolling(window=14).mean()
        new_features[f"{col}_roll_std_7"] = shifted.rolling(window=7).std()

    feature_frame = pd.DataFrame(new_features, index=base.index)
    return pd.concat([base, feature_frame], axis=1).dropna().reset_index(drop=True)


def build_target_matrix(df_features: pd.DataFrame, target_cols: list[str]) -> pd.DataFrame:
    target_data = {}

    for col in target_cols:
        for day in range(1, FORECAST_DAYS + 1):
            target_data[f"{col}_lead_{day}"] = df_features[col].shift(-day)

    return pd.DataFrame(target_data)


def postprocess_prediction(value: float, column: str) -> float:
    if column == "weather_code":
        return float(int(np.clip(round(value), 0, 99)))

    if column in {"sunrise", "sunset"}:
        return float(int(round(value)))

    if column == "daylight_duration":
        return float(max(0, value))

    if "direction" in column:
        return float(value % 360)

    if any(keyword in column for keyword in NON_NEGATIVE_KEYWORDS):
        return float(max(0, value))

    return float(value)


def resolve_prediction_target_cols(model_bundle: dict, prediction_count: int) -> list[str]:
    display_cols = model_bundle["target_cols"]
    model_cols = model_bundle.get("model_target_cols") or get_model_target_cols(display_cols)

    if prediction_count == len(model_cols) * FORECAST_DAYS:
        return model_cols
    if prediction_count == len(display_cols) * FORECAST_DAYS:
        return display_cols

    raise ValueError(
        f"Model returned {prediction_count} values, "
        f"expected {len(model_cols) * FORECAST_DAYS} "
        f"({len(model_cols)} parameters) or "
        f"{len(display_cols) * FORECAST_DAYS} ({len(display_cols)} parameters). "
        f"Retrain the model: python train.py"
    )


def predictions_to_forecast(
    predictions: np.ndarray,
    target_cols: list[str],
) -> pd.DataFrame:
    expected_count = len(target_cols) * FORECAST_DAYS
    if len(predictions) != expected_count:
        raise ValueError(
            f"Invalid prediction count: got {len(predictions)}, "
            f"expected {expected_count} for {len(target_cols)} parameters."
        )

    forecast_rows = []

    for day in range(1, FORECAST_DAYS + 1):
        row = {"date_offset": f"Day {day}"}
        for col_index, col in enumerate(target_cols):
            pred_index = col_index * FORECAST_DAYS + (day - 1)
            row[col] = postprocess_prediction(predictions[pred_index], col)
        forecast_rows.append(row)

    return pd.DataFrame(forecast_rows).set_index("date_offset")


def predict_next_week(
    latest_history: pd.DataFrame,
    model_bundle: dict,
) -> pd.DataFrame:
    feature_source_cols = model_bundle["feature_source_cols"]
    feature_cols = model_bundle["feature_cols"]

    feat_row = create_features(latest_history, feature_source_cols)
    X_input = feat_row[feature_cols].tail(1)
    predictions = model_bundle["model"].predict(X_input)[0]
    model_target_cols = resolve_prediction_target_cols(model_bundle, len(predictions))

    return predictions_to_forecast(predictions, model_target_cols)


def save_model_bundle(model_bundle: dict, model_path: Path = MODEL_PATH) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    if model_path.exists():
        model_path.unlink()
    joblib.dump(model_bundle, model_path)


def load_model_bundle(model_path: Path = MODEL_PATH) -> dict:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}. Run train.py first."
        )

    bundle = joblib.load(model_path)
    if "model_target_cols" not in bundle:
        bundle["model_target_cols"] = get_model_target_cols(bundle["target_cols"])
    return bundle


def format_display_value(column: str, value: float) -> str:
    if column == "weather_code":
        return str(int(value))

    if column in {"sunrise", "sunset"}:
        return (
            pd.to_datetime(int(value), unit="s", utc=True)
            .tz_convert(LOCATION["timezone"])
            .strftime("%H:%M")
        )

    if column in {"daylight_duration", "sunshine_duration"}:
        return f"{value / 3600:.1f} h"

    if "temperature" in column or "apparent_temperature" in column:
        return f"{value:.1f}"

    if column in {"precipitation_sum", "rain_sum"}:
        return f"{value:.1f} mm"

    if column == "snowfall_sum":
        return f"{value:.1f} cm"

    if column == "precipitation_hours":
        return f"{value:.1f} h"

    if "wind_speed" in column or "wind_gusts" in column:
        return f"{value:.1f} km/h"

    if "direction" in column:
        return f"{int(round(value))} deg"

    if column == "shortwave_radiation_sum":
        return f"{value:.1f} MJ/m2"

    if column == "et0_fao_evapotranspiration":
        return f"{value:.2f} mm"

    return f"{value:.2f}"


def get_weather_info(code: int) -> dict[str, str]:
    code = int(np.clip(round(code), 0, 99))

    exact_labels = {
        0: ("☀️", "Clear"),
        1: ("🌤️", "Mainly clear"),
        2: ("🌤️", "Partly cloudy"),
        3: ("☁️", "Overcast"),
        4: ("🌫️", "Haze"),
        5: ("🌫️", "Haze"),
        6: ("🌪️", "Dust"),
        7: ("🌪️", "Dust whirls"),
        8: ("🌪️", "Tornado"),
        9: ("🌪️", "Dust storm"),
        10: ("🌫️", "Mist"),
        11: ("🌨️", "Ice pellets"),
        12: ("🌦️", "Drizzle"),
        13: ("🌨️", "Ice grains"),
        14: ("🌦️", "Precipitation"),
        15: ("🌨️", "Shower precipitation"),
        16: ("🌨️", "Shower precipitation"),
        17: ("⛈️", "Thunderstorm"),
        18: ("🌨️", "Shower precipitation"),
        19: ("🌨️", "Shower precipitation"),
        20: ("🌨️", "Precipitation"),
        21: ("🌨️", "Precipitation"),
        22: ("❄️", "Snow"),
        23: ("❄️", "Snow"),
        24: ("🌧️", "Sleet"),
        25: ("🌨️", "Shower precipitation"),
        26: ("🌨️", "Shower precipitation"),
        27: ("🌨️", "Shower precipitation"),
        28: ("🌨️", "Shower precipitation"),
        29: ("⛈️", "Thunderstorm with hail"),
        30: ("🌫️", "Dust haze"),
        31: ("🌫️", "Dust haze"),
        32: ("🌪️", "High wind"),
        33: ("🌪️", "High wind"),
        34: ("⛈️", "Heavy thunderstorm"),
        35: ("🌪️", "Dust storm"),
        36: ("🌨️", "Blowing snow"),
        37: ("🌪️", "High wind"),
        38: ("🌨️", "Blowing snow"),
        39: ("🌨️", "Blizzard"),
        40: ("🌫️", "Fog"),
        41: ("🌫️", "Fog"),
        42: ("🌫️", "Fog"),
        43: ("🌫️", "Fog"),
        44: ("🌫️", "Fog"),
        45: ("🌫️", "Fog"),
        46: ("🌫️", "Fog"),
        47: ("🌫️", "Fog"),
        48: ("🌫️", "Rime fog"),
        49: ("🌫️", "Fog"),
        51: ("🌦️", "Drizzle"),
        53: ("🌦️", "Drizzle"),
        55: ("🌦️", "Heavy drizzle"),
        56: ("🌧️", "Freezing drizzle"),
        57: ("🌧️", "Freezing drizzle"),
        61: ("🌧️", "Rain"),
        63: ("🌧️", "Rain"),
        65: ("🌧️", "Heavy rain"),
        66: ("🌧️", "Freezing rain"),
        67: ("🌧️", "Freezing rain"),
        71: ("❄️", "Snow"),
        73: ("❄️", "Snow"),
        75: ("❄️", "Heavy snow"),
        77: ("❄️", "Snow grains"),
        80: ("🌦️", "Rain shower"),
        81: ("🌦️", "Rain shower"),
        82: ("🌦️", "Heavy rain shower"),
        85: ("🌨️", "Snow shower"),
        86: ("🌨️", "Heavy snow shower"),
        95: ("⛈️", "Thunderstorm"),
        96: ("⛈️", "Thunderstorm with hail"),
        99: ("⛈️", "Thunderstorm with hail"),
    }

    if code in exact_labels:
        icon, label = exact_labels[code]
        return {"icon": icon, "label": label}

    decade = (code // 10) * 10
    range_labels = {
        0: ("🌤️", "Clear"),
        10: ("🌦️", "Precipitation"),
        20: ("🌧️", "Precipitation"),
        30: ("🌨️", "Blizzard"),
        40: ("🌫️", "Fog"),
        50: ("🌦️", "Drizzle"),
        60: ("🌧️", "Rain"),
        70: ("❄️", "Snow"),
        80: ("🌦️", "Rain shower"),
        90: ("⛈️", "Thunderstorm"),
    }
    icon, label = range_labels.get(decade, ("🌡️", "Mixed conditions"))
    return {"icon": icon, "label": label}


def wind_direction_label(degrees: float) -> str:
    index = int((degrees + 22.5) // 45) % 8
    return WIND_DIRECTIONS[index]


def format_forecast_table(
    forecast_df: pd.DataFrame,
    target_cols: list[str],
    forecast_start_date: pd.Timestamp,
) -> pd.DataFrame:
    day_columns = [
        (forecast_start_date + pd.Timedelta(days=day)).strftime("%d.%m.%Y")
        for day in range(len(forecast_df))
    ]

    display_data = {}
    for col in target_cols:
        label = PARAM_LABELS.get(col, col)
        display_data[label] = [
            format_display_value(col, forecast_df.iloc[day_idx][col])
            for day_idx in range(len(forecast_df))
        ]

    return pd.DataFrame(display_data, index=day_columns).T


def print_forecast_report(
    forecast_df: pd.DataFrame,
    target_cols: list[str],
    last_known_date: pd.Timestamp,
) -> None:
    forecast_start = last_known_date + pd.Timedelta(days=1)
    forecast_end = forecast_start + pd.Timedelta(days=len(forecast_df) - 1)
    display_table = format_forecast_table(forecast_df, target_cols, forecast_start)

    print("\n" + "=" * 72)
    print("=== 7-DAY WEATHER FORECAST ===")
    print("=" * 72)
    print(
        f"Period: {forecast_start.strftime('%d.%m.%Y')} - "
        f"{forecast_end.strftime('%d.%m.%Y')}"
    )
    print(f"Last known date in data: {last_known_date.strftime('%d.%m.%Y')}")
    print()
    print(display_table.to_string())


def build_forecast_response(
    forecast_df: pd.DataFrame,
    target_cols: list[str],
    last_known_date: pd.Timestamp,
) -> dict:
    forecast_start = last_known_date + pd.Timedelta(days=1)
    days = []

    for day_index in range(len(forecast_df)):
        date = forecast_start + pd.Timedelta(days=day_index)
        row = forecast_df.iloc[day_index]
        weather_code = int(row["weather_code"])
        weather = get_weather_info(weather_code)
        wind_degrees = float(row["wind_direction_10m_dominant"])

        days.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "date_display": date.strftime("%d.%m.%Y"),
                "weekday": int(date.weekday()),
                "weather_code": weather_code,
                "weather_icon": weather["icon"],
                "summary": {
                    "temperature_mean": round(float(row["temperature_2m_mean"]), 1),
                    "temperature_max": round(float(row["temperature_2m_max"]), 1),
                    "temperature_min": round(float(row["temperature_2m_min"]), 1),
                    "apparent_temperature_mean": round(float(row["apparent_temperature_mean"]), 1),
                    "precipitation_sum": round(float(row["precipitation_sum"]), 1),
                    "rain_sum": round(float(row["rain_sum"]), 1),
                    "snowfall_sum": round(float(row["snowfall_sum"]), 1),
                    "wind_speed_max": round(float(row["wind_speed_10m_max"]), 1),
                    "wind_gusts_max": round(float(row["wind_gusts_10m_max"]), 1),
                    "wind_direction": int(wind_degrees),
                    "sunrise": float(row["sunrise"]),
                    "sunset": float(row["sunset"]),
                },
                "details": [
                    {
                        "key": column,
                        "raw": float(row[column]),
                    }
                    for column in target_cols
                ],
            }
        )

    forecast_end = forecast_start + pd.Timedelta(days=len(forecast_df) - 1)
    return {
        "timezone": LOCATION["timezone"],
        "last_known_date": last_known_date.strftime("%Y-%m-%d"),
        "last_known_date_display": last_known_date.strftime("%d.%m.%Y"),
        "period_start": forecast_start.strftime("%Y-%m-%d"),
        "period_end": forecast_end.strftime("%Y-%m-%d"),
        "period_display": (
            f"{forecast_start.strftime('%d.%m.%Y')} - {forecast_end.strftime('%d.%m.%Y')}"
        ),
        "forecast_days": len(days),
        "days": days,
    }


def get_forecast() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_PATH}. Run whether_collector.py first."
        )

    model_bundle = load_model_bundle()
    df, target_cols, _ = load_merged_dataset()
    history_days = model_bundle.get("history_days", HISTORY_DAYS)
    latest_history = df.tail(history_days).copy()
    last_known_date = df["date"].max()
    forecast_start = last_known_date + pd.Timedelta(days=1)

    forecast_df = predict_next_week(latest_history, model_bundle)
    forecast_df = apply_computed_sun_times(forecast_df, forecast_start)

    return build_forecast_response(forecast_df, target_cols, last_known_date)


def train_and_save_model() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_PATH}. Run whether_collector.py first."
        )

    df, target_cols, feature_source_cols = load_merged_dataset()
    model_target_cols = get_model_target_cols(target_cols)
    df_features = create_features(df, feature_source_cols)
    feature_cols = [
        col
        for col in df_features.columns
        if "_lag_" in col or "_roll_" in col or col.endswith("_sin") or col.endswith("_cos")
    ]

    Y_df = build_target_matrix(df_features, model_target_cols)
    valid_rows = Y_df.notna().all(axis=1)
    X = df_features.loc[valid_rows, feature_cols]
    Y_df = Y_df.loc[valid_rows]

    model = MultiOutputRegressor(
        LGBMRegressor(
            n_estimators=100,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            n_jobs=1,
            verbose=-1,
        ),
        n_jobs=-1,
    )
    model.fit(X, Y_df)

    model_bundle = {
        "model": model,
        "feature_cols": feature_cols,
        "feature_source_cols": feature_source_cols,
        "model_target_cols": model_target_cols,
        "target_cols": target_cols,
        "target_names": list(Y_df.columns),
        "forecast_days": FORECAST_DAYS,
        "history_days": HISTORY_DAYS,
    }
    save_model_bundle(model_bundle)

    return {
        "model_path": str(MODEL_PATH),
        "rows": len(X),
        "features": len(feature_cols),
        "outputs": Y_df.shape[1],
        "target_cols": len(model_target_cols),
    }
