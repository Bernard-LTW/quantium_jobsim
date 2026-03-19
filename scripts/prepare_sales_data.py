from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


INPUT_PATTERN = "daily_sales_data_*.csv"
INPUT_DIR = Path("data")
OUTPUT_FILE = INPUT_DIR / "formatted_sales_data.csv"
TARGET_PRODUCT = "pink morsel"


def parse_price(price_raw: str) -> Decimal:
    cleaned = price_raw.replace("$", "").replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid price value: {price_raw!r}") from exc


def build_output() -> None:
    input_files = sorted(INPUT_DIR.glob(INPUT_PATTERN))
    if not input_files:
        raise FileNotFoundError(f"No input files found for pattern: {INPUT_PATTERN}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=["Sales", "Date", "Region"])
        writer.writeheader()

        for input_path in input_files:
            with input_path.open("r", newline="", encoding="utf-8") as input_handle:
                reader = csv.DictReader(input_handle)
                for row in reader:
                    if row["product"].strip().lower() != TARGET_PRODUCT:
                        continue

                    quantity = Decimal(row["quantity"].strip())
                    price = parse_price(row["price"])
                    sales = (quantity * price).quantize(Decimal("0.01"))

                    writer.writerow(
                        {
                            "Sales": format(sales, "f"),
                            "Date": row["date"].strip(),
                            "Region": row["region"].strip(),
                        }
                    )

    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    build_output()
