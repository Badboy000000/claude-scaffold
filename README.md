# Claude Scaffold

一条命令，在任意新项目中复刻 Claude Code AI 工程化配置。

## 快速开始

```bash
curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash
```

私有仓库访问：

```bash
GITHUB_TOKEN=your_pat curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash
```

## 它做了什么

1. 从 GitHub 拉取最新配置到临时目录
2. 复制以下内容到当前项目：
   - `.claude/skills/` — 15 个 AI 技能（含路由系统）
   - `.claude/scripts/` — 辅助脚本（路由索引同步、关键词匹配、语义匹配）
   - `.claude/settings.json` — SessionStart hook + 权限配置
   - `CLAUDE.md` — AI 助手铁律配置（3 条核心规则）
   - `CONTEXT.md` — 项目上下文模板（空白，供填写）
3. 验证技能路由索引
4. 清理临时文件

## 安装选项

```bash
# 全量安装
curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash

# 只装 skills，不覆盖 CLAUDE.md 和其他文件
curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash -s -- --skills-only

# 保留已有文件，只补缺
curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash -s -- --no-overwrite

# 指定版本
curl -fsSL https://raw.githubusercontent.com/Badboy000000/claude-scaffold/main/init.sh | bash -s -- --version v1.0
```

## 安装后配置

### 1. 配置 DeepSeek API Key

```bash
cp .claude/scripts/.env.example .claude/scripts/.env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 2. 重新生成路由索引（可选）

```bash
python .claude/scripts/sync-routes.py
```

> 预构建的 `route-index.json` 已包含全部 15 个技能的路由信息，开箱即用。
> 仅在新增或修改技能后需要重新生成。

### 3. 填写项目上下文

编辑 `CONTEXT.md`，定义你项目的领域术语和业务概念。

## 技能清单

| 优先级 | 技能 | 类别 | 说明 |
|--------|------|------|------|
| 1 | skill-router | 元技能 | 自动匹配最合适的技能，零 token 消耗 |
| 2 | diagnose | 调试 | 纪律化的 Bug 诊断循环 |
| 3 | grill-with-docs | 澄清 | 基于文档持续追问，校准需求边界 |
| 4 | zoom-out | 理解 | 放大视角，理解代码上下文 |
| 5 | improve-codebase-architecture | 架构 | 发现架构改进机会 |
| 6 | prototype | 开发 | 快速原型验证设计 |
| 7 | tdd | 开发 | 红绿重构 TDD 工作流 |
| 8 | to-prd | 规划 | 从对话合成 PRD |
| 9 | to-issues | 规划 | 将计划拆分为垂直切片 Issue |
| 10 | triage | 元技能 | Issue 分诊状态机 |
| 10 | self-improving-agent | 元技能 | 捕获学习和纠正，持续改进 |
| 11 | write-a-skill | 元技能 | 创建新技能 |
| 12 | setup-matt-pocock-skills | 元技能 | 检查/初始化项目配置 |
| 13 | caveman | 风格 | 极简输出模式，节省 ~75% token |
| 14 | grill-me | 澄清 | 对你的方案持续压力测试 |

## 自定义

### 添加新技能

1. 在 `.claude/skills/` 下创建新目录
2. 编写 `SKILL.md`
3. 运行 `python .claude/scripts/sync-routes.py` 更新路由索引

### 修改铁律配置

编辑 `CLAUDE.md`，调整 AI 助手的行为规则。

### 更新 scaffold

修改本仓库后，在已有项目中重新执行 init 命令即可同步最新配置。

## 系统要求

- `curl` + `git`（安装必需）
- `Python 3.8+`（技能路由脚本运行必需）
- `sentence-transformers` + `numpy`（语义匹配可选，缺失时回退到关键词匹配）

## 目录结构

```
claude-scaffold/
├── init.sh              # 引导脚本
├── README.md
└── template/
    ├── CLAUDE.md        # AI 铁律配置
    ├── CONTEXT.md       # 项目上下文模板
    └── .claude/
        ├── settings.json
        ├── scripts/
        │   ├── .env.example
        │   ├── sync-routes.py
        │   ├── match-skill.py
        │   └── match-skill-embed.py
        └── skills/      # 15 个技能目录
```

## License

MIT
