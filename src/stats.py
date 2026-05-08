from __future__ import annotations

import math
from typing import Any

import pandas as pd

from .features import compute_history_features
from .preprocess import RED_COLUMNS


class StatsError(ValueError):
    """Raised when historical statistics cannot be built."""


def _range_from_quantile(series: pd.Series, lower: float, upper: float) -> list[int]:
    low = int(math.floor(float(series.quantile(lower))))
    high = int(math.ceil(float(series.quantile(upper))))
    return [low, high]


def _summary_row(metric: str, series: pd.Series, lower: float, upper: float) -> dict[str, Any]:
    return {
        "metric": metric,
        "lower_quantile": lower,
        "upper_quantile": upper,
        "lower_value": float(series.quantile(lower)),
        "upper_value": float(series.quantile(upper)),
        "mean": float(series.mean()),
        "std": float(series.std(ddof=0)),
        "min": float(series.min()),
        "max": float(series.max()),
    }


def build_stats(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    if df.empty:
        raise StatsError("History data is empty; cannot build statistics.")

    pos_lower = float(config["position_quantile"]["lower"])
    pos_upper = float(config["position_quantile"]["upper"])
    shape = config["shape_quantile"]
    sum_lower = float(shape["red_sum_lower"])
    sum_upper = float(shape["red_sum_upper"])
    span_lower = float(shape["span_lower"])
    span_upper = float(shape["span_upper"])
    ac_lower = float(shape.get("ac_lower", sum_lower))
    ac_upper = float(shape.get("ac_upper", sum_upper))

    history_features = compute_history_features(df)

    position_ranges = {
        column: _range_from_quantile(df[column], pos_lower, pos_upper)
        for column in RED_COLUMNS
    }
    red_sum_range = _range_from_quantile(history_features["red_sum"], sum_lower, sum_upper)
    span_range = _range_from_quantile(history_features["span"], span_lower, span_upper)
    ac_range = _range_from_quantile(history_features["ac_value"], ac_lower, ac_upper)

    historical_red_sets = {
        tuple(int(row[column]) for column in RED_COLUMNS)
        for _, row in df.iterrows()
    }
    historical_full_sets = {
        tuple([*(int(row[column]) for column in RED_COLUMNS), int(row["blue"])])
        for _, row in df.iterrows()
    }

    rows = []
    for column in RED_COLUMNS:
        rows.append(_summary_row(column, df[column], pos_lower, pos_upper))
    rows.append(_summary_row("red_sum", history_features["red_sum"], sum_lower, sum_upper))
    rows.append(_summary_row("span", history_features["span"], span_lower, span_upper))
    rows.append(_summary_row("ac_value", history_features["ac_value"], ac_lower, ac_upper))

    return {
        "position_ranges": position_ranges,
        "red_sum_range": red_sum_range,
        "span_range": span_range,
        "ac_range": ac_range,
        "historical_red_sets": historical_red_sets,
        "historical_full_sets": historical_full_sets,
        "historical_features": history_features,
        "stats_summary": pd.DataFrame(rows),
    }
