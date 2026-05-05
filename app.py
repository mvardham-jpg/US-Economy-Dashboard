import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.charts import (
    COLORS,
    comparison_chart,
    degree_premium_chart,
    job_openings_chart,
    unemployment_comparison_chart,
)
from src.fetch import LABELS, UNITS, fetch_all

st.set_page_config(
    page_title="Grad Job Market Dashboard",
    page_icon="🎓",
    layout="wide",
)

st.markdown("""
<style>
.kpi-box {
    border-radius: 14px;
    padding: 20px 14px 16px;
    color: white;
    text-align: center;
    box-shadow: 0 3px 14px rgba(0,0,0,0.13);
}
.kpi-label  { font-size:0.68rem; font-weight:700; text-transform:uppercase;
              letter-spacing:0.9px; opacity:0.85; margin-bottom:6px; }
.kpi-value  { font-size:2.0rem; font-weight:800; line-height:1; }
.kpi-delta  { font-size:0.72rem; opacity:0.80; margin-top:5px; }
.kpi-sub    { font-size:0.66rem; opacity:0.65; margin-top:2px; }

.section-title {
    font-size:1.05rem; font-weight:700; color:#1a1a2e;
    border-left:4px solid #1565C0; padding-left:10px; margin:24px 0 6px;
}
.insight-box {
    background:#f0f4ff; border-left:4px solid #1565C0;
    border-radius:0 8px 8px 0; padding:12px 16px;
    font-size:0.88rem; color:#1a1a2e; margin-bottom:10px;
}
.health-good  { background:#E8F5E9; border:1px solid #A5D6A7;
                border-radius:10px; padding:10px 16px; color:#1B5E20; }
.health-warn  { background:#FFF3E0; border:1px solid #FFCC80;
                border-radius:10px; padding:10px 16px; color:#E65100; }
.health-bad   { background:#FFEBEE; border:1px solid #EF9A9A;
                border-radius:10px; padding:10px 16px; color:#B71C1C; }
.cohort-card  { background:#f8f9ff; border:1px solid #c5cae9;
                border-radius:12px; padding:18px; margin-top:8px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Dashboard")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("**FRED Series**")
    st.markdown(
        "- Overall: `UNRATE`\n"
        "- College Grads: `LNS14027662`\n"
        "- Youth 20–24: `LNS14000036`\n"
        "- Job Openings: `JTSJOL`"
    )
    st.markdown("---")
    st.markdown(
        "<small>Gray bands = NBER recessions.<br>"
        "Data cached locally; click Refresh to re-fetch from FRED.</small>",
        unsafe_allow_html=True,
    )


# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> dict:
    return fetch_all()


st.title("🎓 College Grads & Entry-Level Job Market")
st.markdown(
    "Is now a good time to graduate? How do recessions hit young workers? "
    "Explore 25 years of labor market data from **[FRED](https://fred.stlouisfed.org)**."
)

with st.spinner("Loading labor market data…"):
    try:
        data = load_data()
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

# ── Derived: degree premium ────────────────────────────────────────────────
gap_series = (
    data["unemployment"]["value"]
    .subtract(data["college_grad"]["value"])
    .dropna()
)
gap_df = pd.DataFrame({"value": gap_series})


# ── Helper: year-ago delta ─────────────────────────────────────────────────
def year_ago_delta(df: pd.DataFrame) -> float:
    last = df.index[-1]
    target = last - pd.DateOffset(months=12)
    idx = df.index.get_indexer([target], method="nearest")[0]
    return df["value"].iloc[-1] - df["value"].iloc[idx]


# ── Market health assessment ───────────────────────────────────────────────
current_unemp = data["unemployment"]["value"].iloc[-1]
current_college = data["college_grad"]["value"].iloc[-1]
current_youth = data["youth"]["value"].iloc[-1]

if current_unemp < 4.5:
    health_cls, health_emoji, health_msg = (
        "health-good", "🟢",
        f"Strong market — overall unemployment is {current_unemp:.1f}%, "
        f"college grads sit at just {current_college:.1f}%."
    )
elif current_unemp < 6.5:
    health_cls, health_emoji, health_msg = (
        "health-warn", "🟡",
        f"Mixed conditions — unemployment at {current_unemp:.1f}%. "
        f"College grads fare better at {current_college:.1f}%."
    )
else:
    health_cls, health_emoji, health_msg = (
        "health-bad", "🔴",
        f"Tough market — unemployment at {current_unemp:.1f}%. "
        f"College grads at {current_college:.1f}%."
    )

st.markdown(
    f'<div class="{health_cls}"><b>{health_emoji} Market Health:</b> {health_msg}</div>',
    unsafe_allow_html=True,
)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_overview, tab_cohort, tab_deep, tab_compare = st.tabs([
    "📊 Overview",
    "🎓 Your Graduation Year",
    "🔍 Deep Dive",
    "📈 Compare",
])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
with tab_overview:

    # KPI cards with year-over-year delta
    CARD_COLORS = {
        "unemployment": "#455A64",
        "college_grad": "#1565C0",
        "youth":        "#E65100",
        "job_openings": "#2E7D32",
    }
    kpi_specs = [
        ("unemployment", None),
        ("college_grad", None),
        ("youth", None),
        ("job_openings", "M"),
    ]

    st.markdown('<div class="section-title">Current Snapshot</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (key, override_unit) in zip(cols, kpi_specs):
        df = data[key]
        val = df["value"].iloc[-1]
        date_str = df.index[-1].strftime("%b %Y")
        label = LABELS[key]
        color = CARD_COLORS[key]
        delta = year_ago_delta(df)

        if override_unit == "M":
            display = f"{val / 1_000:.1f}M"
            delta_str = f"{'▲' if delta > 0 else '▼'} {abs(delta)/1_000:.1f}M vs last year"
            sub = f"job openings · {date_str}"
        else:
            display = f"{val:.1f}%"
            arrow = "▲" if delta > 0 else "▼"
            delta_str = f"{arrow} {abs(delta):.1f} pp vs last year"
            sub = f"unemployment · {date_str}"

        with col:
            st.markdown(
                f'<div class="kpi-box" style="background:{color};">'
                f'<div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{display}</div>'
                f'<div class="kpi-delta">{delta_str}</div>'
                f'<div class="kpi-sub">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Degree premium insight
    premium = gap_df["value"].iloc[-1]
    st.markdown(
        f'<div class="insight-box" style="margin-top:14px;">📌 <b>Degree Premium:</b> '
        f'Right now, college grads experience unemployment rates '
        f'<b>{premium:.1f} percentage points lower</b> than the general workforce. '
        f'{"That\'s a strong advantage." if premium > 2 else "The gap has narrowed — a degree helps less than usual."}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Main comparison chart with event annotations
    st.markdown('<div class="section-title">Unemployment by Group (2000–Present)</div>', unsafe_allow_html=True)

    fig = unemployment_comparison_chart(
        data["unemployment"], data["college_grad"], data["youth"]
    )

    # Annotate key events
    events = [
        ("2008-09-15", "2008\nFinancial\nCrisis", "#C62828"),
        ("2020-03-01", "COVID-19", "#C62828"),
        ("2021-07-01", "Great\nResignation", "#1565C0"),
    ]
    for date, label, color in events:
        fig.add_vline(
            x=date, line_dash="dot", line_color=color, line_width=1.5,
            annotation_text=label, annotation_position="top",
            annotation_font_size=9, annotation_font_color=color,
        )

    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — YOUR GRADUATION YEAR
# ══════════════════════════════════════════════════════════════════════════
with tab_cohort:
    st.markdown("### What was the job market like when you graduated?")
    st.markdown(
        "Pick your graduation year and see the unemployment landscape you stepped into — "
        "and how it compares to today."
    )

    grad_year = st.slider(
        "Graduation Year", min_value=2000, max_value=2024, value=2020, step=1
    )
    grad_date = f"{grad_year}-06-01"  # assume June graduation

    # Fetch unemployment values at grad year
    def get_val_at(df: pd.DataFrame, date_str: str) -> tuple[float, str]:
        target = pd.to_datetime(date_str)
        idx = df.index.get_indexer([target], method="nearest")[0]
        return df["value"].iloc[idx], df.index[idx].strftime("%b %Y")

    un_then, un_date  = get_val_at(data["unemployment"], grad_date)
    cg_then, _        = get_val_at(data["college_grad"], grad_date)
    yt_then, _        = get_val_at(data["youth"], grad_date)

    # Job openings (JOLTS starts Dec 2000)
    jo_df = data["job_openings"]
    jo_available = pd.to_datetime(grad_date) >= jo_df.index[0]
    if jo_available:
        jo_then_raw, _ = get_val_at(jo_df, grad_date)
        jo_then = jo_then_raw / 1_000
    else:
        jo_then = None

    # Recession check
    RECESSION_PERIODS = [
        (2001, 3, 2001, 11, "Dot-com bust"),
        (2007, 12, 2009, 6,  "Great Financial Crisis"),
        (2020, 2, 2020, 4,   "COVID-19 recession"),
    ]
    recession_label = None
    for (sy, sm, ey, em, name) in RECESSION_PERIODS:
        if (sy * 12 + sm) <= (grad_year * 12 + 6) <= (ey * 12 + em):
            recession_label = name
            break

    # Market assessment at grad time
    if recession_label:
        grad_emoji, grad_verdict = "😬", f"You graduated smack into the **{recession_label}**."
    elif un_then < 4.5:
        grad_emoji, grad_verdict = "🔥", "You graduated into a **hot job market**. Lucky!"
    elif un_then < 6.0:
        grad_emoji, grad_verdict = "🙂", "You graduated into a **decent market** — not bad."
    else:
        grad_emoji, grad_verdict = "😤", "Rough timing — you faced a **tough job market**."

    # Display cohort card
    jo_str = f"{jo_then:.1f}M" if jo_then else "N/A (pre-JOLTS)"
    st.markdown(
        f'<div class="cohort-card">'
        f'<h3>{grad_emoji} Class of {grad_year}</h3>'
        f'{grad_verdict}<br><br>'
        f'<table style="width:100%;font-size:0.9rem;">'
        f'<tr><th style="text-align:left;">Indicator</th>'
        f'    <th style="text-align:center;">When You Graduated ({un_date})</th>'
        f'    <th style="text-align:center;">Today</th>'
        f'    <th style="text-align:center;">Change</th></tr>'
        f'<tr><td>Overall Unemployment</td>'
        f'    <td style="text-align:center;">{un_then:.1f}%</td>'
        f'    <td style="text-align:center;">{current_unemp:.1f}%</td>'
        f'    <td style="text-align:center;">{"▲" if current_unemp > un_then else "▼"} {abs(current_unemp - un_then):.1f} pp</td></tr>'
        f'<tr><td>College Grad Unemployment</td>'
        f'    <td style="text-align:center;">{cg_then:.1f}%</td>'
        f'    <td style="text-align:center;">{current_college:.1f}%</td>'
        f'    <td style="text-align:center;">{"▲" if current_college > cg_then else "▼"} {abs(current_college - cg_then):.1f} pp</td></tr>'
        f'<tr><td>Youth Unemployment (20–24)</td>'
        f'    <td style="text-align:center;">{yt_then:.1f}%</td>'
        f'    <td style="text-align:center;">{current_youth:.1f}%</td>'
        f'    <td style="text-align:center;">{"▲" if current_youth > yt_then else "▼"} {abs(current_youth - yt_then):.1f} pp</td></tr>'
        f'<tr><td>Job Openings</td>'
        f'    <td style="text-align:center;">{jo_str}</td>'
        f'    <td style="text-align:center;">{data["job_openings"]["value"].iloc[-1]/1_000:.1f}M</td>'
        f'    <td style="text-align:center;">—</td></tr>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

    # Chart with grad year marked
    st.markdown("<br>", unsafe_allow_html=True)
    fig2 = unemployment_comparison_chart(
        data["unemployment"], data["college_grad"], data["youth"]
    )
    fig2.add_vline(
        x=grad_date, line_dash="dash", line_color="#F57F17", line_width=2,
        annotation_text=f"You graduated\n({grad_year})",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color="#F57F17",
    )
    # Annotate key events too
    for date, label, color in [
        ("2008-09-15", "Financial\nCrisis", "#C62828"),
        ("2020-03-01", "COVID-19", "#C62828"),
    ]:
        fig2.add_vline(
            x=date, line_dash="dot", line_color=color, line_width=1.2,
            annotation_text=label, annotation_position="top",
            annotation_font_size=9, annotation_font_color=color,
        )
    st.plotly_chart(fig2, use_container_width=True)

    # Fun extra: how many months to recover from their grad period
    if recession_label:
        recession_ends = {"Dot-com bust": 2003, "Great Financial Crisis": 2011, "COVID-19 recession": 2022}
        recovery_year = recession_ends.get(recession_label)
        if recovery_year:
            st.info(
                f"📅 After the {recession_label}, the college grad unemployment rate didn't fully normalize "
                f"until around **{recovery_year}** — about **{(recovery_year - grad_year)} years** after graduation."
            )


# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════
with tab_deep:
    st.markdown("### Job Openings & the Value of a Degree")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Job Openings (JOLTS)</div>', unsafe_allow_html=True)
        st.caption("Total nonfarm job openings — a proxy for how hungry employers are for workers.")
        st.plotly_chart(job_openings_chart(data["job_openings"]), use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Degree Premium</div>', unsafe_allow_html=True)
        st.caption(
            "How many percentage points lower college grad unemployment is vs the overall rate. "
            "Higher = stronger protection from a degree."
        )
        st.plotly_chart(degree_premium_chart(gap_df), use_container_width=True)

    # Stats callout
    max_premium = gap_df["value"].max()
    max_premium_date = gap_df["value"].idxmax().strftime("%b %Y")
    min_premium = gap_df["value"].min()
    min_premium_date = gap_df["value"].idxmin().strftime("%b %Y")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("Current Degree Premium", f"{gap_df['value'].iloc[-1]:.1f} pp")
    with sc2:
        st.metric("Peak Premium (most valuable)", f"{max_premium:.1f} pp", f"{max_premium_date}")
    with sc3:
        st.metric("Weakest Premium", f"{min_premium:.1f} pp", f"{min_premium_date}")

    st.markdown("---")

    # Animated scatter: youth vs college grad unemployment month by month
    st.markdown('<div class="section-title">Youth vs. College Grad Unemployment — Scatter</div>', unsafe_allow_html=True)
    st.caption("Each dot is one month. X = college grad unemployment, Y = youth (20–24) unemployment. Recessions cluster upper-right.")

    common_idx = data["college_grad"].index.intersection(data["youth"].index)
    scatter_df = pd.DataFrame({
        "college": data["college_grad"].loc[common_idx, "value"],
        "youth":   data["youth"].loc[common_idx, "value"],
        "date":    common_idx,
    })
    scatter_df["year"] = scatter_df["date"].dt.year

    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=scatter_df["college"],
        y=scatter_df["youth"],
        mode="markers",
        marker=dict(
            color=scatter_df["year"],
            colorscale="Viridis",
            size=7,
            colorbar=dict(title="Year", thickness=12),
            opacity=0.75,
        ),
        text=scatter_df["date"].dt.strftime("%b %Y"),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "College Grad: %{x:.1f}%<br>"
            "Youth (20–24): %{y:.1f}%<extra></extra>"
        ),
    ))
    fig_scatter.update_layout(
        template="plotly_white",
        height=420,
        xaxis_title="College Grad Unemployment (%)",
        yaxis_title="Youth Unemployment, 20–24 (%)",
        margin=dict(l=60, r=60, t=30, b=55),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — COMPARE
# ══════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("### Build Your Own Comparison")
    st.markdown("Overlay any two indicators on a dual y-axis chart.")

    ALL_KEYS = ["unemployment", "college_grad", "youth", "job_openings"]
    sel1, sel2 = st.columns(2)
    with sel1:
        key1 = st.selectbox(
            "Primary indicator (left axis)",
            ALL_KEYS, format_func=lambda k: LABELS[k], index=2,
        )
    with sel2:
        remaining = [k for k in ALL_KEYS if k != key1]
        key2 = st.selectbox(
            "Secondary indicator (right axis)",
            remaining, format_func=lambda k: LABELS[k], index=2,
        )

    st.plotly_chart(
        comparison_chart(
            data[key1], data[key2], key1, key2,
            LABELS[key1], LABELS[key2], UNITS[key1], UNITS[key2],
        ),
        use_container_width=True,
    )

    # Fun stat
    corr = (
        data[key1]["value"]
        .reindex(data[key2].index, method="nearest")
        .corr(data[key2]["value"])
    )
    direction = "move together" if corr > 0 else "move in opposite directions"
    strength = "strongly" if abs(corr) > 0.7 else ("somewhat" if abs(corr) > 0.4 else "weakly")
    st.info(
        f"📐 **Correlation:** {LABELS[key1]} and {LABELS[key2]} {strength} {direction} "
        f"(r = {corr:.2f})."
    )


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.76rem;'>"
    "Data: <a href='https://fred.stlouisfed.org' target='_blank'>FRED, Federal Reserve Bank of St. Louis</a>. "
    "Gray shading = NBER recession periods."
    "</div>",
    unsafe_allow_html=True,
)
