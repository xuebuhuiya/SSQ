from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.config import DEFAULT_CONFIG, deep_merge
from src.data_loader import load_history_csv
from src.stats import build_stats


@pytest.fixture
def sample_rows() -> list[dict]:
    return [
        {"issue": "2024001", "date": "2024-01-01", "r1": 1, "r2": 7, "r3": 12, "r4": 18, "r5": 25, "r6": 32, "blue": 8},
        {"issue": "2024002", "date": "2024-01-03", "r1": 2, "r2": 8, "r3": 13, "r4": 19, "r5": 26, "r6": 33, "blue": 4},
        {"issue": "2024003", "date": "2024-01-05", "r1": 3, "r2": 9, "r3": 14, "r4": 20, "r5": 27, "r6": 32, "blue": 11},
        {"issue": "2024004", "date": "2024-01-08", "r1": 4, "r2": 10, "r3": 15, "r4": 21, "r5": 28, "r6": 33, "blue": 1},
        {"issue": "2024005", "date": "2024-01-10", "r1": 5, "r2": 11, "r3": 16, "r4": 22, "r5": 29, "r6": 32, "blue": 16},
        {"issue": "2024006", "date": "2024-01-12", "r1": 6, "r2": 12, "r3": 17, "r4": 23, "r5": 30, "r6": 33, "blue": 7},
        {"issue": "2024007", "date": "2024-01-15", "r1": 1, "r2": 8, "r3": 15, "r4": 22, "r5": 29, "r6": 33, "blue": 9},
        {"issue": "2024008", "date": "2024-01-17", "r1": 2, "r2": 9, "r3": 16, "r4": 23, "r5": 30, "r6": 32, "blue": 10},
        {"issue": "2024009", "date": "2024-01-19", "r1": 3, "r2": 10, "r3": 17, "r4": 24, "r5": 31, "r6": 33, "blue": 12},
        {"issue": "2024010", "date": "2024-01-22", "r1": 4, "r2": 11, "r3": 18, "r4": 25, "r5": 31, "r6": 32, "blue": 6},
    ]


@pytest.fixture
def sample_csv(tmp_path: Path, sample_rows: list[dict]) -> Path:
    path = tmp_path / "history.csv"
    pd.DataFrame(sample_rows).to_csv(path, index=False)
    return path


@pytest.fixture
def sample_config(tmp_path: Path, sample_csv: Path) -> dict:
    return deep_merge(
        DEFAULT_CONFIG,
        {
            "data": {
                "history_csv": str(sample_csv),
                "output_dir": str(tmp_path / "output"),
            },
            "position_quantile": {"lower": 0.0, "upper": 1.0},
            "shape_quantile": {
                "red_sum_lower": 0.0,
                "red_sum_upper": 1.0,
                "span_lower": 0.0,
                "span_upper": 1.0,
                "ac_lower": 0.0,
                "ac_upper": 1.0,
            },
            "generation": {"num_tickets": 3, "random_seed": 123, "max_attempts": 50000},
        },
    )


@pytest.fixture
def sample_history(sample_csv: Path) -> pd.DataFrame:
    return load_history_csv(sample_csv)


@pytest.fixture
def sample_stats(sample_history: pd.DataFrame, sample_config: dict) -> dict:
    return build_stats(sample_history, sample_config)
