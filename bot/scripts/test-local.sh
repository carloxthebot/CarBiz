#!/usr/bin/env bash
# Local end-to-end test for the CarBiz bot (single-process Node server).
#
# Assumes:
#   - `npm start` is running in another shell (or via launchd)
#   - `.env` uses fake-claude as CLAUDE_BIN so no real Claude spawn happens
#
# This exercises: signature check, event_id dedup, whitelist, sqlite persist,
# agent enqueue, fake-claude round-trip, LINE push (will error out with test
# token — that's fine, we only verify status transitions in sqlite).
set -euo pipefail

HUB=${HUB:-http://127.0.0.1:8787}
SECRET=${SECRET:-test-secret-do-not-use-in-prod}
DB=${DB:-/tmp/carbiz-test.sqlite}

sign() {
  printf '%s' "$1" | openssl dgst -sha256 -hmac "$SECRET" -binary | base64
}

make_body() {
  local event_id="$1" text="${2:-hi from test}"
  cat <<JSON
{"events":[{"type":"message","webhookEventId":"$event_id","replyToken":"fake-reply-$event_id","source":{"type":"user","userId":"Utest0000000000000000000000000001"},"message":{"id":"msg-$event_id","type":"text","text":"$text"}}]}
JSON
}

query_sqlite() {
  sqlite3 "$DB" "$1"
}

step() { printf "\n\033[1;34m== %s ==\033[0m\n" "$*"; }
ok()   { printf "\033[1;32mOK\033[0m  %s\n" "$*"; }
fail() { printf "\033[1;31mFAIL\033[0m %s\n" "$*"; exit 1; }

# --- 1. bad signature -> 401 ---
step "1. bad signature -> 401"
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$HUB/api/line/webhook" \
  -H 'content-type: application/json' -H 'x-line-signature: WRONG' \
  -d "$(make_body evt-bad)")
[[ "$status" == "401" ]] && ok "got 401" || fail "expected 401 got $status"

# --- 2. valid signature -> 200 + task row ---
step "2. valid signature, first-time event -> task created"
BODY=$(make_body evt-first "第一次的訊息")
SIG=$(sign "$BODY")
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$HUB/api/line/webhook" \
  -H 'content-type: application/json' -H "x-line-signature: $SIG" -d "$BODY")
[[ "$status" == "200" ]] && ok "got 200" || fail "expected 200 got $status"

# Wait for the fire-and-forget handler to persist + agent to run fake-claude
sleep 3
count=$(query_sqlite "SELECT COUNT(*) FROM tasks WHERE event_id='evt-first'")
[[ "$count" == "1" ]] && ok "1 row for evt-first" || fail "expected 1 row got $count"

# --- 3. same event -> deduped (still 1 row) ---
step "3. duplicate event -> deduped"
curl -s -o /dev/null -X POST "$HUB/api/line/webhook" \
  -H 'content-type: application/json' -H "x-line-signature: $SIG" -d "$BODY"
sleep 1
count=$(query_sqlite "SELECT COUNT(*) FROM tasks WHERE event_id='evt-first'")
[[ "$count" == "1" ]] && ok "still 1 row after retry" || fail "expected 1 got $count"

# --- 4. agent ran, status is done, result_text populated ---
step "4. agent completed, status=done"
status_val=$(query_sqlite "SELECT status FROM tasks WHERE event_id='evt-first'")
result=$(query_sqlite "SELECT result_text FROM tasks WHERE event_id='evt-first'")
[[ "$status_val" == "done" ]] && ok "status=done" || fail "status=$status_val"
[[ -n "$result" ]] && ok "result: $result" || fail "no result_text"

# --- 5. push failed (fake token), but task still done ---
# We don't assert on push — the fake token guarantees a 401 from LINE,
# which is logged but doesn't affect task state.

# --- 6. server restart resilience ---
# Not tested here (requires stop/start), documented in setup.md.

printf "\n\033[1;32mAll checks passed.\033[0m\n"
