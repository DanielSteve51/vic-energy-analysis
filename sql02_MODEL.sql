-- Date dimension : one row per day as in raw data
CREATE TABLE dim_date AS
SELECT
	TO_CHAR(d,'YYYYMMDD') :: INT AS date_key,
	d:: date AS full_date,
	EXTRACT(YEAR FROM d) :: INT AS year,
	EXTRACT(MONTH FROM d) :: INT AS month,
	TO_CHAR(d,'Mon') AS month_name,
	To_CHAR(d,'Dy') AS day_name,
	EXTRACT(DOW FROM d) :: INT IN (6,0) AS is_weekend,
	CASE
		WHEN EXTRACT(MONTH FROM d) IN (12,1,2) THEN 'Summer'
		WHEN EXTRACT(MONTH FROM d) IN (3,4,5) THEN 'Autumn'
		WHEN EXTRACT(MONTH FROM d) IN (6,7,8) THEN 'Winter'
		ELSE 'Spring'
	END AS season
FROM generate_series(
	(SELECT MIN(interval_start)::date FROM clean_price_demand) :: timestamp,
	(SELECT MAX(interval_start)::date FROM clean_price_demand) :: timestamp,
	INTERVAL '1 day'
) AS g(d);


--Time dimension: 5 minute slots throughout the day, so 288 rows
CREATE TABLE dim_time AS
SELECT
	(EXTRACT(HOUR FROM t) * 100 + EXTRACT(MINUTE FROM t)) :: INT AS time_key,
	t:: time AS slot_start,
	EXTRACT(HOUR FROM t)::INT AS hour,
	EXTRACT(MINUTE FROM t)::INT AS minute,
	CASE
		WHEN EXTRACT(HOUR FROM t) < 6 THEN 'Overnight'
		WHEN EXTRACT(HOUR FROM t) < 11 THEN 'Morning'
		WHEN EXTRACT(HOUR FROM t) < 16 THEN 'Midday'
		WHEN EXTRACT(HOUR FROM t) < 21 THEN 'Evening'
		ELSE 'Late Night'
	END AS time_band
FROM generate_series(
	'2000-01-01 00:00' :: timestamp,
	'2000-01-01 23:55' :: timestamp,
	INTERVAL '5 minutes'
) AS g(t);


-- Fact table
CREATE TABLE fact_price_demand AS
SELECT
	region,
	TO_CHAR(interval_start, 'YYYYMMDD')::INT AS date_key,
	(EXTRACT(HOUR FROM interval_start)*100
	+ EXTRACT(MINUTE FROM interval_start)):: INT AS time_key,
	interval_start,
	demand_mw,
	price_aud_mwh,
	is_negative_price,
	is_spike
FROM clean_price_demand;


-- Keys and constraints
ALTER TABLE dim_date ADD PRIMARY KEY (date_key);
ALTER TABLE dim_time ADD PRIMARY KEY (time_key);
ALTER TABLE fact_price_demand ADD PRIMARY KEY(region,interval_start);
ALTER TABLE fact_price_demand  ADD FOREIGN KEY (date_key) REFERENCES dim_date(date_key);
ALTER TABLE fact_price_demand  ADD FOREIGN KEY (time_key) REFERENCES dim_time(time_key);

--Checking load
SELECT COUNT(*) FROM fact_price_demand;   -- 210240
SELECT COUNT(*) FROM dim_date;            -- 730
SELECT COUNT(*) FROM dim_time;            -- 288

--Additional Column
ALTER TABLE dim_date
ADD day_sort INT;

UPDATE dim_date
SET day_sort =
	CASE day_name
		WHEN 'Mon' THEN 1
		WHEN 'Tue' THEN 2
		WHEN 'Wed' THEN 3
		WHEN 'Thu' THEN 4
		WHEN 'Fri' THEN 5
		WHEN 'Sat' THEN 6
		WHEN 'Sun' THEN 7
	END;