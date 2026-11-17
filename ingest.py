import pandas as pd
from sqlalchemy import create_engine

url = "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_202610_VIC1.csv"
df = pd.read_csv(url)
df.columns = [c.lower() for c in df.columns]
df["settlementdate"] = pd.to_datetime(df["settlementdate"])

engine = create_engine("postgresql://postgres:dev@localhost:5432/postgres")
df.to_sql("raw_price_demand", engine, if_exists="replace", index=False)
print(len(df), "rows loaded")