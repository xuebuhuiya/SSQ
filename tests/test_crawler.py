from pathlib import Path

import pandas as pd
import pytest

from src.crawler import CrawlerError, parse_history_html, save_history_csv


SAMPLE_HTML = """
<tbody id="tdata">
<tr class="t_tr1"><!--<td>2</td>--><td>25100</td><td class="t_cfont2">12</td><td class="t_cfont2">16</td><td class="t_cfont2">17</td><td class="t_cfont2">25</td><td class="t_cfont2">30</td><td class="t_cfont2">31</td><td class="t_cfont4">16</td><td>&nbsp;</td><td>2,597,220,563</td><td>11</td><td>7,099,632</td><td>107</td><td>269,812</td><td>383,791,808</td><td>2025-08-31</td></tr>
<tr class="t_tr2"><td>25099</td><td>05</td><td>06</td><td>12</td><td>18</td><td>23</td><td>33</td><td>08</td><td>&nbsp;</td><td>2,554,111,000</td><td>8</td><td>6,000,000</td><td>99</td><td>200,000</td><td>373,000,000</td><td>2025-08-28</td></tr>
</tbody>
"""


def test_parse_history_html_extracts_standard_columns():
    df = parse_history_html(SAMPLE_HTML)

    assert list(df.columns) == [
        "issue",
        "date",
        "r1",
        "r2",
        "r3",
        "r4",
        "r5",
        "r6",
        "blue",
        "sales",
        "pool",
    ]
    assert df.loc[0, "issue"] == "25099"
    assert df.loc[0, ["r1", "r2", "r3", "r4", "r5", "r6"]].tolist() == [5, 6, 12, 18, 23, 33]
    assert df.loc[0, "blue"] == 8
    assert df.loc[0, "sales"] == 373000000
    assert df.loc[0, "pool"] == 2554111000
    assert df.loc[1, "date"] == "2025-08-31"


def test_parse_history_html_rejects_empty_content():
    with pytest.raises(CrawlerError, match="No history rows"):
        parse_history_html("<html></html>")


def test_parse_history_html_rejects_invalid_numbers():
    html = SAMPLE_HTML.replace("<td class=\"t_cfont4\">16</td>", "<td class=\"t_cfont4\">99</td>", 1)

    with pytest.raises(CrawlerError, match="blue ball out of range"):
        parse_history_html(html)


def test_save_history_csv_round_trips(tmp_path: Path):
    df = parse_history_html(SAMPLE_HTML)
    path = save_history_csv(df, tmp_path / "processed" / "ssq_history.csv")

    loaded = pd.read_csv(path, dtype={"issue": str})
    assert path.exists()
    assert len(loaded) == 2
    assert loaded.loc[0, "issue"] == "25099"
