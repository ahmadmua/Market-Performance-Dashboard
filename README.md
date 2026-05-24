# Market Performance Dashboard
### Comparative Analysis of Major Market Indices

End-to-end equity market analysis of 4 major indexes (S&P 500, Nasdaq 100, Dow Jones, TSX Composite) covering 6 years of daily data (2019–2024), built across Python, PostgreSQL, Excel, and Power BI.

---

## Dashboard Preview

<img width="1279" height="900" alt="dashboard" src="https://github.com/user-attachments/assets/0c053412-b885-449c-9184-148d13df862b" />

---

## Tools & Technologies

| Layer | Tools |
|---|---|
| Data ingestion | Python, yfinance |
| Data cleaning | Python, Pandas |
| Feature engineering | Python, Pandas, NumPy |
| Storage | PostgreSQL |
| Analysis | SQL (window functions) |
| Reporting | Excel, openpyxl |
| Visualization | Power BI, DAX |

---

## Data Pipeline

```
yfinance API
     ↓
grab_data.py  →  data/raw/
     ↓
clean.py      →  data/processed/
     ↓
feature.py    →  adds SMA, RSI, volatility, daily return columns
     ↓
load_db.py       →  PostgreSQL (indexes, daily_ohlcv, technical_indicators)
     ↓
export_excel.py  →  formatted Excel report (5 sheets)
     ↓
Power BI         →  dashboard
```

---

## Technical Indicators Engineered

| Indicator | Description |
|---|---|
| `daily_return` | Day-over-day percentage change in close price |
| `sma_20` | 20-day simple moving average |
| `sma_50` | 50-day simple moving average |
| `volatility_7d` | 7-day rolling standard deviation of daily returns |
| `volatility_30d` | 30-day rolling standard deviation of daily returns |
| `rsi` | 14-period Relative Strength Index |
| `rsi_signal` | Overbought / Oversold / Neutral classification |

---

## SQL Queries

8 analytical queries written against the PostgreSQL schema:

- Most volatile indexes by month
- Cross-index return correlation
- RSI crossover events (overbought / oversold)
- 20-day rolling average close using `AVG OVER`
- Month-over-month return change using `LAG`
- Volatility ranking using `RANK OVER`
- Max drawdown periods using `MAX OVER` with unbounded preceding frame
- RSI signal count per index per year

---

## Excel Report

Formatted workbook generated via `export_excel.py` using openpyxl, pulling directly from PostgreSQL:

| Sheet | Contents |
|---|---|
| Monthly Summary | Avg volatility and avg daily return per index per month |
| Volatility Heatmap | Index × month pivot with blue color scale |
| RSI Signals | All overbought / oversold events with red/green row formatting |
| Pair Correlation | Cross-index return correlation table |
| Drawdown Analysis | Worst drawdown events with >10% drawdown highlighted |

---

## Power BI Dashboard

Single-page dashboard with index and time period slicers (1Y, 5Y, 6M, YTD).

**KPI Cards**
| Metric | Value |
|---|---|
| Avg Daily Return | 0.054% |
| Volatility | 1.307% |
| CAGR | 12.06% |
| Sharpe Ratio | 0.49 |
| Max Drawdown | -37.43% |

**Visuals**
- Close price performance — multi-line chart for all 4 indexes (2019–2024)
- Correlation matrix — cross-index return correlation with color scale
- Rolling 30-day volatility — volatility regime chart with 2022 spike visible
- Drawdown over time — peak-to-trough area chart per index
- Monthly return heatmap — year × month grid with red/green conditional formatting
- Daily return distribution (5Y) — histogram across all indexes

**DAX Measures**
- `Avg Daily Return` — average of daily return column
- `Volatility` — standard deviation of daily returns annualised
- `CAGR` — compound annual growth rate over selected period
- `Sharpe Ratio` — avg return divided by std of returns
- `Max Drawdown %` — running peak-to-trough using `FILTER + ALL`

---

## Key Findings

- **Dow Jones and S&P 500 share the highest correlation at 0.95** — moving nearly in lockstep across the 6-year period
- **Nasdaq and TSX are the least correlated at 0.70** — TSX's commodity-driven composition diverges from US tech
- **March 2020 was the worst single month** — S&P 500 dropped -16.36% during the COVID crash
- **2022 was the worst full year** — rate hike cycle drove sustained negative monthly returns across all indexes
- **Volatility spiked sharply in 2022** — visible as a clear peak in the rolling 30-day volatility chart
- **Max drawdown reached -37.43%** — reflecting the combined COVID crash and 2022 bear market over the full period

---
