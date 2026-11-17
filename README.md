# Victorian Energy Price and Demand Analytics

An automated pipeline that ingests AEMO electricity data into Postgres,
models it into a star schema with SQL, and serves a Power BI dashboard.

## Business questions
1. When does Victorian demand peak, and how do prices behave around those peaks?
2. How often do prices spike above a threshold, and at what times of day?
3. How do weekday and weekend patterns differ?
4. How have prices and demand trended month over month?