from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .config import load_config, resolve_path
from .data_loader import load_history_csv
from .generator import generate_tickets
from .stats import build_stats


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SSQ tickets with historical shape constraints.")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML.")
    parser.add_argument("--seed", type=int, help="Override generation.random_seed.")
    parser.add_argument("--num-tickets", type=int, help="Override generation.num_tickets.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        if args.seed is not None:
            config["generation"]["random_seed"] = args.seed
        if args.num_tickets is not None:
            config["generation"]["num_tickets"] = args.num_tickets

        history_csv = resolve_path(config, config["data"]["history_csv"])
        output_dir = resolve_path(config, config["data"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        history_df = load_history_csv(
            history_csv,
            encoding=config["data"].get("encoding", "utf-8-sig"),
            fallback_encoding=config["data"].get("fallback_encoding", "gbk"),
        )
        stats = build_stats(history_df, config)
        tickets = generate_tickets(int(config["generation"]["num_tickets"]), stats, config)

        tickets.to_csv(output_dir / "generated_numbers.csv", index=False, encoding="utf-8-sig")
        stats["stats_summary"].to_csv(output_dir / "stats_summary.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(tickets.attrs["candidate_pool_summary"]).to_csv(
            output_dir / "candidate_pool_summary.csv",
            index=False,
            encoding="utf-8-sig",
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
