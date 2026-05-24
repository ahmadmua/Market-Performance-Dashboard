import yfinance as yf
import pandas as pd
import os

INDEXES = {
    "S&P 500":   "^GSPC",
    "Nasdaq 100": "^NDX",
    "Dow Jones":  "^DJI",
    "TSX":        "^GSPTSE",
}

START_DATE = "2019-01-01"
END_DATE   = "2024-12-31"
RAW_DIR    = "data/raw"

def fetch_index(name: str, ticker: str) -> pd.DataFrame:
    print(f"Fetching {name}...")
    df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]
    df.index.name = "date"
    df["index_name"] = name
    return df

def fetch_all():
    os.makedirs(RAW_DIR, exist_ok=True)
    for name, ticker in INDEXES.items():
        df = fetch_index(name, ticker)
        filename = name.replace(" ", "_").replace("/", "_") + ".csv"
        df.to_csv(f"{RAW_DIR}/{filename}")
        print(f"  Saved {len(df)} rows → {filename}")

if __name__ == "__main__":
    fetch_all()