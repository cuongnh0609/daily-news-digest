#!/usr/bin/env bash
# Daily News Digest — cron wrapper
# Invoked by launchd (com.cuongnh.daily-news-digest.plist) every 5 hours JST.
# Calls `claude` CLI in headless mode with ROUTINE_PROMPT.md. Claude handles
# crawl → HTML generation → git commit + push → email notification.

set -euo pipefail

REPO="/Users/cuongnh0609/git/daily-news-digest"
LOG_DIR="$REPO/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
RUN_LOG="$LOG_DIR/run_${TIMESTAMP}.log"
STREAM_LOG="$LOG_DIR/stream_${TIMESTAMP}.jsonl"

mkdir -p "$LOG_DIR"

# launchd gives a minimal PATH — add common bin dirs + Homebrew + user local
export PATH="/Users/cuongnh0609/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

{
  echo "=== Run started: $(date -Iseconds) ==="
  cd "$REPO"

  echo "--- git pull ---"
  git pull --rebase origin main

  echo "--- invoking claude headless (sonnet 4.6, thinking off, stream-json to $STREAM_LOG) ---"
  claude \
    --model claude-sonnet-4-6 \
    --max-thinking-tokens 0 \
    --permission-mode bypassPermissions \
    --output-format stream-json \
    --verbose \
    --print "$(cat ROUTINE_PROMPT.md)" \
    >"$STREAM_LOG"

  CLAUDE_EXIT=$?
  echo "--- claude exit: $CLAUDE_EXIT ---"
  echo "--- stream log size: $(wc -c <"$STREAM_LOG") bytes, $(wc -l <"$STREAM_LOG") lines ---"

  echo "=== Run finished: $(date -Iseconds) ==="
  exit $CLAUDE_EXIT
} >"$RUN_LOG" 2>&1
