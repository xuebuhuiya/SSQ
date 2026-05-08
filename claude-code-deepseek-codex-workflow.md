# Claude Code + DeepSeek + Codex Review Workflow

本文档用于在其他项目中复用一套协作流程：

- Codex 负责先读取需求、制定/收敛实现计划、控制范围和风险。
- Claude Code 调用 DeepSeek API 负责只读复核计划、补充风险点、实现代码、运行测试。
- Codex 负责审查 DeepSeek 的反馈和实现结果、检查 diff、复核测试日志、提出最小修复意见。
- 最终由 Codex 做一次 `git diff` 和测试结果确认。

## 1. 前置条件

已安装 Claude Code：

```powershell
claude --version
```

能看到类似输出即可：

```text
2.1.128 (Claude Code)
```

已购买并生成 DeepSeek API key。不要把 API key 发到聊天里。

## 2. DeepSeek 环境变量配置

在 PowerShell 中设置 API key：

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN","你的 DeepSeek API Key","User")
```

其他推荐配置：

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL","https://api.deepseek.com/anthropic","User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL","deepseek-v4-pro[1m]","User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_OPUS_MODEL","deepseek-v4-pro[1m]","User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_SONNET_MODEL","deepseek-v4-pro[1m]","User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_HAIKU_MODEL","deepseek-v4-flash","User")
[Environment]::SetEnvironmentVariable("CLAUDE_CODE_SUBAGENT_MODEL","deepseek-v4-flash","User")
[Environment]::SetEnvironmentVariable("CLAUDE_CODE_EFFORT_LEVEL","max","User")
```

设置后关闭 PowerShell，并重新打开。若 Codex 客户端需要调用 `claude`，也建议重启 Codex 客户端。

## 3. 验证配置

在目标项目目录中运行：

```powershell
claude -p "只输出这四个字：调用成功"
```

如果输出：

```text
调用成功
```

说明 Claude Code 已经可以通过 DeepSeek API 工作。

## 4. 模型选择说明

DeepSeek 后台通常不需要给 API key 绑定模型。模型是在 API 调用时指定的。

接入 Claude Code 后，模型由环境变量指定：

```powershell
ANTHROPIC_MODEL=deepseek-v4-pro[1m]
```

临时切换模型：

```powershell
$env:ANTHROPIC_MODEL="deepseek-v4-flash"
claude -p "测试当前模型。"
```

永久切换模型：

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL","deepseek-v4-flash","User")
```

## 5. 推荐协作流程

### Step 1: Codex 先制定实现计划

Codex 先读取需求文档和项目现状，给出一版实现计划。计划应包含：

- 本次要做什么；
- 本次不做什么；
- 需要新增或修改的文件；
- 主要风险点；
- 验收方式和测试命令。

原则：

- Codex 负责收敛范围，不要把可选扩展、后续阶段、低优先级重构一次性塞进计划；
- 简单任务可以由 Codex 直接制定计划并进入执行；
- 复杂任务建议让 DeepSeek 做只读复核。

### Step 2: DeepSeek 只读复核计划

让 Codex 调用 Claude Code/DeepSeek，只读项目并复核 Codex 的计划：

```text
调用 Claude Code/DeepSeek 读取当前项目和以下计划，只做只读复核，不要改文件。

任务：...

Codex 初步计划：
...

请输出：
1. 计划是否过宽；
2. 是否遗漏关键文件或测试；
3. 是否存在安全/鉴权/数据库/构建流程风险；
4. 建议保留、删除或调整的事项。
```

### Step 3: Codex 合并反馈并确定最终计划

Codex 审查 DeepSeek 的复核意见，决定哪些建议采纳、哪些不采纳。

高风险任务需要先收窄范围；涉及产品判断、架构判断、安全判断时，Codex 应先询问用户或自行接手。

### Step 4: DeepSeek 修改代码并运行测试

推荐 prompt：

```text
调用 Claude Code/DeepSeek 按以下最终计划实现。

最终计划：
...

要求：
- 只修改必要文件
- 不要 commit
- 不要 push
- 不要修改无关格式
- 不要删除用户已有改动
- 完成后运行相关测试
- 最后列出修改文件、测试命令和测试结果
```

### Step 5: Codex 审查 diff 和测试日志

Codex 执行：

```powershell
git status
git diff
```

必要时运行项目测试命令，例如：

```powershell
npm test
npm run lint
pytest
cargo test
```

重点审查：

- 是否满足需求
- 是否改动过大
- 是否破坏现有行为
- 是否遗漏测试
- 是否引入安全、权限、数据迁移风险

### Step 6: DeepSeek 做最小修复

如果问题机械且明确，可以继续让 DeepSeek 修：

```text
调用 Claude Code/DeepSeek 根据以下审查意见做最小修复。
只修这些问题，不做额外重构。
审查意见：
...
```

如果问题需要产品判断、架构判断或安全判断，则由 Codex 接手或先询问用户。

### Step 7: Codex 最终检查

Codex 再次执行：

```powershell
git status
git diff
```

并确认：

- 改动范围合理
- 测试结果明确
- 没有自动 commit/push
- 没有泄露 API key
- 没有改动无关文件

## 6. 默认护栏

建议每次 Claude Code 执行都遵守：

```text
- 不允许自动 commit / push
- 不允许修改密钥、环境变量、系统配置
- 不允许删除文件，除非用户明确要求
- 不允许做大范围重构，除非任务明确要求
- 遇到数据库迁移、安全、鉴权、支付、权限控制改动，先停下来
- 不要覆盖用户已有改动
- 完成后必须说明修改文件和测试结果
```

## 7. 在其他项目中的推荐开场命令

进入项目目录后，对 Codex 说：

```text
按 Claude Code/DeepSeek 执行、Codex 审查流程处理这个任务：

任务：...

请先由 Codex 阅读需求和项目，制定一版收敛后的实现计划，明确本次做什么、不做什么、需要修改的文件、风险点和验收方式。
然后调用 Claude Code/DeepSeek 只读复核这个计划，不要改文件。
Codex 审查复核意见后，再决定是否让 DeepSeek 按最终计划执行。
```

如果任务很小，也可以直接说：

```text
按 Claude Code/DeepSeek 执行、Codex 审查流程处理这个小任务：

任务：...

请 Codex 先快速收敛计划；如果风险很低，可以直接让 DeepSeek 实现。
要求不要 commit/push。完成后 Codex 审查 diff 并跑测试。
```

## 8. 常见问题

### Codex 里找不到 `claude`

通常是 PATH 没刷新。重启 Codex 客户端即可。

手动检查：

```powershell
Get-Command claude
claude --version
```

### PowerShell 能调用，但 Codex 不能调用

重启 Codex 客户端。若仍不行，可以用 Claude Code 完整路径兜底：

```powershell
C:\Users\37478\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.exe
```

### 没有看到 DeepSeek 后台选择模型

这是正常的。模型由 API 调用里的 `model` 字段决定，在 Claude Code 集成中由 `ANTHROPIC_MODEL` 等环境变量决定。

### 如何确认 API key 已设置

不要输出 key 明文。只检查是否存在：

```powershell
if ([Environment]::GetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN","User")) { "ANTHROPIC_AUTH_TOKEN is set" } else { "missing" }
```

## 9. 最小可用测试

```powershell
claude -p "只输出这四个字：端到端成功"
```

期望输出：

```text
端到端成功
```
