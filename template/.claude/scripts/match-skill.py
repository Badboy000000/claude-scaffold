#!/usr/bin/env python3
"""
Skill Match — 本地意图匹配器
=============================
根据用户查询，与 route-index.json 中的 triggers 做本地关键词打分，
返回命中最高的技能名（零 API 调用、零 token 消耗）。

用法:
    python match-skill.py "用户原始问题"
    python match-skill.py --top 3 "用户原始问题"
    python match-skill.py --json "用户原始问题"

输出:
    默认:    diagnose
    --top N: diagnose (0.92) | tdd (0.67) | grill-with-docs (0.45)
    --json:  [{"name":"diagnose","score":0.92,"reason":"..."}, ...]
"""

import json
import sys
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "skills" / "skill-router" / "route-index.json"


def tokenize(text: str) -> set[str]:
    """
    中文关键词提取：uni-gram + bi-gram 混合。
    例如 "接口报500错误" →
        {"接口", "口报", "报500", "500", "00错", "错误", ...}
    """
    chars = text.strip()
    tokens = set()

    # 提取连续的字母/数字块作为完整 token（英文术语、数字）
    import re
    blocks = re.findall(r'[a-zA-Z0-9_]+', chars)
    tokens.update(b.lower() for b in blocks)

    # uni-gram（单个中文字符）
    for c in chars:
        if '一' <= c <= '鿿':
            tokens.add(c)

    # bi-gram（中文二字词）
    for i in range(len(chars) - 1):
        a, b = chars[i], chars[i + 1]
        if '一' <= a <= '鿿' and '一' <= b <= '鿿':
            tokens.add(a + b)

    # tri-gram（中文三字词，精准度更高）
    for i in range(len(chars) - 2):
        a, b, c = chars[i], chars[i + 1], chars[i + 2]
        if all('一' <= x <= '鿿' for x in (a, b, c)):
            tokens.add(a + b + c)

    return tokens


def match(query: str, skills: dict, top_n: int = 1) -> list[dict]:
    """
    计算每个技能与查询的匹配得分，返回 Top N。

    scoring:
        - 查询 token 集 与每个 trigger 的 token 集做 Jaccard 相似度
        - 取该技能所有 triggers 的最高分
        - 乘以 priority 衰减系数
    """
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scored = []
    for name, info in skills.items():
        triggers = info.get("triggers", [])
        priority = info.get("priority", 10)

        max_overlap = 0.0
        best_trigger = ""

        for trigger in triggers:
            trigger_tokens = tokenize(trigger)
            if not trigger_tokens:
                continue
            intersection = query_tokens & trigger_tokens
            union = query_tokens | trigger_tokens
            overlap = len(intersection) / len(union) if union else 0

            if overlap > max_overlap:
                max_overlap = overlap
                best_trigger = trigger

        # priority 加权：priority 越小（越紧急），权重越高
        priority_weight = 1.0 / (1.0 + 0.05 * priority)

        score = max_overlap * priority_weight

        if score > 0:
            scored.append({
                "name": name,
                "score": round(score, 4),
                "priority": priority,
                "category": info.get("category", ""),
                "reason": best_trigger,
                "description": info.get("description", ""),
            })

    scored.sort(key=lambda x: (-x["score"], x["priority"]))
    return scored[:top_n]


def main():
    args = sys.argv[1:]

    top_n = 1
    json_out = False

    # 解析参数
    query_parts = []
    i = 0
    while i < len(args):
        if args[i] == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
            i += 2
        elif args[i] == "--json":
            json_out = True
            i += 1
        else:
            query_parts.append(args[i])
            i += 1

    query = " ".join(query_parts).strip()
    if not query:
        print("usage: match-skill.py [--top N] [--json] <query>", file=sys.stderr)
        sys.exit(1)

    # 加载索引
    if not INDEX_PATH.exists():
        print('{"error": "route-index.json not found"}', file=sys.stderr)
        sys.exit(1)

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    skills = index.get("skills", {})

    results = match(query, skills, top_n=top_n)

    if json_out:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("(none)")
        else:
            for r in results:
                print(f"{r['name']} ({r['score']}) [{r['reason']}]")


if __name__ == "__main__":
    main()