from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocess import normalize_history


def load_history_csv(
    path: str | Path,
    encoding: str = "utf-8-sig",
    fallback_encoding: str | None = "gbk",
) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"History CSV not found: {csv_path}")

    try:
        raw = pd.read_csv(csv_path, encoding=encoding)
    except UnicodeDecodeError:
        if not fallback_encoding:
            raise
        raw = pd.read_csv(csv_path, encoding=fallback_encoding)

    return normalize_history(raw)
