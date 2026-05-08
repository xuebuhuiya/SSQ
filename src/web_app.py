from __future__ import annotations

import argparse
import copy
import json as _stdlib_json
import random
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, render_template_string, request

from .config import load_config, resolve_path
from .data_loader import load_history_csv
from .generator import generate_tickets
from .stats import build_stats


HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>双色球策略生成器</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #d8dee9;
      --red: #c92a3a;
      --blue: #1f5fbf;
      --green: #12715b;
      --shadow: 0 10px 30px rgba(23, 32, 51, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    header {
      padding: 22px 28px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 {
      margin: 0 0 6px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }
    header p {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }
    main {
      display: grid;
      grid-template-columns: 340px minmax(0, 1fr);
      gap: 18px;
      padding: 18px;
      max-width: 1280px;
      margin: 0 auto;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .controls { padding: 18px; }
    .results { padding: 18px; min-width: 0; }
    h2 {
      margin: 0 0 14px;
      font-size: 16px;
      font-weight: 700;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin: 14px 0 6px;
    }
    input[type="number"], select {
      width: 100%;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 10px;
      font: inherit;
      background: white;
    }
    fieldset {
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 16px 0 0;
      padding: 10px;
    }
    legend {
      padding: 0 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }
    .check {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 30px;
      color: var(--text);
      font-size: 14px;
      font-weight: 500;
      margin: 0;
    }
    .hint {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }
    .help-list {
      margin: 8px 0 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }
    .help-list li { margin: 3px 0; }
    .actions {
      display: flex;
      gap: 10px;
      margin-top: 18px;
    }
    button {
      height: 40px;
      border: 0;
      border-radius: 6px;
      padding: 0 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    .primary {
      background: var(--red);
      color: white;
      flex: 1;
    }
    .secondary {
      background: #eef2f7;
      color: var(--text);
    }
    .status {
      margin: 0 0 12px;
      min-height: 22px;
      color: var(--muted);
      font-size: 14px;
    }
    .status.error { color: var(--red); }
    .status.ok { color: var(--green); }
    .table-wrap {
      width: 100%;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 760px;
      background: white;
    }
    th, td {
      padding: 10px 9px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 13px;
      white-space: nowrap;
    }
    th { background: #f8fafc; color: var(--muted); font-weight: 700; }
    .reds span, .blue-ball {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      margin-right: 4px;
      border-radius: 50%;
      color: white;
      font-size: 12px;
      font-weight: 700;
    }
    .reds span { background: var(--red); }
    .blue-ball { background: var(--blue); }
    .summary {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fbfcff;
    }
    .metric strong { display: block; font-size: 18px; }
    .metric span { color: var(--muted); font-size: 12px; }
    .guide {
      margin-top: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcff;
      padding: 14px;
    }
    .guide h3 {
      margin: 0 0 10px;
      font-size: 15px;
    }
    .guide-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .guide-block {
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }
    .guide-block:first-child,
    .guide-block:nth-child(2) {
      border-top: 0;
      padding-top: 0;
    }
    .guide-block h4 {
      margin: 0 0 6px;
      font-size: 13px;
    }
    .guide-block p,
    .guide-block li {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }
    .guide-block p { margin: 0; }
    .guide-block ul {
      margin: 0;
      padding-left: 18px;
    }
    @media (max-width: 840px) {
      main { grid-template-columns: 1fr; padding: 12px; }
      header { padding: 18px 14px 12px; }
      .summary { grid-template-columns: 1fr; }
      .guide-grid { grid-template-columns: 1fr; }
      .guide-block:nth-child(2) {
        border-top: 1px solid var(--line);
        padding-top: 10px;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>双色球策略生成器</h1>
    <p>基于历史形态约束和随机生成，不预测开奖结果，请固定预算理性使用。</p>
  </header>
  <main>
    <section class="controls">
      <h2>生成设置</h2>
      <form id="strategyForm">
        <label for="numTickets">注数</label>
        <input id="numTickets" name="num_tickets" type="number" min="1" max="50" value="5">
        <p class="hint">本次生成的号码数量；注数越多，程序会尝试更多候选组合。</p>

        <label for="seed">随机种子</label>
        <input id="seed" name="seed" type="number" min="0" placeholder="留空则每次自动随机">
        <p class="hint">留空时每次生成都会自动使用新种子；填写数字时可复现同一组结果。</p>

        <label for="mode">生成模式</label>
        <select id="mode" name="mode">
          <option value="standard">标准模式</option>
          <option value="coverage">覆盖模式</option>
        </select>
        <p class="hint">标准模式逐注随机；覆盖模式先生成红球池，再用轮转组合生成多注。</p>

        <label for="blueMode">蓝球策略</label>
        <select id="blueMode" name="blue_mode">
          <option value="random">随机</option>
          <option value="anti_popular">反大众</option>
          <option value="layered_rotation">分层轮换</option>
        </select>
        <p class="hint">随机为 1-16 均匀抽取；反大众偏向 10-16；分层轮换在低中高区间切换。</p>

        <fieldset>
          <legend>过滤策略</legend>
          <label class="check"><input type="checkbox" name="enable_position_quantile" checked> 位置分位数</label>
          <label class="check"><input type="checkbox" name="enable_shape_filter" checked> 和值/跨度/奇偶/连号</label>
          <label class="check"><input type="checkbox" name="enable_anti_collision" checked> 反撞号</label>
          <label class="check"><input type="checkbox" name="enable_zone_filter" checked> 三区分布</label>
          <label class="check"><input type="checkbox" name="enable_history_duplicate_filter" checked> 历史重复排除</label>
          <label class="check"><input type="checkbox" name="enable_mod3_filter"> 012 路分布</label>
          <label class="check"><input type="checkbox" name="enable_ac_filter"> AC 值</label>
          <label class="check"><input type="checkbox" name="enable_history_overlap5_filter"> 历史重合 5 红排除</label>
          <ul class="help-list">
            <li>位置分位数：限制第 1 到第 6 个红球落在历史主区间。</li>
            <li>形态过滤：控制和值、跨度、奇偶、大小和连号不过度极端。</li>
            <li>反撞号：减少生日号、顺子号、等差号等大众化组合。</li>
            <li>三区分布：避免红球过度集中在某一区间。</li>
            <li>历史重复：排除历史已出现过的红球组合。</li>
            <li>012 路和 AC 值：用于进一步控制余数分布和离散度，默认关闭。</li>
          </ul>
        </fieldset>

        <div class="actions">
          <button class="primary" type="submit" id="generateBtn">生成号码</button>
          <button class="secondary" type="button" id="resetBtn">重置</button>
        </div>
      </form>
    </section>
    <section class="results">
      <h2>生成结果</h2>
      <p id="status" class="status">选择注数和策略后生成。</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>红球</th>
              <th>蓝球</th>
              <th>和值</th>
              <th>跨度</th>
              <th>奇数</th>
              <th>大号</th>
              <th>三区</th>
              <th>AC</th>
            </tr>
          </thead>
          <tbody id="ticketsBody">
            <tr><td colspan="9">暂无结果</td></tr>
          </tbody>
        </table>
      </div>
      <div id="summary" class="summary"></div>
      <div class="guide">
        <h3>功能说明</h3>
        <div class="guide-grid">
          <div class="guide-block">
            <h4>生成模式</h4>
            <ul>
              <li><strong>标准模式</strong>：每注独立随机生成，再逐注通过过滤器。</li>
              <li><strong>覆盖模式</strong>：先生成一组红球池，再用轮转组合生成多注，适合想要号码之间有覆盖结构时使用。</li>
            </ul>
          </div>
          <div class="guide-block">
            <h4>蓝球策略</h4>
            <ul>
              <li><strong>随机</strong>：在 1-16 中均匀随机。</li>
              <li><strong>反大众</strong>：偏向 10-16，减少常见小号偏好带来的撞号可能。</li>
              <li><strong>分层轮换</strong>：在低区、中区、高区之间切换，再在区间内随机。</li>
            </ul>
          </div>
          <div class="guide-block">
            <h4>基础过滤</h4>
            <ul>
              <li><strong>位置分位数</strong>：限制排序后的第 1 到第 6 个红球落在历史主区间。</li>
              <li><strong>和值/跨度/奇偶/连号</strong>：排除过大、过小、过密、过规律的极端形态。</li>
              <li><strong>三区分布</strong>：避免 6 个红球过度集中在 1-11、12-22、23-33 的某一区。</li>
            </ul>
          </div>
          <div class="guide-block">
            <h4>撞号与扩展过滤</h4>
            <ul>
              <li><strong>反撞号</strong>：减少生日号、顺子号、等差号等大众化组合。</li>
              <li><strong>历史重复</strong>：排除历史上已经出现过的红球组合。</li>
              <li><strong>012 路 / AC 值 / 重合 5 红</strong>：更严格的扩展过滤，可能显著降低候选通过率。</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script>
    const form = document.getElementById("strategyForm");
    const statusEl = document.getElementById("status");
    const body = document.getElementById("ticketsBody");
    const summaryEl = document.getElementById("summary");
    const generateBtn = document.getElementById("generateBtn");
    const filterNames = [
      "enable_position_quantile",
      "enable_shape_filter",
      "enable_anti_collision",
      "enable_zone_filter",
      "enable_history_duplicate_filter",
      "enable_mod3_filter",
      "enable_ac_filter",
      "enable_history_overlap5_filter"
    ];

    function payloadFromForm() {
      const data = new FormData(form);
      const filters = {};
      filterNames.forEach(name => filters[name] = data.has(name));
      return {
        num_tickets: Number(data.get("num_tickets")),
        seed: data.get("seed") === "" ? null : Number(data.get("seed")),
        mode: data.get("mode"),
        blue_mode: data.get("blue_mode"),
        filters
      };
    }

    function renderTickets(tickets) {
      body.innerHTML = "";
      if (!tickets.length) {
        body.innerHTML = '<tr><td colspan="9">暂无结果</td></tr>';
        return;
      }
      for (const ticket of tickets) {
        const reds = ["r1","r2","r3","r4","r5","r6"].map(key =>
          `<span>${String(ticket[key]).padStart(2, "0")}</span>`
        ).join("");
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${ticket.ticket_id}</td>
          <td class="reds">${reds}</td>
          <td><span class="blue-ball">${String(ticket.blue).padStart(2, "0")}</span></td>
          <td>${ticket.red_sum}</td>
          <td>${ticket.span}</td>
          <td>${ticket.odd_count}</td>
          <td>${ticket.big_count}</td>
          <td>${ticket.zone_pattern}</td>
          <td>${ticket.ac_value}</td>
        `;
        body.appendChild(tr);
      }
    }

    function renderSummary(summary) {
      const accepted = summary.find(item => item.step === "accepted");
      const initial = summary[0];
      const ratio = accepted ? `${(Number(accepted.remaining_ratio) * 100).toFixed(2)}%` : "-";
      summaryEl.innerHTML = `
        <div class="metric"><strong>${initial ? initial.remaining_count : "-"}</strong><span>候选尝试</span></div>
        <div class="metric"><strong>${accepted ? accepted.remaining_count : "-"}</strong><span>通过注数</span></div>
        <div class="metric"><strong>${ratio}</strong><span>通过率</span></div>
      `;
    }

    function clearResults(message) {
      body.innerHTML = '<tr><td colspan="9">暂无结果</td></tr>';
      summaryEl.innerHTML = "";
      statusEl.className = "status";
      statusEl.textContent = message;
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearResults("正在生成...");
      generateBtn.disabled = true;
      generateBtn.textContent = "生成中...";
      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payloadFromForm())
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "生成失败");
        renderTickets(data.tickets);
        renderSummary(data.summary);
        statusEl.className = "status ok";
        statusEl.textContent = "生成完成。";
      } catch (error) {
        statusEl.className = "status error";
        statusEl.textContent = error.message;
      } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "生成号码";
      }
    });

    document.getElementById("resetBtn").addEventListener("click", () => {
      form.reset();
      clearResults("选择注数和策略后生成。");
    });
  </script>
</body>
</html>
"""


def _parse_int(value: Any, name: str, minimum: int, maximum: int | None = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if parsed < minimum:
        raise ValueError(f"{name} must be >= {minimum}.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{name} must be <= {maximum}.")
    return parsed


def _build_request_config(base_config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    config = copy.deepcopy(base_config)
    config["generation"]["num_tickets"] = _parse_int(payload.get("num_tickets", 5), "num_tickets", 1, 50)
    seed = payload.get("seed")
    if seed in (None, ""):
        seed = random.SystemRandom().randint(0, 2_147_483_647)
    config["generation"]["random_seed"] = _parse_int(seed, "seed", 0)

    mode = payload.get("mode", "standard")
    if mode not in {"standard", "coverage"}:
        raise ValueError("mode must be standard or coverage.")
    config["generation"]["mode"] = mode

    blue_mode = payload.get("blue_mode", "random")
    if blue_mode not in {"random", "anti_popular", "layered_rotation"}:
        raise ValueError("blue_mode is not supported.")
    config["blue"]["mode"] = blue_mode

    filters = payload.get("filters", {})
    if not isinstance(filters, dict):
        raise ValueError("filters must be an object.")
    for key in (
        "enable_position_quantile",
        "enable_shape_filter",
        "enable_anti_collision",
        "enable_zone_filter",
        "enable_mod3_filter",
        "enable_ac_filter",
        "enable_history_duplicate_filter",
        "enable_history_overlap5_filter",
    ):
        if key in filters:
            config["filters"][key] = bool(filters[key])
    return config


def create_app(config_path: str | Path = "config.yaml") -> Flask:
    app = Flask(__name__)
    base_config = load_config(config_path)

    @app.get("/")
    def index():
        return render_template_string(HTML)

    @app.post("/api/generate")
    def api_generate():
        try:
            payload = request.get_json(silent=True) or {}
            config = _build_request_config(base_config, payload)
            history_csv = resolve_path(config, config["data"]["history_csv"])
            history_df = load_history_csv(
                history_csv,
                encoding=config["data"].get("encoding", "utf-8-sig"),
                fallback_encoding=config["data"].get("fallback_encoding", "gbk"),
            )
            stats = build_stats(history_df, config)
            tickets = generate_tickets(int(config["generation"]["num_tickets"]), stats, config)
        except ValueError as exc:
            return jsonify({"tickets": [], "summary": [], "error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"tickets": [], "summary": [], "error": str(exc)}), 500

        return jsonify(
            {
                "tickets": _stdlib_json.loads(tickets.to_json(orient="records", force_ascii=False)),
                "summary": _stdlib_json.loads(
                    pd.DataFrame(tickets.attrs.get("candidate_pool_summary", [])).to_json(
                        orient="records", force_ascii=False
                    )
                ),
                "error": None,
            }
        )

    return app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SSQ strategy web app.")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    app = create_app(args.config)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main(sys.argv[1:])
