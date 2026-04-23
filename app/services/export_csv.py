import csv
from pathlib import Path
from typing import Any


CSV_FIELDS = (
    "canonical_url",
    "title",
    "price_raw",
    "m2",
    "phone",
    "seller_type",
    "portal",
    "first_seen",
    "last_seen",
    "run_id",
)


def write_listings_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(CSV_FIELDS), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)
