#!/usr/bin/env bash
# Email notification via macOS Mail.app (osascript).
# Usage:   echo "body text" | notify_email.sh "Subject line"
# Reads body from stdin; subject from $1.
# Recipient from $DIGEST_EMAIL_TO (env), default gian@core-corp.co.jp.

set -euo pipefail

SUBJECT="${1:?subject arg required}"
TO="${DIGEST_EMAIL_TO:-gian@core-corp.co.jp}"

BODY_FILE=$(mktemp -t digest_body.XXXXXX)
trap 'rm -f "$BODY_FILE"' EXIT
cat >"$BODY_FILE"

osascript \
  -e 'on run argv' \
  -e '  set theSubject to item 1 of argv' \
  -e '  set theTo to item 2 of argv' \
  -e '  set theBodyFile to item 3 of argv' \
  -e '  set theBody to read (POSIX file theBodyFile) as «class utf8»' \
  -e '  tell application "Mail"' \
  -e '    set newMessage to make new outgoing message with properties {subject:theSubject, content:theBody, visible:false}' \
  -e '    tell newMessage' \
  -e '      make new to recipient at end of to recipients with properties {address:theTo}' \
  -e '    end tell' \
  -e '    send newMessage' \
  -e '  end tell' \
  -e 'end run' \
  -- "$SUBJECT" "$TO" "$BODY_FILE"
