-- Database: Stock_Index
-- Tables: indexes, daily_ohlcv, technical_indicators


-- 1. Most volatile indexes by month (30D volatility)
SELECT
    i.index_name,
    DATE_TRUNC('month', ti.date)              AS month,
    ROUND(AVG(ti.volatility_30d)::NUMERIC, 5) AS avg_volatility
FROM technical_indicators ti
JOIN indexes i ON i.index_id = ti.index_id
GROUP BY i.index_name, month
ORDER BY month, avg_volatility DESC;


-- 2. Cross-index return correlation (all pair combinations)
SELECT
    ia.index_name                                              AS index_a,
    ib.index_name                                              AS index_b,
    ROUND(CORR(a.daily_return, b.daily_return)::NUMERIC, 4)   AS correlation
FROM technical_indicators a
JOIN technical_indicators b ON a.date = b.date
JOIN indexes ia              ON ia.index_id = a.index_id
JOIN indexes ib              ON ib.index_id = b.index_id
WHERE ia.index_name < ib.index_name
GROUP BY ia.index_name, ib.index_name
ORDER BY correlation DESC;


-- 3. RSI crossover events (overbought / oversold only)
SELECT
    i.index_name,
    ti.date,
    ROUND(ti.rsi::NUMERIC, 2) AS rsi,
    ti.rsi_signal
FROM technical_indicators ti
JOIN indexes i ON i.index_id = ti.index_id
WHERE ti.rsi_signal IN ('Overbought', 'Oversold')
ORDER BY ti.date DESC;


-- 4. 20-day rolling average close price (window function)
SELECT
    i.index_name,
    o.date,
    o.close,
    ROUND(AVG(o.close) OVER (
        PARTITION BY o.index_id
        ORDER BY o.date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    )::NUMERIC, 2) AS rolling_avg_20d
FROM daily_ohlcv o
JOIN indexes i ON i.index_id = o.index_id
ORDER BY i.index_name, o.date;


-- 5. Month-over-month return change using LAG
SELECT
    i.index_name,
    month,
    ROUND(avg_monthly_return::NUMERIC, 5)        AS avg_monthly_return,
    ROUND(
        (avg_monthly_return - LAG(avg_monthly_return)
            OVER (PARTITION BY i.index_name ORDER BY month)
        )::NUMERIC, 5
    )                                             AS mom_change
FROM (
    SELECT
        index_id,
        DATE_TRUNC('month', date) AS month,
        AVG(daily_return)         AS avg_monthly_return
    FROM technical_indicators
    GROUP BY index_id, month
) monthly
JOIN indexes i ON i.index_id = monthly.index_id
ORDER BY i.index_name, month;


-- 6. Rank indexes by average 30D volatility (all time)
SELECT
    i.index_name,
    ROUND(AVG(ti.volatility_30d)::NUMERIC, 5)          AS avg_volatility,
    RANK() OVER (ORDER BY AVG(ti.volatility_30d) DESC) AS volatility_rank
FROM technical_indicators ti
JOIN indexes i ON i.index_id = ti.index_id
GROUP BY i.index_name
ORDER BY volatility_rank;


-- 7. Maximum drawdown periods per index
WITH running_max AS (
    SELECT
        i.index_name,
        o.date,
        o.close,
        MAX(o.close) OVER (
            PARTITION BY o.index_id
            ORDER BY o.date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS peak_close
    FROM daily_ohlcv o
    JOIN indexes i ON i.index_id = o.index_id
)
SELECT
    index_name,
    date,
    ROUND(close::NUMERIC, 2)                                      AS close,
    ROUND(peak_close::NUMERIC, 2)                                 AS peak_close,
    ROUND(((close - peak_close) / peak_close * 100)::NUMERIC, 2) AS drawdown_pct
FROM running_max
ORDER BY drawdown_pct ASC
LIMIT 20;


-- 8. RSI signal count per index per year
SELECT
    i.index_name,
    EXTRACT(YEAR FROM ti.date)::INT AS year,
    ti.rsi_signal,
    COUNT(*)                        AS signal_count
FROM technical_indicators ti
JOIN indexes i ON i.index_id = ti.index_id
WHERE ti.rsi_signal IN ('Overbought', 'Oversold')
GROUP BY i.index_name, year, ti.rsi_signal
ORDER BY i.index_name, year, ti.rsi_signal;