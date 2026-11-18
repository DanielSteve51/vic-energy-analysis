SELECT d.season, t.time_band,
       ROUND(AVG(f.price_aud_mwh)::numeric, 2) AS avg_price,
       ROUND(100.0 * AVG(f.is_negative_price::int), 1) AS pct_negative
FROM fact_price_demand f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY d.season, t.time_band
ORDER BY d.season, t.time_band;