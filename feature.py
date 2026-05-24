import pandas as pd
import numpy as np
import os

PROCESSED_DIR = "data/processed"

def compute_features(df: pd.DataFrame) -> pd.DataFrame:

    # Daily return
    df["daily_return"] = df["close"].pct_change()

    # Simple moving averages
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()

    # Rolling volatility (std of daily returns)
    df["volatility_7d"]  = df["daily_return"].rolling(window=7).std()
    df["volatility_30d"] = df["daily_return"].rolling(window=30).std()

    # RSI (14-period)
    df["rsi"] = compute_rsi(df["close"], period=14)

    # RSI signal flag
    df["rsi_signal"] = df["rsi"].apply(
        lambda x: "Overbought" if x > 70 else ("Oversold" if x < 30 else "Neutral")
        if pd.notna(x) else None
    )

    # Drop rows with insufficient lookback (first 50 rows)
    df.dropna(subset=["sma_50"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def engineer_all():
    for file in os.listdir(PROCESSED_DIR):
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(f"{PROCESSED_DIR}/{file}", parse_dates=["date"])
        df = compute_features(df)
        df.to_csv(f"{PROCESSED_DIR}/{file}", index=False)
        print(f"Features added → {file} ({len(df)} rows, {df.columns.tolist()})")

if __name__ == "__main__":
    engineer_all()