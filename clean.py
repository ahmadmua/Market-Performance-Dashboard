import pandas as pd
import os

RAW_DIR       = "data/raw"
PROCESSED_DIR = "data/processed"

def clean_pair(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"], index_col="date")

    # Drop rows where all OHLC values are missing
    df.dropna(subset=["open", "high", "low", "close"], how="all", inplace=True)

    # Forward-fill any remaining gaps (e.g. isolated missing days)
    df[["open", "high", "low", "close"]] = (
        df[["open", "high", "low", "close"]].ffill()
    )

    # Remove weekends (forex closes Friday, yfinance sometimes includes them)
    df = df[df.index.dayofweek < 5]

    # Ensure correct dtypes
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    df["volume"] = df["volume"].fillna(0).astype(int)

    # Reset index for clean export
    df.reset_index(inplace=True)
    return df

def clean_all():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    for file in os.listdir(RAW_DIR):
        if not file.endswith(".csv"):
            continue
        df = clean_pair(f"{RAW_DIR}/{file}")
        df.to_csv(f"{PROCESSED_DIR}/{file}", index=False)
        print(f"Cleaned {file} → {len(df)} rows")

if __name__ == "__main__":
    clean_all()