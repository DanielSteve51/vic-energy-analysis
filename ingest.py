import io
import os
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
FILE_NAME = "PRICE_AND_DEMAND_202610_VIC1.csv"
URL = f"https://aemo.com.au/aemo/data/nem/priceanddemand/{FILE_NAME}"
LOCAL_PATH = Path("data") / FILE_NAME


def extract() -> pd.DataFrame:
    """Download the CSV; fall back to a local copy if the download fails."""
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        print("Downloaded from AEMO")
        return pd.read_csv(io.StringIO(response.text))
    except requests.RequestException as e:
        print(f"Download failed ({e}). Trying local file...")
        if LOCAL_PATH.exists():
            return pd.read_csv(LOCAL_PATH)
        raise FileNotFoundError(
            f"No local file at {LOCAL_PATH}. Download the CSV manually from AEMO "
            "and save it there."
        )


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