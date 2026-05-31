# Claude code Scaffold

  一条命令，在任意新项目中复刻 Claude code AI 工程化配置。

  ## 快速开始

  ```bash
  curl -fsSL https://raw.githubusercontent.com/你的用户名/claude-scaffold/main/init.sh | bash

  它做了什么

  1. 拉取最新配置到临时目录
  2. 复制以下内容到当前项目：
    - .claude/skills/ — 全部 AI 技能
    - .claude/scripts/ — 辅助脚本（路由索引同步等）
    - .claude/settings.json — 权限与 hook 配置模板
    - CLAUDE.md — AI 助手铁律配置
    - CONTEXT.md — 项目上下文模板（空白，供填写）
  3. 运行 sync-routes.py 生成技能路由索引
  4. 清理临时文件

  选项

  # 指定版本
  curl ... | bash -s -- --version v1.0

  # 只装 skills，不覆盖 CLAUDE.md
  curl ... | bash -s -- --skills-only

  # 保留已有文件，只补缺
  curl ... | bash -s -- --no-overwrite

  目录结构

  claude-scaffold/
  ├── init.sh              # 引导脚本
  ├── template/
  │   ├── .claude/
  │   │   ├── skills/      # 所有技能定义
  │   │   ├── scripts/     # 辅助脚本
  │   │   └── settings.json
  │   ├── CLAUDE.md
  │   └── CONTEXT.md       # 空白模板
  └── README.md

  更新配置

  修改本仓库后，在已有项目中重新执行 init 命令即可同步最新配置。

  License

  MIT

  ---
