"""Tests for the SSQ web application."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.web_app import create_app


def _write_web_config(tmp_path: Path, sample_config: dict[str, Any]) -> Path:
    """Write a temporary config YAML for use with create_app()."""
    cfg = dict(sample_config)
    cfg["generation"]["num_tickets"] = 2
    cfg["position_quantile"]["lower"] = 0.0
    cfg["position_quantile"]["upper"] = 1.0
    cfg["shape_quantile"]["red_sum_lower"] = 0.0
    cfg["shape_quantile"]["red_sum_upper"] = 1.0
    cfg["shape_quantile"]["span_lower"] = 0.0
    cfg["shape_quantile"]["span_upper"] = 1.0
    config_path = tmp_path / "web_config.yaml"
    config_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return config_path


def _default_filters() -> dict[str, bool]:
    return {
        "enable_position_quantile": True,
        "enable_shape_filter": True,
        "enable_anti_collision": True,
        "enable_gt31_filter": False,
        "enable_zone_filter": True,
        "enable_history_duplicate_filter": True,
        "enable_mod3_filter": False,
        "enable_ac_filter": False,
        "enable_history_overlap5_filter": False,
    }


class TestGetIndex:
    def test_returns_200(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_controls(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.get("/")
        text = resp.get_data(as_text=True)
        assert "双色球策略生成器" in text
        assert "生成号码" in text
        assert "位置分位数" in text
        assert "蓝球策略" in text
        assert "过滤策略" in text
        assert "本次生成的号码数量" in text
        assert "留空时每次生成都会自动使用新种子" in text
        assert "标准模式逐注随机" in text
        assert "控制和值、跨度、奇偶、大小和连号" in text
        assert "至少包含 32/33" in text
        assert "功能说明" in text
        assert "基础过滤" in text
        assert "撞号与扩展过滤" in text


class TestPostGenerate:
    def test_returns_requested_tickets(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post(
            "/api/generate",
            json={
                "num_tickets": 2,
                "seed": 42,
                "mode": "standard",
                "blue_mode": "random",
                "filters": _default_filters(),
            },
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["error"] is None
        assert len(payload["tickets"]) == 2
        assert payload["summary"][-1]["step"] == "accepted"
        t = payload["tickets"][0]
        for key in ("ticket_id", "r1", "r2", "r3", "r4", "r5", "r6", "blue", "red_sum", "span"):
            assert key in t

    def test_returns_error_for_zero_tickets(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post("/api/generate", json={"num_tickets": 0, "seed": 42})
        assert resp.status_code == 400
        assert "num_tickets" in resp.get_json()["error"]

    def test_returns_error_for_negative_tickets(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post("/api/generate", json={"num_tickets": -1, "seed": 42})
        assert resp.status_code == 400
        assert "num_tickets" in resp.get_json()["error"]

    def test_returns_error_for_non_integer_tickets(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post("/api/generate", json={"num_tickets": "abc", "seed": 42})
        assert resp.status_code == 400
        assert "num_tickets" in resp.get_json()["error"]

    def test_returns_error_for_exceeding_max_tickets(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post("/api/generate", json={"num_tickets": 51, "seed": 42})
        assert resp.status_code == 400
        assert "num_tickets" in resp.get_json()["error"]

    def test_coverage_mode_works(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post(
            "/api/generate",
            json={
                "num_tickets": 3,
                "seed": 42,
                "mode": "coverage",
                "blue_mode": "random",
                "filters": _default_filters(),
            },
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["error"] is None
        assert len(payload["tickets"]) == 3

    def test_anti_popular_blue_works(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post(
            "/api/generate",
            json={
                "num_tickets": 3,
                "seed": 42,
                "mode": "standard",
                "blue_mode": "anti_popular",
                "filters": _default_filters(),
            },
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["error"] is None
        for t in payload["tickets"]:
            assert 10 <= t["blue"] <= 16

    def test_missing_seed_uses_auto_seed(self, tmp_path: Path, sample_config: dict[str, Any]) -> None:
        app = create_app(_write_web_config(tmp_path, sample_config))
        client = app.test_client()
        resp = client.post(
            "/api/generate",
            json={
                "num_tickets": 2,
                "seed": None,
                "mode": "standard",
                "blue_mode": "random",
                "filters": _default_filters(),
            },
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["error"] is None
        assert len(payload["tickets"]) == 2
