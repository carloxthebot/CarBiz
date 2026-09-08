#!/usr/bin/env python3
"""sheets_map.py — snapshot the CarBiz Sheets folder into a local cache.

Writes two things under worker/state/:

  sheets-map.json     index of every sheet + tab in the folder, with the one
                      the worker should treat as the ledger marked `latest`
  data/<tab>.json     full cell values of every tab of the LATEST sheet

Why cache the data, not just the structure: the folder is 17+ historical
copies of the same ledger. Reading them live cost 47 Sheets API calls per
question, blew the 60/min read quota, and made Claude fall back to whatever
copy it could still read (the oldest). With the latest copy cached locally,
a question is a local file read — no quota, no waiting, always the current
version.

Which copy is "latest": the highest MMDD date in the filename, preferring
names that start with "26年" (this year's series). Override with the env var
LATEST_SHEET_NAME when the heuristic picks wrong. Writes through sheets.py
re-dump the affected tab so the cache never lags a write.

Run at bot start, every SHEETS_REFRESH_MIN minutes (bot does this), or by hand
after editing sheets outside the bot.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    sys.stderr.write("gspread + google-auth not installed. Run: pip install -r worker/requirements.txt\n")
    sys.exit(2)

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
DATA_DIR = STATE_DIR / "data"
MAP_PATH = STATE_DIR / "sheets-map.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def client() -> gspread.Client:
    key = os.environ["SHEETS_SERVICE_ACCOUNT_JSON"]
    creds = Credentials.from_service_account_file(key, scopes=SCOPES)
    return gspread.authorize(creds)


# --- picking the latest copy -------------------------------------------------

def _name_score(name: str) -> tuple[int, int]:
    """(is_this_year_series, MMDD) — higher wins."""
    this_year = 1 if name.startswith("26年") else 0
    dates = re.findall(r"(?<!\d)(\d{4})(?!\d)", name)
    mmdd = 0
    for d in dates:
        mm, dd = int(d[:2]), int(d[2:])
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            mmdd = max(mmdd, mm * 100 + dd)
    return (this_year, mmdd)


def pick_latest(files: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not files:
        return None
    override = os.environ.get("LATEST_SHEET_NAME")
    if override:
        for f in files:
            if f.get("name") == override:
                return f
        sys.stderr.write(f"LATEST_SHEET_NAME={override!r} not found, falling back to heuristic\n")
    return max(files, key=lambda f: (_name_score(f.get("name", "")), f.get("modifiedTime", "")))


# --- tab snapshot --------------------------------------------------------------

def _guess_header_row(values: list[list[str]]) -> int:
    """Index of the first row where at least half the cells are non-empty.
    These ledgers have a title banner above the real header."""
    for i, row in enumerate(values[:10]):
        cells = [c for c in row if c.strip()]
        if row and len(cells) >= max(2, len(row) // 2):
            return i
    return 0


def _safe_filename(tab: str) -> str:
    return re.sub(r"[^\w一-鿿-]+", "_", tab).strip("_") or "tab"


def dump_tab(ws: gspread.Worksheet, sheet_id: str, sheet_name: str) -> dict[str, Any]:
    """Fetch one tab, write data/<tab>.json, return its index entry."""
    values = ws.get_all_values()
    header_row = _guess_header_row(values) if values else 0
    headers = values[header_row] if values else []
    fname = _safe_filename(ws.title) + ".json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / fname).write_text(
        json.dumps(
            {
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
                "tab": ws.title,
                "header_row": header_row,      # 0-based index into `rows`
                "headers": headers,
                "rows": values,                # every row incl. banner + header, 1:1 with the sheet
                "fetched_at": _now(),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {
        "name": ws.title,
        "file": f"data/{fname}",
        "rows": max(0, len(values) - header_row - 1),
        "header_row": header_row,
        "headers": [h for h in headers if h.strip()][:12],
    }


def refresh_tab(sheet_id: str, tab: str) -> None:
    """Re-dump one tab after a write. Called by sheets.py."""
    c = client()
    sh = c.open_by_key(sheet_id)
    ws = sh.worksheet(tab)
    entry = dump_tab(ws, sheet_id, sh.title)
    if MAP_PATH.exists():
        m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        latest = m.get("latest") or {}
        if latest.get("id") == sheet_id:
            latest["tabs"] = [entry if t["name"] == tab else t for t in latest.get("tabs", [])]
            m["latest"] = latest
            m["generated_at"] = _now()
            MAP_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


# --- full map -----------------------------------------------------------------

def build_map() -> dict[str, Any]:
    folder_id = os.environ["SHEETS_FOLDER_ID"]
    c = client()
    files = c.list_spreadsheet_files(folder_id=folder_id)
    latest_file = pick_latest(files)

    others = []
    for f in files:
        if latest_file and f["id"] == latest_file["id"]:
            continue
        others.append({"id": f["id"], "name": f.get("name"), "modified": f.get("modifiedTime")})

    latest: dict[str, Any] | None = None
    if latest_file:
        sh = c.open_by_key(latest_file["id"])
        tabs = [dump_tab(ws, latest_file["id"], sh.title) for ws in sh.worksheets()]
        latest = {
            "id": latest_file["id"],
            "name": latest_file.get("name"),
            "modified": latest_file.get("modifiedTime"),
            "tabs": tabs,
        }

    return {
        "folder_id": folder_id,
        "generated_at": _now(),
        "note": "`latest` is the ledger to answer from; its tabs are cached under data/. "
                "`others` are historical copies — only open them when the user names a date.",
        "latest": latest,
        "others": sorted(others, key=lambda o: _name_score(o["name"] or ""), reverse=True),
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> int:
    STATE_DIR.mkdir(exist_ok=True)
    m = build_map()
    MAP_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = m.get("latest")
    if latest:
        print(f"latest: {latest['name']} ({len(latest['tabs'])} tabs cached), {len(m['others'])} historical copies indexed")
    else:
        print("no sheets found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
