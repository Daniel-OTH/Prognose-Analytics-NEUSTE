-- =================================================================
-- 0. Prüfe Version und Erweiterungen
-- =================================================================
SELECT sqlite_version() AS sqlite_version;

-- =================================================================
-- I.    Deskriptive Analyse der Zeitreihen (sales_products)
-- =================================================================

-- 1. Überblick: erste/letzte Zeile & Null-Counts
SELECT * FROM sales_products ORDER BY timestamp        LIMIT 1;
SELECT * FROM sales_products ORDER BY timestamp DESC   LIMIT 1;

SELECT
  SUM(CASE WHEN amount    IS NULL THEN 1 ELSE 0 END) AS null_amount,
  SUM(CASE WHEN product_a IS NULL THEN 1 ELSE 0 END) AS null_a,
  SUM(CASE WHEN product_b IS NULL THEN 1 ELSE 0 END) AS null_b,
  SUM(CASE WHEN product_c IS NULL THEN 1 ELSE 0 END) AS null_c
FROM sales_products;

-- 2. Basisstatistik (Count, Min, Max, Avg) pro Spalte
SELECT
  COUNT(*)           AS cnt_amount,
  MIN(amount)        AS min_amount,
  MAX(amount)        AS max_amount,
  ROUND(AVG(amount),2) AS avg_amount
FROM sales_products;

SELECT
  MIN(product_a)     AS min_a, MAX(product_a) AS max_a, ROUND(AVG(product_a),2) AS avg_a
FROM sales_products;
-- analog für product_b und product_c

-- 3. Boxplot-Quartile (approx) für amount
WITH ordered AS (
  SELECT amount,
         ROW_NUMBER() OVER (ORDER BY amount) AS rn,
         COUNT(*)        OVER ()            AS tot
  FROM sales_products
)
SELECT
  MIN(amount) AS min,
  MAX(amount) AS max,
  AVG(amount) FILTER(WHERE rn BETWEEN tot*0.25 AND tot*0.25+1) AS q1,
  AVG(amount) FILTER(WHERE rn BETWEEN tot*0.50 AND tot*0.50+1) AS median,
  AVG(amount) FILTER(WHERE rn BETWEEN tot*0.75 AND tot*0.75+1) AS q3
FROM ordered;

-- 4. Monatliche & wöchentliche Aggregation (amount)
SELECT
  strftime('%Y-%m', timestamp) AS month,
  SUM(amount)                  AS sum_amount
FROM sales_products
GROUP BY month
ORDER BY month;

SELECT
  strftime('%Y-%W', timestamp) AS year_week,
  SUM(amount)                  AS sum_amount
FROM sales_products
GROUP BY year_week
ORDER BY year_week;

-- 5. Produkt-Zeitreihen pro Monat
SELECT
  strftime('%Y-%m', timestamp)        AS month,
  SUM(product_a) AS sum_a,
  SUM(product_b) AS sum_b,
  SUM(product_c) AS sum_c
FROM sales_products
GROUP BY month
ORDER BY month;

-- 6. Produkt-Anteile gesamt, letztes Jahr, letzter Monat
SELECT 'gesamt' AS periode, product, SUM(units) AS total_units
FROM (
  SELECT 'product_a' AS product, product_a AS units FROM sales_products
  UNION ALL
  SELECT 'product_b', product_b FROM sales_products
  UNION ALL
  SELECT 'product_c', product_c FROM sales_products
)
GROUP BY product
UNION ALL
SELECT 'letztes_jahr', product, SUM(units) FROM (
  SELECT * FROM (
    SELECT 'product_a' AS product, product_a AS units, timestamp FROM sales_products
    UNION ALL
    SELECT 'product_b', product_b, timestamp FROM sales_products
    UNION ALL
    SELECT 'product_c', product_c, timestamp FROM sales_products
  )
  WHERE timestamp >= date((SELECT MAX(timestamp) FROM sales_products), '-1 year')
)
GROUP BY product
UNION ALL
SELECT 'letzter_monat', product, SUM(units) FROM (
  SELECT 'product_a' AS product, product_a AS units, timestamp FROM sales_products
  UNION ALL
  SELECT 'product_b', product_b, timestamp FROM sales_products
  UNION ALL
  SELECT 'product_c', product_c, timestamp FROM sales_products
)
WHERE timestamp >= date((SELECT MAX(timestamp) FROM sales_products), '-1 month')
GROUP BY product;

-- 7. Rolling Mean 30-Tage (Beispiel für amount; echte Rolling-Window)
SELECT
  timestamp,
  ROUND(AVG(amount) OVER (
    ORDER BY timestamp
    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
  ),2) AS rolling_mean_30
FROM sales_products
LIMIT 10;

-- 8. Ausreißer-Heuristik: Top-20 Verkaufstage (amount)
SELECT
  date(timestamp) AS day,
  SUM(amount)     AS total_amount
FROM sales_products
GROUP BY day
ORDER BY total_amount DESC
LIMIT 20;

-- 9. Wochentagsanalyse (amount)
SELECT
  CASE strftime('%w', timestamp)
    WHEN '0' THEN 'So' WHEN '1' THEN 'Mo' WHEN '2' THEN 'Di'
    WHEN '3' THEN 'Mi' WHEN '4' THEN 'Do' WHEN '5' THEN 'Fr'
    WHEN '6' THEN 'Sa'
  END AS weekday,
  ROUND(AVG(amount),2) AS avg_amount
FROM sales_products
GROUP BY weekday
ORDER BY instr('SoMoDiMiDoFrSa', weekday);

-- 10. Autokorrelation-Alternative: Lag-1-Korrelation (amount)
SELECT
  ROUND(
    (SUM((a.amount - m.avg)*(b.amount - m.avg)) ) /
    (SUM((a.amount - m.avg)*(a.amount - m.avg))),
    2
  ) AS lag1_corr
FROM sales_products AS a
JOIN sales_products AS b
  ON b.rowid = a.rowid + 1
CROSS JOIN (
  SELECT AVG(amount) AS avg FROM sales_products
) AS m;

------------------------------------------------------------
-- II.   Kundenbezogene Analyse (sales_multi + customer)
------------------------------------------------------------

-- 11. Verkaufsvolumen pro Region
SELECT
  c.region,
  SUM(s.units) AS total_units
FROM sales_multi AS s
JOIN customer AS c USING(customer_id)
GROUP BY c.region
ORDER BY total_units DESC;

-- 12. Ø Verkaufseinheiten pro Kunde je Region
SELECT
  c.region,
  ROUND(AVG(s.units),2) AS avg_units_per_customer
FROM sales_multi AS s
JOIN customer AS c USING(customer_id)
GROUP BY c.region;

-- 13. Verkaufsvolumen pro Branche (Top-10)
SELECT
  c.branch,
  SUM(s.units) AS total_units
FROM sales_multi AS s
JOIN customer AS c USING(customer_id)
GROUP BY c.branch
ORDER BY total_units DESC
LIMIT 10;

-- 14. Monatliche Aggregation (sales_multi)
SELECT
  strftime('%Y-%m', date) AS month,
  SUM(units)              AS total_units
FROM sales_multi
GROUP BY month
ORDER BY month;

-- 15. Wöchentliche Aggregation (sales_multi)
SELECT
  strftime('%Y-%W', date) AS year_week,
  SUM(units)              AS total_units
FROM sales_multi
GROUP BY year_week
ORDER BY year_week;

-- 16. Top-20 Kunden nach Gesamtverkauf
SELECT
  s.customer_id,
  c.employees,
  SUM(s.units) AS total_units
FROM sales_multi AS s
JOIN customer     AS c USING(customer_id)
GROUP BY s.customer_id
ORDER BY total_units DESC
LIMIT 20;

-- 17. Mitarbeiterzahl vs. Verkaufseinheiten (Vorbereitung für Korrelations­berechnung)
CREATE TEMP VIEW v_cust_sales AS
SELECT
  s.customer_id,
  c.employees,
  SUM(s.units) AS total_units
FROM sales_multi AS s
JOIN customer     AS c USING(customer_id)
GROUP BY s.customer_id;

SELECT * FROM v_cust_sales ORDER BY total_units DESC;
