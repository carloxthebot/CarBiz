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
# The report lives on its own path, not at the site root: CarBiz is meant to
# hold more than one pricing study, and the root is the index of them.
OUT = os.path.join(HERE, "blitz-gr86", "index.html")

SOURCE_URL = ("https://partsnavi.blitz.co.jp/products/search/search_car/list.php"
              "?maker_id=1&car_name_first=1&car_name=GR86&car_model=ZN8&model_year=2024")

# Column order is deliberate: Japan is the reference price, the other three are
# read against it left to right.
COUNTRIES = [("TH", "泰國", "THB", "฿"), ("MY", "馬來西亞", "MYR", "RM"),
             ("SG", "新加坡", "SGD", "S$"), ("HK", "香港", "HKD", "HK$")]
FLAGS = {"TH": "🇹🇭", "MY": "🇲🇾", "SG": "🇸🇬", "HK": "🇭🇰", "PI": "📦"}

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
    tag = entry.get("kind")
    tag = f'<span class="tag{" est" if estimate else ""}">{esc(tag)}</span>' if tag else ""
    body = f'{head}{tag}{sub}'
    if entry.get("url"):
        body = f'<a href="{esc(entry["url"])}" rel="noopener" title="{esc(entry.get("seen",""))}">{body}</a>'
    return body


def cell(retail, grey, sym, rate, jp, researched):
    """One country cell: the retail price found, and under it the landed estimate.

    Both readings sit in the same cell because they answer the same question from
    two directions -- what a shop there charges, and what it costs to bring one in
    yourself. Keeping them side by side is the comparison; hiding one behind a
    toggle made you hold a number in your head while you flipped.

    「—」 and 調查中 stay different claims: the first says we looked and there is no
    public price, the second says nobody has looked. An estimate is a third thing
    again -- arithmetic, never a quote -- so it always carries its 試算 tag and its
    own muted style, and is never allowed to look like a found price."""
    real = bool(retail and retail.get("amount") not in (None, ""))
    empty = f'<span class="none">{"—" if researched else "調查中"}</span>'
    r = money(retail, sym, rate, jp) if real else empty
    out = f'<span class="v-retail">{r}</span>'
    if grey and grey.get("amount") not in (None, ""):
        # A title attribute is a desktop-only affordance -- a phone has no hover,
        # so the arithmetic behind every estimate was simply unreachable there.
        out += (f'<button type="button" class="v-grey" data-calc="{esc(grey.get("note",""))}">'
                f'{money(grey, sym, rate, jp, True)}</button>')
    return f'<td class="lp{" real" if real else ""}">{out}</td>'


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
    stamp = datetime.date.today().isoformat()

    def has_any(code):
        """A price someone actually charges, found in a listing. Every SKU now
        carries a landed estimate, so an estimate can no longer sort the page --
        what still separates the two halves is whether anyone in the four markets
        was observed selling the thing."""
        return any(v.get("amount") not in (None, "")
                   for v in prices.get(code, {}).values())

    covered = sum(1 for c in cats for i in c[3] if has_any(i["code"]))

    head_cols = "".join(f'<th class="lp">{esc(name)}<span class="cur">{esc(cur)}</span></th>'
                        for _, name, cur, _ in COUNTRIES)

    def row(it, cur_line):
        incl, _ = yen(it["price"])
        n = notes(it)
        p, gp = prices.get(it["code"], {}), grey.get(it["code"], {})
        cells = "".join(cell(p.get(cc), gp.get(cc), sym, rates.get(cur3), incl, cc in have)
                        for cc, _, cur3, sym in COUNTRIES)
        return (f'<tr data-s="{esc((cur_line + " " + it["name"] + " " + it["code"] + " " + n).lower())}">'
                f'<td class="nm">{esc(it["name"].replace(" | ", " "))}'
                f'{f"<span class=nt>{esc(n)}</span>" if n else ""}</td>'
                f'<td class="cd">{esc(it["code"])}</td>'
                f'<td class="jp">{"￥{:,}".format(incl) if incl else "—"}</td>{cells}</tr>')

    # The page leads with what can actually be compared. An item nobody in the
    # four markets prices has one number on it, and 77 such rows in front of the
    # 33 that carry a comparison buries the whole point of the table.
    sections, unpriced = [], []
    for slug, title, blurb, items in cats:
        rows, cur_line = [], None
        for it in sorted(items, key=lambda x: (x["line"], -(yen(x["price"])[0] or 0))):
            if not has_any(it["code"]):
                unpriced.append((title, it))
                continue
            if it["line"] != cur_line:
                cur_line = it["line"]
                rows.append(f'<tr class="line"><th colspan="{3 + len(COUNTRIES)}">{esc(cur_line)}</th></tr>')
            rows.append(row(it, cur_line))
        if not rows:
            continue
        n_here = sum(1 for i in items if has_any(i["code"]))
        sections.append(f'''<section id="{slug}">
  <h2>{esc(title)} <span class="cnt">{n_here} / {len(items)}</span></h2>
  <p class="blurb">{esc(blurb)}</p>
  <div class="wrap"><table>
    <thead><tr><th>品項</th><th>Code</th><th class="jp">日本<span class="cur">JPY 稅入</span></th>{head_cols}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</section>''')

    # ---- the other half: nobody there sells it, so only the estimate ------
    nl_rows, cur_cat = [], None
    for cat_title, it in unpriced:
        if cat_title != cur_cat:
            cur_cat = cat_title
            nl_rows.append(f'<tr class="line"><th colspan="{3 + len(COUNTRIES)}">{esc(cat_title)}'
                           f' <span class="eq">{esc(it["line"])}</span></th></tr>')
        nl_rows.append(row(it, cat_title + " " + it["line"]))
    nolocal = f'''<section id="nolocal">
  <h2>四地都沒有查到零售標價 <span class="cnt">{len(unpriced)} / {total}</span></h2>
  <p class="blurb">這些品項在泰、馬、新、港都沒有人公開標價，所以只有日本定價與到岸試算——每一格的數字都是計算值，
  沒有任何一筆是有人真的在賣的價格。查不到的成因有兩種，讀的時候要分開：一種是品項本身在海外沒有流通（電子類幾乎全數如此）；
  另一種是被 BLITZ 自己的料號細分稀釋——NUR-SPEC 排氣與 AERO SPEED 光是尾飾管材質、有無 LED 就拆成十幾個料號，
  海外賣場只會進其中一兩個規格。</p>
  <div class="wrap"><table>
    <thead><tr><th>品項</th><th>Code</th><th class="jp">日本<span class="cur">JPY 稅入</span></th>{head_cols}</tr></thead>
    <tbody>{"".join(nl_rows)}</tbody>
  </table></div>
</section>''' if unpriced else ""

    # ---- appendix: who sells it, what the markup is made of -----------------
    tabs, panels = [], []
    for cc, name, cur3, _ in COUNTRIES:
        d0 = (local.get("countries") or {}).get(cc)
        n_found = sum(1 for c in prices.values() if c.get(cc, {}).get("amount") not in (None, ""))
        tabs.append(f'<button type="button" data-t="{cc}">{FLAGS[cc]} {esc(name)}'
                    f'<span class="cnt">{n_found}</span></button>')
        if not d0:
            panels.append(f'<div class="panel" id="p-{cc}"><p class="blurb">當地售價調查進行中。</p></div>')
            continue
        miss = d0.get("notFound") or []
        chan = "".join(
            f'<li><b>{esc(c.get("name",""))}</b>'
            + (f' — <a href="{esc(c["url"])}" rel="noopener">{esc(c.get("kind","連結"))}</a>' if c.get("url")
               else (f' <span class="eq">{esc(c.get("kind",""))}</span>' if c.get("kind") else ""))
            + (f'<br><span class="eq">{esc(c["note"])}</span>' if c.get("note") else "")
            + '</li>' for c in d0.get("channels", []))
        panels.append(f'''<div class="panel" id="p-{cc}">
  <p class="rate">1 {esc(cur3)} ≈ ￥{rates.get(cur3, 0):.2f}　·　查到零售標價 {n_found} 筆</p>
  <p class="lead">{esc(d0.get("summary",""))}</p>
  {f"<h4>通路</h4><ul>{chan}</ul>" if chan else ""}
  {f'<p class="miss"><b>查不到公開標價：</b>{esc("、".join(miss))}</p>' if miss else ""}
  {f'<p class="miss">{esc(d0["caveat"])}</p>' if d0.get("caveat") else ""}
  {"".join(f'<p class="miss">{esc(x)}</p>' for x in d0.get("extra", []))}
</div>''')

    pi = local.get("greyNote")
    if pi:
        tabs.append(f'<button type="button" data-t="PI">{FLAGS["PI"]} 水貨試算</button>')
        rt = pi.get("ratioTable")
        rt_html = ""
        if rt:
            rt_html = ('<h4>定價比率是怎麼推得的</h4><div class="wrap"><table class="ratio">'
                       + "<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in rt["head"])
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(
                           f'<td class="{"pr" if i == 1 else ""}">{esc(c)}</td>'
                           for i, c in enumerate(r)) + "</tr>" for r in rt["rows"])
                       + "</tbody></table></div>")
        panels.append('<div class="panel" id="p-PI">'
                      + '<p class="lead">' + esc(pi.get("summary", "")) + '</p>'
                      + "".join('<p class="miss">' + esc(x) + '</p>' for x in pi.get("extra", []))
                      + rt_html + '</div>')
    notes_html = (f'<div class="tabs">{"".join(tabs)}</div>'
                  f'<div class="panels">{"".join(panels)}</div>')

    shown = {sec.split('"')[1] for sec in sections}
    nav = ('<a href="#channels">各地通路與稅費</a>'
           + "".join(f'<a href="#{sl}">{esc(t)}</a>' for sl, t, _, _ in cats if sl in shown)
           + ('<a href="#nolocal">只有試算</a>' if unpriced else ""))
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
  --real:#0d6b52; --realbg:#eaf6f1; --line-2:#c8cdd6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#0e1013; --card:#15181d; --ink:#e8eaed; --dim:#98a1ad; --line:#252a31;
           --accent:#5aa9f8; --accentbg:#132436; --head:#1b1f26; --jpbg:#171b21;
           --real:#5fc9a4; --realbg:#12291f; --line-2:#3a424d; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:18px/1.65 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans TC",
  "PingFang TC","Segoe UI",sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1340px; margin:0 auto; padding:0 20px 80px; }}
header {{ padding:48px 0 28px; border-bottom:1px solid var(--line); }}
h1 {{ margin:0 0 8px; font-size:38px; letter-spacing:-.02em; }}
.sub {{ color:var(--dim); margin:0 0 22px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:10px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 16px; }}
.stat b {{ display:block; font-size:28px; letter-spacing:-.01em; }}
.stat span {{ color:var(--dim); font-size:15px; }}
nav {{ position:sticky; top:0; z-index:5; background:var(--bg); padding:14px 0;
  border-bottom:1px solid var(--line); display:flex; gap:10px; align-items:center; }}
.chips {{ display:flex; gap:8px; flex-wrap:wrap; }}
nav a {{ color:var(--ink); text-decoration:none; font-size:16px; padding:7px 14px;
  border:1px solid var(--line); border-radius:999px; background:var(--card); white-space:nowrap; }}
nav a:hover {{ border-color:var(--accent); color:var(--accent); }}
#q {{ flex:1; min-width:180px; padding:7px 12px; border:1px solid var(--line);
  border-radius:999px; background:var(--card); color:var(--ink); font-size:16px; }}
#q:focus {{ outline:none; border-color:var(--accent); }}
section {{ margin:40px 0 0; }}
h2 {{ font-size:26px; margin:0 0 6px; letter-spacing:-.01em; }}
.cnt {{ font-size:15px; color:var(--dim); font-weight:400; background:var(--head);
  border-radius:999px; padding:2px 9px; vertical-align:3px; }}
.blurb {{ color:var(--dim); margin:0 0 16px; font-size:16px; line-height:1.7; }}
.wrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:17px; min-width:1040px; }}
thead th {{ text-align:left; font-size:13px; letter-spacing:.06em; color:var(--dim);
  text-transform:uppercase; padding:12px 16px; border-bottom:1px solid var(--line);
  background:var(--head); font-weight:600; }}
thead th.jp, thead th.lp {{ text-align:right; }}
.cur {{ display:block; font-size:12.5px; letter-spacing:.04em; color:var(--dim);
  font-weight:400; text-transform:none; margin-top:1px; }}
tbody td {{ padding:13px 16px; border-bottom:1px solid var(--line); vertical-align:top; }}
tbody tr:last-child td {{ border-bottom:none; }}
tr.line th {{ text-align:left; padding:14px 16px 8px; font-size:15px; color:var(--accent);
  background:var(--accentbg); border-bottom:1px solid var(--line); font-weight:600; }}
.nm {{ font-weight:500; min-width:220px; }}
.nt {{ display:block; color:var(--dim); font-size:14px; font-weight:400; margin-top:3px; line-height:1.45; }}
.cd {{ color:var(--dim); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.jp {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap;
  font-weight:600; background:var(--jpbg); }}
.lp {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.lp.real {{ background:var(--realbg); box-shadow:inset 3px 0 0 var(--real); }}
.lp.real .v-retail {{ font-weight:600; }}
.lp a {{ color:var(--ink); text-decoration:none; border-bottom:1px dotted var(--accent); }}
.lp a:hover {{ color:var(--accent); }}
.lp .none {{ color:var(--line); }}
.v-retail {{ display:block; }}
.v-grey {{ display:block; width:100%; margin-top:6px; padding:6px 0 0;
  border:none; border-top:1px dotted var(--line); background:none; color:var(--dim);
  font:inherit; text-align:right; cursor:pointer; }}
.v-grey:hover .tag.est {{ border-color:var(--accent); color:var(--accent); }}
#calc {{ position:fixed; left:0; right:0; bottom:0; z-index:20; background:var(--card);
  border-top:2px solid var(--accent); padding:20px 24px 24px; font-size:16px;
  line-height:1.75; max-height:52vh; overflow-y:auto;
  box-shadow:0 -8px 32px rgba(0,0,0,.16); }}
#calc b {{ display:block; font-size:14px; letter-spacing:.05em; color:var(--dim);
  text-transform:uppercase; margin-bottom:6px; }}
#calc p {{ margin:0; max-width:900px; }}
#calcx {{ position:absolute; top:12px; right:16px; font:inherit; font-size:26px; line-height:1;
  background:none; border:none; color:var(--dim); cursor:pointer; padding:4px 8px; }}
#calcx:hover {{ color:var(--ink); }}
.eq {{ display:block; font-size:13.5px; color:var(--dim); font-weight:400; font-variant-numeric:tabular-nums; }}
.tag {{ font-size:12.5px; border-radius:4px; padding:1px 6px; margin-left:6px; vertical-align:1px;
  border:1px solid var(--real); color:var(--real); background:var(--realbg); }}
.tag.est {{ border-style:dashed; border-color:var(--line-2); color:var(--dim); background:transparent; }}
.tabs {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:-1px; }}
.tabs button {{ font:inherit; font-size:17px; padding:11px 18px; cursor:pointer;
  background:var(--bg); color:var(--dim); border:1px solid var(--line);
  border-bottom-color:transparent; border-radius:12px 12px 0 0; white-space:nowrap; }}
.tabs button:hover {{ color:var(--ink); }}
.tabs button.on {{ background:var(--card); color:var(--ink); font-weight:600; border-bottom-color:var(--card); }}
.tabs .cnt {{ margin-left:8px; font-size:13px; }}
.panels {{ background:var(--card); border:1px solid var(--line); border-radius:0 12px 12px 12px;
  padding:24px 26px; }}
.panel {{ display:none; }}
.panel.on {{ display:block; }}
.panel h4 {{ margin:22px 0 6px; font-size:15px; letter-spacing:.05em; text-transform:uppercase;
  color:var(--dim); }}
.panel ul {{ margin:0; padding-left:20px; font-size:16px; }}
.panel li {{ margin-bottom:9px; }}
.panel a {{ color:var(--accent); }}
table.ratio {{ min-width:0; font-size:15px; }}
table.ratio td {{ white-space:normal; }}
table.ratio td.pr {{ font-weight:600; }}
.lead {{ font-size:18px; line-height:1.8; margin:0 0 4px; }}
.rate {{ color:var(--dim); font-size:14px; margin:0 0 12px; font-variant-numeric:tabular-nums; }}
.note {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; }}
.note h3 {{ margin:0 0 8px; font-size:19px; }}
.note.pi {{ border-color:var(--accent); background:var(--accentbg); grid-column:1/-1; }}
.note ul {{ margin:10px 0 0; padding-left:20px; font-size:16px; }}
.note li {{ margin-bottom:5px; }}
.note a {{ color:var(--accent); }}
.miss {{ font-size:15.5px; line-height:1.75; color:var(--dim); margin:12px 0 0; }}
footer {{ margin-top:56px; padding-top:20px; border-top:1px solid var(--line); color:var(--dim); font-size:15.5px; line-height:1.75; }}
footer a {{ color:var(--accent); }}
tr.hide {{ display:none; }}
/* On a phone the chip rows wrapped to four or five lines and pushed the table
   off the screen. One swipeable line each instead -- the row is the affordance,
   so it keeps a visible edge rather than fading out. */
@media (max-width:780px) {{
  nav {{ flex-direction:column; align-items:stretch; gap:10px; }}
  #q {{ width:100%; min-width:0; }}
  .chips, .tabs {{ flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none;
    scroll-snap-type:x proximity; -webkit-overflow-scrolling:touch;
    margin:0 -14px; padding:0 14px 2px; }}
  .chips::-webkit-scrollbar, .tabs::-webkit-scrollbar {{ display:none; }}
  .chips a, .tabs button {{ scroll-snap-align:start; flex:0 0 auto; }}
  .panels {{ border-radius:12px; padding:20px 18px; }}
}}
@media (max-width:640px) {{ h1 {{ font-size:30px; }} .page {{ padding:0 14px 60px; }}
  .panels {{ margin:0 -14px; border-radius:0; border-left:none; border-right:none; }} }}
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
    <div class="stat"><b>{covered} <span style="font-size:14px;color:var(--dim)">/ {total}</span></b><span>查到零售標價（{covered / total * 100:.0f}%）</span></div>
    <div class="stat"><b>{total}</b><span>有到岸試算</span></div>
    <div class="stat"><b>￥{min(jp_all):,}–{max(jp_all):,}</b><span>日本定價區間</span></div>
  </div>
</header>
<nav><input id="q" type="search" placeholder="搜尋品項、Code、備註…" autocomplete="off">
<div class="chips">{nav}</div></nav>
<section id="channels">
  <h2>各地通路與稅費</h2>
  <p class="blurb">先讀這一節：各地由誰在賣、價差從哪裡來、哪些品項查不到公開標價，以及當地法規擋掉了什麼。下面的價格表要對照這裡才看得懂。</p>
  <div class="notes">{notes_html}</div>
</section>
{"".join(sections)}
{nolocal}
<div id="calc" hidden><button type="button" id="calcx" aria-label="關閉">×</button>
  <b>這一格是怎麼算出來的</b><p id="calct"></p></div>
<footer>
  日本價來源：<a href="{SOURCE_URL}" rel="noopener">BLITZ 商品検索システム</a>（GR86 / ZN8 / 2024 年式，全類別），擷取日 {stamp}，為日本國內含稅定價，不含運費、關稅與當地稅。<br>
  當地售價逐筆附來源連結（點價格即可開啟），為查訪當日的公開標價；括號內折算日圓僅供比較，匯率{f"：{rate_line}" if rate_line else "待補"}。查不到公開標價的品項一律留白，不做估算。<br>
  「水貨到岸試算」是從日本出口通路買進、加運費與當地關稅與稅金後的<strong>計算值</strong>，不是任何業者的報價，一律標示為試算；計算依據寫在各地卡片裡。<br>
  以 <code>./scrape.py &amp;&amp; ./greycalc.py &amp;&amp; ./build.py</code> 重新產生。
</footer>
</div>
<script>
// Every estimate has its own arithmetic -- the exporter ratio differs by product
// line, the freight by size band, the duty and tax by destination -- so each one
// carries its own working, shown in one shared panel rather than 440 hidden rows.
const calc = document.getElementById('calc'), calct = document.getElementById('calct');
document.addEventListener('click', e => {{
  const b = e.target.closest('.v-grey');
  if (!b) return;
  calct.textContent = b.dataset.calc;
  calc.hidden = false;
}});
document.getElementById('calcx').addEventListener('click', () => {{ calc.hidden = true; }});
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') calc.hidden = true; }});

// Country intel is five long reads; showing them all at once buried the tables.
const tabs = [...document.querySelectorAll('.tabs button')];
const show = k => {{
  tabs.forEach(b => b.classList.toggle('on', b.dataset.t === k));
  document.querySelectorAll('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + k));
}};
tabs.forEach(b => b.addEventListener('click', () => show(b.dataset.t)));
if (tabs.length) show(tabs[0].dataset.t);

const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase();
  calc.hidden = true;
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
    print(f"{total} 品項 / {len(cats)} 分類 / {covered} 筆有價格（含試算） → {OUT}")


if __name__ == "__main__":
    main()
