#!/usr/bin/env python3
"""scrape.py — pull the BLITZ parts-navigator listing for the GR86 (ZN8) and
write it to data/blitz-gr86-zn8.json.

The source is BLITZ's own 商品検索システム, queried for maker=Toyota, car=GR86,
model=ZN8, model_year=2024, with every product category selected. Re-run it to
refresh; the page is server-rendered, so no browser is needed.

One markup trap, and it is the whole reason this file exists: the results table
does NOT wrap each product in its own `.row`. A product line opens a single
`<div class="row">` and every row after the first follows as flat sibling
`<div class="td ...">` cells. Splitting on `.row` finds 41 of the 110 products
and looks perfectly correct while doing it. The real row boundary is
`td td_model first`.
"""
import html, json, os, re, sys, urllib.request

URL = ("https://partsnavi.blitz.co.jp/products/search/search_car/list.php"
       "?maker_id=1&car_name_first=1&car_name=GR86&car_model=ZN8&model_year=2024"
       + "".join(f"&category_id%5B%5D={c}" for c in
                 [1, 24, 34, 2, 19, 3, 21, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 35]))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "blitz-gr86-zn8.json")


def clean(s):
    s = re.sub(r"<br\s*/?>", " | ", s)          # BLITZ uses <br> as a field separator
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def parse(page):
    groups = []
    for part in re.split(r'<div class="hs-accordion active mb-\[5px\]" id="item_\d+_btn">', page)[1:]:
        m = re.search(r'<span class="font-semibold tracking-wider">\s*(.*?)\s*</span>', part, re.S)
        line = clean(m.group(1)) if m else "?"
        items = []
        for chunk in re.split(r'<div class="td td_model first">', part)[1:]:
            def td(cls):
                mm = re.search(r'<div class="td %s[^"]*">(.*?)</div>' % cls, chunk, re.S)
                return clean(mm.group(1)) if mm else ""
            items.append({
                "vehicle": clean(chunk.split("</div>")[0]),
                "name": td("td_name"), "year": td("td_year"), "model": td("td_type"),
                "engine": td("td_engine"), "price": td("td_price"), "code": td("td_code"),
                "note1": td("td_note_1"), "note2": td("td_note_2"),
            })
        if items:
            groups.append({"line": line, "items": items})
    return groups


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    groups = parse(page)
    total = sum(len(g["items"]) for g in groups)
    # The listing has been 42 lines / 110 items since 2026-08-29. A sudden drop
    # means the markup moved again, not that BLITZ discontinued everything --
    # fail loudly instead of committing a half-empty page.
    if total < 80:
        sys.exit(f"scrape: only {total} items parsed (expected ~110) — markup probably changed")
    json.dump(groups, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"{len(groups)} 產品線 / {total} 品項 → {OUT}")


if __name__ == "__main__":
    main()
