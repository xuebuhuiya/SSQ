from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = ["issue", "date", "r1", "r2", "r3", "r4", "r5", "r6", "blue"]
RED_COLUMNS = ["r1", "r2", "r3", "r4", "r5", "r6"]


class HistoryDataError(ValueError):
    """Raised when historical draw data is invalid."""


def normalize_history(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise HistoryDataError(f"Missing required columns: {', '.join(missing)}")
    if df.empty:
        raise HistoryDataError("History CSV contains no rows.")

    normalized = df.copy()
    normalized = normalized.drop_duplicates(subset=["issue"], keep="last")
    normalized["date"] = pd.to_datetime(normalized["date"], errors="raise")

    for column in RED_COLUMNS + ["blue"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="raise").astype(int)

    rows: list[dict] = []
    for _, row in normalized.iterrows():
        reds = [int(row[column]) for column in RED_COLUMNS]
        if len(set(reds)) != 6:
            raise HistoryDataError(f"Duplicate red balls in issue {row['issue']}: {reds}")
        if any(red < 1 or red > 33 for red in reds):
            raise HistoryDataError(f"Red ball out of range in issue {row['issue']}: {reds}")
        blue = int(row["blue"])
        if blue < 1 or blue > 16:
            raise HistoryDataError(f"Blue ball out of range in issue {row['issue']}: {blue}")

        sorted_reds = sorted(reds)
        item = row.to_dict()
        for column, red in zip(RED_COLUMNS, sorted_reds):
            item[column] = red
        item["blue"] = blue
        rows.append(item)

    return pd.DataFrame(rows).reset_index(drop=True)
