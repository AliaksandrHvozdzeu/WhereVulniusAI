import sys

import pandas as pd

from forecast_service import (
    DATA_PATH,
    apply_computed_sun_times,
    load_merged_dataset,
    load_model_bundle,
    predict_next_week,
    print_forecast_report,
    train_and_save_model,
)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    print("Loading data...")
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_PATH}. Run whether_collector.py first."
        )

    df, target_cols, feature_source_cols = load_merged_dataset()
    print(f"Daily parameters (targets): {len(target_cols)}")
    print(f"Hourly parameters (features): {len(feature_source_cols) - len(target_cols)}")
    print(f"Total Excel parameters in training: {len(feature_source_cols)}")

    print("Building features and training...")
    stats = train_and_save_model()
    print(f"Training set size: {stats['rows']} rows, {stats['features']} features")
    print(f"Output count: {stats['outputs']} ({stats['target_cols']} x 7)")
    print(f"Model saved: {stats['model_path']}")

    model_bundle = load_model_bundle()
    latest_history = df.tail(model_bundle["history_days"]).copy()
    last_known_date = df["date"].max()
    forecast_start = last_known_date + pd.Timedelta(days=1)

    future_forecast = predict_next_week(latest_history, model_bundle)
    future_forecast = apply_computed_sun_times(future_forecast, forecast_start)
    print_forecast_report(future_forecast, target_cols, last_known_date)


if __name__ == "__main__":
    main()
