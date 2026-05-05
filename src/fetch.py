import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"

SERIES_IDS = {
    "gdp_growth": "A191RL1Q225SBEA",
    "cpi": "CPIAUCSL",
    "unemployment": "UNRATE",
    "fed_funds": "FEDFUNDS",
}

LABELS = {
    "gdp_growth": "GDP Growth Rate",
    "cpi": "CPI Inflation Index",
    "unemployment": "Unemployment Rate",
    "fed_funds": "Federal Funds Rate",
}

UNITS = {
    "gdp_growth": "%",
    "cpi": "Index",
    "unemployment": "%",
    "fed_funds": "%",
}

START_DATE = "2000-01-01"


def _get_fred() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "FRED_API_KEY not set. Create a .env file with FRED_API_KEY=your_key_here. "
            "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    return Fred(api_key=api_key)


def _fetch_one(key: str, fred: Fred) -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    csv_path = DATA_DIR / f"{key}.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path, index_col=0, parse_dates=True)

    series = fred.get_series(SERIES_IDS[key], observation_start=START_DATE)
    df = pd.DataFrame({"value": series})
    df.index.name = "date"
    df = df.dropna()
    df.to_csv(csv_path)
    return df


def fetch_all(force_refresh: bool = False) -> dict:
    """Fetch all indicators. Returns cached CSVs when available."""
    fred = _get_fred()
    if force_refresh:
        for key in SERIES_IDS:
            path = DATA_DIR / f"{key}.csv"
            if path.exists():
                path.unlink()
    return {key: _fetch_one(key, fred) for key in SERIES_IDS}
