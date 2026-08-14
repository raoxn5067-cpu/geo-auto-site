#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态站点构建器
读取 content/ 下的 Markdown，渲染成 public/ 下的 HTML。
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_DIR = ROOT / "src" / "templates"
PUBLIC_DIR = ROOT / "public"
DATA_FILE = ROOT / "src" / "data" / "topics.json"

SITE_NAME = "GEO 每日洞察"
SITE_DESCRIPTION = "面向 AI 搜索引擎的每日自动更新内容站"


def load_posts() -> list[dict]:
    posts = []
    if not CONTENT_DIR.exists():
        return posts

    for path in sorted(CONTENT_DIR.glob("*.md"), reverse=True):
        post = frontmatter.load(path)
        posts.append({
            "title": post.get("title", "未命名"),
            "summary": post.get("summary", ""),
            "date": post.get("date", ""),
            "iso_date": post.get("iso_date", ""),
            "slug": post.get("slug", path.stem),
            "content": post.content,
        })
    return posts


def estimate_read_time(text: str) -> int:
    words = len(re.findall(r"[\u4e00-\u9fa5]", text)) + len(re.findall(r"[a-zA-Z0-9]+", text))
    return max(1, round(words / 300))


def render_markdown(md: str) -> str:
    return markdown.markdown(
        md,
        extensions=[
            "toc",
            "tables",
            "fenced_code",
            "nl2br",
            "md_in_html",
        ],
    )


def build():
    PUBLIC_DIR.mkdir(exist_ok=True)
    for old in PUBLIC_DIR.iterdir():
        if old.is_dir():
            shutil.rmtree(old)
        else:
            old.unlink()

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )

    year = datetime.now().year
    base_path = os.environ.get("BASE_PATH", "")

    posts = load_posts()

    # 首页
    index_html = env.get_template("index.html").render(
        site_name=SITE_NAME,
        site_description=SITE_DESCRIPTION,
        posts=posts,
        year=year,
        base_path=base_path,
        canonical_url=f"{base_path}/",
        lang="zh-CN",
    )
    (PUBLIC_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # 文章页
    for post in posts:
        post_dir = PUBLIC_DIR / post["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        html = env.get_template("post.html").render(
            site_name=SITE_NAME,
            site_description=SITE_DESCRIPTION,
            title=post["title"],
            summary=post["summary"],
            date=post["date"],
            iso_date=post["iso_date"],
            read_time=estimate_read_time(post["content"]),
            content_html=render_markdown(post["content"]),
            year=year,
            base_path=base_path,
            canonical_url=f"{base_path}/{post['slug']}/",
            lang="zh-CN",
        )
        (post_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"构建完成: {len(posts)} 篇文章 -> {PUBLIC_DIR}")


if __name__ == "__main__":
    build()
