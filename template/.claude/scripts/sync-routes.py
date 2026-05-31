#!/usr/bin/env python3
"""
Skill Route Index Synchronizer
===============================
扫描 .claude/skills/ 目录，检测新增/修改/删除的技能，
调用 DeepSeek API 自动分析新技能并更新 route-index.json。

用法:
    python sync-routes.py              # 检测并更新
    python sync-routes.py --dry-run    # 只检测，不更新
    python sync-routes.py --force-all  # 强制重新分析所有技能
"""

import json
import hashlib
import os
import sys
import time
from pathlib import Path

import requests

# ── 路径配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"
INDEX_PATH = SKILLS_DIR / "skill-router" / "route-index.json"

# ── DeepSeek API 配置 ─────────────────────────────────────
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-pro"
REQUEST_TIMEOUT = 30

# skill-router 自身不参与路由索引（它是路由规则本身）
SKIP_SKILLS = {"skill-router"}


# ═══════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════

def get_api_key() -> str:
    """从环境变量或 .env 文件读取 API Key"""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key

    env_file = PROJECT_ROOT / ".claude" / "scripts" / ".env"
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def content_hash(text: str) -> str:
    """计算 SKILL.md 内容的哈希值"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_frontmatter(content: str) -> dict:
    """解析 SKILL.md 的 YAML frontmatter（简版解析器）"""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    fm_text = content[3:end].strip()
    result = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            result[key] = val
    return result


# ═══════════════════════════════════════════════════════════
# 技能扫描
# ═══════════════════════════════════════════════════════════

def scan_skills() -> dict[str, dict]:
    """扫描 skills 目录，返回 {name: {frontmatter, content, hash}}"""
    skills = {}
    if not SKILLS_DIR.exists():
        print(f"[ERROR] skills 目录不存在: {SKILLS_DIR}")
        return skills

    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name in SKIP_SKILLS:
            continue

        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            print(f"[WARN] {name}: 缺少 SKILL.md，跳过")
            continue

        content = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        skills[name] = {
            "name": name,
            "frontmatter": fm,
            "content": content,
            "hash": content_hash(content),
        }

    return skills


def load_index() -> dict:
    """加载路由索引"""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {"version": "1.0", "skills": {}}


def save_index(index: dict):
    """保存路由索引"""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(index, ensure_ascii=False, indent=2)
    INDEX_PATH.write_text(json_text + "\n", encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 差异检测
# ═══════════════════════════════════════════════════════════

def detect_changes(skills: dict, index: dict) -> tuple[set, set, set]:
    """
    返回 (new, removed, modified) 三组技能名集合。
    SKIP_SKILLS 中的技能不参与差异检测。
    """
    indexed = set(index.get("skills", {}).keys()) - SKIP_SKILLS
    current = set(skills.keys())

    new = current - indexed
    removed = indexed - current

    modified = set()
    for name in current & indexed:
        old_hash = index["skills"][name].get("content_hash", "")
        # 如果没有历史哈希（手动创建的索引），不在首次运行时标记为修改
        if not old_hash:
            continue
        if skills[name]["hash"] != old_hash:
            modified.add(name)

    return new, removed, modified


# ═══════════════════════════════════════════════════════════
# LLM 调用
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是一个技能路由分析器。你的任务是阅读技能文档，提取路由信息。

对于给定的技能，返回一个 JSON 对象，包含以下字段：

- triggers: 字符串数组，描述哪些用户意图/场景触发此技能（中文短语，3-6 个）
- description: 一句话功能描述（中文，20 字以内）
- priority: 整数 2-20，路由优先级（数字越小越优先）
- category: 分类，必须是以下之一：
    "clarification" (需求澄清),
    "development" (开发实现),
    "debugging" (调试修复),
    "understanding" (代码理解),
    "architecture" (架构改进),
    "planning" (规划文档),
    "meta" (元技能/配置),
    "style" (输出风格)

优先级参考：
2-3: 紧急诊断类（错误、bug）
3-4: 需求澄清类
4-5: 代码理解类
5-6: 架构改进类
6-7: 原型验证类
7-8: 正式开发类
8-10: 文档规划类
10-12: 任务管理类
12-14: 辅助/风格类

只返回 JSON 对象，不要有其他内容。"""


def analyze_skill(api_key: str, skill_name: str, skill_content: str) -> dict | None:
    """调用 DeepSeek API 分析技能并返回路由信息"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 只传 SKILL.md 的前 3000 字符，足够分析用途
    truncated = skill_content[:3000]

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"技能名称：{skill_name}\n\n技能内容：\n{truncated}"},
        ],
        "temperature": 0.1,
        "max_tokens": 1000,
    }

    try:
        resp = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] API 请求失败: {e}")
        return None

    result = resp.json()
    content = result["choices"][0]["message"]["content"].strip()

    # 提取 JSON（处理可能的 markdown 代码块）
    if "```" in content:
        lines = content.split("\n")
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith("```"):
                in_json = not in_json
                continue
            if in_json:
                json_lines.append(line)
        if json_lines:
            content = "\n".join(json_lines)

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[ERROR] LLM 返回的 JSON 解析失败: {e}")
        print(f"[DEBUG] 原始内容:\n{content}")
        return None


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

def main(dry_run: bool = False, force_all: bool = False):
    print("=" * 60)
    print("Skill Route Index Synchronizer")
    print("=" * 60)

    # 1. 扫描技能
    print("\n[1/4] 扫描 skills 目录...")
    skills = scan_skills()
    print(f"  发现 {len(skills)} 个技能: {', '.join(skills.keys()) or '(无)'}")

    if not skills:
        print("\n[END] 没有发现任何技能。")
        return

    # 2. 加载索引
    print("\n[2/4] 加载路由索引...")
    index = load_index()
    indexed_count = len(index.get("skills", {}))
    print(f"  索引中已有 {indexed_count} 个技能")

    # 3. 检测差异
    print("\n[3/4] 检测差异...")
    if force_all:
        new = set(skills.keys())
        removed = set()
        modified = set(skills.keys())
        print(f"  (force-all) 将重新分析全部 {len(new)} 个技能")
    else:
        new, removed, modified = detect_changes(skills, index)

    print(f"  新增: {len(new)} 个 {list(new) if new else '(无)'}")
    print(f"  删除: {len(removed)} 个 {list(removed) if removed else '(无)'}")
    print(f"  修改: {len(modified)} 个 {list(modified) if modified else '(无)'}")

    to_analyze = new | modified

    # 4. 处理
    print(f"\n[4/4] {'[DRY RUN] ' if dry_run else ''}更新索引...")

    if not to_analyze and not removed:
        print("  没有变化，索引已是最新。")
        return

    # 处理删除
    for name in removed:
        if not dry_run:
            del index["skills"][name]
        print(f"  [移除] {name}")

    # 处理新增和修改
    if to_analyze:
        api_key = get_api_key()
        if not api_key:
            print("\n[ERROR] 未找到 DEEPSEEK_API_KEY！")
            print("  请设置环境变量 DEEPSEEK_API_KEY 或创建 .claude/scripts/.env 文件:")
            print('  DEEPSEEK_API_KEY="your-api-key-here"')
            sys.exit(1)

        for i, name in enumerate(sorted(to_analyze), 1):
            print(f"\n  [{i}/{len(to_analyze)}] 分析: {name}")

            if dry_run:
                print(f"    (dry-run) 将调用 API 分析此技能")
                continue

            skill = skills[name]
            result = analyze_skill(api_key, name, skill["content"])

            if result is None:
                print(f"    [FAIL] 分析失败，跳过")
                continue

            # 验证必要字段
            required = ["triggers", "description", "priority", "category"]
            missing = [f for f in required if f not in result]
            if missing:
                print(f"    [FAIL] LLM 返回缺少字段: {missing}")
                continue

            index["skills"][name] = {
                "triggers": result["triggers"],
                "description": result["description"],
                "priority": result["priority"],
                "category": result["category"],
                "content_hash": skill["hash"],
            }

            print(f"    [OK] priority={result['priority']} "
                  f"category={result['category']} "
                  f"triggers={result['triggers'][:3]}")

            # 避免频繁请求
            if i < len(to_analyze):
                time.sleep(1)

    # 保存
    if not dry_run:
        save_index(index)
        print(f"\n[DONE] 索引已更新，共 {len(index['skills'])} 个技能")
    else:
        print(f"\n[DONE] (dry-run) 以上为预览，未实际修改索引")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    force_all = "--force-all" in sys.argv
    main(dry_run=dry_run, force_all=force_all)