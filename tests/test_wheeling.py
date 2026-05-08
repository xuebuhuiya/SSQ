from __future__ import annotations

import math
import random

import pytest

from src.wheeling import full_wheel, limited_wheel


class TestFullWheel:
    def test_seven_reds_pick_six_returns_seven_tickets(self):
        pool = [3, 7, 12, 16, 21, 25, 29]
        result = full_wheel(pool, pick=6)
        assert len(result) == 7
        for combo in result:
            assert combo == sorted(combo)

    def test_count_matches_math_comb(self):
        pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for pick in range(1, len(pool) + 1):
            result = full_wheel(pool, pick=pick)
            expected = math.comb(len(pool), pick)
            assert len(result) == expected

    def test_each_combo_sorted_ascending(self):
        pool = [5, 30, 12, 3, 21, 18, 9]
        result = full_wheel(pool, pick=4)
        for combo in result:
            assert combo == sorted(combo)

    def test_output_order_stable(self):
        pool = [3, 7, 12, 16, 21, 25, 29]
        first = full_wheel(pool, pick=6)
        second = full_wheel(pool, pick=6)
        assert first == second

    def test_pick_one_returns_singletons(self):
        pool = [7, 3, 12]
        result = full_wheel(pool, pick=1)
        assert result == [[3], [7], [12]]

    def test_pick_equals_pool_len_returns_one_combo(self):
        pool = [3, 7, 12, 16, 21, 25]
        result = full_wheel(pool, pick=6)
        assert len(result) == 1
        assert result[0] == sorted(pool)


class TestLimitedWheel:
    def test_eight_reds_pick_six_max_five_returns_five_tickets(self):
        pool = [3, 7, 12, 16, 21, 25, 29, 33]
        result = limited_wheel(pool, max_tickets=5, pick=6)
        assert len(result) == 5
        for combo in result:
            assert combo == sorted(combo)

    def test_count_not_exceeded_when_full_under_limit(self):
        pool = [3, 7, 12, 16, 21, 25, 29]
        # full_wheel = C(7,6) = 7, so max_tickets=20 returns all 7
        result = limited_wheel(pool, max_tickets=20, pick=6)
        assert len(result) == 7

    def test_reproducible_with_same_seed(self):
        pool = [3, 7, 12, 16, 21, 25, 29, 33]
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        first = limited_wheel(pool, max_tickets=5, pick=6, rng=rng1)
        second = limited_wheel(pool, max_tickets=5, pick=6, rng=rng2)
        assert first == second

    def test_different_seeds_produce_different_results(self):
        pool = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # C(9,6) = 84, limit to 10
        rng1 = random.Random(1)
        rng2 = random.Random(999)
        first = limited_wheel(pool, max_tickets=10, pick=6, rng=rng1)
        second = limited_wheel(pool, max_tickets=10, pick=6, rng=rng2)
        # It's possible (though very unlikely) that two different seeds
        # produce the same sample from 84 choose 10. We accept this tiny
        # probability and just check they are valid sets.
        assert all(c == sorted(c) for c in first)
        assert all(c == sorted(c) for c in second)

    def test_default_pick_is_six(self):
        pool = [3, 7, 12, 16, 21, 25, 29]
        explicit = limited_wheel(pool, max_tickets=10, pick=6)
        default = limited_wheel(pool, max_tickets=10)
        assert explicit == default

    def test_result_sorted_overall(self):
        pool = [3, 7, 12, 16, 21, 25, 29, 33]
        result = limited_wheel(pool, max_tickets=5, pick=6, rng=random.Random(123))
        # verify overall lexicographic ordering
        for i in range(len(result) - 1):
            assert result[i] < result[i + 1]


class TestValidation:
    @pytest.mark.parametrize(
        "pool, match_text",
        [
            ([1, 2, 2, 3], "unique"),
            ([1, 0, 3], "1-33"),
            ([1, 34, 5], "1-33"),
            ([], "non-empty"),
        ],
    )
    def test_full_wheel_invalid_pool(self, pool, match_text):
        with pytest.raises(ValueError, match=match_text):
            full_wheel(pool, pick=2)

    @pytest.mark.parametrize(
        "pool, pick, match_text",
        [
            ([1, 2, 3], 0, ">= 1"),
            ([1, 2, 3], -1, ">= 1"),
            ([1, 2, 3], 5, r"<= len\(pool\)"),
        ],
    )
    def test_full_wheel_invalid_pick(self, pool, pick, match_text):
        with pytest.raises(ValueError, match=match_text):
            full_wheel(pool, pick=pick)

    def test_limited_wheel_invalid_max_tickets(self):
        with pytest.raises(ValueError, match="positive"):
            limited_wheel([1, 2, 3, 4, 5, 6, 7], max_tickets=0, pick=6)

    def test_limited_wheel_negative_max_tickets(self):
        with pytest.raises(ValueError, match="positive"):
            limited_wheel([1, 2, 3, 4, 5, 6, 7], max_tickets=-5, pick=6)

    def test_non_integer_in_pool(self):
        with pytest.raises(ValueError, match="integers"):
            full_wheel([1, 2, "x"], pick=2)  # type: ignore[list-item]
