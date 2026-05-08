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
    assert first.attrs["candidate_pool_summary"]["accepted_count"] == 3


def test_generate_tickets_raises_when_attempts_exhausted(sample_stats, sample_config):
    sample_config["generation"]["max_attempts"] = 1

    with pytest.raises(GenerationError):
        generate_tickets(5, sample_stats, sample_config)
