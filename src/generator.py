from __future__ import annotations

import random
from typing import Any

import pandas as pd

from .blue_strategy import generate_blue
from .features import compute_red_features, mod3_counts, zone_counts
from .filters import enabled_filter_names, pass_all_filters


class GenerationError(RuntimeError):
    """Raised when tickets cannot be generated under current constraints."""


def generate_random_reds(rng: random.Random | None = None) -> list[int]:
    rng = rng or random.Random()
    return sorted(rng.sample(range(1, 34), 6))


def _ticket_record(ticket_id: int, reds: list[int], blue: int, config: dict[str, Any]) -> dict[str, Any]:
    features = compute_red_features(reds)
    zones = zone_counts(reds)
    mods = mod3_counts(reds)
    return {
        "ticket_id": ticket_id,
        "r1": reds[0],
        "r2": reds[1],
        "r3": reds[2],
        "r4": reds[3],
        "r5": reds[4],
        "r6": reds[5],
        "blue": blue,
        "mode": config["generation"].get("mode", "standard"),
        "filters_used": ",".join(enabled_filter_names(config)),
        "red_sum": features["red_sum"],
        "span": features["span"],
        "odd_count": features["odd_count"],
        "big_count": features["big_count"],
        "zone_pattern": "-".join(str(count) for count in zones),
        "mod3_pattern": "-".join(str(count) for count in mods),
        "ac_value": features["ac_value"],
        "notes": "historical_shape_constrained_random",
    }


def generate_ticket(
    stats: dict[str, Any],
    config: dict[str, Any],
    rng: random.Random | None = None,
) -> dict[str, Any]:
    rng = rng or random.Random(config["generation"].get("random_seed"))
    max_attempts = int(config["generation"]["max_attempts"])
    for _ in range(max_attempts):
        reds = generate_random_reds(rng)
        blue = generate_blue(config, rng=rng)
        passed, reasons = pass_all_filters(reds, blue, stats, config)
        if passed:
            return _ticket_record(1, reds, blue, config)
    raise GenerationError(f"Unable to generate a ticket within max_attempts={max_attempts}.")


def _build_candidate_pool_summary(
    filtered_attempts: int,
    accepted: int,
    fail_counts: dict[str, int],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    filter_order = [
        ("position_filter_failed", "position_filter", "enable_position_quantile"),
        ("shape_filter_failed", "shape_filter", "enable_shape_filter"),
        ("anti_collision_filter_failed", "anti_collision_filter", "enable_anti_collision"),
        ("zone_filter_failed", "zone_filter", "enable_zone_filter"),
        ("mod3_filter_failed", "mod3_filter", "enable_mod3_filter"),
        ("ac_filter_failed", "ac_filter", "enable_ac_filter"),
        ("history_duplicate_filter_failed", "history_duplicate_filter", "enable_history_duplicate_filter"),
    ]
    enabled_steps = [
        (reason, step)
        for reason, step, config_key in filter_order
        if config["filters"].get(config_key, False)
    ]

    rows: list[dict[str, Any]] = []
    remaining = filtered_attempts
    rows.append({
        "step": "initial_random",
        "remaining_count": remaining,
        "removed_count": 0,
        "remaining_ratio": 1.0,
        "notes": "attempts reaching filters (excl. intra-batch duplicates)",
    })
    for reason, step in enabled_steps:
        removed = fail_counts.get(reason, 0)
        remaining -= removed
        rows.append({
            "step": step,
            "remaining_count": remaining,
            "removed_count": removed,
            "remaining_ratio": round(remaining / filtered_attempts, 6) if filtered_attempts else 0.0,
            "notes": reason,
        })
    reported_failures = {reason for reason, _ in enabled_steps}
    other_removed = sum(
        count for reason, count in fail_counts.items() if reason not in reported_failures
    )
    if other_removed:
        remaining -= other_removed
        rows.append({
            "step": "other_filter",
            "remaining_count": remaining,
            "removed_count": other_removed,
            "remaining_ratio": round(remaining / filtered_attempts, 6) if filtered_attempts else 0.0,
            "notes": "unmapped filter failures",
        })
    rows.append({
        "step": "accepted",
        "remaining_count": accepted,
        "removed_count": 0,
        "remaining_ratio": round(accepted / filtered_attempts, 6) if filtered_attempts else 0.0,
        "notes": "passed all filters",
    })
    return rows


def generate_tickets(n: int, stats: dict[str, Any], config: dict[str, Any]) -> pd.DataFrame:
    rng = random.Random(config["generation"].get("random_seed"))
    max_attempts = int(config["generation"]["max_attempts"])
    records: list[dict[str, Any]] = []
    attempts = 0
    seen: set[tuple[int, ...]] = set()
    fail_counts: dict[str, int] = {}
    filtered_attempts = 0

    while len(records) < n and attempts < max_attempts:
        attempts += 1
        reds = generate_random_reds(rng)
        blue = generate_blue(config, rng=rng)
        key = (*reds, blue)
        if key in seen:
            continue
        filtered_attempts += 1
        passed, reasons = pass_all_filters(reds, blue, stats, config)
        if not passed:
            fail_counts[reasons[0]] = fail_counts.get(reasons[0], 0) + 1
            continue
        seen.add(key)
        records.append(_ticket_record(len(records) + 1, reds, blue, config))

    if len(records) < n:
        raise GenerationError(
            f"Generated {len(records)} of {n} tickets within max_attempts={max_attempts}."
        )

    df = pd.DataFrame(records)
    df.attrs["candidate_pool_summary"] = _build_candidate_pool_summary(
        filtered_attempts, len(records), fail_counts, config
    )
    return df
