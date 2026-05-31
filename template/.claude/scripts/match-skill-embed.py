#!/usr/bin/env python3
"""
Skill Match — Embedding 语义匹配器
====================================
基于本地轻量 embedding 模型，对用户查询与技能 triggers 做语义相似度匹配。
零 API 调用、零 token 消耗，首次运行自动下载模型（~100MB）。

用法:
    python match-skill-embed.py "用户原始问题"
    python match-skill-embed.py --top 3 "用户原始问题"
    python match-skill-embed.py --json "用户原始问题"

依赖:
    pip install sentence-transformers numpy
"""

import json
import sys
from pathlib import Path
import hashlib

import numpy as np

# ── 路径配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "skills" / "skill-router" / "route-index.json"
CACHE_DIR = PROJECT_ROOT / "scripts" / ".embedding_cache"
EMBED_PATH = CACHE_DIR / "embeddings.npy"
META_PATH = CACHE_DIR / "meta.json"

# ── 模型配置 ──────────────────────────────────────────────
MODEL_NAME = "BAAI/bge-small-zh-v1.5"  # 中文专用，102MB

_model = None


def get_model():
    """懒加载 embedding 模型（单例）"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def index_hash(index: dict) -> str:
    """计算 route-index.json 内容的哈希（忽略 content_hash 字段）"""
    # 只哈希 triggers + description + priority（这些影响 embedding）
    stripped = {}
    for name, info in index.get("skills", {}).items():
        stripped[name] = {
            "triggers": info.get("triggers", []),
            "description": info.get("description", ""),
            "priority": info.get("priority", 10),
        }
    raw = json.dumps(stripped, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def build_embeddings(index: dict, model) -> tuple[np.ndarray, list[str], str]:
    """
    为所有技能的 triggers + description 计算 embedding。
    返回 (embeddings_matrix, skill_names, hash)。
    """
    texts = []
    names = []
    for name, info in index.get("skills", {}).items():
        # 拼接该技能的所有语义信息
        parts = list(info.get("triggers", []))
        desc = info.get("description", "")
        if desc:
            parts.append(desc)
        texts.append("；".join(parts))
        names.append(name)

    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings, names, index_hash(index)


def load_or_build_embeddings(index: dict, model) -> tuple[np.ndarray, list[str]]:
    """加载缓存或重新构建 embeddings"""
    current_hash = index_hash(index)

    # 检查缓存
    if EMBED_PATH.exists() and META_PATH.exists():
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        if meta.get("hash") == current_hash and meta.get("model") == MODEL_NAME:
            embeddings = np.load(EMBED_PATH)
            names = meta.get("names", [])
            if len(names) == embeddings.shape[0]:
                return embeddings, names

    # 重新构建
    print(f"[embed] building cache for {len(index.get('skills', {}))} skills...", file=sys.stderr)
    embeddings, names, _ = build_embeddings(index, model)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBED_PATH, embeddings)
    META_PATH.write_text(json.dumps({
        "hash": current_hash,
        "model": MODEL_NAME,
        "names": names,
    }, ensure_ascii=False), encoding="utf-8")

    print(f"[embed] cache ready ({embeddings.shape[0]} skills, {embeddings.shape[1]}d)", file=sys.stderr)
    return embeddings, names


def match(query: str, index: dict, top_n: int = 1) -> list[dict]:
    """语义匹配主逻辑"""
    model = get_model()
    embeddings, names = load_or_build_embeddings(index, model)

    # 编码查询
    query_vec = model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]

    # cosine 相似度（已 normalize，直接点积）
    scores = embeddings @ query_vec

    # priority 衰减（仅微调，语义为主）
    scored = []
    for i, name in enumerate(names):
        info = index["skills"].get(name, {})
        priority = info.get("priority", 10)
        semantic_score = float(scores[i])

        # priority 做小幅度微调：±5%
        priority_bonus = 1.0 + 0.05 * (10 - priority) / 10
        final_score = semantic_score * priority_bonus

        if final_score > 0.05:  # 最小阈值
            scored.append({
                "name": name,
                "score": round(final_score, 4),
                "semantic": round(semantic_score, 4),
                "priority": priority,
                "category": info.get("category", ""),
                "description": info.get("description", ""),
            })

    scored.sort(key=lambda x: -x["score"])
    return scored[:top_n]


def main():
    args = sys.argv[1:]

    top_n = 1
    json_out = False
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
        print("usage: match-skill-embed.py [--top N] [--json] <query>", file=sys.stderr)
        sys.exit(1)

    if not INDEX_PATH.exists():
        print('{"error": "route-index.json not found"}', file=sys.stderr)
        sys.exit(1)

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    results = match(query, index, top_n=top_n)

    if json_out:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("(none)")
        else:
            for r in results:
                print(f"{r['name']} ({r['score']}) ")


if __name__ == "__main__":
    main()