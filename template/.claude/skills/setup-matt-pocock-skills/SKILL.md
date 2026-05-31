---
name: setup-matt-pocock-skills
description: 初始化或验证当前项目的 Matt Pocock Skills 工程配置。适用于 Trae 环境，重点检查 .trae/skills、.trae/rules、CONTEXT.md、docs/adr、docs/agents、.scratch/issues 等配置是否完整；可按用户要求只检查不改写，也可生成初始化方案。
---

# setup-matt-pocock-skills

## 何时使用

当用户希望初始化、检查、修复或验证当前项目的 Matt Pocock Skills 工程配置时，使用本技能。

典型触发语包括：

- 初始化 Matt Pocock skills
- 配置 Matt Pocock skills
- 检查当前项目的 skills 配置
- 验证当前项目的 Trae skills 配置
- 检查 .trae/skills 是否完整
- 检查 .trae/rules 是否完整
- 帮我配置 tdd / diagnose / triage / to-prd / to-issues 的项目工作流
- 只检查，不要修改任何文件
- verify current setup
- check current setup
- don't rewrite anything, just report drift

## 核心目标

本技能负责帮助当前项目建立或验证一套适用于 Trae 的 Matt Pocock Skills 工程工作流。

它不负责直接开发业务功能。

它主要负责：

- 检查当前项目的 skills 是否安装完整；
- 检查当前项目的 rules 是否配置完整；
- 检查项目上下文文档是否存在；
- 检查 issue tracker 配置是否明确；
- 检查 triage 标签是否明确；
- 检查领域文档结构是否清晰；
- 在用户允许时生成或修复缺失配置；
- 在用户要求验证时，只报告问题，不改写文件。

## Trae 适配原则

本项目优先使用 Trae 原生配置结构：

```text
your-project/
├── .trae/
│   ├── skills/
│   └── rules/
├── CONTEXT.md
├── CONTEXT-MAP.md
├── docs/
│   ├── adr/
│   └── agents/
└── .scratch/
    └── issues/
```

各目录职责：

- `.trae/skills/`：存放 Trae 项目技能；
- `.trae/rules/`：存放 Trae 项目规则；
- `CONTEXT.md`：单项目领域上下文；
- `CONTEXT-MAP.md`：多上下文项目或 monorepo 的上下文索引；
- `docs/adr/`：架构决策记录；
- `docs/agents/`：AI 工程技能使用的项目配置说明；
- `.scratch/issues/`：本地 Markdown issue tracker。

## AGENTS.md / CLAUDE.md 处理原则

Trae 可以兼容读取 `AGENTS.md` 和 `CLAUDE.md`，但本技能不默认依赖它们。

默认推荐：

```text
主配置来源：.trae/skills/ + .trae/rules/
兼容上下文：AGENTS.md / CLAUDE.md 可关闭
```

只有在用户明确要求兼容其他 AI 编程工具时，才建议创建或修改：

- `AGENTS.md`
- `CLAUDE.md`

否则，项目规则优先放入：

```text
.trae/rules/
```

## 工作模式

本技能有两种工作模式。

### 1. 初始化模式

当用户要求“初始化”“配置”“生成规则”“搭建工作流”时，进入初始化模式。

初始化模式可以：

- 检查缺失项；
- 询问关键决策；
- 生成配置草案；
- 在用户确认后创建或修改文件。

### 2. 验证模式

当用户要求“检查”“验证”“只看不改”“不要写入”“verify”“check”时，进入验证模式。

验证模式必须遵守：

- 只读取；
- 只报告；
- 不创建文件；
- 不修改文件；
- 不覆盖配置；
- 不自动修复；
- 不删除任何内容。

验证模式的目标是报告当前项目相对于推荐结构的差异。

输出应包含：

- 已存在项；
- 缺失项；
- 可能冲突项；
- 建议修复项；
- 是否需要用户确认后再进入初始化或修复模式。

## 标准检查清单

开始时检查以下内容是否存在。

```text
.trae/
.trae/skills/
.trae/rules/
.trae/skills/grill-with-docs/
.trae/skills/grill-me/
.trae/skills/tdd/
.trae/skills/diagnose/
.trae/skills/triage/
.trae/skills/to-prd/
.trae/skills/to-issues/
.trae/skills/prototype/
.trae/skills/zoom-out/
.trae/skills/improve-codebase-architecture/
.trae/skills/write-a-skill/
.trae/skills/caveman/
.trae/skills/setup-matt-pocock-skills/
CONTEXT.md
CONTEXT-MAP.md
docs/
docs/adr/
docs/agents/
docs/agents/issue-tracker.md
docs/agents/triage-labels.md
docs/agents/domain.md
.scratch/
.scratch/issues/
AGENTS.md
CLAUDE.md
README.md
package.json
.git/
```

不要假设这些文件一定存在。

## 可执行检查命令

如果可以执行命令，优先使用命令检查。

### macOS / Linux / Git Bash

```bash
pwd
ls -la
find .trae -maxdepth 4 -type f 2>/dev/null
find docs -maxdepth 4 -type f 2>/dev/null
find .scratch -maxdepth 4 -type f 2>/dev/null
git remote -v 2>/dev/null
```

### Windows PowerShell

```powershell
Get-Location
Get-ChildItem -Force
Get-ChildItem .trae -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem docs -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem .scratch -Recurse -Force -ErrorAction SilentlyContinue
git remote -v
```

如果命令无法运行，改用项目文件树和用户提供的信息进行判断。

## 必装 Skills 检查

推荐第一批必装 skills：

```text
grill-with-docs
tdd
diagnose
zoom-out
improve-codebase-architecture
prototype
to-prd
to-issues
```

推荐第二批可选 skills：

```text
grill-me
caveman
write-a-skill
triage
setup-matt-pocock-skills
```

检查每个 skill 时，至少确认：

- 是否存在对应目录；
- 是否存在 `SKILL.md`；
- 如果该 skill 依赖辅助文件，辅助文件是否一起存在。

例如：

`tdd` 推荐包含：

```text
SKILL.md
deep-modules.md
interface-design.md
mocking.md
refactoring.md
tests.md
```

`triage` 推荐包含：

```text
SKILL.md
AGENT-BRIEF.md
OUT-OF-SCOPE.md
```

## Rules 检查

推荐 `.trae/rules/` 至少包含：

```text
00-project-guardrails.md
01-skill-router.md
02-engineering-workflow.md
```

### 00-project-guardrails.md 应覆盖

- 先理解项目，再修改代码；
- 先确认需求边界；
- 小步修改；
- 不做无关重构；
- 不引入无必要依赖；
- 不覆盖用户已有业务逻辑；
- 涉及配置、鉴权、环境变量、数据库迁移、构建脚本时必须谨慎；
- 修改前说明计划；
- 修改后说明验证结果。

### 01-skill-router.md 应覆盖

- 需求不清楚 → `grill-with-docs` / `grill-me`
- 新功能 / 复杂逻辑 / 重构 → `tdd`
- Bug / 报错 / 性能问题 → `diagnose`
- 任务分流 → `triage`
- 需求文档 → `to-prd`
- 拆任务 → `to-issues`
- 代码理解 → `zoom-out`
- 架构改进 → `improve-codebase-architecture`
- 技术验证 → `prototype`
- 写新技能 → `write-a-skill`
- 极简输出 → `caveman`
- 初始化或验证配置 → `setup-matt-pocock-skills`

### 02-engineering-workflow.md 应覆盖

- 理解；
- 计划；
- 实现；
- 验证；
- 总结。

## docs/agents 检查

推荐存在以下文件：

```text
docs/agents/issue-tracker.md
docs/agents/triage-labels.md
docs/agents/domain.md
```

### issue-tracker.md 应说明

当前项目 issue 写在哪里。

可选项：

- GitHub Issues
- GitLab Issues
- 本地 Markdown
- Jira
- Linear
- 飞书
- 钉钉
- 其他

如果是本地 Markdown，推荐：

```text
.scratch/issues/
```

文件命名建议：

```text
YYYYMMDD-short-title.md
```

### triage-labels.md 应说明

默认任务分类：

```text
bug
enhancement
```

默认任务状态：

```text
needs-triage
needs-info
ready-for-agent
ready-for-human
wontfix
```

如果用户要求中文，也可以映射成中文标签，但要保留英文原义，避免和原 skills 语义冲突。

### domain.md 应说明

当前项目使用哪种领域文档结构。

单上下文项目推荐：

```text
CONTEXT.md
docs/adr/
```

多上下文或 monorepo 项目推荐：

```text
CONTEXT-MAP.md
多个子系统 CONTEXT.md
多个 docs/adr/
```

## 初始化模式流程

### 第一步：探查项目

先读取项目结构，确认现状。

输出：

```markdown
## 当前检查结果

### 已存在

- ...

### 缺失

- ...

### 可能冲突

- ...

### 初步建议

- ...
```

### 第二步：确认配置来源

一次只问一个决策。

先问：

```markdown
## 需要确认：配置来源

我建议当前项目采用：

- 主配置：`.trae/skills/` + `.trae/rules/`
- 兼容配置：不默认依赖 `AGENTS.md` / `CLAUDE.md`

是否按这个方式继续？
```

用户确认后，再进入下一步。

### 第三步：确认 Issue tracker

询问：

```markdown
## 需要确认：Issue tracker

`to-prd`、`to-issues`、`triage` 需要知道任务写到哪里。

推荐：

- 个人本地项目：`.scratch/issues/`
- 团队 GitHub 项目：GitHub Issues

当前项目你希望使用哪一种？
```

### 第四步：确认 Triage labels

询问：

```markdown
## 需要确认：任务标签

默认使用：

- `bug`
- `enhancement`
- `needs-triage`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`
- `wontfix`

是否沿用这套英文标签？
```

### 第五步：确认领域文档结构

询问：

```markdown
## 需要确认：领域文档结构

推荐：

- 普通项目：`CONTEXT.md` + `docs/adr/`
- monorepo / 多子系统项目：`CONTEXT-MAP.md` + 多个子系统 `CONTEXT.md`

当前项目使用哪一种？
```

### 第六步：生成写入计划

在真正写入前，必须列出将要创建或修改的文件。

格式：

```markdown
## 将要创建 / 修改

- `.trae/rules/00-project-guardrails.md`
- `.trae/rules/01-skill-router.md`
- `.trae/rules/02-engineering-workflow.md`
- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/agents/domain.md`
- `CONTEXT.md`
- `docs/adr/`
- `.scratch/issues/`

## 等待确认

请确认是否写入这些文件。
```

用户确认后才能写入。

## 验证模式流程

当用户要求“只检查、不修改”时，使用以下流程。

### 第一步：读取项目结构

只读取，不写入。

### 第二步：对照推荐结构

检查：

- `.trae/skills/` 是否存在；
- 必装 skills 是否存在；
- 可选 skills 是否存在；
- 每个 skill 是否有 `SKILL.md`；
- `tdd`、`triage` 等带辅助文件的 skill 是否完整；
- `.trae/rules/` 是否存在；
- 三个推荐 rules 是否存在；
- `CONTEXT.md` 或 `CONTEXT-MAP.md` 是否存在；
- `docs/adr/` 是否存在；
- `docs/agents/` 是否存在；
- `.scratch/issues/` 是否存在；
- 是否存在可能重复的 `AGENTS.md` / `CLAUDE.md` 配置。

### 第三步：输出验证报告

格式：

```markdown
## 验证报告

### 通过项

- ...

### 缺失项

- ...

### 配置漂移

- ...

### 可能冲突

- ...

### 建议修复顺序

1. ...
2. ...
3. ...

## 未做修改

本次只检查，没有创建、修改或删除任何文件。
```

## 写入规则

### 允许写入的前提

只有用户明确确认后，才可以创建或修改文件。

用户确认语包括：

- 确认
- 可以写入
- 开始创建
- 按这个方案执行
- 帮我生成这些文件

### 禁止自动写入的情况

以下情况禁止自动写入：

- 用户说“只检查”
- 用户说“不要修改”
- 用户说“先看看”
- 用户说“先给方案”
- 用户没有明确确认
- 涉及覆盖已有配置但用户未确认

## 文件覆盖规则

- 不要覆盖已有 `.trae/rules/` 文件，除非用户确认。
- 不要覆盖已有 `CONTEXT.md`，只能追加建议或展示补丁。
- 不要删除 `AGENTS.md` 或 `CLAUDE.md`，只能提示可能重复。
- 不要删除已有 skills。
- 不要修改用户已有业务代码。
- 不要把临时任务进展写入 `CONTEXT.md`。
- 不要把实现细节误写成领域规则。

## 完成后输出

初始化完成后输出：

```markdown
## 初始化完成

已完成：

- Trae skills 检查
- Trae rules 初始化
- issue tracker 配置
- triage labels 配置
- domain docs 配置

## 后续使用

- 需求澄清：使用 `grill-with-docs`
- 新功能开发：使用 `tdd`
- Bug 排查：使用 `diagnose`
- 任务分流：使用 `triage`
- 需求文档：使用 `to-prd`
- 任务拆分：使用 `to-issues`
- 架构分析：使用 `improve-codebase-architecture`
- 快速验证：使用 `prototype`
- 极简输出：使用 `caveman`
```

验证完成后输出：

```markdown
## 验证完成

本次只检查，没有修改任何文件。

### 下一步建议

- ...
```

## 重要限制

- 不要一次问多个决策问题。
- 不要默认创建 `AGENTS.md`。
- 不要默认创建 `CLAUDE.md`。
- 不要默认改写 `.trae/rules/`。
- 不要默认改写 `CONTEXT.md`。
- 不要自动删除任何文件。
- 不要把 Trae 配置和 Claude 配置混为一谈。
- 不要在验证模式中写入文件。