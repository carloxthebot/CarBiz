#!/usr/bin/env python3
"""build.py — render data/blitz-gr86-zn8.json into a single self-contained
index.html (no build step, no CDN, opens straight off the filesystem).

Two inputs:
  data/blitz-gr86-zn8.json   BLITZ's Japanese listing (written by scrape.py)
  data/prices-local.json     researched TH / HK / MY street prices (optional)

Local prices sit in the SAME row as the Japanese price, one column per country,
joined on BLITZ's code no. -- the only stable SKU key across all four markets.
A separate per-country section would make you scroll to compare the one thing
the page exists to compare.

prices-local.json is optional on purpose: the Japanese listing has to render
whether or not the local research is finished, and each country lands separately.
Missing country -> its column shows 調查中; missing SKU -> that cell shows 「—」.
"""
import json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "blitz-gr86-zn8.json")
LOCAL = os.path.join(HERE, "data", "prices-local.json")
OUT = os.path.join(HERE, "index.html")

SOURCE_URL = ("https://partsnavi.blitz.co.jp/products/search/search_car/list.php"
              "?maker_id=1&car_name_first=1&car_name=GR86&car_model=ZN8&model_year=2024")

# Column order is deliberate: Japan is the reference price, the other three are
# read against it left to right.
COUNTRIES = [("TH", "泰國", "THB", "฿"), ("MY", "馬來西亞", "MYR", "RM"),
             ("SG", "新加坡", "SGD", "S$"), ("HK", "香港", "HKD", "HK$")]

CATEGORIES = [
    ("suspension", "懸吊・底盤", "車高調、拉桿、懸吊臂",
     ["DAMPER ZZ-R", "MIRACLE ADJUSTER Series", "SUSPENSION ARM", "B-MCB",
      "STABILINK ADJUSTER", "STRUT TOWER BAR", "TRUSS BAR"]),
    ("brake", "煞車", "大四／六活塞卡鉗套件",
     ["BIG CALIPER KIT II"]),
    ("intake", "進氣", "香菇頭、進氣管、集氣箱",
     ["CORE TYPE AIR CLEANER", "SUS POWER AIR FILTER Series", "CARBON INTAKE SYSTEM",
      "SUCTION KIT", "DRY CARBON SUCTION KIT", "HYBRID AIRCON FILTER"]),
    ("exhaust", "排氣", "NUR-SPEC 全段與尾飾管",
     ["NUR-SPEC Exhaust System"]),
    ("cooling", "冷卻・油溫", "水箱、油冷、感知器座",
     ["RACING RADIATOR TypeZS", "RACING RADIATOR CAP", "RACING OIL COOLER KIT BR",
      "RACING RADIATOR HOSE KIT", "RACING OIL FILTER", "OIL SENSOR ATTACHMENT",
      "WATER TEMP SENSOR ATTACHMENT"]),
    ("ecu", "電子・ECU・儀表", "油門控制、ECU、多功能顯示",
     ["OBDIIアダプター(LASERオプション品)", "OBDIIアダプター86/BRZ専用項目(LASERオプション品)",
      "Touch-B.R.A.I.N. PLUS 86/BRZ専用項目", "Touch-B.R.A.I.N. PLUS", "FLD METER",
      "Power Thro NA", "Sma Thro X", "Thro Con / Sma Thro", "Power Con X", "Power Con NA",
      "Speed Jumper", "BLITZ TUNING ECU", "TV-NAVI Jumper / TV Jumper", "RACING METER PANEL"]),
    ("aero", "外觀空力", "AERO SPEED 前中後定風翼",
     ["AERO SPEED"]),
    ("interior", "內裝・配件", "排檔頭、手煞車、油蓋、引擎蓋撐桿",
     ["OIL FILLER CAP", "SHIFT KNOB", "HAND BRAKE LEVER", "SMART PHONE HOLDER",
      "ENGINE HOOD DAMPER"]),
]


def yen(s):
    """'￥205,700 | (￥187,000)' -> (205700, 187000). Either half may be absent."""
    nums = [int(n.replace(",", "")) for n in re.findall(r"￥([\d,]+)", s or "")]
    return (nums[0] if nums else None), (nums[1] if len(nums) > 1 else None)


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def notes(it):
    return " ／ ".join(p for p in (it.get("note2"), it.get("note1")) if p).replace(" | ", " ")


def money(entry, sym, rate, jp, estimate=False):
    """Inner markup of one price: the local figure, then what it means vs Japan."""
    amt = entry["amount"]
    head = f'{sym}{amt:,.0f}' if isinstance(amt, (int, float)) else esc(amt)
    sub = ""
    if isinstance(amt, (int, float)) and rate:
        equiv = amt * rate
        mult = f" ×{equiv / jp:.2f}" if jp else ""
        sub = f'<span class="eq">≈￥{equiv:,.0f}{mult}</span>'
    tag = "試算" if estimate else entry.get("kind")
    tag = f'<span class="tag{" est" if estimate else ""}">{esc(tag)}</span>' if tag else ""
    body = f'{head}{tag}{sub}'
    if entry.get("url"):
        body = f'<a href="{esc(entry["url"])}" rel="noopener" title="{esc(entry.get("seen",""))}">{body}</a>'
    return body


def cell(retail, grey, sym, rate, jp, researched):
    """One country cell, carrying both readings; the toggle shows one at a time.

    「—」 and 調查中 are different claims: the first says we looked and there is no
    public price, the second says nobody has looked yet. Collapsing them would
    quietly turn an unfinished column into a finding. A parallel-import figure is
    a third thing again -- a calculation, never a quote -- so it is always tagged
    試算 and never silently mixed into the retail reading."""
    empty = f'<span class="none">{"—" if researched else "調查中"}</span>'
    r = money(retail, sym, rate, jp) if retail and retail.get("amount") not in (None, "") else empty
    g = (f'<span class="est">{money(grey, sym, rate, jp, True)}</span>'
         if grey and grey.get("amount") not in (None, "") else f'<span class="none">—</span>')
    return f'<td class="lp"><span class="v-retail">{r}</span><span class="v-grey">{g}</span></td>'


def main():
    groups = json.load(open(DATA))
    by_line = {g["line"]: g["items"] for g in groups}
    local = json.load(open(LOCAL)) if os.path.exists(LOCAL) else {}
    rates = (local.get("meta") or {}).get("rates") or {}       # JPY per 1 local unit
    prices = local.get("prices") or {}
    grey = local.get("grey") or {}          # 水貨到岸試算, keyed the same way
    have = {cc for cc in (c[0] for c in COUNTRIES) if (local.get("countries") or {}).get(cc)}

    placed, cats = set(), []
    for slug, title, blurb, lines in CATEGORIES:
        items = []
        for ln in lines:
            for it in by_line.get(ln, []):
                items.append(dict(it, line=ln))
                placed.add(ln)
        if items:
            cats.append((slug, title, blurb, items))
    leftover = [dict(it, line=ln) for ln, its in by_line.items() if ln not in placed for it in its]
    if leftover:
        cats.append(("other", "其他", "尚未歸類", leftover))

    total = sum(len(c[3]) for c in cats)
    jp_all = [p for p in (yen(i["price"])[0] for c in cats for i in c[3]) if p]
    covered = sum(1 for c in cats for i in c[3] if prices.get(i["code"]))
    stamp = datetime.date.today().isoformat()

    head_cols = "".join(f'<th class="lp">{esc(name)}<span class="cur">{esc(cur)}</span></th>'
                        for _, name, cur, _ in COUNTRIES)

    sections = []
    for slug, title, blurb, items in cats:
        rows, cur_line = [], None
        for it in sorted(items, key=lambda x: (x["line"], -(yen(x["price"])[0] or 0))):
            if it["line"] != cur_line:
                cur_line = it["line"]
                rows.append(f'<tr class="line"><th colspan="{3 + len(COUNTRIES)}">{esc(cur_line)}</th></tr>')
            incl, _ = yen(it["price"])
            n = notes(it)
            p = prices.get(it["code"], {})
            gp = grey.get(it["code"], {})
            cells = "".join(cell(p.get(cc), gp.get(cc), sym, rates.get(cur3), incl, cc in have)
                            for cc, _, cur3, sym in COUNTRIES)
            rows.append(
                f'<tr data-s="{esc((cur_line + " " + it["name"] + " " + it["code"] + " " + n).lower())}">'
                f'<td class="nm">{esc(it["name"].replace(" | ", " "))}'
                f'{f"<span class=nt>{esc(n)}</span>" if n else ""}</td>'
                f'<td class="cd">{esc(it["code"])}</td>'
                f'<td class="jp">{"￥{:,}".format(incl) if incl else "—"}</td>{cells}</tr>')
        sections.append(f'''<section id="{slug}">
  <h2>{esc(title)} <span class="cnt">{len(items)}</span></h2>
  <p class="blurb">{esc(blurb)}</p>
  <div class="wrap"><table>
    <thead><tr><th>品項</th><th>Code</th><th class="jp">日本<span class="cur">JPY 稅入</span></th>{head_cols}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</section>''')

    # ---- appendix: who sells it, what the markup is made of -----------------
    notes_html = ""
    for cc, name, cur3, _ in COUNTRIES:
        d = (local.get("countries") or {}).get(cc)
        if not d:
            notes_html += (f'<div class="note"><h3>{esc(name)}</h3>'
                           f'<p class="blurb">當地售價調查進行中。</p></div>')
            continue
        miss = d.get("notFound") or []
        chan = "".join(f'<li>{esc(c.get("name",""))}'
                       + (f' — <a href="{esc(c["url"])}" rel="noopener">{esc(c.get("kind","連結"))}</a>' if c.get("url") else "")
                       + (f' <span class="eq">{esc(c["note"])}</span>' if c.get("note") else "")
                       + '</li>' for c in d.get("channels", []))
        notes_html += f'''<div class="note"><h3>{esc(name)}
  <span class="cur">1 {esc(cur3)} ≈ ￥{rates.get(cur3, 0):.2f}</span></h3>
  <p class="blurb">{esc(d.get("summary",""))}</p>
  {f"<ul>{chan}</ul>" if chan else ""}
  {f'<p class="miss"><b>查不到公開標價：</b>{esc("、".join(miss))}</p>' if miss else ""}
  {f'<p class="miss">{esc(d["caveat"])}</p>' if d.get("caveat") else ""}
  {"".join(f'<p class="miss">{esc(x)}</p>' for x in d.get("extra", []))}
</div>'''

    nav = ('<a href="#channels">各地通路與稅費</a>'
           + "".join(f'<a href="#{s}">{esc(t)}</a>' for s, t, _, _ in cats)
           + '<button id="mode" type="button">切換：水貨到岸試算</button>')
    rate_line = "・".join(f"1 {c} ≈ ￥{rates[c]:.2f}" for _, _, c, _ in COUNTRIES if rates.get(c))

    html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BLITZ × GR86 (ZN8) 四地價格對照</title>
<style>
:root {{
  --bg:#f7f8fa; --card:#fff; --ink:#14161a; --dim:#616a76; --line:#e3e6eb;
  --accent:#0b64c8; --accentbg:#eaf2fd; --head:#f0f2f5; --jpbg:#fbfcfe;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#0e1013; --card:#15181d; --ink:#e8eaed; --dim:#98a1ad; --line:#252a31;
           --accent:#5aa9f8; --accentbg:#132436; --head:#1b1f26; --jpbg:#171b21; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans TC",
  "PingFang TC","Segoe UI",sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1180px; margin:0 auto; padding:0 20px 80px; }}
header {{ padding:48px 0 28px; border-bottom:1px solid var(--line); }}
h1 {{ margin:0 0 6px; font-size:30px; letter-spacing:-.02em; }}
.sub {{ color:var(--dim); margin:0 0 22px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:10px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 16px; }}
.stat b {{ display:block; font-size:22px; letter-spacing:-.01em; }}
.stat span {{ color:var(--dim); font-size:12px; }}
nav {{ position:sticky; top:0; z-index:5; background:var(--bg); padding:14px 0;
  border-bottom:1px solid var(--line); display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
nav a {{ color:var(--ink); text-decoration:none; font-size:13px; padding:5px 11px;
  border:1px solid var(--line); border-radius:999px; background:var(--card); white-space:nowrap; }}
nav a:hover {{ border-color:var(--accent); color:var(--accent); }}
#q {{ flex:1; min-width:180px; padding:7px 12px; border:1px solid var(--line);
  border-radius:999px; background:var(--card); color:var(--ink); font-size:13px; }}
#q:focus {{ outline:none; border-color:var(--accent); }}
section {{ margin:40px 0 0; }}
h2 {{ font-size:20px; margin:0 0 4px; letter-spacing:-.01em; }}
.cnt {{ font-size:12px; color:var(--dim); font-weight:400; background:var(--head);
  border-radius:999px; padding:2px 9px; vertical-align:3px; }}
.blurb {{ color:var(--dim); margin:0 0 14px; font-size:13px; }}
.wrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; min-width:860px; }}
thead th {{ text-align:left; font-size:11px; letter-spacing:.06em; color:var(--dim);
  text-transform:uppercase; padding:10px 14px; border-bottom:1px solid var(--line);
  background:var(--head); font-weight:600; }}
thead th.jp, thead th.lp {{ text-align:right; }}
.cur {{ display:block; font-size:10px; letter-spacing:.04em; color:var(--dim);
  font-weight:400; text-transform:none; margin-top:1px; }}
tbody td {{ padding:11px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
tbody tr:last-child td {{ border-bottom:none; }}
tr.line th {{ text-align:left; padding:12px 14px 6px; font-size:12px; color:var(--accent);
  background:var(--accentbg); border-bottom:1px solid var(--line); font-weight:600; }}
.nm {{ font-weight:500; min-width:220px; }}
.nt {{ display:block; color:var(--dim); font-size:11.5px; font-weight:400; margin-top:3px; line-height:1.45; }}
.cd {{ color:var(--dim); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.jp {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap;
  font-weight:600; background:var(--jpbg); }}
.lp {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.lp a {{ color:var(--ink); text-decoration:none; border-bottom:1px dotted var(--accent); }}
.lp a:hover {{ color:var(--accent); }}
.lp .none {{ color:var(--line); }}
.v-grey {{ display:none; }}
body.grey .v-retail {{ display:none; }}
body.grey .v-grey {{ display:inline; }}
.est {{ color:var(--dim); }}
.tag.est {{ border-style:dashed; border-color:var(--accent); color:var(--accent); }}
#mode {{ font:inherit; font-size:13px; padding:5px 11px; border:1px solid var(--accent);
  border-radius:999px; background:var(--card); color:var(--accent); cursor:pointer;
  white-space:nowrap; margin-left:auto; }}
body.grey #mode {{ background:var(--accent); color:#fff; }}
.eq {{ display:block; font-size:11px; color:var(--dim); font-weight:400; font-variant-numeric:tabular-nums; }}
.tag {{ font-size:10px; color:var(--dim); border:1px solid var(--line); border-radius:4px;
  padding:0 4px; margin-left:5px; vertical-align:1px; }}
.notes {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }}
.note {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; }}
.note h3 {{ margin:0 0 6px; font-size:15px; }}
.note ul {{ margin:8px 0 0; padding-left:18px; font-size:13px; }}
.note li {{ margin-bottom:5px; }}
.note a {{ color:var(--accent); }}
.miss {{ font-size:12.5px; color:var(--dim); margin:12px 0 0; }}
footer {{ margin-top:56px; padding-top:20px; border-top:1px solid var(--line); color:var(--dim); font-size:12.5px; }}
footer a {{ color:var(--accent); }}
tr.hide {{ display:none; }}
@media (max-width:640px) {{ h1 {{ font-size:24px; }} .page {{ padding:0 14px 60px; }} }}
</style>
</head>
<body>
<div class="page">
<header>
  <h1>BLITZ × GR86 <span style="color:var(--dim);font-weight:400">ZN8</span></h1>
  <p class="sub">FA24／2021.10– ・ 日本、泰國、香港、馬來西亞四地售價同列對照</p>
  <div class="stats">
    <div class="stat"><b>{total}</b><span>品項</span></div>
    <div class="stat"><b>{len(by_line)}</b><span>產品線</span></div>
    <div class="stat"><b>{len(cats)}</b><span>分類</span></div>
    <div class="stat"><b>{covered}</b><span>查到當地售價</span></div>
    <div class="stat"><b>￥{min(jp_all):,}–{max(jp_all):,}</b><span>日本定價區間</span></div>
  </div>
</header>
<nav><input id="q" type="search" placeholder="搜尋品項、Code、備註…" autocomplete="off">{nav}</nav>
<section id="channels">
  <h2>各地通路與稅費</h2>
  <p class="blurb">先讀這一節：各地由誰在賣、價差從哪裡來、哪些品項查不到公開標價，以及當地法規擋掉了什麼。下面的價格表要對照這裡才看得懂。</p>
  <div class="notes">{notes_html}</div>
</section>
{"".join(sections)}
<footer>
  日本價來源：<a href="{SOURCE_URL}" rel="noopener">BLITZ 商品検索システム</a>（GR86 / ZN8 / 2024 年式，全類別），擷取日 {stamp}，為日本國內含稅定價，不含運費、關稅與當地稅。<br>
  當地售價逐筆附來源連結（點價格即可開啟），為查訪當日的公開標價；括號內折算日圓僅供比較，匯率{f"：{rate_line}" if rate_line else "待補"}。查不到公開標價的品項一律留白，不做估算。<br>
  「水貨到岸試算」是從日本出口通路買進、加運費與當地關稅與稅金後的<strong>計算值</strong>，不是任何業者的報價，一律標示為試算；計算依據寫在各地卡片裡。<br>
  以 <code>./scrape.py &amp;&amp; ./build.py</code> 重新產生。
</footer>
</div>
<script>
const mode = document.getElementById('mode');
mode.addEventListener('click', () => {{
  const grey = document.body.classList.toggle('grey');
  mode.textContent = grey ? '切換：當地零售價' : '切換：水貨到岸試算';
}});
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase();
  document.querySelectorAll('tbody tr[data-s]').forEach(tr => {{
    tr.classList.toggle('hide', v && !tr.dataset.s.includes(v));
  }});
  // A product-line header with nothing left under it is noise, so hide it too.
  document.querySelectorAll('tr.line').forEach(h => {{
    let n = h.nextElementSibling, any = false;
    while (n && !n.classList.contains('line')) {{
      if (n.dataset.s && !n.classList.contains('hide')) {{ any = true; break; }}
      n = n.nextElementSibling;
    }}
    h.classList.toggle('hide', !any);
  }});
  document.querySelectorAll('section').forEach(s => {{
    const rows = s.querySelectorAll('tbody tr[data-s]');
    if (!rows.length) return;
    s.style.display = [...rows].some(r => !r.classList.contains('hide')) ? '' : 'none';
  }});
}});
</script>
</body>
</html>'''
    open(OUT, "w").write(html)
    print(f"{total} 品項 / {len(cats)} 分類 / {covered} 筆有當地售價 → {OUT}")


if __name__ == "__main__":
    main()
