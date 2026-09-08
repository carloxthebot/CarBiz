#!/usr/bin/env python3
"""sheets.py — Google Sheets CLI for the CarBiz worker.

Every subcommand prints JSON to stdout so Claude can consume it directly.
Auth is the service account in $SHEETS_SERVICE_ACCOUNT_JSON.

Read side is LOCAL-FIRST. sheets_map.py keeps the latest ledger cached under
worker/state/data/, so reads and searches never touch Google:

  cached <tab>                         The latest ledger's tab, from cache.
  find <keyword>                       Grep every cached tab of the latest ledger.

Only these hit Google (historical copies, or a deliberate fresh read):

  read <sheet_id> <tab> [a1_range]     Live read of any sheet in the folder.

Writes go to Google and then re-dump the touched tab so the cache never lags:

  append <sheet_id> <tab> <row_json>   Append one row; returns the row number.
  update <sheet_id> <tab> <a1> <val>   Set a single cell.
  undo <sheet_id> <tab> <row_number>   Delete a 1-indexed row.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    sys.stderr.write("gspread + google-auth not installed. Run: pip install -r worker/requirements.txt\n")
    sys.exit(2)

from sheets_map import DATA_DIR, MAP_PATH, refresh_tab, _safe_filename  # noqa: E402

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


def _latest() -> dict[str, Any]:
    if not MAP_PATH.exists():
        sys.stderr.write("cache missing — run worker/tools/sheets_map.py first\n")
        sys.exit(1)
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    latest = m.get("latest")
    if not latest:
        sys.stderr.write("no latest sheet in cache\n")
        sys.exit(1)
    return latest


# --- local reads --------------------------------------------------------------

def cmd_cached(tab: str) -> dict[str, Any]:
    path = DATA_DIR / (_safe_filename(tab) + ".json")
    if not path.exists():
        latest = _latest()
        names = [t["name"] for t in latest.get("tabs", [])]
        sys.stderr.write(f"tab {tab!r} not cached; available: {names}\n")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_find(keyword: str) -> dict[str, Any]:
    latest = _latest()
    needle = keyword.lower()
    hits: list[dict[str, Any]] = []
    for t in latest.get("tabs", []):
        path = DATA_DIR / Path(t["file"]).name
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for r_idx, row in enumerate(doc["rows"], start=1):
            for c_idx, cell in enumerate(row, start=1):
                if needle in cell.lower():
                    hits.append({"tab": t["name"], "row": r_idx, "col": c_idx, "value": cell})
    return {"sheet_id": latest["id"], "sheet_name": latest["name"], "keyword": keyword, "hits": hits}


# --- live read ----------------------------------------------------------------

def cmd_read(sheet_id: str, tab: str, a1: str | None = None) -> dict[str, Any]:
    ws = _tab(_client(), sheet_id, tab)
    values = ws.get(a1) if a1 else ws.get_all_values()
    return {"sheet_id": sheet_id, "tab": tab, "range": a1, "values": values}


# --- writes (then refresh cache) ----------------------------------------------

def _after_write(sheet_id: str, tab: str) -> None:
    try:
        refresh_tab(sheet_id, tab)
    except Exception as e:  # cache lag is survivable; the write already happened
        sys.stderr.write(f"warning: cache refresh failed: {e}\n")


def cmd_append(sheet_id: str, tab: str, row_json: str) -> dict[str, Any]:
    row = json.loads(row_json)
    if not isinstance(row, list):
        sys.stderr.write("row_json must be a JSON array of cell values\n")
        sys.exit(2)
    ws = _tab(_client(), sheet_id, tab)
    result = ws.append_row(row, value_input_option="USER_ENTERED")
    updated_range = result.get("updates", {}).get("updatedRange", "")
    _after_write(sheet_id, tab)
    return {"sheet_id": sheet_id, "tab": tab, "row": _row_from_range(updated_range), "wrote": row}


def cmd_update(sheet_id: str, tab: str, a1: str, value: str) -> dict[str, Any]:
    ws = _tab(_client(), sheet_id, tab)
    ws.update(a1, [[value]], value_input_option="USER_ENTERED")
    _after_write(sheet_id, tab)
    return {"sheet_id": sheet_id, "tab": tab, "cell": a1, "value": value}


def cmd_undo(sheet_id: str, tab: str, row_number: str) -> dict[str, Any]:
    row_no = int(row_number)
    ws = _tab(_client(), sheet_id, tab)
    ws.delete_rows(row_no)
    _after_write(sheet_id, tab)
    return {"sheet_id": sheet_id, "tab": tab, "deleted_row": row_no}


def num(s):
    """'¥149,600 ' / '$32,175' / '25' -> number; '' or junk -> ''."""
    if isinstance(s, (int, float)):
        return s
    t = re.sub(r"[¥$,\s]", "", str(s or ""))
    if t in ("", "-"):
        return ""
    try:
        return int(t) if re.fullmatch(r"-?\d+", t) else float(t)
    except ValueError:
        return ""


# --- normalized order table (新_訂單) ------------------------------------------
#
# The fixed-column ledger. Claude never has to know column order: add_order
# takes item fields by name, fills 訂單ID/批次/下單日/狀態/NO/formulas, and inserts
# at row 2 so the sheet stays newest-first. Undo/status work by 訂單ID or 批次,
# not row number, because the sheet is sorted and rows move.

ORDER_TAB = "新_訂單"
STATUSES = ["已下單", "已到日本", "已出貨", "已到台", "已交付", "取消"]
ITEM_FIELDS = ["客戶", "品牌", "品名", "料號", "數量", "單價¥", "日本運費¥", "匯款手續費¥", "交期", "物流批次", "備註"]


def _order_ws() -> tuple[gspread.Worksheet, dict[str, int], str]:
    latest = _latest()
    ws = _tab(_client(), latest["id"], ORDER_TAB)
    headers = ws.row_values(1)
    col = {h.strip(): i for i, h in enumerate(headers) if h.strip()}  # 0-based
    for need in ("訂單ID", "批次", "下單日", "狀態", "NO", "品名", "數量", "單價¥", "日幣合計¥", "台幣合計$", "匯率"):
        if need not in col:
            raise RuntimeError(f"{ORDER_TAB} missing column {need!r}; headers={headers}")
    return ws, col, latest["id"]


def _a1col(i: int) -> str:
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _latest_rate(ws: gspread.Worksheet, col: dict[str, int]) -> Any:
    """Most recent non-empty 匯率 (sheet is newest-first, so first hit wins)."""
    for v in ws.col_values(col["匯率"] + 1)[1:]:
        n = num(v)
        if n != "":
            return n
    return ""


def cmd_add_order(items_json: str, batch: str | None = None, date: str | None = None) -> dict[str, Any]:
    """items_json: JSON array of objects with any of ITEM_FIELDS. 客戶 goes to 備註
    as「客戶:X」if there is no 客戶 column. Returns the 訂單IDs written."""
    from datetime import date as _date
    items = json.loads(items_json)
    if not isinstance(items, list) or not items:
        sys.stderr.write("items_json must be a non-empty JSON array of objects\n"); sys.exit(2)

    today = _date.today() if not date else _date.fromisoformat(date)
    mmdd = today.strftime("%m%d")
    batch_name = (batch or mmdd)
    batch_name = batch_name if batch_name.endswith("訂單") else f"{batch_name}訂單"
    date_iso = today.isoformat()
    id_prefix = today.strftime("%Y%m%d") + "-"

    ws, col, sheet_id = _order_ws()
    ids = ws.col_values(col["訂單ID"] + 1)[1:]
    batches = ws.col_values(col["批次"] + 1)[1:]
    nos = ws.col_values(col["NO"] + 1)[1:]
    seq = max([int(x.split("-")[1]) for x in ids if x.startswith(id_prefix) and x.split("-")[-1].isdigit()] or [0])
    no = max([int(n) for b, n in zip(batches, nos) if b == batch_name and str(n).isdigit()] or [0])
    # default 匯率 = latest one on the sheet, so 台幣合計 shows immediately; override per item with "匯率"
    rate_default = _latest_rate(ws, col)

    width = max(col.values()) + 1
    rows: list[list[Any]] = []
    written: list[str] = []
    for k, it in enumerate(items):
        seq += 1; no += 1
        r_idx = 2 + k  # rows are inserted as a block starting at row 2
        row: list[Any] = [""] * width
        oid = f"{id_prefix}{seq:03d}"
        row[col["訂單ID"]] = oid
        row[col["批次"]] = batch_name
        row[col["下單日"]] = date_iso
        row[col["狀態"]] = "已下單"
        row[col["NO"]] = no
        for f in ITEM_FIELDS:
            if f in col and it.get(f) not in (None, ""):
                v = it[f]
                row[col[f]] = num(v) if f in ("數量", "單價¥", "日本運費¥", "匯款手續費¥") and num(v) != "" else v
        row[col["匯率"]] = num(it["匯率"]) if it.get("匯率") not in (None, "") else rate_default
        if "客戶" not in col and it.get("客戶"):
            memo = str(row[col["備註"]] or "")
            row[col["備註"]] = f"客戶:{it['客戶']}" + (f";{memo}" if memo else "")
        I, J, K, L, M, O = (_a1col(col[x]) for x in ("數量", "單價¥", "日本運費¥", "匯款手續費¥", "日幣合計¥", "匯率"))
        row[col["日幣合計¥"]] = f"=IF({I}{r_idx}=\"\",\"\",{I}{r_idx}*{J}{r_idx}+N({K}{r_idx})+N({L}{r_idx}))"
        row[col["台幣合計$"]] = f"=IF(OR({O}{r_idx}=\"\",{M}{r_idx}=\"\"),\"\",ROUND({M}{r_idx}*{O}{r_idx}))"
        rows.append(row); written.append(oid)

    ws.insert_rows(rows, row=2, value_input_option="USER_ENTERED")
    _after_write(sheet_id, ORDER_TAB)
    return {"tab": ORDER_TAB, "batch": batch_name, "date": date_iso, "order_ids": written, "count": len(written),
            "rate_used": rate_default}


def _rows_matching(ws: gspread.Worksheet, col: dict[str, int], target: str) -> list[int]:
    """1-based sheet rows whose 訂單ID == target, or whose 批次 == target / target+'訂單'."""
    ids = ws.col_values(col["訂單ID"] + 1)
    batches = ws.col_values(col["批次"] + 1)
    t2 = target if target.endswith("訂單") else target + "訂單"
    hits = [i + 1 for i, v in enumerate(ids) if i > 0 and v == target]
    if not hits:
        hits = [i + 1 for i, v in enumerate(batches) if i > 0 and v in (target, t2)]
    return hits


def cmd_set_status(target: str, status: str) -> dict[str, Any]:
    if status not in STATUSES:
        sys.stderr.write(f"status must be one of {STATUSES}\n"); sys.exit(2)
    ws, col, sheet_id = _order_ws()
    rows = _rows_matching(ws, col, target)
    if not rows:
        sys.stderr.write(f"no rows match {target!r}\n"); sys.exit(1)
    c = _a1col(col["狀態"])
    ws.batch_update([{"range": f"{c}{r}", "values": [[status]]} for r in rows], value_input_option="USER_ENTERED")
    _after_write(sheet_id, ORDER_TAB)
    return {"tab": ORDER_TAB, "target": target, "status": status, "rows_updated": len(rows)}


def cmd_undo_order(target: str) -> dict[str, Any]:
    ws, col, sheet_id = _order_ws()
    rows = _rows_matching(ws, col, target)
    if not rows:
        sys.stderr.write(f"no rows match {target!r}\n"); sys.exit(1)
    if len(rows) > 20:
        sys.stderr.write(f"refusing to delete {len(rows)} rows at once; delete by 訂單ID\n"); sys.exit(1)
    for r in sorted(rows, reverse=True):  # bottom-up so indices stay valid
        ws.delete_rows(r)
    _after_write(sheet_id, ORDER_TAB)
    return {"tab": ORDER_TAB, "target": target, "rows_deleted": len(rows)}


def cmd_lookup_item(keyword: str) -> dict[str, Any]:
    """Past orders of the same item, newest first — used to prefill 料號/單價/品牌."""
    doc = cmd_cached(ORDER_TAB)
    h = doc["header_row"]
    hdr = doc["rows"][h]
    col = {c.strip(): i for i, c in enumerate(hdr) if c.strip()}
    needle = keyword.lower()
    out = []
    for r in doc["rows"][h + 1:]:
        g = lambda k: (r[col[k]] if k in col and col[k] < len(r) else "")
        hay = f"{g('品牌')} {g('品名')} {g('料號')}".lower()
        if needle in hay:
            out.append({k: g(k) for k in ("訂單ID", "下單日", "品牌", "品名", "料號", "單價¥", "日本運費¥", "交期")})
    return {"keyword": keyword, "matches": out[:10]}


def _row_from_range(rng: str) -> int | None:
    m = re.search(r"(\d+)(?::[A-Z]+\d+)?$", rng)
    return int(m.group(1)) if m else None


DISPATCH = {
    "cached":      (cmd_cached,      (1, 1)),
    "find":        (cmd_find,        (1, 1)),
    "lookup_item": (cmd_lookup_item, (1, 1)),
    "read":        (cmd_read,        (2, 3)),
    "add_order":   (cmd_add_order,   (1, 3)),  # items_json [batch] [date]
    "set_status":  (cmd_set_status,  (2, 2)),
    "undo_order":  (cmd_undo_order,  (1, 1)),
    "append":      (cmd_append,      (3, 3)),
    "update":      (cmd_update,      (4, 4)),
    "undo":        (cmd_undo,        (3, 3)),
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
