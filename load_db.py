import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = "postgresql://postgres:root@localhost:5432/Stock_Index" # postgresql://user:pass@localhost:5432/index_db
PROCESSED_DIR = "data/processed"

INDEX_META = {
    "S&P_500":    ("US", "Large Cap"),
    "Nasdaq_100": ("US", "Technology"),
    "Dow_Jones":  ("US", "Blue Chip"),
    "TSX":        ("CA", "Broad Market"),
}


def get_or_create_index(conn, index_name: str, country: str, category: str) -> int:
    result = conn.execute(
        text("SELECT index_id FROM indexes WHERE index_name = :name"),
        {"name": index_name}
    ).fetchone()
    if result:
        return result[0]
    result = conn.execute(
        text("""
            INSERT INTO indexes (index_name, country, category)
            VALUES (:name, :country, :category)
            RETURNING index_id
        """),
        {"name": index_name, "country": country, "category": category}
    ).fetchone()
    return result[0]


def load_index(conn, filepath: str, file_key: str):
    # Derive display name from file key e.g. S&P_500 → S&P 500
    index_name = file_key.replace("_", " ").replace("S P", "S&P").replace("Nasdaq 100", "Nasdaq 100")

    # Match against INDEX_META keys
    meta_key = file_key  # e.g. "S&P_500"
    if meta_key not in INDEX_META:
        print(f"  Skipping unknown index key: {meta_key}")
        return

    country, category = INDEX_META[meta_key]
    index_id = get_or_create_index(conn, index_name, country, category)

    df = pd.read_csv(filepath, parse_dates=["date"])
    df["index_id"] = index_id

    # Load OHLCV
    ohlcv_cols = ["index_id", "date", "open", "high", "low", "close", "volume"]
    df[ohlcv_cols].to_sql(
        "daily_ohlcv", conn,
        if_exists="append", index=False,
        method="multi"
    )

    # Load indicators
    indicator_cols = [
        "index_id", "date", "daily_return",
        "sma_20", "sma_50",
        "volatility_7d", "volatility_30d",
        "rsi", "rsi_signal"
    ]
    df[indicator_cols].to_sql(
        "technical_indicators", conn,
        if_exists="append", index=False,
        method="multi"
    )
    print(f"Loaded {len(df)} rows for {index_name}")


def load_all():
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        for file in os.listdir(PROCESSED_DIR):
            if not file.endswith(".csv"):
                continue
            file_key = file.replace(".csv", "")
            load_index(conn, f"{PROCESSED_DIR}/{file}", file_key)


if __name__ == "__main__":
    load_all()
