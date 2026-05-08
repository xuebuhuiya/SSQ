from __future__ import annotations

import random

import pandas as pd
import pytest

from src.blue_strategy import generate_blue


def test_random_returns_1_to_16():
    config = {"blue": {"mode": "random"}}
    rng = random.Random(42)
    for _ in range(100):
        blue = generate_blue(config, rng=rng)
        assert 1 <= blue <= 16


def test_anti_popular_returns_10_to_16():
    config = {"blue": {"mode": "anti_popular"}}
    rng = random.Random(42)
    for _ in range(100):
        blue = generate_blue(config, rng=rng)
        assert 10 <= blue <= 16


def test_layered_rotation_covers_multiple_zones():
    config = {"blue": {"mode": "layered_rotation"}}
    zones = set()
    for length in [0, 1, 2]:
        df = pd.DataFrame({"blue": range(length)})
        blue = generate_blue(config, df)
        if 1 <= blue <= 5:
            zones.add("low")
        elif 6 <= blue <= 11:
            zones.add("mid")
        else:
            zones.add("high")
    assert len(zones) >= 2


def test_layered_rotation_reproducible():
    config = {"blue": {"mode": "layered_rotation"}}
    df = pd.DataFrame({"blue": [1, 2, 3]})

    rng1 = random.Random(42)
    rng2 = random.Random(42)
    blue1 = generate_blue(config, df, rng=rng1)
    blue2 = generate_blue(config, df, rng=rng2)
    assert blue1 == blue2


def test_unsupported_mode_raises_value_error():
    config = {"blue": {"mode": "nonexistent_mode"}}
    with pytest.raises(ValueError, match="Unsupported blue mode"):
        generate_blue(config)
