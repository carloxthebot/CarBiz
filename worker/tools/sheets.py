#!/usr/bin/env python3
"""sheets.py — Google Sheets CLI for the CarBiz worker.

All subcommands print JSON to stdout so Claude can consume the result directly.
Auth is a Google service account whose JSON key path lives in the environment
variable SHEETS_SERVICE_ACCOUNT_JSON. The service account must have been
granted access to the target Drive folder (share the folder to the SA email).

Subcommands:
  read <sheet_id> <tab> [a1_range]     Read cells (default: whole tab).
  find <keyword>                       Search every sheet in $SHEETS_FOLDER_ID.
  append <sheet_id> <tab> <row_json>   Append one row; returns the row number.
  update <sheet_id> <tab> <a1> <val>   Set a single cell.
  undo <sheet_id> <tab> <row_number>   Delete a specific 1-indexed row.

Deliberately no `list` — the dispatcher generates a fresh sheets-map cache
via sheets_map.py and hands it to the worker on stdin, so the worker doesn't
spend a Sheets round-trip on the trivial question "what tabs exist".
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    sys.stderr.write("gspread + google-auth not installed. Run: pip install -r worker/requirements.txt\n")
    sys.exit(2)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _client() -> gspread.Client:
    key = os.environ.get("SHEETS_SERVICE_ACCOUNT_JSON")
    if not key:
        sys.stderr.write("SHEETS_SERVICE_ACCOUNT_JSON not set\n")
        sys.exit(2)
    creds = Credentials.from_service_account_file(key, scopes=SCOPES)
    return gspread.authorize(creds)


def _tab(client: gspread.Client, sheet_id: str, tab: str) -> gspread.Worksheet:
    return client.open_by_key(sheet_id).worksheet(tab)


def cmd_read(sheet_id: str, tab: str, a1: str | None = None) -> dict[str, Any]:
    ws = _tab(_client(), sheet_id, tab)
    values = ws.get(a1) if a1 else ws.get_all_values()
    return {"sheet_id": sheet_id, "tab": tab, "range": a1, "values": values}


def cmd_find(keyword: str) -> dict[str, Any]:
    """Search every accessible sheet in $SHEETS_FOLDER_ID for cells containing keyword.

    Cheap heuristic: pull each sheet's values via get_all_values and grep in-process.
    Bad for very large folders, fine for a team-managed order book.
    """
    folder_id = os.environ.get("SHEETS_FOLDER_ID")
    if not folder_id:
        sys.stderr.write("SHEETS_FOLDER_ID not set\n")
        sys.exit(2)
    client = _client()
    files = client.list_spreadsheet_files(folder_id=folder_id)
    hits: list[dict[str, Any]] = []
    needle = keyword.lower()
    for f in files:
        try:
            sh = client.open_by_key(f["id"])
        except Exception as e:
            hits.append({"sheet_id": f["id"], "error": str(e)})
            continue
        for ws in sh.worksheets():
            for row_idx, row in enumerate(ws.get_all_values(), start=1):
                for col_idx, cell in enumerate(row, start=1):
                    if needle in cell.lower():
                        hits.append({
                            "sheet_id": f["id"],
                            "sheet_name": f.get("name"),
                            "tab": ws.title,
                            "row": row_idx,
                            "col": col_idx,
                            "value": cell,
                        })
    return {"keyword": keyword, "hits": hits}


def cmd_append(sheet_id: str, tab: str, row_json: str) -> dict[str, Any]:
    row = json.loads(row_json)
    if not isinstance(row, list):
        sys.stderr.write("row_json must be a JSON array of cell values\n")
        sys.exit(2)
    ws = _tab(_client(), sheet_id, tab)
    result = ws.append_row(row, value_input_option="USER_ENTERED")
    # gspread returns the updated range like 'Sheet1!A5:D5' — extract row number
    updated_range = result.get("updates", {}).get("updatedRange", "")
    row_no = _parse_row_from_range(updated_range)
    return {"sheet_id": sheet_id, "tab": tab, "row": row_no, "wrote": row}


def cmd_update(sheet_id: str, tab: str, a1: str, value: str) -> dict[str, Any]:
    ws = _tab(_client(), sheet_id, tab)
    ws.update(a1, [[value]], value_input_option="USER_ENTERED")
    return {"sheet_id": sheet_id, "tab": tab, "cell": a1, "value": value}


def cmd_undo(sheet_id: str, tab: str, row_number: str) -> dict[str, Any]:
    row_no = int(row_number)
    ws = _tab(_client(), sheet_id, tab)
    ws.delete_rows(row_no)
    return {"sheet_id": sheet_id, "tab": tab, "deleted_row": row_no}


def _parse_row_from_range(rng: str) -> int | None:
    # 'Sheet1!A5:D5' -> 5. Best-effort; None if unparseable.
    import re
    m = re.search(r"(\d+)(?::[A-Z]+\d+)?$", rng)
    return int(m.group(1)) if m else None


DISPATCH = {
    "read":   (cmd_read,   (2, 3)),
    "find":   (cmd_find,   (1, 1)),
    "append": (cmd_append, (3, 3)),
    "update": (cmd_update, (4, 4)),
    "undo":   (cmd_undo,   (3, 3)),
}


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in DISPATCH:
        sys.stderr.write(__doc__ or "")
        return 2
    fn, (lo, hi) = DISPATCH[argv[1]]
    args = argv[2:]
    if not (lo <= len(args) <= hi):
        sys.stderr.write(f"'{argv[1]}' expects {lo}-{hi} args, got {len(args)}\n")
        return 2
    try:
        result = fn(*args)
    except Exception as e:
        sys.stderr.write(f"{type(e).__name__}: {e}\n")
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
