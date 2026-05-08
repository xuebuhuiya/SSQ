import pandas as pd
import pytest

from src.stats import StatsError, build_stats


def test_build_stats_outputs_expected_keys(sample_history, sample_config):
    stats = build_stats(sample_history, sample_config)

    assert "r1" in stats["position_ranges"]
    assert stats["red_sum_range"][0] <= stats["red_sum_range"][1]
    assert len(stats["historical_red_sets"]) == len(sample_history)
    assert {"metric", "lower_value", "upper_value"}.issubset(stats["stats_summary"].columns)


def test_build_stats_rejects_empty_history(sample_config):
    with pytest.raises(StatsError, match="empty"):
        build_stats(pd.DataFrame(), sample_config)
