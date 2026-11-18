import io
import os
import time
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- Config from .env ---
load_dotenv()
DB_UNAME = os.getenv("DB_UNAME")
DB_PWD = quote_plus(os.getenv("DB_PWD"))
DB_URL = os.getenv("DB_URL")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_UNAME}:{DB_PWD}@{DB_URL}:{DB_PORT}/{DB_NAME}"
)

# --- Extract ---
START, END = "2024-11", "2026-10"
HEADERS = {"User-Agent": "vic-energy-analytics (personal portfolio project)"}


def extract_month(yyyymm: str) -> pd.DataFrame:
    file_name = f"PRICE_AND_DEMAND_{yyyymm}_VIC1.csv"
    local_path = Path("data") / file_name

    if local_path.exists():                      # cache: don't re-download
        return pd.read_csv(local_path)

    url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/{file_name}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    local_path.parent.mkdir(exist_ok=True)       # create data/ if missing
    local_path.write_text(response.text)         # save a copy
    time.sleep(1)                                # be polite to the server
    return pd.read_csv(io.StringIO(response.text))


def extract() -> pd.DataFrame:
    frames = []
    for m in pd.period_range(START, END, freq="M"):
        yyyymm = m.strftime("%Y%m")
        try:
            frames.append(extract_month(yyyymm))
            print(f"{yyyymm}: ok")
        except requests.RequestException as e:
            print(f"{yyyymm}: skipped ({e})")
    return pd.concat(frames, ignore_index=True)

# --- Transform (light cleaning only; heavy work happens in SQL) ---
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower() for c in df.columns]
    df["settlementdate"] = pd.to_datetime(df["settlementdate"])
    return df


# --- Load ---
def load(df: pd.DataFrame) -> None:
    df.to_sql("raw_price_demand", engine, if_exists="replace", index=False)
    print(f"{len(df)} rows loaded into raw_price_demand")


if __name__ == "__main__":
    data = extract()
    data = transform(data)
    load(data)