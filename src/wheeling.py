from __future__ import annotations

import random
from itertools import combinations


def _validate_pool(pool: list[int]) -> None:
    if not isinstance(pool, list) or not pool:
        raise ValueError("pool must be a non-empty list of integers.")
    if len(pool) != len(set(pool)):
        raise ValueError("pool must contain unique integers.")
    for n in pool:
        if not isinstance(n, int):
            raise ValueError(f"pool must contain integers, got {type(n).__name__}: {n}")
        if n < 1 or n > 33:
            raise ValueError(f"pool values must be in 1-33, got {n}.")


def _validate_pick(pick: int, pool_len: int) -> None:
    if not isinstance(pick, int) or pick < 1:
        raise ValueError(f"pick must be >= 1, got {pick}.")
    if pick > pool_len:
        raise ValueError(f"pick ({pick}) must be <= len(pool) ({pool_len}).")


def full_wheel(pool: list[int], pick: int = 6) -> list[list[int]]:
    _validate_pool(pool)
    _validate_pick(pick, len(pool))
    return [list(combo) for combo in combinations(sorted(pool), pick)]


def limited_wheel(
    pool: list[int],
    max_tickets: int,
    pick: int = 6,
    rng: random.Random | None = None,
) -> list[list[int]]:
    _validate_pool(pool)
    _validate_pick(pick, len(pool))
    if not isinstance(max_tickets, int) or max_tickets <= 0:
        raise ValueError(f"max_tickets must be a positive integer, got {max_tickets}.")

    all_combos = [list(combo) for combo in combinations(sorted(pool), pick)]
    if len(all_combos) <= max_tickets:
        return all_combos

    rng = rng or random.Random()
    sampled = rng.sample(all_combos, max_tickets)
    sampled.sort()
    return sampled
