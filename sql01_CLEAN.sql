-- creating clean table from raw data
CREATE TABLE clean_price_demand AS
SELECT
    region,
    settlementdate,
    settlementdate - INTERVAL '5 minutes' AS interval_start,
    totaldemand AS demand_mw,
    rrp AS price_aud_mwh,
    rrp < 0   AS is_negative_price,
    rrp > 300 AS is_spike
FROM raw_price_demand;

ALTER TABLE clean_price_demand ADD PRIMARY KEY (region, settlementdate);
ALTER TABLE clean_price_demand ALTER COLUMN demand_mw SET NOT NULL;
ALTER TABLE clean_price_demand ALTER COLUMN price_aud_mwh SET NOT NULL;

Select * FROM clean_price_demand;