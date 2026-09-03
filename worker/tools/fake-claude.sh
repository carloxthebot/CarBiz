#!/usr/bin/env python3
"""fake-claude — local dispatcher round-trip test double.

Pretends to be the `claude` CLI:
- ignores argv (dispatcher always calls: -p <prompt> --output-format json --dangerously-skip-permissions)
- reads the user payload from stdin (task_id + raw_message + sheets_map + ...)
- prints one JSON blob shaped like `claude -p --output-format json` output
- exits 0

Real claude would spawn tools, take time, burn tokens. We don't need any of
that for verifying the dispatcher's data plumbing.
"""
import json
import sys

payload = json.load(sys.stdin)
reply = f"[fake-claude] 已收到「{payload['raw_message']}」(task {payload['task_id'][:8]})"
json.dump({"result": reply}, sys.stdout, ensure_ascii=False)
sys.stdout.write("\n")
