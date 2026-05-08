from __future__ import annotations

import random
from typing import Any


def generate_blue(config: dict[str, Any], history_df=None, rng: random.Random | None = None) -> int:
    rng = rng or random.Random()
    mode = config.get("blue", {}).get("mode", "random")
    if mode == "random":
        return rng.randint(1, 16)
    if mode == "anti_popular":
        return rng.choice([10, 11, 12, 13, 14, 15, 16])
    if mode == "layered_rotation":
        if history_df is not None:
            zone = len(history_df) % 3
        else:
            zone = rng.randint(0, 2)
        if zone == 0:
            return rng.randint(1, 5)
        elif zone == 1:
            return rng.randint(6, 11)
        else:
            return rng.randint(12, 16)
    raise ValueError(f"Unsupported blue mode: {mode}")
