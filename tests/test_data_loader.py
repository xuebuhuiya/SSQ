import pandas as pd
import pytest

from src.data_loader import load_history_csv
from src.preprocess import HistoryDataError, normalize_history


def test_load_history_csv_sorts_reds_and_deduplicates_issue(tmp_path):
    path = tmp_path / "history.csv"
    pd.DataFrame(
        [
            {"issue": "1", "date": "2024-01-01", "r1": 6, "r2": 1, "r3": 5, "r4": 2, "r5": 4, "r6": 3, "blue": 8},
            {"issue": "1", "date": "2024-01-02", "r1": 7, "r2": 2, "r3": 6, "r4": 3, "r5": 5, "r6": 4, "blue": 9},
        ]
    ).to_csv(path, index=False)

    df = load_history_csv(path)

    assert len(df) == 1
    assert df.loc[0, ["r1", "r2", "r3", "r4", "r5", "r6"]].tolist() == [2, 3, 4, 5, 6, 7]
    assert df.loc[0, "blue"] == 9


def test_normalize_history_rejects_invalid_red(sample_rows):
    sample_rows[0]["r1"] = 34
    df = pd.DataFrame(sample_rows)

    with pytest.raises(HistoryDataError, match="Red ball out of range"):
        normalize_history(df)


def test_normalize_history_rejects_missing_columns(sample_rows):
    df = pd.DataFrame(sample_rows).drop(columns=["blue"])

    with pytest.raises(HistoryDataError, match="Missing required columns"):
        normalize_history(df)
