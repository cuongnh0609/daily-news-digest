# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not an application codebase**. It is the configuration + assets for a Claude Code **Routine** that runs every 5 hours (JST cron `0 0,5,10,15,20 * * *`) and produces a news digest HTML for a Software/Cloud Engineer living in Tokyo, studying JLPT N2+. Three files are the entire "product":

- `ROUTINE_PROMPT.md` — the prompt pasted into the Routine's Prompt field. **Source of truth for behavior.** Everything the Routine does (sources, counts, layout, dedup, Slack format) lives here.
- `news_template.html` — HTML/CSS skeleton the Routine fills per run. Three color-coded sections, 2-column responsive layout (≥1000px), dark mode toggle (Light/System/Dark, persisted in localStorage), impact badges. Placeholders: `{{DATE}}`, `{{HOUR}}`, `{{DOW}}`.
- `README.md` — human-facing setup guide (Vietnamese, v3) for creating/updating the Routine, connecting GitHub + Slack, and switching the schedule from `daily` preset to the 5-hour cron.

No build, test runner, or package manifest. Editing these files *is* the development workflow.

## Single-repo flow

This repo (`daily-news-digest`) holds both the Routine configuration **and** receives the Routine's output. The Routine commits output here: `news/YYYY-MM-DD_HH.html` on branch `claude/news-YYYY-MM-DD-HH`, plus `state/last_run_urls.json` for cross-run deduplication. The Routine does **not** merge to `main`.

"Update the routine" means: edit `ROUTINE_PROMPT.md` here, then the user pastes it into the Routine via the web UI or `/schedule update <routine-id>`.

## Output contract the prompt must uphold

When editing `ROUTINE_PROMPT.md`, preserve these invariants:

- **11 articles per run**, split **5 / 3 / 3** across sections A (Japan general news, JP), B (Tech/AI in Japanese, JP), C (Global Tech/AI, EN).
- **B and C must be ≥ 2/3 AI-focused** (Claude Code, AI-driven dev, agentic, LLM, MCP, RAG) — at most 1 non-AI article per section.
- **Two-column layout per article**: left = article body + Vietnamese translation; right = vocabulary + grammar (JP sections) or term glossary + impact note (EN section).
- **Section C impact badges** `🔴 HIGH / 🟠 MEDIUM / 🟡 LOW` — Slack message reports count per badge.
- **Dedup is mandatory, runs first**: Bước 0 in the prompt reads `state/last_run_urls.json`, builds a blocklist from the last **48h** of runs, applies fuzzy title matching (>70% similar = duplicate) + canonical URL matching, then falls back to widening the time window (5h→12h→24h for A, 24h→48h→72h for B/C) or reducing article count if blocked out.
- **State schema**: `{ last_run_at, runs: [{ run_at, urls, titles }] }` with a rolling **7-day** window (entries older than 7 days are dropped on update).
- **Copyright**: rewrite content, never quote more than 15 consecutive words; keep English technical terms in Vietnamese translations (deploy, container, runtime, pull request).

## Template ↔ prompt alignment

Template and prompt are currently in sync at v3:
- Three sections: `#japan-news` (red), `#japan-tech` (green), `#global-tech` (blue).
- `article.news-card` + `news-card--jp` / `news-card--en` layout variants.
- `.impact-badge.high|medium|low` for section C.
- `[data-theme="light|dark"]` with `prefers-color-scheme` fallback.

If you change the prompt's contract (section IDs, classes, badge names, placeholders), verify the template still matches — and vice versa. The template comment block near the top instructs the Routine on usage; keep it accurate.

## Working with the user

- Primary language in source files is Vietnamese with Japanese headings and English technical terms. Preserve that mix; do not "translate to English" unless asked.
- User is on **Claude Max** (15 Routine runs/day). The 5-hour cadence uses 5/15 — headroom remains for ad-hoc Routine work.
- Target model for the Routine is **Claude Opus 4.7**. Current token budget is ~15–25K output tokens/run.
- User's Slack handle for the DM is `@cuongnh`. claude.ai account timezone must be `Asia/Tokyo (UTC+9)` for the cron to fire at JST.
