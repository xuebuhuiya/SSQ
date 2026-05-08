from src.filters import (
    pass_all_filters,
    pass_anti_collision_filter,
    pass_history_duplicate_filter,
    pass_zone_filter,
)


def test_anti_collision_requires_gt31(sample_config):
    assert pass_anti_collision_filter([1, 7, 12, 18, 25, 32], sample_config)
    assert not pass_anti_collision_filter([1, 7, 12, 18, 25, 31], sample_config)
    assert not pass_anti_collision_filter([1, 2, 3, 4, 5, 6], sample_config)


def test_zone_filter_limits_concentration(sample_config):
    assert pass_zone_filter([1, 8, 12, 19, 26, 32], sample_config)
    assert not pass_zone_filter([1, 2, 3, 4, 5, 32], sample_config)


def test_history_duplicate_filter_rejects_existing(sample_stats, sample_config):
    assert not pass_history_duplicate_filter([1, 7, 12, 18, 25, 32], 8, sample_stats, sample_config)
    assert pass_history_duplicate_filter([1, 7, 12, 18, 26, 32], 8, sample_stats, sample_config)


def test_pass_all_filters_returns_reasons(sample_stats, sample_config):
    passed, reasons = pass_all_filters([1, 2, 3, 4, 5, 6], 1, sample_stats, sample_config)

    assert not passed
    assert reasons
