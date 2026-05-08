# 双色球历史形态约束选号器

这是一个基于双色球历史开奖数据的理性选号辅助工具。它通过历史形态约束与随机选号结合，过滤极端组合、明显规律组合和过度大众化组合。

本项目不是预测模型，不尝试预测未来开奖号码，也不承诺提高单注中奖概率。

## 运行方式

先准备本地历史 CSV，默认路径为 `data/processed/ssq_history.csv`。最小字段如下：

```csv
issue,date,r1,r2,r3,r4,r5,r6,blue
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
- 反撞号过滤；
- 蓝球随机生成。

默认关闭但代码支持：

- 012 路过滤；
- AC 值过滤；
- 历史重合 5 红过滤。

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
  data_loader.py
  preprocess.py
  features.py
  stats.py
  filters.py
  blue_strategy.py
  generator.py
  main.py
tests/
```

## 免责声明

本项目仅用于概率统计学习、历史数据分析和娱乐性选号辅助。

彩票开奖结果理论上是随机事件。历史数据中的形态分布不能作为未来开奖结果的可靠预测依据。

本项目的意义在于控制预算、保持随机性、避免极端组合、避免大众化组合、降低撞号风险。请理性购彩，不要过度投入。
