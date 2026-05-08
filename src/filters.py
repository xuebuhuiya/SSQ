from __future__ import annotations

from typing import Any

from .features import ac_value, compute_red_features, mod3_counts, zone_counts
from .preprocess import RED_COLUMNS


def _is_arithmetic_sequence(reds: list[int]) -> bool:
    reds = sorted(reds)
    diffs = [right - left for left, right in zip(reds, reds[1:])]
    return len(set(diffs)) == 1


def pass_position_filter(reds: list[int], stats: dict[str, Any], config: dict[str, Any]) -> bool:
    ranges = stats["position_ranges"]
    for column, red in zip(RED_COLUMNS, sorted(reds)):
        low, high = ranges[column]
        if red < low or red > high:
            return False
    return True


def pass_shape_filter(reds: list[int], stats: dict[str, Any], config: dict[str, Any]) -> bool:
    features = compute_red_features(reds)
    red_low, red_high = stats["red_sum_range"]
    span_low, span_high = stats["span_range"]
    if not red_low <= features["red_sum"] <= red_high:
        return False
    if not span_low <= features["span"] <= span_high:
        return False
    if features["odd_count"] in (0, 6):
        return False
    if features["big_count"] in (0, 6):
        return False
    if features["max_consecutive_len"] > int(config["rules"]["max_consecutive_len"]):
        return False
    return True


def pass_anti_collision_filter(reds: list[int], config: dict[str, Any]) -> bool:
    reds = sorted(reds)
    if compute_red_features(reds)["max_consecutive_len"] >= 6:
        return False
    if _is_arithmetic_sequence(reds):
        return False
    return True


def pass_gt31_filter(reds: list[int], config: dict[str, Any]) -> bool:
    if not config["rules"].get("require_gt31", True):
        return True
    return any(red > 31 for red in reds)


def pass_zone_filter(reds: list[int], config: dict[str, Any]) -> bool:
    counts = zone_counts(reds)
    return (
        max(counts) <= int(config["rules"]["max_zone_count"])
        and sum(count > 0 for count in counts) >= int(config["rules"]["min_zone_covered"])
    )


def pass_mod3_filter(reds: list[int], config: dict[str, Any]) -> bool:
    return max(mod3_counts(reds)) <= int(config["rules"]["max_mod3_count"])


def pass_ac_filter(reds: list[int], stats: dict[str, Any], config: dict[str, Any]) -> bool:
    low, high = stats["ac_range"]
    value = ac_value(reds)
    return low <= value <= high


def pass_history_duplicate_filter(
    reds: list[int],
    blue: int | None,
    stats: dict[str, Any],
    config: dict[str, Any],
) -> bool:
    red_tuple = tuple(sorted(int(red) for red in reds))
    if red_tuple in stats["historical_red_sets"]:
        return False
    if blue is not None and (*red_tuple, int(blue)) in stats["historical_full_sets"]:
        return False
    if config["filters"].get("enable_history_overlap5_filter", False):
        candidate = set(red_tuple)
        for historical in stats["historical_red_sets"]:
            if len(candidate & set(historical)) >= 5:
                return False
    return True


def pass_all_filters(
    reds: list[int],
    blue: int | None,
    stats: dict[str, Any],
    config: dict[str, Any],
) -> tuple[bool, list[str]]:
    filters = config["filters"]
    reasons: list[str] = []
    if filters.get("enable_position_quantile", True) and not pass_position_filter(reds, stats, config):
        reasons.append("position_filter_failed")
    if filters.get("enable_shape_filter", True) and not pass_shape_filter(reds, stats, config):
        reasons.append("shape_filter_failed")
    if filters.get("enable_anti_collision", True) and not pass_anti_collision_filter(reds, config):
        reasons.append("anti_collision_filter_failed")
    if filters.get("enable_gt31_filter", False) and not pass_gt31_filter(reds, config):
        reasons.append("gt31_filter_failed")
    if filters.get("enable_zone_filter", True) and not pass_zone_filter(reds, config):
        reasons.append("zone_filter_failed")
    if filters.get("enable_mod3_filter", False) and not pass_mod3_filter(reds, config):
        reasons.append("mod3_filter_failed")
    if filters.get("enable_ac_filter", False) and not pass_ac_filter(reds, stats, config):
        reasons.append("ac_filter_failed")
    if filters.get("enable_history_duplicate_filter", True) and not pass_history_duplicate_filter(reds, blue, stats, config):
        reasons.append("history_duplicate_filter_failed")
    return (not reasons, reasons)


def enabled_filter_names(config: dict[str, Any]) -> list[str]:
    mapping = {
        "enable_position_quantile": "position",
        "enable_shape_filter": "shape",
        "enable_anti_collision": "anti_collision",
        "enable_gt31_filter": "gt31",
        "enable_zone_filter": "zone",
        "enable_mod3_filter": "mod3",
        "enable_ac_filter": "ac",
        "enable_history_duplicate_filter": "history_duplicate",
        "enable_history_overlap5_filter": "history_overlap5",
    }
    return [name for key, name in mapping.items() if config["filters"].get(key, False)]
