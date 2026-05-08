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
        blue = generate_blue(config, rng)
        passed, _ = pass_all_filters(reds, blue, stats, config)
        if passed:
            return _ticket_record(1, reds, blue, config)
    raise GenerationError(f"Unable to generate a ticket within max_attempts={max_attempts}.")


def generate_tickets(n: int, stats: dict[str, Any], config: dict[str, Any]) -> pd.DataFrame:
    rng = random.Random(config["generation"].get("random_seed"))
    max_attempts = int(config["generation"]["max_attempts"])
    records: list[dict[str, Any]] = []
    attempts = 0
    seen: set[tuple[int, ...]] = set()

    while len(records) < n and attempts < max_attempts:
        attempts += 1
        reds = generate_random_reds(rng)
        blue = generate_blue(config, rng)
        key = (*reds, blue)
        if key in seen:
            continue
        passed, _ = pass_all_filters(reds, blue, stats, config)
        if not passed:
            continue
        seen.add(key)
        records.append(_ticket_record(len(records) + 1, reds, blue, config))

    if len(records) < n:
        raise GenerationError(
            f"Generated {len(records)} of {n} tickets within max_attempts={max_attempts}."
        )

    df = pd.DataFrame(records)
    df.attrs["candidate_pool_summary"] = {
        "generation_attempts": attempts,
        "accepted_count": len(records),
        "rejected_count": attempts - len(records),
        "acceptance_ratio": len(records) / attempts if attempts else 0.0,
        "notes": "random_candidates_with_enabled_filters",
    }
    return df
