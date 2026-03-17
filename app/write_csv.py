import csv
import os
from pathlib import Path

CSV_PATH = Path("./data/daily_metrics.csv")
FIELDNAMES = ["date", "user_id", "searches", "purchases", "total_purchased_amount"]


def write_csv(rows):
    """
    Append metric rows to the daily_metrics.csv output file.

    Rows must be tuples of:
        (date, user_id, searches, purchases, total_purchased_amount)

    Opens in append mode and writes the header only when the file does not
    yet exist, so multiple batch flushes within one run accumulate correctly
    into a single file without duplicating the header row.
    """
    if not rows:
        return

    os.makedirs(CSV_PATH.parent, exist_ok=True)
    file_exists = CSV_PATH.exists()

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        for date, user_id, searches, purchases, amount in rows:
            writer.writerow({
                "date": date,
                "user_id": user_id,
                "searches": searches,
                "purchases": purchases,
                "total_purchased_amount": amount,
            })


def reset_csv():
    """Delete the CSV so a fresh pipeline run starts with a clean file."""
    if CSV_PATH.exists():

        CSV_PATH.unlink()