from pathlib import Path

import yaml

from src.main import run


def test_main_writes_expected_outputs(tmp_path: Path, sample_config: dict):
    config_path = tmp_path / "config.yaml"
    output_dir = tmp_path / "output"
    sample_config["data"]["output_dir"] = str(output_dir)
    sample_config["generation"]["num_tickets"] = 2
    config_path.write_text(yaml.safe_dump(sample_config), encoding="utf-8")

    exit_code = run(["--config", str(config_path)])

    assert exit_code == 0
    assert (output_dir / "generated_numbers.csv").exists()
    assert (output_dir / "stats_summary.csv").exists()
    assert (output_dir / "candidate_pool_summary.csv").exists()


def test_main_returns_error_for_missing_history(tmp_path: Path, sample_config: dict):
    config_path = tmp_path / "config.yaml"
    sample_config["data"]["history_csv"] = str(tmp_path / "missing.csv")
    config_path.write_text(yaml.safe_dump(sample_config), encoding="utf-8")

    assert run(["--config", str(config_path)]) == 1


def test_main_writes_coverage_outputs(tmp_path: Path, sample_coverage_config: dict):
    config_path = tmp_path / "coverage.yaml"
    output_dir = tmp_path / "coverage-output"
    sample_coverage_config["data"]["output_dir"] = str(output_dir)
    sample_coverage_config["generation"]["num_tickets"] = 2
    config_path.write_text(yaml.safe_dump(sample_coverage_config), encoding="utf-8")

    exit_code = run(["--config", str(config_path)])

    assert exit_code == 0
    generated = (output_dir / "generated_numbers.csv").read_text(encoding="utf-8-sig")
    summary = (output_dir / "candidate_pool_summary.csv").read_text(encoding="utf-8-sig")
    assert "coverage" in generated
    assert "initial_random" in summary
    assert "accepted" in summary
