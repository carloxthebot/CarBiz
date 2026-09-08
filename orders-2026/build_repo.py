#!/usr/bin/env python3
"""Build the artifact-format page (no doctype/html/head/body — the host wraps it)."""
import base64, json, html, re
from collections import defaultdict
from pathlib import Path

S = Path("/private/tmp/claude-501/-Users-carlox-Personal/bae455ed-b844-4d8b-bf32-ff71834ff136/scratchpad")
OUT = Path("/Users/carlox/Personal/CarBiz/orders-2026/index.html")
A = json.loads((S / "analysis.json").read_text(encoding="utf-8"))
L = json.loads((S / "links.json").read_text(encoding="utf-8"))
P = {k: v for k, v in json.loads((S / "products.json").read_text(encoding="utf-8")).items()
     if not k.startswith("_")}
BL, PL = L["brands"], L["products"]


# The artifact CSP admits no external image hosts, so every official photo is
# downscaled (sips, 640px/q72) and inlined as a data: URI. imgs/ is built by the
# fetch step; a missing file just falls back to the "no photo" placeholder.
IMGDIR = S / "imgs"


def data_uri(key: str) -> str | None:
    """Repo build: copy the photo into orders-2026/img/ and return a relative
    path. (The artifact build inlines the same file as a data: URI instead,
    because the artifact CSP admits no external or sibling files.)"""
    src = IMGDIR / f"{key.replace('/', '_')}.jpg"
    if not src.exists():
        return None
    dst_dir = OUT.parent / "img"
    dst_dir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", key) + ".jpg"
    (dst_dir / name).write_bytes(src.read_bytes())
    return f"img/{name}"


def prod(it):
    """Official product record for an item, matched on 料號 then 品名."""
    hay = f'{it["part"]} {it["name"]}'.lower()
    best = None
    for k, v in P.items():
        if k.lower() in hay and (best is None or len(k) > len(best[0])):
            best = (k, v)
    return best[1] if best else None
items, T = A["items"], A["totals"]
e = lambda s: html.escape(str(s or ""))
m = lambda n: f"{int(round(n)):,}"


def agg(key):
    c = defaultdict(lambda: {"n": 0, "jpy": 0.0})
    for i in items:
        k = i.get(key)
        if k:
            c[k]["n"] += 1; c[k]["jpy"] += i["jpy"]
    return sorted(c.items(), key=lambda kv: -kv[1]["jpy"])


def plink(it):
    r = prod(it)
    if r and r.get("url"):
        return r["url"]
    hay = f'{it["part"]} {it["name"]}'.lower()
    for k, u in PL.items():
        if k.lower() in hay:
            return u
    return None


cats, brands, models = agg("category"), agg("brand"), agg("model")
mons = sorted(((k, v) for k, v in
               ((d, {"n": sum(1 for i in items if i["date"][:7] == d),
                     "jpy": sum(i["jpy"] for i in items if i["date"][:7] == d)})
                for d in sorted({i["date"][:7] for i in items}))))
mmax = max(v["jpy"] for _, v in mons)
byc = defaultdict(list)
for i in items:
    byc[i["category"]].append(i)
ncust = len({c for i in items for c in i["customers"]})

CSS = """
/* Palette taken from the two brands this ledger spends most on:
   ENDLESS caliper blue and OHLINS damper gold. Neutrals carry a slight
   blue bias so they read as chosen next to that accent. */
:root{
  --ground:#f2f4f7; --panel:#ffffff; --sunk:#e9ecf1;
  --ink:#14171c; --ink-2:#5a6472; --ink-3:#8b95a4;
  --rule:#dde1e8; --rule-2:#c6ccd6;
  --endless:#0b46c9; --endless-soft:#e6edfd;
  --ohlins:#c8931a; --ohlins-soft:#faf1dc;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --disp:"Chivo","Helvetica Neue",-apple-system,"PingFang TC","Noto Sans TC",sans-serif;
  --body:-apple-system,BlinkMacSystemFont,"Hiragino Sans","PingFang TC","Noto Sans TC","Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0d1014; --panel:#161a20; --sunk:#1e232b;
    --ink:#e7eaee; --ink-2:#9aa4b2; --ink-3:#6b7686;
    --rule:#252b34; --rule-2:#39414d;
    --endless:#6f9cff; --endless-soft:#131f38;
    --ohlins:#e0b451; --ohlins-soft:#2a2314;
  }
}
:root[data-theme="dark"]{
  --ground:#0d1014; --panel:#161a20; --sunk:#1e232b;
  --ink:#e7eaee; --ink-2:#9aa4b2; --ink-3:#6b7686;
  --rule:#252b34; --rule-2:#39414d;
  --endless:#6f9cff; --endless-soft:#131f38;
  --ohlins:#e0b451; --ohlins-soft:#2a2314;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:16px/1.6 var(--body);-webkit-font-smoothing:antialiased}
.page{max-width:1120px;margin:0 auto;padding:0 20px 96px}

/* masthead: the ledger's own vitals, not a decorative hero */
header{padding:56px 0 0}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;
  color:var(--endless);margin:0 0 14px}
h1{font:700 clamp(30px,4.4vw,44px)/1.05 var(--disp);letter-spacing:-.025em;margin:0 0 12px;text-wrap:balance}
.lede{color:var(--ink-2);margin:0 0 30px;max-width:62ch;font-size:16.5px}
.vitals{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.vital{background:var(--panel);padding:16px 18px}
.vital b{display:block;font:700 25px/1.15 var(--disp);font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.vital span{display:block;font:500 11.5px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);margin-top:7px}
.vital.accent b{color:var(--endless)}

/* filter rail */
.rail{position:sticky;top:0;z-index:9;background:var(--ground);
  padding:14px 0;margin:34px 0 0;border-bottom:1px solid var(--rule);
  display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.rail a{font:500 13.5px/1 var(--body);color:var(--ink-2);text-decoration:none;
  padding:8px 13px;border:1px solid var(--rule);border-radius:2px;background:var(--panel)}
.rail a:hover,.rail a:focus-visible{color:var(--endless);border-color:var(--endless)}
#q{flex:1;min-width:200px;padding:8px 13px;border:1px solid var(--rule-2);border-radius:2px;
  background:var(--panel);color:var(--ink);font:14px var(--body)}
#q:focus{outline:2px solid var(--endless);outline-offset:-1px;border-color:transparent}

section{margin:52px 0 0;scroll-margin-top:76px}
h2{font:700 21px/1.2 var(--disp);letter-spacing:-.015em;margin:0 0 4px}
h2 em{font:500 12px/1 var(--mono);font-style:normal;letter-spacing:.08em;color:var(--ink-3);margin-left:9px}
.note{color:var(--ink-2);font-size:14.5px;margin:0 0 18px;max-width:64ch}

.panel{background:var(--panel);border:1px solid var(--rule);border-radius:3px;overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:15px}
table.w{min-width:820px}
th{text-align:left;font:600 11px/1 var(--mono);letter-spacing:.11em;text-transform:uppercase;
  color:var(--ink-3);padding:12px 16px;background:var(--sunk);border-bottom:1px solid var(--rule);white-space:nowrap}
th.r{text-align:right}
td{padding:12px 16px;border-bottom:1px solid var(--rule);vertical-align:top}
tr:last-child td{border-bottom:none}
td.num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;
  font-size:13.5px;font-weight:500;white-space:nowrap}
td.yen{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;
  font-size:14px;font-weight:600;white-space:nowrap}
td.code{font-family:var(--mono);font-size:12.5px;color:var(--ink-2);white-space:nowrap}
td.nm{font-weight:500;min-width:230px;line-height:1.45}
.sub{display:block;color:var(--ink-3);font-size:13px;font-weight:400;margin-top:4px}

/* share-of-total measure: one scale across each table, labelled by the yen column */
.meas{display:flex;align-items:center;gap:10px;min-width:140px}
.meas i{display:block;height:9px;background:var(--endless);border-radius:1px;flex:none}
.meas i.g{background:var(--ohlins)}
.meas u{font:500 11.5px/1 var(--mono);color:var(--ink-3);text-decoration:none;font-variant-numeric:tabular-nums}

a.src{color:var(--endless);text-decoration:none;font-family:var(--mono);font-size:12.5px;white-space:nowrap}
a.src:hover,a.src:focus-visible{text-decoration:underline}
.chip{display:inline-block;font:500 11px/1.5 var(--mono);letter-spacing:.04em;
  padding:2px 7px;border-radius:2px;background:var(--endless-soft);color:var(--endless);margin-left:6px}
.chip.c{background:var(--ohlins-soft);color:var(--ohlins)}
/* identified products: official photo + the manufacturer's own wording,
   with the ledger's shorthand kept underneath so the two can be reconciled */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:1px;
  background:var(--rule);border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.card{background:var(--panel);display:flex;flex-direction:column}
.shot{aspect-ratio:4/3;background:var(--sunk);display:grid;place-items:center;overflow:hidden}
.shot img{width:100%;height:100%;object-fit:contain;background:#fff}
.shot .none{font:500 11px/1 var(--mono);letter-spacing:.1em;color:var(--ink-3);text-transform:uppercase}
.card .body{padding:14px 16px 16px;display:flex;flex-direction:column;gap:7px;flex:1}
.card .of{font:500 14.5px/1.4 var(--body);margin:0}
.card .of a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule-2)}
.card .of a:hover,.card .of a:focus-visible{color:var(--endless);border-color:var(--endless)}
.card .raw{color:var(--ink-3);font-size:12.5px;line-height:1.45;margin:0}
.card .meta{margin-top:auto;padding-top:9px;border-top:1px solid var(--rule);
  display:flex;align-items:baseline;justify-content:space-between;gap:8px}
.card .meta b{font:600 15px/1 var(--mono);font-variant-numeric:tabular-nums}
.card .meta span{font:500 11px/1 var(--mono);letter-spacing:.06em;color:var(--ink-3)}
.card .warn{font:500 12px/1.45 var(--body);color:var(--ohlins);margin:0}
h3{font:600 15px/1.3 var(--disp);margin:30px 0 9px;display:flex;align-items:baseline;gap:10px}
h3 em{font:500 11.5px/1 var(--mono);font-style:normal;letter-spacing:.07em;color:var(--ink-3)}
footer{margin-top:72px;padding-top:22px;border-top:1px solid var(--rule);color:var(--ink-3);font-size:13.5px;line-height:1.7}
footer b{color:var(--ink-2);font-weight:600}
tr.off{display:none}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def meas(v, mx, gold=False):
    pct = 0 if not mx else v / mx * 100
    return (f'<div class="meas"><i class="{"g" if gold else ""}" style="width:{max(pct*.62,1.5):.1f}%"></i>'
            f'<u>{pct:.0f}%</u></div>')


p = ['<!DOCTYPE html>', '<html lang="zh-Hant">', '<head>',
     '<meta charset="utf-8">',
     '<meta name="viewport" content="width=device-width, initial-scale=1">',
     '<title>CarBiz 2026 採購年報</title>',
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chivo:wght@500;700&family=JetBrains+Mono:wght@500;600&display=swap">',
     f"<style>{CSS}</style>", '</head>', '<body>',
     '<div class="page">']

p.append(f"""<header>
<p class="eyebrow">Ledger · {A['range'][0]} – {A['range'][1]}</p>
<h1>今年買了什麼</h1>
<p class="lede">從訂單帳本整理出的 {T['batches']} 批、{T['lines']} 個品項。按類別、品牌與車型拆解，
每個品牌附官方網站。客戶以代號表示，代買費與運費不列入品項統計。</p>
<div class="vitals">
  <div class="vital accent"><b>¥{m(T['jpy'])}</b><span>日幣總額</span></div>
  <div class="vital"><b>NT${m(T['twd'])}</b><span>台幣總額</span></div>
  <div class="vital"><b>{T['lines']}</b><span>品項</span></div>
  <div class="vital"><b>{T['batches']}</b><span>批次</span></div>
  <div class="vital"><b>{len(brands)}</b><span>品牌</span></div>
  <div class="vital"><b>{ncust}</b><span>客戶</span></div>
</div>
</header>

<div class="rail">
  <a href="#cat">類別</a><a href="#brand">品牌</a><a href="#model">車型</a>
  <a href="#ident">官方資料</a><a href="#top">高價品項</a><a href="#all">全部明細</a>
  <input id="q" type="search" placeholder="搜尋品名、品牌、料號、客戶代號…" aria-label="搜尋明細">
</div>""")

# category
p.append(f'<section id="cat"><h2>類別<em>{len(cats)} 類</em></h2>'
         '<p class="note">外觀空力、懸吊底盤、鋁圈輪胎、煞車是四大宗，合計佔全年金額八成。</p>'
         '<div class="panel"><table><thead><tr><th>類別</th><th class="r">品項</th>'
         '<th class="r">日幣</th><th>佔全年</th></tr></thead><tbody>')
for n, v in cats:
    p.append(f'<tr><td class="nm">{e(n)}</td><td class="num">{v["n"]}</td>'
             f'<td class="yen">¥{m(v["jpy"])}</td><td>{meas(v["jpy"], T["jpy"])}</td></tr>')
p.append('</tbody></table></div></section>')

# brand
lk = sum(1 for n, _ in brands if BL.get(n))
p.append(f'<section id="brand"><h2>品牌<em>{len(brands)} 家 · {lk} 家附官方連結</em></h2>'
         '<p class="note">集中度很高：ENDLESS、ÖHLINS、BBS、RAYS 四家就佔四成金額。'
         'CUSCO 筆數最多但單價低，多是拉桿與補強件。</p>'
         '<div class="panel"><table class="w"><thead><tr><th>品牌</th><th class="r">品項</th>'
         '<th class="r">日幣</th><th>佔全年</th><th>官方網站</th></tr></thead><tbody>')
for n, v in brands:
    u = BL.get(n)
    a = (f'<a class="src" href="{e(u)}" target="_blank" rel="noopener">'
         f'{e(re.sub(r"^https?://(www\\.)?", "", u).rstrip("/"))} ↗</a>') if u else '<span class="code" style="color:var(--ink-3)">—</span>'
    p.append(f'<tr><td class="nm">{e(n)}</td><td class="num">{v["n"]}</td>'
             f'<td class="yen">¥{m(v["jpy"])}</td><td>{meas(v["jpy"], T["jpy"])}</td><td>{a}</td></tr>')
p.append('</tbody></table></div></section>')

# model
p.append(f'<section id="model"><h2>車型<em>{len(models)} 種</em></h2>'
         '<p class="note">GR Yaris 一枝獨秀，其次是 GR86／BRZ 與 Subaru 家族。'
         '通用件與油品沒有車型標註，不列入。</p>'
         '<div class="panel"><table><thead><tr><th>車型</th><th class="r">品項</th>'
         '<th class="r">日幣</th><th>佔全年</th></tr></thead><tbody>')
for n, v in models:
    p.append(f'<tr><td class="nm">{e(n)}</td><td class="num">{v["n"]}</td>'
             f'<td class="yen">¥{m(v["jpy"])}</td><td>{meas(v["jpy"], T["jpy"], True)}</td></tr>')
p.append('</tbody></table></div></section>')

# identified products — official name, official photo, ledger shorthand kept
ided = [i for i in sorted(items, key=lambda x: -x["jpy"]) if prod(i)]
seen_key, cards = set(), []
for i in ided:
    r = prod(i)
    k = r["official"]
    if k in seen_key:
        continue
    seen_key.add(k); cards.append((i, r))
for i, r in cards:  # resolve each card's inlined photo once
    hit = next((k for k, v in P.items() if v.get("official") == r["official"] and v.get("img")), None)
    r["_uri"] = data_uri(hit) if hit else None
withimg = sum(1 for _, r in cards if r.get("_uri"))
p.append(f'<section id="ident"><h2>查到官方資料的品項<em>{len(cards)} 項 · {withimg} 張官方照片</em></h2>'
         '<p class="note">帳本裡的品名是速記，這裡換成各廠商官方寫法，照片取自製造商官網。'
         '下方灰字是帳本原本的寫法，方便對照。</p><div class="cards">')
for i, r in cards:
    img = (f'<img src="{r["_uri"]}" alt="{e(r["official"])}" loading="lazy">'
           ) if r.get("_uri") else '<span class="none">官網無產品照</span>'
    of = e(r["official"])
    if r.get("url"):
        of = f'<a href="{e(r["url"])}" target="_blank" rel="noopener">{of} ↗</a>'
    warn = f'<p class="warn">⚠ {e(r["note"])}</p>' if r.get("note") else ""
    tags = "".join(f'<span class="chip">{e(i["model"])}</span>' for _ in [1] if i["model"])
    tags += "".join(f'<span class="chip c">{e(c)}</span>' for c in i["customers"])
    p.append(f'<article class="card"><div class="shot">{img}</div><div class="body">'
             f'<p class="of">{of}</p><p class="raw">帳本：{e(i["name"])}{tags}</p>{warn}'
             f'<div class="meta"><b>¥{m(i["jpy"])}</b><span>{e(r.get("brand") or i["brand"])} · {e(i["batch"])}</span></div>'
             f'</div></article>')
p.append('</div></section>')

# top items
p.append('<section id="top"><h2>高價品項<em>Top 20</em></h2>'
         '<p class="note">單筆金額前 20 名。有查到官方產品頁的品名可點。</p>'
         '<div class="panel"><table class="w"><thead><tr><th>品項</th><th>品牌</th>'
         '<th>類別</th><th>批次</th><th class="r">日幣</th></tr></thead><tbody>')
for i in sorted(items, key=lambda x: -x["jpy"])[:20]:
    u = plink(i)
    nm = (f'<a class="src" style="font-family:var(--body);font-size:15px;font-weight:500" '
          f'href="{e(u)}" target="_blank" rel="noopener">{e(i["name"])} ↗</a>') if u else e(i["name"])
    tags = "".join(f'<span class="chip">{e(i["model"])}</span>' for _ in [1] if i["model"])
    tags += "".join(f'<span class="chip c">{e(c)}</span>' for c in i["customers"])
    sub = f'<span class="sub">料號 {e(i["part"])}</span>' if i["part"] else ""
    p.append(f'<tr><td class="nm">{nm}{tags}{sub}</td><td class="code">{e(i["brand"])}</td>'
             f'<td class="code">{e(i["category"])}</td><td class="code">{e(i["batch"])}</td>'
             f'<td class="yen">¥{m(i["jpy"])}</td></tr>')
p.append('</tbody></table></div></section>')

# all
p.append(f'<section id="all"><h2>全部明細<em>{len(items)} 筆</em></h2>'
         '<p class="note">依類別分組、組內按金額排序。上方搜尋框可即時篩選。</p>')
for cat, lst in sorted(byc.items(), key=lambda kv: -sum(x["jpy"] for x in kv[1])):
    p.append(f'<h3>{e(cat)}<em>{len(lst)} 筆 · ¥{m(sum(x["jpy"] for x in lst))}</em></h3>'
             '<div class="panel"><table class="w f"><thead><tr><th>品名</th><th>品牌</th>'
             '<th>料號</th><th>批次</th><th class="r">量</th><th class="r">日幣</th></tr></thead><tbody>')
    for i in sorted(lst, key=lambda x: -x["jpy"]):
        u = plink(i)
        nm = (f'<a class="src" style="font-family:var(--body);font-size:15px;font-weight:500" '
              f'href="{e(u)}" target="_blank" rel="noopener">{e(i["name"])} ↗</a>') if u else e(i["name"])
        tags = "".join(f'<span class="chip">{e(i["model"])}</span>' for _ in [1] if i["model"])
        tags += "".join(f'<span class="chip c">{e(c)}</span>' for c in i["customers"])
        hay = e(f'{i["name"]} {i["brand"]} {i["part"]} {i["batch"]} {i["model"]} {" ".join(i["customers"])}').lower()
        p.append(f'<tr data-h="{hay}"><td class="nm">{nm}{tags}</td><td class="code">{e(i["brand"])}</td>'
                 f'<td class="code">{e(i["part"])}</td><td class="code">{e(i["batch"])}</td>'
                 f'<td class="num">{int(i["qty"]) if i["qty"] else ""}</td>'
                 f'<td class="yen">¥{m(i["jpy"])}</td></tr>')
    p.append('</tbody></table></div>')
p.append('</section>')

p.append(f"""<footer>
<b>資料來源</b> 訂單帳本「{e(A['generated_from'])}」，{T['lines']} 個品項；另有 {T['fee_lines']} 筆代買費未計入。<br>
<b>客戶代號</b> C01–C{ncust:02d} 為代號，對照表不在此頁。<br>
<b>品牌與類別</b> 依品名關鍵字自動判讀；少數原始資料沒有品名的歸為「其他」。<br>
<b>官方連結與照片</b> 逐一實際抓取驗證（HTTP 200 且為圖片），非推測網址；圖片直接引用製造商網站，
價格與規格以各廠商公告為準。
</footer></div>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{
  const v=q.value.trim().toLowerCase();
  document.querySelectorAll('table.f tbody tr').forEach(r=>r.classList.toggle('off',v&&!r.dataset.h.includes(v)));
  document.querySelectorAll('table.f').forEach(t=>{{
    const on=t.querySelectorAll('tbody tr:not(.off)').length;
    const pn=t.closest('.panel'),h=pn.previousElementSibling;
    pn.style.display=on?'':'none';
    if(h&&h.tagName==='H3')h.style.display=on?'':'none';
  }});
}});
</script>
</body>
</html>""")

OUT.write_text("\n".join(p), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes) · brands linked {lk}/{len(brands)} · customers {ncust}")
