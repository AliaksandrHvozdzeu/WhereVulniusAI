import openmeteo_requests
import pandas as pd
import requests_cache
from pathlib import Path
from retry_requests import retry

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snow_depth",
    "snowfall",
    "weather_code",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "et0_fao_evapotranspiration",
    "vapour_pressure_deficit",
    "wind_gusts_10m",
    "wind_direction_100m",
    "wind_direction_10m",
    "wind_speed_100m",
    "wind_speed_10m",
    "soil_temperature_0_to_7cm",
    "soil_temperature_7_to_28cm",
    "soil_temperature_28_to_100cm",
    "soil_temperature_100_to_255cm",
    "soil_moisture_0_to_7cm",
    "soil_moisture_7_to_28cm",
    "soil_moisture_28_to_100cm",
    "soil_moisture_100_to_255cm",
]

DAILY_VARS = [
    "weather_code",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "precipitation_hours",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
]

DAILY_INT64_VARS = {"sunrise", "sunset"}

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2016-07-12",
    "end_date": "2026-07-12",
    "daily": DAILY_VARS,
    "hourly": HOURLY_VARS,
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

hourly = response.Hourly()
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )
}
for index, var in enumerate(HOURLY_VARS):
    hourly_data[var] = hourly.Variables(index).ValuesAsNumpy()

hourly_dataframe = pd.DataFrame(data=hourly_data)
print("\nHourly data\n", hourly_dataframe)

daily = response.Daily()
daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )
}
for index, var in enumerate(DAILY_VARS):
    variable = daily.Variables(index)
    if var in DAILY_INT64_VARS:
        daily_data[var] = variable.ValuesInt64AsNumpy()
    else:
        daily_data[var] = variable.ValuesAsNumpy()

daily_dataframe = pd.DataFrame(data=daily_data)
print("\nDaily data\n", daily_dataframe)

def _excel_safe(df: pd.DataFrame) -> pd.DataFrame:
    export_df = df.copy()
    if pd.api.types.is_datetime64_any_dtype(export_df["date"]):
        export_df["date"] = export_df["date"].dt.tz_localize(None)
    return export_df


data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)

output_path = data_dir / "weather_data.xlsx"
legacy_csv_files = (data_dir / "hourly_data.csv", data_dir / "daily_data.csv")

if output_path.exists():
    output_path.unlink()
for legacy_path in legacy_csv_files:
    if legacy_path.exists():
        legacy_path.unlink()

with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
    _excel_safe(hourly_dataframe).to_excel(writer, sheet_name="hourly", index=False)
    _excel_safe(daily_dataframe).to_excel(writer, sheet_name="daily", index=False)

print(f"Saved data to {output_path}")
