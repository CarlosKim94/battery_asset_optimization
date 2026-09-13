from pathlib import Path

import pandas as pd


def load_prices(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])

    required_columns = {
        "timestamp",
        "price_eur_mwh",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df["price_eur_mwh"].isna().any():
        raise ValueError("Price data contains missing values.")

    df = df.sort_values("timestamp").reset_index(drop=True)

    return df