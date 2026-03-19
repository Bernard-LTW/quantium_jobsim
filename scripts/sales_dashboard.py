from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "formatted_sales_data.csv"
PRICE_INCREASE_DATE = datetime(2021, 1, 15)
APP_TITLE = "Soul Foods Pink Morsel Sales Visualiser"
REGION_OPTIONS = ["all", "north", "east", "south", "west"]


def load_daily_sales(region: str = "all") -> tuple[list[datetime], list[float]]:
    """Aggregate total Pink Morsel sales by day for a selected region."""
    daily_sales: dict[datetime, Decimal] = defaultdict(Decimal)
    normalised_region = region.strip().lower()

    with DATA_FILE.open("r", newline="", encoding="utf-8") as data_handle:
        reader = csv.DictReader(data_handle)
        for row in reader:
            row_region = row["Region"].strip().lower()
            if normalised_region != "all" and row_region != normalised_region:
                continue
            date = datetime.strptime(row["Date"].strip(), "%Y-%m-%d")
            daily_sales[date] += Decimal(row["Sales"].strip())

    sorted_dates = sorted(daily_sales.keys())
    sorted_sales = [float(daily_sales[date]) for date in sorted_dates]
    return sorted_dates, sorted_sales


def calculate_pre_post_average(
    dates: list[datetime], sales: list[float]
) -> tuple[float, float, str]:
    """Compare average daily sales before and after 2021-01-15."""
    before_sales = [value for date, value in zip(dates, sales) if date < PRICE_INCREASE_DATE]
    after_sales = [value for date, value in zip(dates, sales) if date >= PRICE_INCREASE_DATE]

    if not before_sales or not after_sales:
        return 0.0, 0.0, "Insufficient data to compare periods."

    before_average = sum(before_sales) / len(before_sales)
    after_average = sum(after_sales) / len(after_sales)

    if after_average > before_average:
        insight = "Average daily sales are higher after the price increase."
    elif after_average < before_average:
        insight = "Average daily sales are higher before the price increase."
    else:
        insight = "Average daily sales are unchanged across the price increase."

    return before_average, after_average, insight


def build_figure(region: str = "all") -> go.Figure:
    dates, sales = load_daily_sales(region)
    before_avg, after_avg, insight = calculate_pre_post_average(dates, sales)
    region_label = "All regions" if region == "all" else f"{region.title()} region"

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=dates,
            y=sales,
            mode="lines",
            name=f"{region_label} sales",
            line={"color": "#6ce5e8", "width": 2.5},
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Sales: $%{y:,.2f}<extra></extra>",
        )
    )

    figure.update_layout(
        title=f"Pink Morsel Daily Sales Over Time ({region_label})",
        xaxis_title="Date",
        yaxis_title="Total Daily Sales (AUD)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"l": 60, "r": 30, "t": 80, "b": 60},
        xaxis={"gridcolor": "rgba(255,255,255,0.1)"},
        yaxis={"gridcolor": "rgba(255,255,255,0.1)"},
        shapes=[
            {
                "type": "line",
                "xref": "x",
                "yref": "paper",
                "x0": PRICE_INCREASE_DATE.strftime("%Y-%m-%d"),
                "x1": PRICE_INCREASE_DATE.strftime("%Y-%m-%d"),
                "y0": 0,
                "y1": 1,
                "line": {"color": "#ff6b6b", "width": 2, "dash": "dash"},
            }
        ],
        annotations=[
            {
                "text": "Price increase: 2021-01-15",
                "xref": "x",
                "yref": "paper",
                "x": PRICE_INCREASE_DATE.strftime("%Y-%m-%d"),
                "y": 1.06,
                "showarrow": False,
                "font": {"size": 11, "color": "#ff6b6b"},
            },
            {
                "text": (
                    f"Before avg: {before_avg:,.2f} | After avg: {after_avg:,.2f} | "
                    f"<b>{insight}</b>"
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.15,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12},
            }
        ],
    )

    return figure


app = Dash(__name__)
app.title = APP_TITLE
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(APP_TITLE, className="app-title"),
                html.P(
                    "Explore whether Pink Morsel sales were stronger before or after "
                    "the 15 Jan 2021 price increase.",
                    className="app-subtitle",
                ),
            ],
            className="title-block",
        ),
        html.Div(
            [
                html.Div("Filter by region", className="radio-label"),
                dcc.RadioItems(
                    id="region-filter",
                    options=[{"label": option.title(), "value": option} for option in REGION_OPTIONS],
                    value="all",
                    inline=True,
                    className="region-radio-group",
                    inputClassName="region-radio-input",
                    labelClassName="region-radio-option",
                ),
            ],
            className="control-card",
        ),
        html.Div(
            [dcc.Graph(id="sales-line-chart", figure=build_figure("all"), className="sales-graph")],
            className="graph-card",
        ),
    ],
    className="app-shell",
)


@app.callback(Output("sales-line-chart", "figure"), Input("region-filter", "value"))
def update_line_chart(region: str) -> go.Figure:
    return build_figure(region)


if __name__ == "__main__":
    app.run(debug=True)
