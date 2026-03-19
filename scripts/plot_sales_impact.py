from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt


FORMATTED_DATA_FILE = Path("data/formatted_sales_data.csv")
RAW_DATA_PATTERN = "daily_sales_data_*.csv"
DATA_DIR = Path("data")
OUTPUT_CHART_FILE = DATA_DIR / "pink_morsel_sales_impact.png"
TARGET_PRODUCT = "pink morsel"


def parse_price(price_raw: str) -> Decimal:
    return Decimal(price_raw.replace("$", "").replace(",", "").strip())


def load_daily_sales() -> tuple[list[datetime], list[float]]:
    daily_sales: dict[datetime, Decimal] = defaultdict(Decimal)

    with FORMATTED_DATA_FILE.open("r", newline="", encoding="utf-8") as data_handle:
        reader = csv.DictReader(data_handle)
        for row in reader:
            date = datetime.strptime(row["Date"].strip(), "%Y-%m-%d")
            daily_sales[date] += Decimal(row["Sales"].strip())

    sorted_dates = sorted(daily_sales.keys())
    sorted_sales = [float(daily_sales[date]) for date in sorted_dates]
    return sorted_dates, sorted_sales


def detect_price_change() -> tuple[datetime | None, Decimal | None, Decimal | None]:
    pink_prices_by_date: dict[datetime, set[Decimal]] = defaultdict(set)

    for input_path in sorted(DATA_DIR.glob(RAW_DATA_PATTERN)):
        with input_path.open("r", newline="", encoding="utf-8") as input_handle:
            reader = csv.DictReader(input_handle)
            for row in reader:
                if row["product"].strip().lower() != TARGET_PRODUCT:
                    continue
                date = datetime.strptime(row["date"].strip(), "%Y-%m-%d")
                pink_prices_by_date[date].add(parse_price(row["price"]))

    if not pink_prices_by_date:
        return None, None, None

    sorted_dates = sorted(pink_prices_by_date.keys())
    baseline_price = min(pink_prices_by_date[sorted_dates[0]])

    for date in sorted_dates:
        prices = pink_prices_by_date[date]
        if len(prices) != 1:
            continue
        price = next(iter(prices))
        if price != baseline_price:
            return date, baseline_price, price

    return None, baseline_price, None


def plot_sales_impact() -> None:
    dates, sales = load_daily_sales()
    if not dates:
        raise ValueError("No sales data found in formatted_sales_data.csv")

    price_change_date, old_price, new_price = detect_price_change()

    fig, axis = plt.subplots(figsize=(14, 7))
    axis.plot(dates, sales, linewidth=1.3, color="#1f77b4")
    axis.set_title("Pink Morsel Daily Sales Over Time", fontsize=14)
    axis.set_xlabel("Date")
    axis.set_ylabel("Total Daily Sales")
    axis.grid(alpha=0.25)

    if price_change_date and old_price is not None and new_price is not None:
        axis.axvline(
            x=price_change_date,
            color="#d62728",
            linestyle="--",
            linewidth=1.5,
            label=f"Price increase ({old_price} to {new_price})",
        )
        axis.legend()

    fig.tight_layout()
    fig.savefig(OUTPUT_CHART_FILE, dpi=150)
    plt.close(fig)

    print(f"Wrote {OUTPUT_CHART_FILE}")
    if price_change_date:
        print(
            "Detected price change on "
            f"{price_change_date.strftime('%Y-%m-%d')}: {old_price} -> {new_price}"
        )


if __name__ == "__main__":
    plot_sales_impact()
