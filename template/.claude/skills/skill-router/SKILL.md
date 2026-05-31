---
name: skill-router
description: 根据用户意图自动匹配最合适的 Skill。调用本地脚本匹配，零额外 token 消耗。
---

# Skill Router

本技能负责根据用户请求选择合适的 skill，不负责展开具体执行流程。

## 匹配机制（零 token 消耗）

**不读取 route-index.json！** 改为调用本地脚本进行关键词匹配：

```bash
python .claude/scripts/match-skill.py "<用户原始问题>"
```

脚本在本地对 route-index.json 做 trigram + Jaccard 打分 × priority 加权，
返回命中最高的技能名。零 API 调用、零 token 消耗、毫秒级响应。

## 路由流程

```
用户发消息
    │
    ▼
用户明确指定了 skill？ ──是──▶ 使用用户指定的 skill
    │ 否
    ▼
Bash: python .claude/scripts/match-skill.py "<用户问题>"
    │
    ▼
返回技能名（如 diagnose、tdd）
    │
    ▼
调用 Skill("命中的技能")
    │
    ▼
开场说明：采用：xxx  原因：匹配 trigger "xxx"
```

## 得分阈值

| 最高得分 | 行为 |
|----------|------|
| ≥ 0.03 | 直接采用 Top 1 |
| < 0.03 | 得分太低，不强匹配，直接普通回答或追问一句澄清 |

## 常见组合

当用户意图明确涉及多阶段工作时：

| 场景 | 推荐顺序 |
|---|---|
| 未知原因的 bug | `diagnose` → `tdd` |
| 模糊的新功能 | `grill-with-docs` → `to-prd` → `to-issues` → `tdd` |
| 大型架构改造 | `zoom-out` → `improve-codebase-architecture` → `prototype` → `tdd` |
| 配置体系检查 | `setup-matt-pocock-skills` → `triage` → `to-issues` |

## 开场格式

自动选择 skill 后，使用极简格式说明：

```text
采用：xxx
原因：匹配 trigger "xxx"，score=x.xx
```

## 索引维护

当 `.claude/skills/` 下新增或修改技能时：

```bash
python .claude/scripts/sync-routes.py
```

该脚本调 DeepSeek API 分析新技能 → 更新 route-index.json。match-skill.py 下一次运行即自动生效。