from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "data": {
        "history_csv": "data/processed/ssq_history.csv",
        "output_dir": "data/output",
        "encoding": "utf-8-sig",
        "fallback_encoding": "gbk",
    },
    "generation": {
        "mode": "standard",
        "num_tickets": 5,
        "random_seed": 42,
        "max_attempts": 100000,
    },
    "filters": {
        "enable_anti_collision": True,
        "enable_gt31_filter": False,
        "enable_position_quantile": True,
        "enable_shape_filter": True,
        "enable_zone_filter": True,
        "enable_mod3_filter": False,
        "enable_ac_filter": False,
        "enable_history_duplicate_filter": True,
        "enable_history_overlap5_filter": False,
    },
    "position_quantile": {"lower": 0.10, "upper": 0.90},
    "shape_quantile": {
        "red_sum_lower": 0.10,
        "red_sum_upper": 0.90,
        "span_lower": 0.10,
        "span_upper": 0.90,
        "ac_lower": 0.10,
        "ac_upper": 0.90,
    },
    "rules": {
        "max_consecutive_len": 3,
        "require_gt31": True,
        "max_zone_count": 4,
        "min_zone_covered": 2,
        "max_mod3_count": 4,
    },
    "coverage": {
        "red_pool_size": 8,
        "max_tickets": 28,
        "pick": 6,
    },
    "blue": {"mode": "random"},
}


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ConfigError("Config file must contain a YAML mapping.")

    config = deep_merge(DEFAULT_CONFIG, loaded)
    config["_config_path"] = str(config_path)
    config["_base_dir"] = str(config_path.parent)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    for section in ("data", "generation", "filters", "rules", "blue"):
        if section not in config or not isinstance(config[section], dict):
            raise ConfigError(f"Missing or invalid config section: {section}")

    num_tickets = int(config["generation"].get("num_tickets", 0))
    max_attempts = int(config["generation"].get("max_attempts", 0))
    if num_tickets <= 0:
        raise ConfigError("generation.num_tickets must be positive.")
    if max_attempts <= 0:
        raise ConfigError("generation.max_attempts must be positive.")

    for section, lower_key, upper_key in (
        ("position_quantile", "lower", "upper"),
        ("shape_quantile", "red_sum_lower", "red_sum_upper"),
        ("shape_quantile", "span_lower", "span_upper"),
    ):
        lower = float(config[section][lower_key])
        upper = float(config[section][upper_key])
        if not 0 <= lower <= upper <= 1:
            raise ConfigError(f"Invalid quantile range: {section}.{lower_key}/{upper_key}")

    mode = config["generation"].get("mode", "standard")
    if mode == "coverage":
        coverage = config.get("coverage", {})
        if not isinstance(coverage, dict):
            raise ConfigError("coverage config must be a mapping.")
        red_pool_size = int(coverage.get("red_pool_size", 0))
        pick = int(coverage.get("pick", 6))
        max_tickets = int(coverage.get("max_tickets", 0))
        if pick != 6:
            raise ConfigError(f"coverage.pick must be 6, got {pick}.")
        if red_pool_size < pick or red_pool_size > 33:
            raise ConfigError(f"coverage.red_pool_size must be between pick ({pick}) and 33, got {red_pool_size}.")
        if max_tickets <= 0:
            raise ConfigError("coverage.max_tickets must be positive.")


def resolve_path(config: dict[str, Any], value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return Path(config.get("_base_dir", ".")).resolve() / path
