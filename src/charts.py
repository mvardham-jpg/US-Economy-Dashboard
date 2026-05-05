import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

COLORS = {
    "unemployment": "#455A64",   # slate
    "college_grad": "#1565C0",   # blue
    "youth": "#E65100",          # orange
    "job_openings": "#2E7D32",   # green
    "gap": "#6A1B9A",            # purple
}

RECESSIONS = [
    ("2001-03-01", "2001-11-30"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]

_RECESSION_COLOR = "rgba(150, 150, 150, 0.18)"


def _add_recession_shading(fig) -> None:
    for start, end in RECESSIONS:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor=_RECESSION_COLOR,
            layer="below", line_width=0,
        )


def _recession_legend_trace() -> go.Scatter:
    return go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=11, color="rgba(150,150,150,0.45)", symbol="square"),
        name="NBER Recession",
    )


def _base_layout(title: str, height: int = 400) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color="#1a1a2e"), x=0),
        hovermode="x unified",
        template="plotly_white",
        height=height,
        margin=dict(l=60, r=24, t=56, b=55),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        legend=dict(
            orientation="h", yanchor="top", y=1.16, xanchor="right", x=1,
            font=dict(size=11), bgcolor="rgba(255,255,255,0)",
        ),
    )


def unemployment_comparison_chart(
    df_overall: pd.DataFrame,
    df_college: pd.DataFrame,
    df_youth: pd.DataFrame,
) -> go.Figure:
    """Three unemployment rates on a single y-axis for direct comparison."""
    fig = go.Figure()
    fig.add_trace(_recession_legend_trace())

    traces = [
        (df_overall, "unemployment", "Overall Unemployment"),
        (df_college, "college_grad", "College Grads (BA+, 25+)"),
        (df_youth, "youth", "Youth 20–24 (Entry-Level)"),
    ]
    for df, key, label in traces:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["value"],
            name=label,
            line=dict(color=COLORS[key], width=2.5),
            hovertemplate=f"<b>{label}</b>: %{{y:.1f}}%<extra></extra>",
        ))

    _add_recession_shading(fig)
    fig.update_layout(**_base_layout("Unemployment Rate by Group", height=430))
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06), type="date")
    fig.update_yaxes(title_text="Unemployment Rate", ticksuffix="%")
    return fig


def job_openings_chart(df: pd.DataFrame) -> go.Figure:
    """Job openings as a filled area chart (values in thousands → display millions)."""
    fig = go.Figure()
    fig.add_trace(_recession_legend_trace())

    millions = df["value"] / 1_000
    fig.add_trace(go.Scatter(
        x=df.index, y=millions,
        name="Job Openings",
        mode="lines",
        line=dict(color=COLORS["job_openings"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(46,125,50,0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Openings: %{y:.2f}M<extra></extra>",
    ))

    _add_recession_shading(fig)
    fig.update_layout(**_base_layout("Total Job Openings (JOLTS)", height=400))
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06), type="date")
    fig.update_yaxes(title_text="Millions of Openings", ticksuffix="M")
    return fig


def degree_premium_chart(gap_df: pd.DataFrame) -> go.Figure:
    """
    Filled area showing the gap: Overall unemployment − College Grad unemployment.
    A larger gap means a degree provides more protection against unemployment.
    """
    fig = go.Figure()
    fig.add_trace(_recession_legend_trace())

    fig.add_trace(go.Scatter(
        x=gap_df.index, y=gap_df["value"],
        name="Degree Premium",
        mode="lines",
        line=dict(color=COLORS["gap"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(106,27,154,0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Premium: +%{y:.2f} pp<extra></extra>",
    ))

    _add_recession_shading(fig)
    fig.update_layout(**_base_layout(
        "Degree Premium — How Much Lower is College Grad Unemployment?",
        height=400,
    ))
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06), type="date")
    fig.update_yaxes(title_text="Percentage Points Lower", ticksuffix=" pp")
    return fig


def comparison_chart(
    df1: pd.DataFrame, df2: pd.DataFrame,
    key1: str, key2: str,
    label1: str, label2: str,
    unit1: str, unit2: str,
) -> go.Figure:
    """Dual y-axis comparison for any two indicators."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    _add_recession_shading(fig)
    fig.add_trace(_recession_legend_trace(), secondary_y=False)

    y1 = df1["value"] / 1_000 if unit1 == "K" else df1["value"]
    y2 = df2["value"] / 1_000 if unit2 == "K" else df2["value"]
    disp1 = "M" if unit1 == "K" else unit1
    disp2 = "M" if unit2 == "K" else unit2

    fig.add_trace(go.Scatter(
        x=df1.index, y=y1, name=label1,
        line=dict(color=COLORS[key1], width=2.5),
        hovertemplate=f"<b>{label1}</b>: %{{y:.2f}} {disp1}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df2.index, y=y2, name=label2,
        line=dict(color=COLORS[key2], width=2.5, dash="dash"),
        hovertemplate=f"<b>{label2}</b>: %{{y:.2f}} {disp2}<extra></extra>",
    ), secondary_y=True)

    layout = _base_layout("Custom Comparison", height=460)
    layout["margin"]["r"] = 80
    fig.update_layout(**layout)

    s1 = "%" if disp1 == "%" else ""
    s2 = "%" if disp2 == "%" else ""
    fig.update_yaxes(title_text=f"{label1} ({disp1})", ticksuffix=s1,
                     secondary_y=False, color=COLORS[key1], title_font_color=COLORS[key1])
    fig.update_yaxes(title_text=f"{label2} ({disp2})", ticksuffix=s2,
                     secondary_y=True, color=COLORS[key2], title_font_color=COLORS[key2])
    return fig
