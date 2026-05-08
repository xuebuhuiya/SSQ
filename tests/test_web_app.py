from pathlib import Path

import yaml

from src.web_app import create_app


def _write_web_config(tmp_path: Path, sample_config: dict) -> Path:
    config_path = tmp_path / "web_config.yaml"
    sample_config["generation"]["num_tickets"] = 2
    sample_config["position_quantile"]["lower"] = 0.0
    sample_config["position_quantile"]["upper"] = 1.0
    sample_config["shape_quantile"]["red_sum_lower"] = 0.0
    sample_config["shape_quantile"]["red_sum_upper"] = 1.0
    sample_config["shape_quantile"]["span_lower"] = 0.0
    sample_config["shape_quantile"]["span_upper"] = 1.0
    config_path.write_text(yaml.safe_dump(sample_config), encoding="utf-8")
    return config_path


def test_web_index_returns_tool_controls(tmp_path: Path, sample_config: dict):
    app = create_app(_write_web_config(tmp_path, sample_config))
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "双色球策略生成器" in text
    assert "生成号码" in text
    assert "位置分位数" in text


def test_generate_api_returns_requested_tickets(tmp_path: Path, sample_config: dict):
    app = create_app(_write_web_config(tmp_path, sample_config))
    client = app.test_client()

    response = client.post(
        "/api/generate",
        json={
            "num_tickets": 2,
            "seed": 42,
            "mode": "standard",
            "blue_mode": "random",
            "filters": {
                "enable_position_quantile": True,
                "enable_shape_filter": True,
                "enable_anti_collision": True,
                "enable_zone_filter": True,
                "enable_history_duplicate_filter": True,
                "enable_mod3_filter": False,
                "enable_ac_filter": False,
                "enable_history_overlap5_filter": False,
            },
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["error"] is None
    assert len(payload["tickets"]) == 2
    assert payload["summary"][-1]["step"] == "accepted"


def test_generate_api_rejects_invalid_num_tickets(tmp_path: Path, sample_config: dict):
    app = create_app(_write_web_config(tmp_path, sample_config))
    client = app.test_client()

    response = client.post("/api/generate", json={"num_tickets": 0})

    assert response.status_code == 400
    assert "num_tickets" in response.get_json()["error"]
