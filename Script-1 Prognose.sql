-- 1. Überblick: Prognosezeitraum in forecast_general_sales
SELECT MIN(ds) AS first_forecast, MAX(ds) AS last_forecast
FROM forecast_general_sales;

-- 2. Grundstatistik zur Prognose
SELECT
  COUNT(*) AS total_days,
  ROUND(MIN(yhat), 1) AS min_forecast,
  ROUND(MAX(yhat), 1) AS max_forecast,
  ROUND(AVG(yhat), 1) AS avg_forecast
FROM forecast_general_sales;

-- 3. Monatliche Mittelwerte der Prognose (forecast_general_sales)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_monthly AS
SELECT
  strftime('%Y-%m', ds) AS month,
  ROUND(AVG(yhat), 1) AS avg_forecast
FROM forecast_general_sales
GROUP BY month
ORDER BY month;

-- 4. Rolling Mean (7 Tage) – allgemeiner Forecast Summary
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_rolling7 AS
SELECT
  ds,
  ROUND(AVG(yhat) OVER (
    ORDER BY ds
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ), 1) AS rolling_7day_avg
FROM forecast_general_sales;

-- 5. Höchste prognostizierte Tage (Peaks)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_peaks AS
SELECT
  ds,
  ROUND(yhat, 1) AS forecast
FROM forecast_general_sales
ORDER BY yhat DESC
LIMIT 10;

-- 6. Vergleich der Produktprognosen (60 Tage)
CREATE VIEW IF NOT EXISTS view_forecast_products_60days AS
SELECT
  a.ds,
  ROUND(a.yhat, 1) AS product_a,
  ROUND(b.yhat, 1) AS product_b,
  ROUND(c.yhat, 1) AS product_c
FROM forecast_product_a a
JOIN forecast_product_b b ON a.ds = b.ds
JOIN forecast_product_c c ON a.ds = c.ds
WHERE a.ds BETWEEN DATE('now') AND DATE('now', '+60 days')
ORDER BY a.ds;


--II
-- 7. Produktanteile insgesamt (Forecast)
SELECT 'product_a' AS product, ROUND(AVG(yhat), 1) AS avg_forecast FROM forecast_product_a
UNION ALL
SELECT 'product_b', ROUND(AVG(yhat), 1) FROM forecast_product_b
UNION ALL
SELECT 'product_c', ROUND(AVG(yhat), 1) FROM forecast_product_c;


-- III

-- 8. Durchschnittlicher Forecast pro Region
SELECT 'Nord' AS region, ROUND(AVG(yhat), 1) AS avg_forecast FROM forecast_Region_Nord
UNION ALL
SELECT 'Mitte', ROUND(AVG(yhat), 1) FROM forecast_Region_Mitte
UNION ALL
SELECT 'Süd', ROUND(AVG(yhat), 1) FROM forecast_Region_Süd;


-- 9. Durchschnittlicher Forecast pro Segment
SELECT 'Automotive' AS segment, ROUND(AVG(yhat), 1) FROM forecast_Segment_Automotive
UNION ALL SELECT 'Retail', ROUND(AVG(yhat), 1) FROM forecast_Segment_Retail
UNION ALL SELECT 'Logistics', ROUND(AVG(yhat), 1) FROM forecast_Segment_Logistics
UNION ALL SELECT 'Healthcare', ROUND(AVG(yhat), 1) FROM forecast_Segment_Healthcare
UNION ALL SELECT 'Food & Beverage', ROUND(AVG(yhat), 1) FROM "forecast_Segment_Food_and_Beverage"
UNION ALL SELECT 'IT Services', ROUND(AVG(yhat), 1) FROM "forecast_Segment_IT_Services"
UNION ALL SELECT 'Manufacturing', ROUND(AVG(yhat), 1) FROM forecast_Segment_Manufacturing;


-- IV

-- 10. Kunden mit höchsten Prognosewerten
SELECT 'Kunde_002' AS customer, ROUND(AVG(yhat), 1) AS avg_forecast FROM "forecast_Kunde_Kunde_002"
UNION ALL SELECT 'Kunde_014', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_014"
UNION ALL SELECT 'Kunde_018', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_018"
UNION ALL SELECT 'Kunde_048', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_048"
UNION ALL SELECT 'Kunde_049', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_049"
UNION ALL SELECT 'Kunde_057', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_057"
UNION ALL SELECT 'Kunde_078', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_078"
UNION ALL SELECT 'Kunde_085', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_085"
UNION ALL SELECT 'Kunde_090', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_090"
UNION ALL SELECT 'Kunde_101', ROUND(AVG(yhat), 1) FROM "forecast_Kunde_Kunde_101"
ORDER BY avg_forecast DESC;


--V
-- 11. Forecast Confidence Spread (Uncertainty Range)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_spread AS
SELECT
  ds,
  ROUND(yhat_upper - yhat_lower, 1) AS forecast_spread
FROM forecast_general_sales
ORDER BY ds;


-- 12. Forecast Trend Over Time (Start vs. End Forecast)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_trend_summary AS
WITH first_last AS (
  SELECT
    (SELECT ds FROM forecast_general_sales ORDER BY ds ASC LIMIT 1) AS first_day,
    (SELECT ds FROM forecast_general_sales ORDER BY ds DESC LIMIT 1) AS last_day,
    (SELECT yhat FROM forecast_general_sales ORDER BY ds ASC LIMIT 1) AS first_forecast,
    (SELECT yhat FROM forecast_general_sales ORDER BY ds DESC LIMIT 1) AS last_forecast
)
SELECT
  first_day,
  last_day,
  ROUND(first_forecast, 1) AS first_forecast,
  ROUND(last_forecast, 1) AS last_forecast,
  ROUND(((last_forecast - first_forecast) / first_forecast) * 100, 1) AS total_growth_percent
FROM first_last;


-- 13. Monthly Growth Rate (Month-over-Month)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_monthly_growth AS
WITH monthly AS (
  SELECT strftime('%Y-%m', ds) AS month, AVG(yhat) AS avg_forecast
  FROM forecast_general_sales
  GROUP BY month
)
SELECT
  month,
  ROUND(avg_forecast, 1) AS current_avg,
  ROUND(LAG(avg_forecast) OVER (ORDER BY month), 1) AS previous_avg,
  ROUND(((avg_forecast - LAG(avg_forecast) OVER (ORDER BY month)) / LAG(avg_forecast) OVER (ORDER BY month)) * 100, 1) AS growth_percent
FROM monthly;


-- 14. Anomaly Detection (Spikes over Rolling 7-Day Avg)
CREATE VIEW IF NOT EXISTS view_forecast_general_sales_anomalies AS
SELECT
  ds,
  ROUND(yhat, 1) AS yhat,
  ROUND(AVG(yhat) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS rolling_avg,
  ROUND(yhat - AVG(yhat) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS deviation,
  CASE
    WHEN ABS(yhat - AVG(yhat) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)) > 100 THEN 'Spike'
    ELSE 'Normal'
  END AS anomaly_flag
FROM forecast_general_sales;

-- VI

-- 15. Monthly forecast per customer (example: Kunde_002)
SELECT
  strftime('%Y-%m', ds) AS month,
  ROUND(AVG(yhat), 1) AS avg_forecast,
  'Kunde_002' AS customer
FROM forecast_Kunde_Kunde_002
GROUP BY month
