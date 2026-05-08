from src.features import ac_value, compute_red_features, max_consecutive_len, mod3_counts, zone_counts


def test_compute_red_features():
    features = compute_red_features([3, 8, 14, 19, 26, 32])

    assert features["red_sum"] == 102
    assert features["odd_count"] == 2
    assert features["big_count"] == 3
    assert features["span"] == 29
    assert features["has_gt31"] is True
    assert features["birthday_ratio"] == 5 / 6


def test_helper_counts():
    assert max_consecutive_len([1, 2, 3, 8, 9, 20]) == 3
    assert zone_counts([1, 8, 12, 19, 26, 33]) == (2, 2, 2)
    assert mod3_counts([3, 4, 5, 6, 7, 8]) == (2, 2, 2)
    assert ac_value([3, 8, 14, 19, 26, 32]) > 0
