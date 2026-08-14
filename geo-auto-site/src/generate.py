#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEO 内容自动生成器
每天调用 OpenAI API 生成一篇面向 AI 搜索引擎优化的文章。
"""

import os
import json
import random
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import frontmatter
from openai import OpenAI


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
TOPICS_FILE = ROOT / "src" / "data" / "topics.json"


def load_topics() -> dict:
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_topic(topics: list[str]) -> str:
    """随机选择一个主题；可改为按顺序或根据已生成内容去重。"""
    return random.choice(topics)


def build_prompt(topic: str, niche: str, lang: str) -> str:
    return f"""你是一位资深的 {niche} 领域内容专家。请围绕以下主题创作一篇面向 AI 搜索引擎（如 ChatGPT Search、Perplexity、Gemini）优化的文章：

主题：{topic}

要求：
1. 标题必须是一个用户会搜索的问句或问题解决型短语，简洁有力。
2. 开头给出 50 字以内的核心结论（summary），让 AI 搜索引擎能直接抓取答案。
3. 正文使用清晰的 H2/H3 层级，包含：背景、关键要点、实操建议、常见误区。
4. 必须包含一个 FAQ 小节，至少 3 个问答对，使用用户真实搜索口吻。
5. 使用列表、表格、加粗等方式提升可读性。
6. 语言自然、信息密度高，避免空话和营销腔。
7. 全文控制在 1200-1800 字。
8. 输出格式为 Markdown，不要包含 YAML frontmatter，只返回正文 Markdown。

语言：{lang}
"""


def clean_markdown(md: str) -> str:
    # 移除模型可能输出的代码块包裹
    md = md.strip()
    if md.startswith("```markdown"):
        md = md[len("```markdown"):].strip()
    if md.startswith("```"):
        md = md[3:].strip()
    if md.endswith("```"):
        md = md[:-3].strip()
    return md


def extract_title(md: str) -> str:
    # 提取第一个 # 标题
    match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "未命名文章"


def extract_summary(md: str) -> str:
    # 提取第一个加粗或普通段落作为摘要
    lines = [l.strip() for l in md.splitlines() if l.strip()]
    for line in lines[1:]:  # 跳过标题
        if line.startswith("**") and "结论" in line:
            continue
        text = re.sub(r"\*\*|__", "", line)
        if len(text) > 20 and not text.startswith("#"):
            return text[:200]
    return ""


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE)
    s = re.sub(r"[-\s]+", "-", s.strip())
    return s[:80].strip("-") or "post"


def generate_article(topic: Optional[str] = None) -> dict:
    config = load_topics()
    topic = topic or pick_topic(config["topics"])

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("环境变量 OPENAI_API_KEY 未设置")

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(topic, config["niche"], config["language"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 成本低、速度快；可升级为 gpt-4o
        messages=[
            {"role": "system", "content": "你是一名擅长 GEO（Generative Engine Optimization）的内容专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2500,
    )

    raw_md = response.choices[0].message.content or ""
    body = clean_markdown(raw_md)
    title = extract_title(body)
    summary = extract_summary(body)
    slug = slugify(title)

    now = datetime.now(timezone(timedelta(hours=8)))  # 北京时间
    date_str = now.strftime("%Y-%m-%d")
    iso_str = now.isoformat()

    post = frontmatter.Post(
        body,
        title=title,
        summary=summary,
        date=date_str,
        iso_date=iso_str,
        topic=topic,
        slug=slug,
        tags=[config["niche"]],
    )

    CONTENT_DIR.mkdir(exist_ok=True)
    filename = f"{date_str}-{slug}.md"
    filepath = CONTENT_DIR / filename

    # 如果当天已存在，追加序号
    counter = 1
    while filepath.exists():
        filename = f"{date_str}-{slug}-{counter}.md"
        filepath = CONTENT_DIR / filename
        counter += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    print(f"已生成文章: {filepath}")
    print(f"标题: {title}")
    return {"filepath": str(filepath), "title": title, "summary": summary}


if __name__ == "__main__":
    result = generate_article()
    print(json.dumps(result, ensure_ascii=False, indent=2))
