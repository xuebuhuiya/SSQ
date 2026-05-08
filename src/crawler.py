from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd


DEFAULT_HISTORY_URL = (
    "https://datachart.500.com/ssq/history/newinc/history.php?start={start}&end={end}"
)
DEFAULT_START = "03001"
DEFAULT_END = "99999"
REQUIRED_OUTPUT_COLUMNS = [
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


class CrawlerError(RuntimeError):
    """Raised when history data cannot be fetched or parsed."""


def _clean_cell(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return value.replace("\xa0", "").strip()


def _clean_number(value: str) -> int | None:
    value = value.replace(",", "").strip()
    if not value:
        return None
    return int(value)


def parse_history_html(content: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row_html in re.findall(r"<tr[^>]*class=[\"']?t_tr[^>]*>(.*?)</tr>", content, re.I | re.S):
        row_html = re.sub(r"<!--.*?-->", "", row_html, flags=re.S)
        cells = [_clean_cell(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.I | re.S)]
        if len(cells) < 16:
            continue

        try:
            reds = [int(value) for value in cells[1:7]]
            blue = int(cells[7])
            if len(reds) != 6 or len(set(reds)) != 6:
                raise ValueError("red balls must be 6 unique values")
            if any(red < 1 or red > 33 for red in reds):
                raise ValueError("red ball out of range")
            if blue < 1 or blue > 16:
                raise ValueError("blue ball out of range")
        except ValueError as exc:
            raise CrawlerError(f"Invalid draw row for issue {cells[0]!r}: {exc}") from exc

        rows.append(
            {
                "issue": cells[0],
                "date": cells[15],
                "r1": reds[0],
                "r2": reds[1],
                "r3": reds[2],
                "r4": reds[3],
                "r5": reds[4],
                "r6": reds[5],
                "blue": blue,
                "sales": _clean_number(cells[14]),
                "pool": _clean_number(cells[9]),
            }
        )

    if not rows:
        raise CrawlerError("No history rows found in HTML content.")

    df = pd.DataFrame(rows, columns=REQUIRED_OUTPUT_COLUMNS)
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(subset=["issue"], keep="last")
    return df.sort_values("issue").reset_index(drop=True)


def fetch_history_html(
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    url_template: str = DEFAULT_HISTORY_URL,
    timeout: int = 30,
) -> str:
    url = url_template.format(start=start, end=end)
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; SSQStrategyCrawler/1.0)",
            "Referer": "https://datachart.500.com/ssq/history/history.shtml",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
    except URLError as exc:
        raise CrawlerError(f"Failed to fetch history data: {exc}") from exc

    for encoding in (charset, "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def crawl_history(
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    url_template: str = DEFAULT_HISTORY_URL,
    timeout: int = 30,
) -> pd.DataFrame:
    return parse_history_html(fetch_history_html(start, end, url_template, timeout))


def save_history_csv(df: pd.DataFrame, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch SSQ historical draw data.")
    parser.add_argument("--start", default=DEFAULT_START, help="Start issue, e.g. 03001.")
    parser.add_argument("--end", default=DEFAULT_END, help="End issue, e.g. 99999.")
    parser.add_argument("--output", default="data/processed/ssq_history.csv", help="Output CSV path.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        df = crawl_history(args.start, args.end, timeout=args.timeout)
        path = save_history_csv(df, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved {len(df)} SSQ history rows to {path}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
