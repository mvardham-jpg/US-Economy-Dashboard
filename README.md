<<<<<<< HEAD
# US Economic Dashboard

A clean, interactive Streamlit dashboard for key US macroeconomic indicators, powered by the [FRED API](https://fred.stlouisfed.org/) (Federal Reserve Economic Data) and Plotly.

![Dashboard Screenshot](screenshot.png)
*(Replace with an actual screenshot after running the app)*

---

## Features

- **4 KPI cards** — latest readings for GDP Growth, CPI, Unemployment, and Federal Funds Rate
- **Interactive time-series charts** — one per indicator with a drag-to-zoom range slider
- **Multi-indicator comparison** — overlay any two indicators on dual y-axes
- **NBER recession shading** — all charts shade the 2001, 2008, and 2020 recession periods
- **Local CSV caching** — data is fetched from FRED once and stored in `data/`; no re-fetch on every page load
- **Sidebar refresh** — one-click button to pull fresh data from FRED at any time

---

## Data Sources

| Indicator | FRED Series ID | Description |
|-----------|---------------|-------------|
| GDP Growth Rate | `A191RL1Q225SBEA` | Real GDP percent change from preceding period (quarterly, SAAR) |
| CPI Inflation | `CPIAUCSL` | Consumer Price Index for All Urban Consumers: All Items in U.S. City Average |
| Unemployment Rate | `UNRATE` | Civilian Unemployment Rate (monthly, seasonally adjusted) |
| Federal Funds Rate | `FEDFUNDS` | Effective Federal Funds Rate (monthly) |

All series are pulled from **January 2000** onward (25+ years).

Recession periods sourced from the [NBER Business Cycle Dating Committee](https://www.nber.org/research/business-cycle-dating).

---

## Project Structure

```
us-economic-dashboard/
├── app.py              # Streamlit entry point
├── src/
│   ├── __init__.py
│   ├── fetch.py        # FRED API calls + CSV caching
│   └── charts.py       # Reusable Plotly chart builders
├── data/               # Auto-generated CSV cache (gitignored)
│   └── .gitkeep
├── requirements.txt
├── .env.example        # Template — copy to .env and fill in your key
├── .gitignore
└── README.md
```

---

## Setup

### 1. Get a free FRED API key

Register at [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html). The key is free and instant.

### 2. Clone and install

```bash
git clone <your-repo-url>
cd us-economic-dashboard

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
# Open .env and replace the placeholder with your actual key:
# FRED_API_KEY=abcdef1234567890abcdef1234567890
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. On first load it fetches all series from FRED and saves them to `data/*.csv`. Subsequent loads use the cached files (< 1 second startup).

### 5. Refresh data

Click **Refresh Data** in the sidebar to clear the cache and re-fetch from FRED.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web app framework |
| `plotly` | Interactive charts |
| `fredapi` | FRED API client |
| `python-dotenv` | Load `.env` into environment |
| `pandas` | Data manipulation |
| `requests` | HTTP (required by fredapi) |

---

## Notes

- The `.env` file is listed in `.gitignore` and will never be committed.
- CSV files in `data/` are also gitignored — each user fetches their own copy.
- NBER recession dates are hardcoded (they are historical facts that rarely change).
=======
# US-Economy-Dashboard
>>>>>>> 50e6f2c2183e05e4af8c05af50ce04a716eed87c
