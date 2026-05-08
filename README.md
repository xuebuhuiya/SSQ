# 双色球历史形态约束选号器

这是一个基于双色球历史开奖数据的理性选号辅助工具。它通过历史形态约束与随机选号结合，过滤极端组合、明显规律组合和过度大众化组合。

本项目不是预测模型，不尝试预测未来开奖号码，也不承诺提高单注中奖概率。

## 运行方式

先准备本地历史 CSV，默认路径为 `data/processed/ssq_history.csv`。最小字段如下：

```csv
issue,date,r1,r2,r3,r4,r5,r6,blue
```

可以使用内置爬虫从 500 彩票网历史数据页抓取并保存为本地 CSV：

```bash
python -m src.crawler --start 03001 --end 99999 --output data/processed/ssq_history.csv
```

爬虫输出字段包含：

```csv
issue,date,r1,r2,r3,r4,r5,r6,blue,sales,pool
```

安装依赖并运行：

```bash
pip install -r requirements.txt
python -m src.main --config config.yaml
```

可选覆盖随机种子和注数：

```bash
python -m src.main --config config.yaml --seed 42 --num-tickets 5
```

## 打开本地网页

如果只想通过界面操作，先确认依赖已安装、`data/processed/ssq_history.csv` 已存在，然后启动本地网页服务：

```bash
python -m src.web_app --config config.yaml --host 127.0.0.1 --port 5000
```

然后打开：

```text
http://127.0.0.1:5000/
```

网页支持选择注数、生成模式、蓝球策略和过滤策略，并会展示生成结果与过滤摘要。

终端关闭
```bash
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000 -State Listen).OwningProcess
```

## 输出文件

运行后会写入 `data/output/`：

| 文件 | 说明 |
|---|---|
| `generated_numbers.csv` | 生成的号码列表 |
| `stats_summary.csv` | 历史统计边界摘要 |
| `candidate_pool_summary.csv` | 生成尝试和过滤摘要 |

## 默认策略

默认启用：

- 六球排序位置分位数过滤；
- 红球和值、跨度、奇偶、大小、连号形态过滤；
- 三区分布过滤；
- 历史重复组合过滤；
- 反撞号过滤，排除顺子号、等差号等明显规律组合；
- 蓝球随机生成。

默认关闭但代码支持：

- 至少包含 32/33 过滤，该规则会明显提高第 6 位为 32 或 33 的概率，适合明确想避开全部红球都在 1-31 的组合时单独启用；
- 012 路过滤；
- AC 值过滤；
- 历史重合 5 红过滤。

## 蓝球模式

通过 `blue.mode` 配置蓝球生成策略：

```yaml
blue:
  mode: "random"       # random / anti_popular / layered_rotation
```

| 模式 | 说明 |
|---|---|
| `random` | 在 01~16 范围内均匀随机生成。 |
| `anti_popular` | 从 10~16 的大号区域均匀随机生成，避开常见小号区域以降低撞号可能。 |
| `layered_rotation` | 按已开奖期数轮转三个区域：区域 A（01~05）、区域 B（06~11）、区域 C（12~16），每期轮换一个区域再从中随机。若无历史数据则随机选定一个区域。 |

这些模式仅用于随机辅助和撞号风险控制，不代表预测。

## 轮转工具

`src/wheeling.py` 提供轮转算法，供 coverage 模式调用，也可独立使用：

- **`full_wheel(pool, pick=6)`** — 对给定红球池生成全部 C(n, 6) 种组合。
- **`limited_wheel(pool, max_tickets, pick=6, rng=None)`** — 从全部组合中随机采样至多 `max_tickets` 注，支持固定随机种子以复现结果。当组合总数不超过 `max_tickets` 时返回全部。

## 生成模式

### standard 模式（默认）

`generation.mode: "standard"` 按注独立随机生成红球，每注逐一通过所有启用的历史形态过滤器。各注之间互不影响。

### coverage 模式

`generation.mode: "coverage"` 在形态过滤器基础上增加轮转覆盖：每次尝试时先从 01~33 中随机抽取一个红球池（大小由 `coverage.red_pool_size` 指定），对池内红球调用 `limited_wheel` 做有限轮转组合，再逐组合校验过滤器。多注号码共享同一个红球池的覆盖结构。

启用 coverage 模式需在 `config.yaml` 中配置：

```yaml
generation:
  mode: "coverage"

coverage:
  red_pool_size: 8   # 红球池大小（6~33），每次尝试随机抽取
  max_tickets: 28     # 单次轮转生成的上限注数
  pick: 6             # 每注从池中选取的红球数（固定 6）
```

### 模式对比

| 维度 | standard | coverage |
|---|---|---|
| 红球生成 | 每注独立随机 6 个红球 | 先建红球池，池内轮转组合 |
| 注间关系 | 各注独立，无结构关联 | 同一批注共享红球池覆盖结构 |
| 过滤器 | 逐注校验 | 逐注校验 |
| 适用场景 | 随机辅助选号 | 覆盖型多注组合，控制预算 |

## 项目结构

```text
README.md
requirements.txt
config.yaml
data/
  processed/
  output/
src/
  config.py
  crawler.py
  data_loader.py
  preprocess.py
  features.py
  stats.py
  filters.py
  blue_strategy.py
  generator.py
  wheeling.py
  main.py
tests/
```

## 免责声明

本项目仅用于概率统计学习、历史数据分析和娱乐性选号辅助。

彩票开奖结果理论上是随机事件。历史数据中的形态分布不能作为未来开奖结果的可靠预测依据。

本项目的意义在于控制预算、保持随机性、避免极端组合、避免大众化组合、降低撞号风险。请理性购彩，不要过度投入。
