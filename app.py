import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.charts import comparison_chart, time_series_chart
from src.fetch import LABELS, UNITS, fetch_all

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="US Economic Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* KPI cards */
.kpi-box {
    border-radius: 14px;
    padding: 22px 14px 18px;
    color: white;
    text-align: center;
    box-shadow: 0 3px 14px rgba(0,0,0,0.13);
    margin-bottom: 2px;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.85;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2.15rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.5px;
}
.kpi-sub {
    font-size: 0.70rem;
    opacity: 0.72;
    margin-top: 6px;
}

/* Section titles */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a2e;
    border-left: 4px solid #1565C0;
    padding-left: 10px;
    margin: 28px 0 6px;
}

/* Footer */
.footer {
    text-align: center;
    color: #888;
    font-size: 0.76rem;
    margin-top: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Controls")
    refresh = st.button("Refresh Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("**Series IDs (FRED)**")
    st.markdown(
        "- GDP Growth: `A191RL1Q225SBEA`\n"
        "- CPI: `CPIAUCSL`\n"
        "- Unemployment: `UNRATE`\n"
        "- Fed Funds: `FEDFUNDS`"
    )
    st.markdown("---")
    st.markdown(
        "<small>Gray bands mark NBER recession periods.<br>"
        "Data is cached locally in <code>data/</code>; "
        "click <b>Refresh Data</b> to re-fetch from FRED.</small>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<small><a href='https://fred.stlouisfed.org' target='_blank'>"
        "Federal Reserve Economic Data</a></small>",
        unsafe_allow_html=True,
    )

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> dict:
    return fetch_all()


st.title("US Economic Dashboard")
st.markdown(
    "Macroeconomic indicators sourced from the "
    "**[FRED database](https://fred.stlouisfed.org)**, Federal Reserve Bank of St. Louis."
)

with st.spinner("Loading economic data…"):
    try:
        data = load_data()
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

# ── KPI Cards ──────────────────────────────────────────────────────────────
CARD_COLORS = {
    "gdp_growth": "#1565C0",
    "cpi": "#C62828",
    "unemployment": "#2E7D32",
    "fed_funds": "#6A1B9A",
}

ALL_KEYS = ["gdp_growth", "cpi", "unemployment", "fed_funds"]

st.markdown(
    '<div class="section-title">Current Readings</div>', unsafe_allow_html=True
)

kpi_cols = st.columns(4)
for col, key in zip(kpi_cols, ALL_KEYS):
    df = data[key]
    val = df["value"].iloc[-1]
    date_str = df.index[-1].strftime("%b %Y")
    unit = UNITS[key]
    label = LABELS[key]
    color = CARD_COLORS[key]

    if unit == "%":
        display = f"{val:.2f}%"
    else:
        display = f"{val:,.1f}"
        label_with_unit = f"{label} ({unit})"

    with col:
        st.markdown(
            f'<div class="kpi-box" style="background:{color};">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{display}</div>'
            f'<div class="kpi-sub">As of {date_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Time Series Charts ─────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title">Time Series (drag range slider to zoom)</div>',
    unsafe_allow_html=True,
)

r1c1, r1c2 = st.columns(2)
with r1c1:
    st.plotly_chart(
        time_series_chart(
            data["gdp_growth"], "gdp_growth", LABELS["gdp_growth"], UNITS["gdp_growth"]
        ),
        use_container_width=True,
    )
with r1c2:
    st.plotly_chart(
        time_series_chart(data["cpi"], "cpi", LABELS["cpi"], UNITS["cpi"]),
        use_container_width=True,
    )

r2c1, r2c2 = st.columns(2)
with r2c1:
    st.plotly_chart(
        time_series_chart(
            data["unemployment"],
            "unemployment",
            LABELS["unemployment"],
            UNITS["unemployment"],
        ),
        use_container_width=True,
    )
with r2c2:
    st.plotly_chart(
        time_series_chart(
            data["fed_funds"], "fed_funds", LABELS["fed_funds"], UNITS["fed_funds"]
        ),
        use_container_width=True,
    )

st.markdown("---")

# ── Comparison Chart ───────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title">Multi-Indicator Comparison</div>',
    unsafe_allow_html=True,
)

sel_col1, sel_col2 = st.columns(2)
with sel_col1:
    key1 = st.selectbox(
        "Primary indicator (left axis)",
        ALL_KEYS,
        format_func=lambda k: LABELS[k],
        index=2,  # unemployment
    )
with sel_col2:
    remaining = [k for k in ALL_KEYS if k != key1]
    key2 = st.selectbox(
        "Secondary indicator (right axis)",
        remaining,
        format_func=lambda k: LABELS[k],
        index=0,
    )

st.plotly_chart(
    comparison_chart(
        data[key1],
        data[key2],
        key1,
        key2,
        LABELS[key1],
        LABELS[key2],
        UNITS[key1],
        UNITS[key2],
    ),
    use_container_width=True,
)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer">'
    'Data: <a href="https://fred.stlouisfed.org" target="_blank">FRED, Federal Reserve Bank of St. Louis</a>. '
    "Gray shading = NBER recession periods."
    "</div>",
    unsafe_allow_html=True,
)
