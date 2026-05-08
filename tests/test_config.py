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
