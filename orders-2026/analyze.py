#!/usr/bin/env python3
"""Classify the 2026 order ledger: brand, part category, car model. Writes analysis.json."""
import json, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from customers import extract as split_customer  # noqa: E402


def nfkc(s: str) -> str:
    """Full-width → half-width. The ledger has part numbers typed in full-width
    (ＥＣＺＤＹＶＭＧ), which match nothing until normalized."""
    return unicodedata.normalize("NFKC", str(s or ""))

REPO = Path("/Users/carlox/Personal/CarBiz")
d = json.load(open(REPO / "worker/state/data/新_訂單.json"))
h = d["header_row"]; hdr = [c.strip() for c in d["rows"][h]]
col = {c: i for i, c in enumerate(hdr) if c}
rows = []
for r in d["rows"][h + 1:]:
    g = lambda k: (r[col[k]] if k in col and col[k] < len(r) else "")
    if g("訂單ID"):
        rows.append({k: g(k) for k in col})

def num(s):
    t = re.sub(r"[¥$,\s]", "", str(s or ""))
    try: return float(t) if t not in ("", "-") else 0.0
    except ValueError: return 0.0

# --- brand: prefer the 品牌 column, else sniff the name -------------------------
BRAND_PAT = [
    ("ENDLESS", r"ENDLESS"), ("CUSCO", r"CUSCO"), ("OHLINS", r"OHLINS|オーリンズ"),
    ("HKS", r"\bHKS\b"), ("BBS", r"\bBBS\b"), ("RAYS", r"\bRAYS?\b|TE37|VMF|グラムライツ"),
    ("TOM'S", r"TOM'?S|TOMS"), ("MUGEN", r"MUGEN|無限"), ("TRD", r"\bTRD\b"),
    ("BLITZ", r"BLITZ"), ("TEIN", r"TEIN"), ("SPOON", r"SPOON"), ("TRUST/GReddy", r"TRUST|GReddy"),
    ("WAKO'S", r"WAKO'?S"), ("柿本改", r"柿本"), ("ROWEN", r"ROWEN"), ("VOLTEX", r"VOLTEX"),
    ("VALENTI", r"VALENTI"), ("TANABE", r"TANABE"), ("SARD", r"SARD"), ("DIXCEL", r"DIXCEL"),
    ("KUHL", r"KUHL"), ("LAILE", r"LAILE|ライル"), ("SYMS", r"SYMS"), ("OS技研", r"OS技研|OS GIKEN"),
    ("WedsSport", r"WEDS"), ("TWS", r"TWS"), ("RS-R", r"RS-?R|RSR"), ("VERUS", r"verus"),
    ("AIMGAIN", r"AIMGAIN"), ("PROVA", r"PROVA"), ("VARIS", r"VARIS"), ("AKEA", r"AKEA"),
    ("Bridgestone", r"POTENZA|普利司通|ブリヂストン"), ("近藤エンジニアリング", r"近藤|匠project"),
    # MODELLISTA before the TOYOTA fallback: the ledger's "CROWNCROSS" line is a
    # MODELLISTA accessory kit for the Crown Crossover — the car, not a brand.
    ("MODELLISTA", r"MODELLISTA|モデリスタ|クールシャイン"),
    ("Real Speed Engineering", r"\bRSE\b"), ("FORTEC", r"FORTEC"),
    ("MONSTER SPORT", r"MONSTER"), ("STI", r"\bSTI\b"), ("Kansai Service", r"Kansai"),
    ("RJ", r"^RJ$"), ("SYMS", r"SYMS"),
    ("SUBARU 原廠", r"SUBARU|スバル|六代森|LEVORG|レヴォーグ"),
    ("HONDA 原廠", r"HONDA|本田|ホンダ|CIVIC|シビック"),
    ("TOYOTA 原廠", r"TOYOTA|トヨタ"),
]
# Order matters: first match wins, so specific patterns come before generic ones.
CATS = [
    ("煞車", r"卡鉗|キャリパー|來令|ブレーキ|パッド|碟盤|ローター|BRAKE|MX72|CCRG|剎車|煞車|油管|RF650"),
    ("傳動", r"CLUTCH|クラッチ|離合器|\bLSD\b|デフ|飛輪"),
    ("鋁圈・輪胎", r"鋁圈|ホイール|WHEEL|TE37|VMF|G025|RI-[SA]|POTENZA|RW007|輪胎|タイヤ|中心蓋|CAP MODEL|螺絲 M1[24]|PLGM"),
    ("排氣", r"排氣|マフラー|EXHAUST|柿本|触媒|中段|尾飾|LEGAMAX|PREMIUM01"),
    ("進氣・引擎", r"進氣|エアクリ|中冷|インタークーラー|渦輪|タービン|皮帶|プーリー|油冷|オイルクーラー|卸壓閥|ブローオフ|HEAD COVER|PLUG COVER|機油蓋|機油芯|オイルフィルタ"),
    ("懸吊・底盤", r"避震|ダンパー|サスペンション|車高|拉桿|防傾|ブッシュ|襯套|DFV|コンプリート|スタビ|タワーバー|アームバー|補強|制震|油壓桿|アンダーパネル|下護板|上座|ロワアーム|BEST"),
    ("外觀・空力", r"尾翼|ウイング|ウィング|WING|鴨尾|前下|後下|側裙|スポイラー|套件|エアロ|保桿|バンパー|カーボン|卡夢|亮黑|導流|導風|ボンネット|風刀|貼紙|貼|字標|エンブレム|後視鏡蓋|ミラーカバー|クールシャイン|護罩"),
    ("燈系", r"尾燈|日行燈|テールランプ|ヘッドライト|LED|燈|ランプ|繼電器|喇叭|ホーン"),
    ("內裝・電子", r"旋鈕|方向盤|ステアリング|椅|シート|儀表|メーター|ミラー|鏡片|晴雨窗|バイザー|プロテクター|踏板|ペダル|空氣清淨"),
    ("油品・耗材", r"0W|5W|オイル|\bOIL\b|4CT|PROS|SFV|機油精|冷媒|水蓋|油壺|クーラント|ワイパー|雨刷|膠條|ウェザー"),
]
MODELS = [
    ("GR Yaris", r"GR\s*Y|GRY|ヤリス|GXPA16|MXPA12"),
    ("GR86 / BRZ", r"GR86|ZN8|BRZ|ZD8"),
    ("WRX / STI", r"WRX|VBH|VAB|STI"),
    ("Levorg", r"LEVORG|レヴォーグ|VN5|六代森"),
    ("Civic Type R", r"CIVIC|シビック|FL5|TYPE\s*R|typeR"),
    ("Tesla Model 3", r"TESLA|MODEL3|MODEL 3"),
    ("Porsche 718/987", r"BOXSTER|CAYMAN|ボクスター|ケイマン|98[127]"),
    ("Skyline Q50", r"SKYLINE|Q50|400R"),
    ("Mazda ND (MX-5)", r"\bND\b|MAZDA|ロードスター"),
    ("Crown Crossover", r"CROWNCROSS|クラウンクロス"),
    ("Forester", r"FORESTER|フォレスター|六代森|\bSJ[G]?\b"),
    ("Suzuki Swift Sport", r"ZC33"),
    ("Subaru XV / Crosstrek", r"\bXV\b|CROSSTREK"),
    ("Honda Prelude", r"PRELUDE|BF1"),
]

def sniff(pats, *fields):
    hay = " ".join(str(f or "") for f in fields)
    for label, pat in pats:
        if re.search(pat, hay, re.I):
            return label
    return ""

items, fees = [], []
for r in rows:
    name = nfkc(r.get("品名")).strip()
    raw_brand = nfkc(r.get("品牌")).strip()
    part = nfkc(r.get("料號")).strip()
    blob = f"{raw_brand} {name} {part}"
    if re.search(r"代買費|手續費|運費", blob) and not re.search(r"卡鉗|鋁圈|避震", blob):
        fees.append(r); continue
    if not name and not raw_brand:
        continue
    # The 品牌 column is hand-typed, so it sometimes holds a part name (リアバンパー),
    # a car model (BRZ), or a size — none of which are brands. Only trust it as a
    # fallback when it doesn't look like one of those.
    NOT_A_BRAND = r"^(BRZ|VN|ND|バンパー|リア|フロント|後保護板|後箱|ウイング|ウィング)|バンパー$|ウイング$"
    fallback = "" if re.search(NOT_A_BRAND, raw_brand, re.I) else raw_brand
    brand = sniff(BRAND_PAT, raw_brand, name) or fallback or "其他"
    # Strip customer names out of the product name; the page shows codes instead.
    clean_name, customers = split_customer(name)
    items.append({
        "id": r["訂單ID"], "batch": r["批次"], "date": r["下單日"], "status": r["狀態"],
        "brand": brand, "name": re.sub(r"\s+", " ", clean_name)[:120],
        "customers": customers, "part": part,
        "qty": num(r.get("數量")), "jpy": num(r.get("日幣合計¥")), "twd": num(r.get("台幣合計$")),
        "category": sniff(CATS, name, raw_brand, part) or "其他",
        "model": sniff(MODELS, name, raw_brand, part) or "",
    })

out = {
    "generated_from": "新_訂單 (26年家瑞訂單0803更新)",
    "range": [min(i["date"] for i in items), max(i["date"] for i in items)],
    "totals": {"lines": len(items), "batches": len(set(i["batch"] for i in items)),
               "jpy": sum(i["jpy"] for i in items), "twd": sum(i["twd"] for i in items),
               "fee_lines": len(fees), "fee_twd": sum(num(f.get("台幣合計$")) for f in fees)},
    "items": items,
}
Path("/private/tmp/claude-501/-Users-carlox-Personal/bae455ed-b844-4d8b-bf32-ff71834ff136/scratchpad/analysis.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

def agg(key):
    c = defaultdict(lambda: [0, 0.0])
    for i in items:
        if i[key]:
            c[i[key]][0] += 1; c[i[key]][1] += i["jpy"]
    return sorted(c.items(), key=lambda kv: -kv[1][1])

print(f"items={len(items)} fees={len(fees)} ¥{out['totals']['jpy']:,.0f} NT${out['totals']['twd']:,.0f}")
for k in ("category", "brand", "model"):
    print(f"\n=== {k} ===")
    for name, (n, jpy) in agg(k)[:12]:
        print(f"  {name:<22} {n:>3} 筆  ¥{jpy:>10,.0f}")
