from __future__ import annotations

import pandas as pd

from .preprocess import RED_COLUMNS


def max_consecutive_len(reds: list[int]) -> int:
    reds = sorted(reds)
    best = current = 1
    for previous, current_red in zip(reds, reds[1:]):
        if current_red == previous + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def zone_counts(reds: list[int]) -> tuple[int, int, int]:
    return (
        sum(1 <= red <= 11 for red in reds),
        sum(12 <= red <= 22 for red in reds),
        sum(23 <= red <= 33 for red in reds),
    )


def mod3_counts(reds: list[int]) -> tuple[int, int, int]:
    return (
        sum(red % 3 == 0 for red in reds),
        sum(red % 3 == 1 for red in reds),
        sum(red % 3 == 2 for red in reds),
    )


def ac_value(reds: list[int]) -> int:
    reds = sorted(reds)
    diffs = {
        reds[j] - reds[i]
        for i in range(len(reds))
        for j in range(i + 1, len(reds))
    }
    return len(diffs) - (len(reds) - 1)


def compute_red_features(reds: list[int]) -> dict[str, int | float | bool]:
    reds = sorted(int(red) for red in reds)
    if len(reds) != 6 or len(set(reds)) != 6:
        raise ValueError("Exactly 6 unique red balls are required.")
    if any(red < 1 or red > 33 for red in reds):
        raise ValueError("Red balls must be in range 1-33.")

    zone_1, zone_2, zone_3 = zone_counts(reds)
    mod0, mod1, mod2 = mod3_counts(reds)
    odd_count = sum(red % 2 == 1 for red in reds)
    big_count = sum(red >= 17 for red in reds)
    return {
        "red_sum": sum(reds),
        "odd_count": odd_count,
        "even_count": 6 - odd_count,
        "big_count": big_count,
        "small_count": 6 - big_count,
        "span": max(reds) - min(reds),
        "max_consecutive_len": max_consecutive_len(reds),
        "zone_1_count": zone_1,
        "zone_2_count": zone_2,
        "zone_3_count": zone_3,
        "mod0_count": mod0,
        "mod1_count": mod1,
        "mod2_count": mod2,
        "ac_value": ac_value(reds),
        "has_gt31": any(red > 31 for red in reds),
        "birthday_ratio": sum(red <= 31 for red in reds) / 6,
    }


def compute_history_features(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        reds = [int(row[column]) for column in RED_COLUMNS]
        features = compute_red_features(reds)
        features["issue"] = row["issue"]
        records.append(features)
    return pd.DataFrame(records)
