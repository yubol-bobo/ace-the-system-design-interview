#!/usr/bin/env python3
"""
Renders Study-Guide topic pages from structured data.
Each TOPIC entry produces a self-contained bilingual HTML page
under /pages/guide/<category>/<slug>.html
"""
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "pages" / "guide"

CATEGORY_LABELS = {
    "foundations": ("Foundations", "基础功"),
    "distributed": ("Distributed Systems", "分布式系统"),
    "classical":   ("Classical Designs", "经典设计"),
    "llm":         ("LLM Systems", "LLM 系统"),
    "ml":          ("ML Systems", "ML 系统"),
    "safety":      ("Safety", "安全"),
}

def depth_prefix(category: str) -> str:
    # pages/guide/<cat>/file.html  → ../../../  to repo root
    return "../../../"

PAGE_TPL = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_en} — SD-Guide</title>
  <meta name="description" content="{desc_en}">
  <link rel="stylesheet" href="{root}assets/css/main.css">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>

  <nav class="nav">
    <div class="nav-inner">
      <a class="nav-brand" href="{root}index.html"><span class="nav-brand-logo">SD</span><span>SD-Guide</span></a>
      <ul class="nav-links">
        <li><a href="{root}index.html"><span data-lang="en">Home</span><span data-lang="zh">首页</span></a></li>
        <li><a href="{root}pages/arena/index.html" data-match="/arena"><span data-lang="en">真题 Arena</span><span data-lang="zh">真题竞技场</span></a></li>
        <li><a href="{root}pages/guide/index.html" class="active" data-match="/guide"><span data-lang="en">Study Guide</span><span data-lang="zh">学习手册</span></a></li>
        <li><a href="{root}pages/resources/index.html" data-match="/resources"><span data-lang="en">Resources</span><span data-lang="zh">资源</span></a></li>
        <li><a href="{root}pages/about/index.html" data-match="/about"><span data-lang="en">About</span><span data-lang="zh">关于</span></a></li>
      </ul>
      <div class="nav-tools">
        <button class="icon-btn" id="lang-toggle">中文</button>
        <button class="icon-btn" id="theme-toggle">☀</button>
      </div>
    </div>
  </nav>

  <main class="page-body">
    <div class="container">

      <div class="breadcrumb">
        <a href="{root}pages/guide/index.html"><span data-lang="en">Study Guide</span><span data-lang="zh">学习手册</span></a>
        <span>›</span>
        <span class="crumb-category">{cat_en}<span data-lang="zh" style="display:none">{cat_zh}</span></span>
      </div>

      <header class="page-header">
        <h1 class="page-title">
          <span data-lang="en">{title_en}</span>
          <span data-lang="zh">{title_zh}</span>
        </h1>
        <div class="topic-meta">
          {tag_html}
        </div>
        <p class="page-subtitle">
          <span data-lang="en">{lead_en}</span>
          <span data-lang="zh">{lead_zh}</span>
        </p>
      </header>

      <article class="topic-prose">
        <nav class="topic-toc">
          <h4><span data-lang="en">On this page</span><span data-lang="zh">本页目录</span></h4>
          <ol>
            {toc_html}
          </ol>
        </nav>

        <div data-lang="en">
{body_en}
        </div>
        <div data-lang="zh">
{body_zh}
        </div>
      </article>

      <section class="topic-footer-links">
        {footer_links_html}
      </section>

    </div>
  </main>

  <footer class="footer">
    <div class="container">
      <p>
        <span data-lang="en">© SD-Guide · Built for OpenAI &amp; Anthropic system design prep. Not affiliated with either company.</span>
        <span data-lang="zh">© SD-Guide · 为 OpenAI 与 Anthropic 系统设计面试准备。与两家公司无关联。</span>
      </p>
    </div>
  </footer>

  <script src="{root}assets/js/app.js"></script>
</body>
</html>
"""


def render_topic(topic):
    """Render a single topic dict → HTML file."""
    category = topic["category"]
    slug     = topic["slug"]
    root     = depth_prefix(category)
    cat_en, cat_zh = CATEGORY_LABELS[category]

    # Tags
    tag_html = "".join(
        f'<span class="tag">{t}</span>' for t in topic.get("tags", [])
    )

    # Book references
    refs = topic.get("refs", [])
    if refs:
        refs_html = '<span class="tag" style="background:var(--openai-glow);border-color:var(--openai)">📚 ' + \
                    " · ".join(refs) + '</span>'
        tag_html = refs_html + tag_html

    # TOC
    toc_items = topic.get("toc_en", [])
    toc_items_zh = topic.get("toc_zh", toc_items)
    toc_html_parts = []
    for i, (en, zh) in enumerate(zip(toc_items, toc_items_zh), 1):
        anchor = f"s{i}"
        toc_html_parts.append(
            f'<li><a href="#{anchor}"><span data-lang="en">{en}</span>'
            f'<span data-lang="zh">{zh}</span></a></li>'
        )
    toc_html = "\n            ".join(toc_html_parts)

    # Footer cross-links
    footer_parts = []
    for label_en, label_zh, href, title_en, title_zh in topic.get("links", []):
        footer_parts.append(
            f'<a href="{href}">'
            f'<span class="label"><span data-lang="en">{label_en}</span>'
            f'<span data-lang="zh">{label_zh}</span></span>'
            f'<strong><span data-lang="en">{title_en}</span>'
            f'<span data-lang="zh">{title_zh}</span></strong></a>'
        )
    footer_links_html = "\n        ".join(footer_parts)

    # Render
    html = PAGE_TPL.format(
        root=root,
        title_en=topic["title_en"],
        title_zh=topic["title_zh"],
        desc_en=topic.get("desc_en", topic.get("lead_en","")),
        cat_en=cat_en,
        cat_zh=cat_zh,
        tag_html=tag_html,
        lead_en=topic["lead_en"],
        lead_zh=topic["lead_zh"],
        toc_html=toc_html,
        body_en=topic["body_en"],
        body_zh=topic["body_zh"],
        footer_links_html=footer_links_html,
    )

    # Write
    out_path = OUTPUT_DIR / category / f"{slug}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✓ {category}/{slug}.html")


# Import all topic definitions
def run(topics):
    for t in topics:
        render_topic(t)


if __name__ == "__main__":
    # Lazy import so each topics file can be generated independently
    import importlib, sys
    mod_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mod_name == "all":
        for name in ["topics_foundations", "topics_distributed",
                     "topics_classical", "topics_llm",
                     "topics_ml", "topics_safety"]:
            try:
                m = importlib.import_module(name)
                run(m.TOPICS)
            except Exception as e:
                print(f"⚠  {name}: {e}")
    else:
        m = importlib.import_module(mod_name)
        run(m.TOPICS)
