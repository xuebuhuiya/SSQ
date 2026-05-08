from pathlib import Path

import pytest

from src.config import ConfigError, load_config, resolve_path


def test_load_config_uses_defaults_and_safe_yaml(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("generation:\n  num_tickets: 2\n", encoding="utf-8")

    config = load_config(config_path)

    assert config["generation"]["num_tickets"] == 2
    assert config["data"]["history_csv"] == "data/processed/ssq_history.csv"
    assert resolve_path(config, "data/output") == tmp_path / "data" / "output"


def test_invalid_config_rejected(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("generation:\n  num_tickets: 0\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="num_tickets"):
        load_config(config_path)


class TestCoverageConfigValidation:
    def test_pick_not_six_rejected(self, tmp_path: Path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "generation:\n  mode: coverage\n"
            "coverage:\n  red_pool_size: 8\n  max_tickets: 10\n  pick: 5\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="pick"):
            load_config(config_path)

    def test_red_pool_size_below_pick_rejected(self, tmp_path: Path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "generation:\n  mode: coverage\n"
            "coverage:\n  red_pool_size: 5\n  max_tickets: 10\n  pick: 6\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="red_pool_size"):
            load_config(config_path)

    def test_red_pool_size_above_33_rejected(self, tmp_path: Path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "generation:\n  mode: coverage\n"
            "coverage:\n  red_pool_size: 34\n  max_tickets: 10\n  pick: 6\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="red_pool_size"):
            load_config(config_path)

    def test_max_tickets_not_positive_rejected(self, tmp_path: Path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "generation:\n  mode: coverage\n"
            "coverage:\n  red_pool_size: 8\n  max_tickets: 0\n  pick: 6\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigError, match="max_tickets"):
            load_config(config_path)

    def test_valid_coverage_config_accepted(self, tmp_path: Path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "generation:\n  mode: coverage\n"
            "coverage:\n  red_pool_size: 10\n  max_tickets: 20\n  pick: 6\n",
            encoding="utf-8",
        )
        config = load_config(config_path)
        assert config["generation"]["mode"] == "coverage"
        assert config["coverage"]["red_pool_size"] == 10
