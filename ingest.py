import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()  # reads the .env file into environment variables

DB_UNAME = os.getenv("DB_UNAME")
DB_PWD = quote_plus(os.getenv("DB_PWD"))
DB_URL = os.getenv("DB_URL")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql://{DB_UNAME}:{DB_PWD}@{DB_URL}:{DB_PORT}/{DB_NAME}"
)

url = "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_202610_VIC1.csv"
df = pd.read_csv(url)
df.columns = [c.lower() for c in df.columns]
df["settlementdate"] = pd.to_datetime(df["settlementdate"])

df.to_sql("raw_price_demand", engine, if_exists="replace", index=False)
print(len(df), "rows loaded")