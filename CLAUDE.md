# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not an application codebase**. It is the configuration + assets for a daily Japanese/Tech news digest that runs every 5 hours (JST) for a Software/Cloud Engineer in Tokyo studying JLPT N2+.

**Execution model: local cron (launchd) on the user's MacBook — NOT Anthropic Routines.** A launchd plist fires `scripts/run_digest.sh` at `00/05/10/15/20` JST. The wrapper invokes `claude --permission-mode bypassPermissions --print "$(cat ROUTINE_PROMPT.md)"`, and the headless Claude CLI handles crawl → HTML → git commit/push → email notification per the prompt.

Key files:

- `ROUTINE_PROMPT.md` — prompt piped into `claude --print`. **Source of truth for behavior.** Name still says "routine" for historical reasons; it now means the 5-hour cron job.
- `news_template.html` — HTML/CSS skeleton filled per run. Three color-coded sections, 2-column responsive layout, dark mode toggle, impact badges. Placeholders: `{{DATE}}`, `{{HOUR}}`, `{{DOW}}`.
- `scripts/run_digest.sh` — cron wrapper. Does `git pull` → `claude --print ...` → logs to `logs/run_<timestamp>.log`.
- `scripts/notify_email.sh` — reads body from stdin, sends via macOS Mail.app (osascript). Recipient from `$DIGEST_EMAIL_TO` (default `gian@core-corp.co.jp`).
- `scripts/com.cuongnh.daily-news-digest.plist` — launchd plist. Installed to `~/Library/LaunchAgents/`, loaded with `launchctl bootstrap`.
- `README.md` — Vietnamese setup guide for launchd installation + test runs.

No build, test runner, or package manifest. Editing these files *is* the development workflow.

## Single-repo flow

This repo (`cuongnh0609/daily-news-digest`, private on GitHub) holds config + assets **and** receives output. The cron run commits to branch `claude/news-YYYY-MM-DD-HH` and pushes; does **not** merge to `main`. `state/last_run_urls.json` is committed on the same branch for cross-run deduplication.

"Update the routine" now means: edit `ROUTINE_PROMPT.md`, commit + push to `main`. The next cron run does `git pull` in the wrapper, so it picks up the new prompt automatically.

## Output contract the prompt must uphold

When editing `ROUTINE_PROMPT.md`, preserve these invariants:

- **11 articles per run**, split **5 / 3 / 3** across sections A (Japan general news, JP), B (Tech/AI in Japanese, JP), C (Global Tech/AI, EN).
- **B and C must be ≥ 2/3 AI-focused** (Claude Code, AI-driven dev, agentic, LLM, MCP, RAG) — at most 1 non-AI article per section.
- **Two-column layout per article**: left = article body + Vietnamese translation; right = vocabulary + grammar (JP) or term glossary + impact note (EN).
- **Section C impact badges** `🔴 HIGH / 🟠 MEDIUM / 🟡 LOW` — email summary reports count per badge.
- **Dedup is mandatory, runs first (Bước 0)**: reads `state/last_run_urls.json`, builds blocklist from the last **48h** of runs, applies fuzzy title matching (>70% similar = duplicate) + canonical URL matching. Falls back to widening time window (5h→12h→24h for A, 24h→48h→72h for B/C) or reducing count if blocked out.
- **State schema**: `{ last_run_at, runs: [{ run_at, urls, titles }] }` with rolling **7-day** window.
- **Notification (Bước 5)**: after `git push`, pipe a Slack-style summary (all 11 titles + impact counts + branch/file links) into `./scripts/notify_email.sh "<subject>"`. The script emails via Mail.app.
- **Copyright**: rewrite content, never quote more than 15 consecutive words; keep English technical terms in Vietnamese translations (deploy, container, runtime, pull request).

## Template ↔ prompt alignment

Template and prompt are in sync at v3:
- Sections `#japan-news` (red), `#japan-tech` (green), `#global-tech` (blue).
- `article.news-card` + `news-card--jp` / `news-card--en` layout variants.
- `.impact-badge.high|medium|low` for section C.
- `[data-theme="light|dark"]` with `prefers-color-scheme` fallback.

If you change the prompt's contract (section IDs, classes, badge names, placeholders), verify the template still matches — and vice versa.

## Execution gotchas

- **Cron PATH is minimal.** `scripts/run_digest.sh` prepends `/Users/cuongnh0609/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin` — if the user's `claude` binary moves, update that line.
- **launchd does not wake the Mac.** If the MacBook is asleep at 00:00/05:00 JST, the run is skipped silently. User accepted this tradeoff.
- **Timezone** is read from macOS System Settings, not from the plist. Machine must be `Asia/Tokyo`.
- **`claude --permission-mode bypassPermissions`** auto-accepts all tool calls. Prompt is trusted because it's committed to the repo under user control.
- **`gh` / `git` auth** uses the user's local credentials (`~/.config/gh/`, `~/.gitconfig`). No GitHub App involved.
- **Mail.app must be configured** for `notify_email.sh` to work. If not, swap osascript for curl-SMTP (requires app password).
- **Logs at `logs/`** are `.gitignore`d — user reviews them locally after each run.

## Working with the user

- Primary language in source files is Vietnamese with Japanese headings and English technical terms. Preserve that mix; do not "translate to English" unless asked.
- User is on **Claude Max** — token usage from headless `claude` runs counts against the monthly plan.
- **Model pinned to Sonnet 4.6** via `--model claude-sonnet-4-6` in `scripts/run_digest.sh` (faster than Opus 4.7, acceptable quality for news digest). Change there if you want to override per-run.
- The prompt includes an "⚡ Quy tắc hiệu quả" section (parallel `web_fetch`, RSS-first, 3 fetches/article cap). Preserve these when editing — they roughly halve wall-clock time.
- User's email for notifications: `gian@core-corp.co.jp` (via `$DIGEST_EMAIL_TO` env in the plist).
