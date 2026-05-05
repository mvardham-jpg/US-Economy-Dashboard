import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

COLORS = {
    "gdp_growth": "#1565C0",
    "cpi": "#C62828",
    "unemployment": "#2E7D32",
    "fed_funds": "#6A1B9A",
}

# NBER recession periods (start, end inclusive)
RECESSIONS = [
    ("2001-03-01", "2001-11-30"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]

_RECESSION_COLOR = "rgba(150, 150, 150, 0.18)"


def _add_recession_shading(fig, secondary_y: bool = False) -> None:
    for start, end in RECESSIONS:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=_RECESSION_COLOR,
            layer="below",
            line_width=0,
        )


def _recession_legend_trace() -> go.Scatter:
    return go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=11, color="rgba(150,150,150,0.45)", symbol="square"),
        name="NBER Recession",
    )


def _base_layout(title: str, height: int = 390) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color="#1a1a2e"), x=0),
        hovermode="x unified",
        template="plotly_white",
        height=height,
        margin=dict(l=60, r=24, t=56, b=55),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.14,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0)",
        ),
    )


def time_series_chart(
    df: pd.DataFrame, key: str, label: str, unit: str
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(_recession_legend_trace())

    suffix = "%" if unit == "%" else ""
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["value"],
            mode="lines",
            name=label,
            line=dict(color=COLORS[key], width=2.5),
            hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{label}: %{{y:.2f}} {unit}<extra></extra>",
        )
    )

    _add_recession_shading(fig)

    fig.update_layout(**_base_layout(label))
    fig.update_xaxes(
        rangeslider=dict(visible=True, thickness=0.06),
        type="date",
    )
    fig.update_yaxes(title_text=unit, ticksuffix=suffix)

    return fig


def comparison_chart(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key1: str,
    key2: str,
    label1: str,
    label2: str,
    unit1: str,
    unit2: str,
) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    _add_recession_shading(fig)

    fig.add_trace(_recession_legend_trace(), secondary_y=False)

    fig.add_trace(
        go.Scatter(
            x=df1.index,
            y=df1["value"],
            name=label1,
            line=dict(color=COLORS[key1], width=2.5),
            hovertemplate=f"<b>{label1}</b>: %{{y:.2f}} {unit1}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df2.index,
            y=df2["value"],
            name=label2,
            line=dict(color=COLORS[key2], width=2.5, dash="dash"),
            hovertemplate=f"<b>{label2}</b>: %{{y:.2f}} {unit2}<extra></extra>",
        ),
        secondary_y=True,
    )

    suffix1 = "%" if unit1 == "%" else ""
    suffix2 = "%" if unit2 == "%" else ""

    layout = _base_layout("Multi-Indicator Comparison", height=460)
    layout["margin"]["r"] = 80
    fig.update_layout(**layout)

    fig.update_yaxes(
        title_text=f"{label1} ({unit1})",
        ticksuffix=suffix1,
        secondary_y=False,
        color=COLORS[key1],
        title_font_color=COLORS[key1],
    )
    fig.update_yaxes(
        title_text=f"{label2} ({unit2})",
        ticksuffix=suffix2,
        secondary_y=True,
        color=COLORS[key2],
        title_font_color=COLORS[key2],
    )

    return fig
