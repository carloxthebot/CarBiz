#!/usr/bin/env python3
"""digest.py — the daily morning report, computed from the local cache.

Deterministic on purpose: no Claude, no Google calls, same shape every day.
Reads worker/state/data/新_訂單.json and prints LINE-ready text to stdout.
The bot pushes it at DIGEST_HOUR and on demand (「早報」).

Quiet days still report STATE (outstanding, stuck, missing data, stale rate);
an anomaly section appears only when there is something to fix.

Usage: digest.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / "state"
ORDER_JSON = STATE / "data" / "新_訂單.json"
MAP_JSON = STATE / "sheets-map.json"

STUCK_ORDERED_DAYS = 30   # 已下單 this long without progress
STUCK_JAPAN_DAYS = 14     # 已到日本 this long without shipping
RATE_STALE_DAYS = 14
OPEN = {"已下單", "已到日本", "已出貨", "已到台"}


def num(s):
    t = re.sub(r"[¥$,\s]", "", str(s or ""))
    try:
        return float(t) if t not in ("", "-") else 0.0
    except ValueError:
        return 0.0


def pdate(s: str):
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def fmt_money(n: float) -> str:
    return f"{int(round(n)):,}"


def load_rows():
    doc = json.loads(ORDER_JSON.read_text(encoding="utf-8"))
    h = doc["header_row"]
    hdr = [c.strip() for c in doc["rows"][h]]
    col = {c: i for i, c in enumerate(hdr) if c}
    rows = []
    for r in doc["rows"][h + 1:]:
        g = lambda k: (r[col[k]] if k in col and col[k] < len(r) else "")
        if not g("訂單ID"):
            continue
        rows.append({k: g(k) for k in col})
    return rows, doc.get("fetched_at", "")


def build(today: date) -> str:
    rows, fetched = load_rows()
    open_rows = [r for r in rows if r["狀態"] in OPEN]
    by_batch = defaultdict(list)
    for r in open_rows:
        by_batch[r["批次"]].append(r)

    latest_batch_date = max((pdate(r["下單日"]) for r in rows if pdate(r["下單日"])), default=None)
    days_since = (today - latest_batch_date).days if latest_batch_date else None

    twd_open = sum(num(r["台幣合計$"]) for r in open_rows)
    jpy_open = sum(num(r["日幣合計¥"]) for r in open_rows)

    stuck_ordered = [r for r in open_rows if r["狀態"] == "已下單" and pdate(r["下單日"]) and (today - pdate(r["下單日"])).days > STUCK_ORDERED_DAYS]
    stuck_japan = [r for r in open_rows if r["狀態"] == "已到日本" and pdate(r["下單日"]) and (today - pdate(r["下單日"])).days > STUCK_JAPAN_DAYS]

    missing_part = [r for r in open_rows if not r["料號"].strip() or r["料號"].strip() == "?"]
    missing_price = [r for r in open_rows if num(r["單價¥"]) == 0]
    missing_qty = [r for r in open_rows if num(r["數量"]) == 0]

    # only nag about duplicates in batches still open — delivered history is settled
    dup = Counter((r["批次"], r["料號"].strip()) for r in open_rows if r["料號"].strip() and r["料號"].strip() != "?")
    dups = [(b, p, n) for (b, p), n in dup.items() if n > 1]

    rate, rate_date = "", None
    for r in rows:  # newest first
        if num(r["匯率"]):
            rate, rate_date = r["匯率"], pdate(r["下單日"])
            break
    rate_age = (today - rate_date).days if rate_date else None

    # ---- text ----
    md = f"{today.month}/{today.day}"
    head = f"📋 {md} 早報"
    if latest_batch_date:
        head += f"(上一批 {latest_batch_date.strftime('%m%d')},{days_since} 天前)"
    lines = [head]

    n_batches, n_items = len(by_batch), len(open_rows)
    lines.append(f"・未交付:{n_batches} 批 / {n_items} 筆,¥{fmt_money(jpy_open)} ≈ NT${fmt_money(twd_open)}")
    if by_batch:
        top = sorted(by_batch.items(), key=lambda kv: sum(num(r['台幣合計$']) for r in kv[1]), reverse=True)[:3]
        lines.append("  最大三批:" + "、".join(f"{b.replace('訂單','')} NT${fmt_money(sum(num(r['台幣合計$']) for r in rs))}" for b, rs in top))

    stuck_line = []
    if stuck_ordered:
        bs = sorted({r["批次"].replace("訂單", "") for r in stuck_ordered})
        stuck_line.append(f"下單>{STUCK_ORDERED_DAYS}天仍未交付 {len(stuck_ordered)} 筆({'、'.join(bs[:4])}{'…' if len(bs) > 4 else ''})")
    if stuck_japan:
        stuck_line.append(f"到日本>{STUCK_JAPAN_DAYS}天未出貨 {len(stuck_japan)} 筆")
    lines.append("・卡住:" + ("；".join(stuck_line) if stuck_line else "無"))

    miss = []
    if missing_part: miss.append(f"料號空白 {len(missing_part)}")
    if missing_price: miss.append(f"單價空白 {len(missing_price)}")
    if missing_qty: miss.append(f"數量空白 {len(missing_qty)}")
    lines.append("・待補:" + ("、".join(miss) if miss else "無"))

    if rate:
        stale = f",已 {rate_age} 天未更新" if rate_age is not None and rate_age > RATE_STALE_DAYS else ""
        lines.append(f"・匯率:{rate}({rate_date.strftime('%m/%d') if rate_date else '?'}{stale})")

    if dups:
        lines.append("⚠️ 同批重複料號:" + "、".join(f"{b.replace('訂單','')} {p}×{n}" for b, p, n in dups[:5]))

    if fetched:
        try:
            age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched.replace("Z", "+00:00"))).total_seconds() / 3600
            if age_h > 24:
                lines.append(f"⚠️ 快取已 {int(age_h)} 小時未更新")
        except Exception:
            pass

    lines.append("追問:「哪些卡住」「0731 明細」「誰還沒付」")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    a = ap.parse_args()
    today = date.fromisoformat(a.date) if a.date else date.today()
    if not ORDER_JSON.exists():
        sys.stderr.write("cache missing: run sheets_map.py first\n")
        return 1
    print(build(today))
    return 0


if __name__ == "__main__":
    sys.exit(main())
