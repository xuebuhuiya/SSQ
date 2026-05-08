import pytest

from src.generator import GenerationError, generate_random_reds, generate_tickets


def test_generate_random_reds_unique_sorted():
    reds = generate_random_reds()

    assert reds == sorted(reds)
    assert len(reds) == 6
    assert len(set(reds)) == 6
    assert all(1 <= red <= 33 for red in reds)


def test_generate_tickets_is_reproducible(sample_stats, sample_config):
    first = generate_tickets(3, sample_stats, sample_config)
    second = generate_tickets(3, sample_stats, sample_config)

    assert first.to_dict("records") == second.to_dict("records")
    assert list(first.columns) == [
        "ticket_id",
        "r1",
        "r2",
        "r3",
        "r4",
        "r5",
        "r6",
        "blue",
        "mode",
        "filters_used",
        "red_sum",
        "span",
        "odd_count",
        "big_count",
        "zone_pattern",
        "mod3_pattern",
        "ac_value",
        "notes",
    ]
    summary = first.attrs["candidate_pool_summary"]
    assert isinstance(summary, list)
    accepted_row = [r for r in summary if r["step"] == "accepted"][0]
    assert accepted_row["remaining_count"] == 3


def test_generate_tickets_raises_when_attempts_exhausted(sample_stats, sample_config):
    sample_config["generation"]["max_attempts"] = 1

    with pytest.raises(GenerationError):
        generate_tickets(5, sample_stats, sample_config)


def test_generate_coverage_tickets_is_reproducible(sample_stats, sample_coverage_config):
    first = generate_tickets(4, sample_stats, sample_coverage_config)
    second = generate_tickets(4, sample_stats, sample_coverage_config)

    assert first.to_dict("records") == second.to_dict("records")
    assert len(first) == 4
    assert set(first["mode"]) == {"coverage"}
    assert all(note == "coverage_wheeling_constrained" for note in first["notes"])


def test_generate_coverage_respects_max_tickets(sample_stats, sample_coverage_config):
    sample_coverage_config["generation"]["num_tickets"] = 5
    sample_coverage_config["coverage"]["max_tickets"] = 2

    df = generate_tickets(5, sample_stats, sample_coverage_config)

    assert len(df) == 2
    assert set(df["mode"]) == {"coverage"}


def test_generate_coverage_summary_mentions_wheeling(sample_stats, sample_coverage_config):
    df = generate_tickets(3, sample_stats, sample_coverage_config)
    summary = df.attrs["candidate_pool_summary"]

    assert summary[0]["step"] == "initial_random"
    assert "coverage" in summary[0]["notes"]
    assert summary[-1]["step"] == "accepted"
    assert "wheeling" in summary[-1]["notes"]


def test_generate_blue_compatible_signature():
    from src.blue_strategy import generate_blue

    config = {"blue": {"mode": "random"}}
    blue = generate_blue(config, None)
    assert 1 <= blue <= 16


def test_generate_blue_with_rng_reproducible():
    import random
    from src.blue_strategy import generate_blue

    config = {"blue": {"mode": "random"}}
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    assert generate_blue(config, rng=rng1) == generate_blue(config, rng=rng2)


def test_generate_blue_history_df_not_mistaken_for_rng():
    import pandas as pd
    from src.blue_strategy import generate_blue

    config = {"blue": {"mode": "random"}}
    df = pd.DataFrame({"blue": [1, 2, 3]})
    blue = generate_blue(config, df)
    assert 1 <= blue <= 16


def test_candidate_pool_summary_structure(sample_stats, sample_config):
    import pandas as pd

    df = generate_tickets(3, sample_stats, sample_config)
    summary = df.attrs["candidate_pool_summary"]
    assert isinstance(summary, list)
    assert all(
        {"step", "remaining_count", "removed_count", "remaining_ratio", "notes"}
        <= set(r.keys())
        for r in summary
    )
    steps = [r["step"] for r in summary]
    assert steps[0] == "initial_random"
    assert steps[-1] == "accepted"
    assert all(isinstance(r["remaining_ratio"], float) for r in summary)


def test_candidate_pool_summary_counts_add_up(sample_stats, sample_config):
    df = generate_tickets(3, sample_stats, sample_config)
    summary = df.attrs["candidate_pool_summary"]
    initial = summary[0]
    accepted = [r for r in summary if r["step"] == "accepted"][0]
    total_removed = sum(r["removed_count"] for r in summary)
    assert initial["remaining_count"] == accepted["remaining_count"] + total_removed


def test_coverage_raises_when_attempts_exhausted(sample_stats, sample_coverage_config):
    sample_coverage_config["generation"]["max_attempts"] = 1
    sample_coverage_config["generation"]["num_tickets"] = 999
    with pytest.raises(GenerationError):
        generate_tickets(999, sample_stats, sample_coverage_config)


def test_coverage_reds_all_valid(sample_stats, sample_coverage_config):
    df = generate_tickets(5, sample_stats, sample_coverage_config)
    for _, row in df.iterrows():
        reds = [row["r1"], row["r2"], row["r3"], row["r4"], row["r5"], row["r6"]]
        assert reds == sorted(reds)
        assert all(1 <= r <= 33 for r in reds)
        assert len(set(reds)) == 6


def test_coverage_blue_in_range(sample_stats, sample_coverage_config):
    df = generate_tickets(5, sample_stats, sample_coverage_config)
    assert all(1 <= b <= 16 for b in df["blue"])
