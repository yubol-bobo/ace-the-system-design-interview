# Ace the System Design Interview

Bilingual (English / 中文) study hub for system design interviews at OpenAI, Anthropic, Google, xAI, and other frontier AI labs.

**Live site:** <https://yubol-bobo.github.io/ace-the-system-design-interview/>

## What's Inside

| Section | Description |
|---------|-------------|
| **真题 Arena** | 100 verified interview questions (38 OpenAI + 31 Anthropic + 25 Google + 6 xAI) with sources, filterable by company, category, difficulty, and frequency. Each question has a detailed solution page covering architecture, APIs, data models, trade-offs, and follow-ups. |
| **Study Guide** | 20 deep-dive topic notes across 6 tracks: Foundations, Distributed Systems, Classical Designs, LLM Systems, ML Systems, and Safety. Cross-references 8 canonical books by chapter. |
| **Resources** | Curated books, blogs, courses, and repos ranked by interview relevance. |
| **About & Roadmap** | Methodology, credibility scoring (S/A/B/C/D), an 8-week study plan, and the site's tech stack. |

## Project Structure

```
index.html              # Landing page
.nojekyll               # Tells GitHub Pages to serve files literally
assets/
  css/main.css          # Styles (~1,000 lines)
  js/app.js             # Theme toggle, language switch, arena filtering
pages/
  arena/                # Arena index + 100 question detail pages
  guide/                # Study guide topics (6 tracks, 20 pages)
  resources/            # External resource links
  about/                # Methodology & roadmap
books/                  # (local-only, gitignored) reference PDFs/EPUBs
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

The site is deployed via GitHub Pages from the `main` branch at repository root. The `.nojekyll` file disables Jekyll processing so paths like `pages/arena/index.html` work as-is.

## Disclaimer

Not affiliated with OpenAI, Anthropic, Google, or xAI. Content synthesised from publicly available interview reports (LeetCode, Blind, PracHub, Glassdoor, Jointaro, GitHub, 小红书) and canonical textbooks and engineering blogs. Reference PDFs are kept locally and are not included in this repository.

## License

For personal study use.
