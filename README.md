# SD-Guide — Ace the System Design Interview

Bilingual (English / 中文) study hub for system design interviews at OpenAI, Anthropic, and other frontier AI labs.

**Live site:** <https://yubol-bobo.github.io/ace-the-system-design-interview/>

## What's Inside

| Section | Description |
|---------|-------------|
| **真题 Arena** | 36+ verified interview questions (OpenAI & Anthropic) with sources, filterable by company, category, difficulty, and frequency. Each question has a detailed solution page covering architecture, APIs, data models, trade-offs, and follow-ups. |
| **Study Guide** | 18 deep-dive topic notes across 5 tracks: Foundations, Distributed Systems, Classical Designs, LLM Systems, and ML Systems. Cross-references 7 canonical books by chapter. |
| **Resources** | Curated books, blogs, courses, and repos ranked by interview relevance. |
| **About & Roadmap** | Methodology, credibility scoring (S/A/B/C/D), an 8-week study plan, and the site's tech stack. |

## Project Structure

```
index.html              # Landing page
assets/
  css/main.css          # Styles
  js/app.js             # Theme toggle, language switch, filtering
pages/
  arena/                # Interview question index + individual question pages
  guide/                # Study guide topics (foundations, distributed, classical, llm, ml, safety)
  resources/            # External resource links
  about/                # Methodology & roadmap
books/                  # Reference PDFs/EPUBs (7 canonical texts)
```

## Features

- Dark/light theme toggle
- One-click English/中文 language switch
- Company, category, and difficulty filters in the Arena
- Static HTML — no build step, deploy anywhere

## Local Development

Open `index.html` in a browser, or serve locally:

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

## Deployment

The site is deployed via GitHub Pages from the `main` branch.

## License

For personal study use.
