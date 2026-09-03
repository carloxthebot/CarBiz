#!/usr/bin/env python3
"""sheets_map.py — snapshot the CarBiz Sheets folder into worker/state/sheets-map.json.

Rationale: without a cached map, every worker run would spend 20-30 seconds
walking the folder to find "which sheet holds what". Instead, we snapshot the
folder shape into a small JSON that ships to the worker on stdin (via
dispatcher.mjs), so the worker can jump straight to the right sheet/tab.

Refresh cadence: run this at dispatcher start and again on a launchd/cron
timer every few hours, or manually after adding a new sheet or renaming tabs.
Cheap enough (a few API calls per sheet) that "every 6 hours" is fine.

The snapshot per tab captures: tab name, header row, row count, and the most
recent value in the header's first date-looking column (so the worker can
answer "上個月 XX 客戶" without opening the sheet just to see the date range).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    sys.stderr.write("gspread + google-auth not installed. Run: pip install -r worker/requirements.txt\n")
    sys.exit(2)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

DATE_HINTS = ("日期", "date", "訂單日", "下單日")
DATE_PATTERNS = [
    re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}"),
    re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"),
]


def _client() -> gspread.Client:
    key = os.environ["SHEETS_SERVICE_ACCOUNT_JSON"]
    creds = Credentials.from_service_account_file(key, scopes=SCOPES)
    return gspread.authorize(creds)


def _find_date_col(headers: list[str]) -> int | None:
    for idx, h in enumerate(headers):
        if any(hint in h.lower() for hint in DATE_HINTS):
            return idx
    return None


def _snapshot_tab(ws: gspread.Worksheet) -> dict[str, Any]:
    values = ws.get_all_values()
    if not values:
        return {"name": ws.title, "rows": 0, "headers": []}
    headers = values[0]
    date_col = _find_date_col(headers)
    last_date = None
    if date_col is not None and len(values) > 1:
        # walk from the bottom looking for a date-shaped value
        for row in reversed(values[1:]):
            if date_col < len(row) and row[date_col]:
                cell = row[date_col].strip()
                if any(p.match(cell) for p in DATE_PATTERNS):
                    last_date = cell
                    break
    return {
        "name": ws.title,
        "rows": len(values) - 1,          # excluding header
        "headers": headers,
        "date_column": date_col,
        "last_date_seen": last_date,
    }


def build_map() -> dict[str, Any]:
    folder_id = os.environ["SHEETS_FOLDER_ID"]
    client = _client()
    files = client.list_spreadsheet_files(folder_id=folder_id)
    sheets = []
    for f in files:
        try:
            sh = client.open_by_key(f["id"])
            tabs = [_snapshot_tab(ws) for ws in sh.worksheets()]
        except Exception as e:
            sheets.append({"id": f["id"], "name": f.get("name"), "error": str(e)})
            continue
        sheets.append({
            "id": f["id"],
            "name": f.get("name"),
            "tabs": tabs,
        })
    return {
        "folder_id": folder_id,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "sheets": sheets,
    }


def main() -> int:
    out = Path(__file__).resolve().parent.parent / "state" / "sheets-map.json"
    out.parent.mkdir(exist_ok=True)
    m = build_map()
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} ({len(m['sheets'])} sheets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
