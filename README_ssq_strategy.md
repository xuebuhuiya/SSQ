# 双色球历史形态约束选号器

## 1. 项目目标

本项目的目标是基于双色球历史开奖数据，构建一个“理性选号辅助工具”。

需要强调：

本项目 **不是预测模型**，不尝试预测未来开奖号码，也不认为历史数据可以提高单注中奖概率。

本项目的核心目标是：

1. 基于历史开奖数据统计常见号码形态；
2. 过滤极端组合、明显规律组合、生日号集中组合；
3. 降低和大众选号习惯撞号的可能性；
4. 保持随机性，避免追热号、冷号；
5. 在固定预算内生成少量可购买号码。

简单来说：

> 这不是“预测中奖号码”，而是“在合理历史形态空间内随机选号”。

---

## 2. 基本规则

双色球规则：

- 红球：从 1–33 中选择 6 个，不重复；
- 蓝球：从 1–16 中选择 1 个；
- 红球通常按升序排列；
- 每注由 `6 个红球 + 1 个蓝球` 组成。

理论组合数：

```text
C(33, 6) * 16 = 17,721,088
```

其中红球组合数为：

```text
C(33, 6) = 1,107,568
```

---

## 3. 数据来源建议

历史开奖数据可以来自以下来源：

### 3.1 中彩网

中彩网数据相对更权威，适合作为校验源。

建议字段：

```text
issue,date,r1,r2,r3,r4,r5,r6,blue,sales,pool
```

### 3.2 500彩票网

500彩票网历史数据页面结构相对规整，适合作为爬取源。

建议用于：

- 批量抓取历史数据；
- 本地保存 CSV；
- 后续统计分析。

### 3.3 本地 CSV

建议最终程序统一读取本地 CSV，而不是每次都在线爬取。

推荐格式：

```csv
issue,date,r1,r2,r3,r4,r5,r6,blue,sales,pool
2024001,2024-01-01,1,3,7,12,24,31,8,xxx,xxx
```

最小必须字段：

```text
issue,date,r1,r2,r3,r4,r5,r6,blue
```

---

## 4. 项目边界

本项目不做以下事情：

1. 不预测下一期开奖号码；
2. 不使用热号、冷号作为核心预测依据；
3. 不使用深度学习、机器学习拟合开奖号码；
4. 不做倍投、追号、回本策略；
5. 不承诺提高中奖概率。

本项目可以做：

1. 统计历史开奖形态；
2. 构建候选号码池；
3. 使用多种规则过滤候选组合；
4. 随机生成少量号码；
5. 控制预算和注数；
6. 输出可解释的选号结果。

---

## 5. 总体策略

目前项目一共包含 11 类策略。

| 编号 | 策略名称 | 是否默认启用 | 作用 |
|---|---|---|---|
| 1 | 纯随机策略 | 是 | 保留基准随机性 |
| 2 | 反撞号策略 | 是 | 避免生日号、规律号、大众号 |
| 3 | 历史组合形态约束 | 是 | 用和值、跨度、奇偶、大小、连号过滤极端组合 |
| 4 | 六球排序位置区间策略 | 是 | 限制第1球到第6球落在历史主区间 |
| 5 | 历史重复/相似组合排除 | 是 | 排除历史完全重复，可选排除重合5红 |
| 6 | 胆拖/复式/轮转覆盖 | 可选 | 预算充足时扩大覆盖 |
| 7 | 分区覆盖策略 | 是 | 避免号码过度集中在某一区 |
| 8 | 012路/余数分布策略 | 可选 | 避免模3分布极端 |
| 9 | AC值/离散度策略 | 可选 | 排除过于规律的号码 |
| 10 | 奖池/开奖日/资金策略 | 是 | 控制预算，不盲目加注 |
| 11 | 蓝球独立策略 | 是 | 蓝球随机或分层轮换 |

---

## 6. 推荐默认组合

默认主策略建议使用：

```text
六球排序位置区间
+ 历史和值/跨度/连号/奇偶约束
+ 三区分布约束
+ 历史重复排除
+ 反撞号过滤
+ 蓝球随机
```

也就是：

```text
策略4 + 策略3 + 策略7 + 策略5 + 策略2 + 策略11
```

---

## 7. 三种运行模式

### 7.1 轻量模式

适合每期 1–2 注。

规则：

```text
纯随机
反撞号
六球排序位置 5%–95%
排除历史6红完全重复
蓝球随机
```

特点：

- 保留较强随机性；
- 只排除少量极端组合；
- 适合长期小额购买。

---

### 7.2 标准模式

适合每期 2–5 注。

规则：

```text
六球排序位置 10%–90%
和值 10%–90%
跨度 10%–90%
奇偶比不过度极端
大小比不过度极端
三区分布不过度极端
最大连续长度 <= 3
排除历史6红完全重复
可选排除历史重合5红
蓝球随机或分层轮换
```

特点：

- 推荐作为主模式；
- 过滤强度适中；
- 保持历史形态合理性。

---

### 7.3 覆盖模式

适合偶尔奖池较高、预算稍微增加时使用。

规则：

```text
先生成 7–8 个候选红球
用轮转/小复式生成多注
再经过反撞号、和值、跨度、连号过滤
控制总注数
```

示例：

```text
7红全组合 = C(7,6) = 7注
8红全组合 = C(8,6) = 28注
9红全组合 = C(9,6) = 84注
10红全组合 = C(10,6) = 210注
```

建议：

- 常规不要超过 8 红轮转；
- 不建议常态使用 9 红或 10 红；
- 覆盖模式必须受预算限制。

---

## 8. 核心过滤策略说明

### 8.1 纯随机策略

红球：

```text
从 1–33 中随机选 6 个，不重复，升序排列
```

蓝球：

```text
从 1–16 中随机选 1 个
```

用途：

- 作为基准策略；
- 防止所有号码都被人为规则过度约束；
- 建议每期至少保留 1 注纯随机号码。

---

### 8.2 反撞号策略

目标：

降低中奖后和大量用户平分奖金的可能性。

需要避免：

```text
生日号集中组合
明显顺子号
整齐间隔号
全部小号
全部 1–31 区间
过于人工化的组合
```

建议规则：

```text
至少包含 1 个 > 31 的红球
不要全部红球 <= 31
不要出现 4 个及以上连续号
不要是明显等差数列
不要是 01 02 03 04 05 06
不要是 05 10 15 20 25 30
```

注意：

该策略不提高中奖概率，只是降低撞号风险。

---

### 8.3 历史组合形态约束策略

对每期历史红球计算以下特征：

```text
red_sum              红球和值
odd_count            奇数数量
even_count           偶数数量
big_count            大号数量，通常 17–33
small_count          小号数量，通常 1–16
span                 跨度，max(red) - min(red)
consecutive_count    连号数量
max_consecutive_len  最大连续长度
```

推荐过滤方式：

```text
red_sum 保留历史 10%–90% 分位数
span 保留历史 10%–90% 分位数
odd_count 不允许 0 或 6
big_count 不允许 0 或 6
max_consecutive_len <= 3
```

可选：

```text
red_sum 使用 5%–95% 作为宽松模式
red_sum 使用 20%–80% 作为严格模式
```

---

### 8.4 六球排序位置区间策略

这是本项目最核心的历史形态策略。

每期红球升序排列：

```text
03 08 14 19 26 32
```

对应：

```text
pos1 = 03
pos2 = 08
pos3 = 14
pos4 = 19
pos5 = 26
pos6 = 32
```

统计历史数据中：

```text
pos1 的历史分布
pos2 的历史分布
pos3 的历史分布
pos4 的历史分布
pos5 的历史分布
pos6 的历史分布
```

然后使用分位数约束。

推荐三档：

| 模式 | 分位数 |
|---|---|
| 宽松 | 5%–95% |
| 标准 | 10%–90% |
| 严格 | 20%–80% |

标准模式示例：

```text
pos1 in historical_pos1_q10_to_q90
pos2 in historical_pos2_q10_to_q90
pos3 in historical_pos3_q10_to_q90
pos4 in historical_pos4_q10_to_q90
pos5 in historical_pos5_q10_to_q90
pos6 in historical_pos6_q10_to_q90
```

注意：

这个策略不是预测，而是限制排序位置落在历史主分布范围内。

---

### 8.5 历史重复/相似组合排除策略

建议默认启用：

```text
排除历史上完全出现过的 6 红组合
排除历史上完全出现过的 6 红 + 1 蓝组合
```

可选启用：

```text
排除与历史任意一期重合 5 个红球的组合
```

不建议默认启用：

```text
排除与历史任意一期重合 4 个红球的组合
```

原因：

重合 4 个红球会过滤掉太多组合，过于激进。

实现方式：

```python
def red_overlap(candidate_reds, history_reds):
    return len(set(candidate_reds) & set(history_reds))
```

规则：

```text
if overlap == 6:
    reject
if strict_mode and overlap >= 5:
    reject
```

---

### 8.6 分区覆盖策略

把红球 1–33 分为三区：

```text
一区：01–11
二区：12–22
三区：23–33
```

统计每注红球在三区中的数量。

推荐规则：

```text
不要 6 个红球全部来自同一区
不要 5 个红球集中在同一区
优先保留 2-2-2、1-2-3、1-3-2、2-1-3 等分布
```

默认规则可以简单设置为：

```text
每个区最多 4 个红球
至少覆盖 2 个区
```

---

### 8.7 012路/余数分布策略

按除以 3 的余数分类：

```text
0路：3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33
1路：1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31
2路：2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32
```

推荐规则：

```text
不要 6 个红球全部来自同一路
不要 5 个红球来自同一路
优先保留 2-2-2、1-2-3、1-3-2 这类结构
```

默认可选规则：

```text
每一路最多 4 个红球
```

---

### 8.8 AC值/离散度策略

AC值用于描述号码之间差值结构的丰富程度。

简单计算方式：

1. 对 6 个红球两两做差；
2. 统计不同差值的数量；
3. 用不同差值数量减去 `n - 1`，其中 `n = 6`。

伪代码：

```python
def ac_value(reds):
    reds = sorted(reds)
    diffs = set()
    for i in range(len(reds)):
        for j in range(i + 1, len(reds)):
            diffs.add(reds[j] - reds[i])
    return len(diffs) - (len(reds) - 1)
```

建议：

```text
排除 AC 值过低的组合
保留历史 AC 值的主分布范围
```

默认可以先不启用，或者只作为输出参考。

---

### 8.9 蓝球独立策略

蓝球不要复杂预测，建议独立处理。

支持三种模式：

#### A. 纯随机

```text
1–16 均匀随机
```

默认推荐。

#### B. 反大众蓝球

避开用户常选数字，例如生日、纪念日、幸运数字。

注意这不是提高中奖概率，只是降低撞号可能。

#### C. 分层轮换

将蓝球分为：

```text
低区：01–05
中区：06–11
高区：12–16
```

长期购买时轮换不同区间。

默认建议：

```text
blue_mode = random
```

---

### 8.10 奖池/资金策略

该策略不参与号码生成，只控制购买行为。

建议：

```text
固定月预算
固定每期注数
不倍投
不追号
不因为连续未中奖而加注
奖池高时可以使用覆盖模式，但必须设置注数上限
```

示例预算：

```text
每期 2 注，每注 2 元
每周 3 期
每月约 12 期
月支出约 48 元
```

推荐：

```text
普通模式：每期 2–5 注
覆盖模式：偶尔使用，不超过 28 注
```

---

## 9. 推荐项目结构

建议 Codex 按以下结构创建项目：

```text
ssq-strategy/
│
├── README.md
├── requirements.txt
├── config.yaml
│
├── data/
│   ├── raw/
│   │   └── ssq_history_raw.csv
│   ├── processed/
│   │   └── ssq_history.csv
│   └── output/
│       ├── generated_numbers.csv
│       ├── stats_summary.csv
│       └── candidate_pool_summary.csv
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── crawler.py
│   ├── preprocess.py
│   ├── stats.py
│   ├── features.py
│   ├── filters.py
│   ├── generator.py
│   ├── blue_strategy.py
│   ├── wheeling.py
│   ├── config.py
│   └── main.py
│
├── notebooks/
│   └── analysis.ipynb
│
└── tests/
    ├── test_features.py
    ├── test_filters.py
    └── test_generator.py
```

---

## 10. 配置文件设计

建议使用 `config.yaml`。

示例：

```yaml
data:
  history_csv: "data/processed/ssq_history.csv"
  output_dir: "data/output"

generation:
  mode: "standard"
  num_tickets: 5
  random_seed: 42
  max_attempts: 100000

filters:
  enable_anti_collision: true
  enable_position_quantile: true
  enable_shape_filter: true
  enable_zone_filter: true
  enable_mod3_filter: false
  enable_ac_filter: false
  enable_history_duplicate_filter: true
  enable_history_overlap5_filter: false

position_quantile:
  lower: 0.10
  upper: 0.90

shape_quantile:
  red_sum_lower: 0.10
  red_sum_upper: 0.90
  span_lower: 0.10
  span_upper: 0.90

rules:
  max_consecutive_len: 3
  require_gt31: true
  max_zone_count: 4
  min_zone_covered: 2
  max_mod3_count: 4

blue:
  mode: "random"
```

---

## 11. 主要模块说明

### 11.1 data_loader.py

负责读取历史数据。

函数建议：

```python
def load_history_csv(path: str) -> pd.DataFrame:
    pass
```

要求：

- 检查必要字段；
- 转换红球、蓝球为整数；
- 确保红球升序；
- 去除重复期号；
- 返回标准 DataFrame。

---

### 11.2 preprocess.py

负责数据清洗。

函数建议：

```python
def normalize_history(df: pd.DataFrame) -> pd.DataFrame:
    pass
```

处理内容：

```text
字段重命名
日期解析
红球排序
缺失值检查
重复开奖检查
非法号码检查
```

---

### 11.3 features.py

负责计算号码特征。

函数建议：

```python
def compute_red_features(reds: list[int]) -> dict:
    pass

def compute_history_features(df: pd.DataFrame) -> pd.DataFrame:
    pass

def ac_value(reds: list[int]) -> int:
    pass

def max_consecutive_len(reds: list[int]) -> int:
    pass

def zone_counts(reds: list[int]) -> tuple[int, int, int]:
    pass

def mod3_counts(reds: list[int]) -> tuple[int, int, int]:
    pass
```

输出特征：

```text
red_sum
odd_count
even_count
big_count
small_count
span
max_consecutive_len
zone_1_count
zone_2_count
zone_3_count
mod0_count
mod1_count
mod2_count
ac_value
has_gt31
birthday_ratio
```

---

### 11.4 stats.py

负责根据历史数据生成统计边界。

函数建议：

```python
def build_stats(df: pd.DataFrame, config: dict) -> dict:
    pass
```

需要生成：

```text
每个排序位置的分位数范围
和值分位数范围
跨度分位数范围
AC值分位数范围
历史红球集合
历史完整组合集合
历史特征分布摘要
```

示例输出：

```python
{
    "position_ranges": {
        "r1": [1, 8],
        "r2": [4, 13],
        "r3": [9, 19],
        "r4": [15, 25],
        "r5": [21, 30],
        "r6": [27, 33],
    },
    "red_sum_range": [70, 140],
    "span_range": [18, 31],
    "historical_red_sets": set(...),
    "historical_full_sets": set(...),
}
```

---

### 11.5 filters.py

负责过滤候选组合。

函数建议：

```python
def pass_position_filter(reds: list[int], stats: dict, config: dict) -> bool:
    pass

def pass_shape_filter(reds: list[int], stats: dict, config: dict) -> bool:
    pass

def pass_anti_collision_filter(reds: list[int], config: dict) -> bool:
    pass

def pass_zone_filter(reds: list[int], config: dict) -> bool:
    pass

def pass_mod3_filter(reds: list[int], config: dict) -> bool:
    pass

def pass_ac_filter(reds: list[int], stats: dict, config: dict) -> bool:
    pass

def pass_history_duplicate_filter(
    reds: list[int],
    blue: int | None,
    stats: dict,
    config: dict
) -> bool:
    pass

def pass_all_filters(
    reds: list[int],
    blue: int | None,
    stats: dict,
    config: dict
) -> tuple[bool, list[str]]:
    pass
```

`pass_all_filters` 建议返回：

```python
(True, [])
```

或：

```python
(False, ["position_filter_failed", "red_sum_out_of_range"])
```

这样方便调试。

---

### 11.6 generator.py

负责生成号码。

函数建议：

```python
def generate_random_reds() -> list[int]:
    pass

def generate_ticket(stats: dict, config: dict) -> dict:
    pass

def generate_tickets(n: int, stats: dict, config: dict) -> pd.DataFrame:
    pass
```

输出格式：

```text
ticket_id,r1,r2,r3,r4,r5,r6,blue,mode,filters_used,notes
```

示例：

```csv
ticket_id,r1,r2,r3,r4,r5,r6,blue,mode,filters_used,notes
1,3,8,14,19,26,32,11,standard,"position,shape,zone,duplicate,anti_collision","ok"
```

---

### 11.7 blue_strategy.py

负责蓝球生成。

函数建议：

```python
def generate_blue(config: dict, history_df: pd.DataFrame | None = None) -> int:
    pass
```

支持模式：

```text
random
anti_popular
layered_rotation
```

默认：

```text
random
```

---

### 11.8 wheeling.py

负责轮转/复式策略。

函数建议：

```python
def full_wheel(pool: list[int], pick: int = 6) -> list[list[int]]:
    pass

def limited_wheel(pool: list[int], max_tickets: int) -> list[list[int]]:
    pass
```

示例：

```python
pool = [3, 7, 12, 16, 21, 25, 29, 33]
tickets = full_wheel(pool, pick=6)
```

---

### 11.9 main.py

主程序入口。

建议支持：

```bash
python -m src.main --config config.yaml
```

主要流程：

```text
1. 读取 config
2. 读取历史 CSV
3. 清洗历史数据
4. 计算历史特征
5. 构建统计边界
6. 生成候选号码
7. 应用过滤器
8. 输出结果 CSV
9. 输出统计摘要
```

---

## 12. 输出文件

### 12.1 generated_numbers.csv

字段：

```text
ticket_id
r1,r2,r3,r4,r5,r6
blue
mode
filters_used
red_sum
span
odd_count
big_count
zone_pattern
mod3_pattern
ac_value
notes
```

---

### 12.2 stats_summary.csv

字段：

```text
metric
lower_quantile
upper_quantile
lower_value
upper_value
mean
std
min
max
```

例如：

```text
pos1,0.10,0.90,1,8,4.2,2.3,1,16
red_sum,0.10,0.90,70,140,105.5,22.1,35,180
span,0.10,0.90,18,31,25.4,4.8,5,32
```

---

### 12.3 candidate_pool_summary.csv

记录过滤过程。

字段：

```text
step
remaining_count
removed_count
remaining_ratio
notes
```

示例：

```text
initial_random,100000,0,1.000,start
position_filter,65000,35000,0.650,position quantile
shape_filter,48000,17000,0.480,sum/span/odd/big
zone_filter,42000,6000,0.420,zone balance
duplicate_filter,41980,20,0.4198,history duplicate
```

---

## 13. 代码实现原则

1. 不要写成玄学预测器；
2. 所有过滤规则必须可解释；
3. 每个过滤器独立成函数；
4. 每个过滤器可以通过 config 开关；
5. 默认保留随机性；
6. 不要过度过滤；
7. 输出时说明每注号码通过了哪些规则；
8. 不要输出“推荐必中”之类的文本；
9. 所有统计范围都从历史数据计算得到；
10. 程序应该支持固定随机种子，便于复现。

---

## 14. 推荐实现顺序

建议 Codex 按下面顺序开发：

### 第一阶段：基础版本

实现：

```text
data_loader.py
preprocess.py
features.py
stats.py
generator.py
main.py
```

支持：

```text
读取历史 CSV
计算排序位置分位数
计算和值和跨度分位数
随机生成号码
输出 generated_numbers.csv
```

---

### 第二阶段：过滤器版本

实现：

```text
filters.py
```

支持：

```text
位置分位数过滤
和值过滤
跨度过滤
连号过滤
历史重复过滤
反撞号过滤
三区过滤
```

---

### 第三阶段：扩展版本

实现：

```text
blue_strategy.py
wheeling.py
```

支持：

```text
蓝球分层轮换
012路过滤
AC值过滤
7红/8红轮转
过滤过程摘要
```

---

### 第四阶段：分析可视化

可选实现：

```text
notebooks/analysis.ipynb
```

分析内容：

```text
第1球到第6球历史分布
红球和值分布
跨度分布
奇偶比分布
三区分布
蓝球历史分布
过滤前后候选池变化
```

---

## 15. 示例运行流程

```bash
pip install -r requirements.txt
python -m src.main --config config.yaml
```

输出：

```text
data/output/generated_numbers.csv
data/output/stats_summary.csv
data/output/candidate_pool_summary.csv
```

---

## 16. requirements.txt 建议

```txt
pandas
numpy
pyyaml
requests
beautifulsoup4
lxml
matplotlib
```

如果暂时不写爬虫，可以先不使用：

```txt
requests
beautifulsoup4
lxml
```

---

## 17. 示例生成结果

```text
模式：standard
注数：5

01: 03 08 14 19 26 32 + 11
02: 02 07 13 21 28 33 + 04
03: 05 11 17 22 29 32 + 15
04: 01 09 16 23 27 31 + 08
05: 04 10 18 24 30 33 + 02
```

输出时需要附带说明：

```text
以上号码由历史形态约束和随机生成共同得到。
它们不代表预测结果，也不保证提高中奖概率。
请固定预算、理性购买。
```

---

## 18. 重要免责声明

本项目仅用于概率统计学习、历史数据分析和娱乐性选号辅助。

彩票开奖结果理论上是随机事件。历史数据中的形态分布不能作为未来开奖结果的可靠预测依据。

本项目所有策略的意义在于：

```text
控制预算
保持随机性
避免极端组合
避免大众化组合
降低撞号风险
```

而不是：

```text
预测中奖号码
提高单注中奖概率
保证盈利
```

请理性购彩，不要过度投入。

---

## 19. 给 Codex 的任务提示

请根据 README.md 创建完整 Python 项目。优先实现第一阶段和第二阶段，不需要先写爬虫，先假设 `data/processed/ssq_history.csv` 已经存在。

代码要求：

1. 模块清晰；
2. 可配置；
3. 可复现；
4. 每个过滤器可以单独开关；
5. 输出 `generated_numbers.csv`、`stats_summary.csv` 和 `candidate_pool_summary.csv`；
6. 不要写成预测器，不要输出“必中”“提高中奖率”等表述。
