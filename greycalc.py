#!/usr/bin/env python3
"""greycalc.py — compute the 水貨到岸試算 (parallel-import landed cost) for every
SKU and write it into data/prices-local.json under "grey".

Everything here is ARITHMETIC on sourced inputs, never a quote. It lives in its
own script so the numbers on the page can be re-derived and audited rather than
typed in by hand.

Two tiers of estimate, and the page labels every cell with which one it is:

  實報  Both inputs are real quotes: RHDJapan's item price and RHDJapan's actual
        cart freight, captured 2026-08-29. Seven SKUs.
  公式  The item price comes from Black Hawk Japan's pricing formula and the
        freight from a published carrier rate for the SKU's size band. Everything
        else. Black Hawk prices its BLITZ range off a clean multiple of the
        ex-tax MSRP -- measured on 13 SKUs and reproduced to within a percent --
        so applying it to the rest of the catalogue is interpolation inside a
        known rule, not a guess about a shop's behaviour.

Item price and freight must come from the SAME channel. Black Hawk never quotes
freight, so the 公式 tier pairs its price with a published carrier rate rather
than with RHDJapan's negotiated one; that overstates freight slightly, which is
the safe direction.

Tax treatment per destination, from each customs authority:
  HK  no duty on general goods, no GST/VAT. The import declaration charge on a
      HK$10,000-60,000 consignment is HK$0.20-2.00 -- rounds to nothing.
  SG  9% GST on CIF, but an item whose sales value (shipping excluded) is
      S$400 or less and travels by air or post is relieved entirely; over that,
      a TradeNet permit fee of S$3.19 applies. No relief by sea or land.
  TH  30% MFN on the HS 8708 lines, then 7% VAT on CIF + duty. No de minimis
      since 2026-01-01.
  MY  30% MFN for a private consignee who cannot furnish a Form AJ, then 10%
      SST. CIF <= RM500 by air courier is exempt from both.

What this does NOT model: courier clearance/handling fees in HK and SG (no
sourced figure), UPS fuel surcharge, volumetric weight on the courier bands
(a 120x40x40 box bills as 38.4 kg, so the coilover and exhaust numbers are
floors), and Thailand's HS classification for caliper assemblies, which is
assumed to sit at the 30% upper bound.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "data", "prices-local.json")
DATA = os.path.join(HERE, "data", "blitz-gr86-zn8.json")

# ---- tier 1: measured. (RHDJapan item ¥, freight KL, freight HK, freight SG) --
MEASURED = {
    "92467": (124_289, 10_423, 10_165, 15_512),
    "98208": (218_559, 14_800, None, 15_512),
    "86104": (363_579, 18_954, None, None),
    "63199": (131_679, 36_579, 33_525, None),
    "55301": (17_559, 2_830, None, None),
    "96133": (14_839, 3_353, None, None),
    "96101": (14_839, 3_353, None, None),
}

# ---- tier 2: Black Hawk Japan's ratio against the EX-TAX MSRP ----------
# The ratio is not a judgement call and it is not hard-coded: it is DERIVED here
# from Black Hawk Japan's actual listed prices, captured 2026-08-29, divided by
# the ex-consumption-tax MSRP that scrape.py already holds for the same part
# number. BHJ prices its BLITZ range off a clean multiple per product family --
# that is what made this possible -- so the observations below pin a ratio for
# each family, and a family with no observation says so on the page.
OBSERVED = {                 # BLITZ code -> Black Hawk Japan listed price, JPY
    "92467": 124_901, "92208": 146_942, "93136": 185_682, "98467": 206_934,
    "98208": 233_165, "92599": 180_338,          # DAMPER ZZ-R
    "96133": 14_238, "96101": 14_238, "96800": 15_052,   # bars
    "63199": 119_011, "63199V": 127_511,          # NUR-SPEC
    "86104": 355_212, "86105": 255_023,           # BIG CALIPER KIT II
    "55301": 17_002,                              # SUCTION KIT
    "56275": 26_959,                              # CORE TYPE AIR CLEANER
    "59624": 4_736,                               # SUS POWER AIR FILTER
    "18709": 2_204,                               # RACING OIL FILTER
    "10479": 89_501,                              # OIL COOLER KIT BR
    "13851": 11_901, "13850": 5_950, "13852": 6_375,     # interior
    "19185": 27_323,                              # RACING METER PANEL
}
# Families BHJ does not list are given the modal observed ratio rather than an
# invented one, and every such cell says on the page that it was borrowed.
DEFAULT_RATIO = 0.85

# ---- freight bands. Published Japan Post Zone 2 rates (identical for all four
# destinations) unless the band is too big or too long for the post, where the
# measured RHDJapan courier quote stands in.
BAND_SMALL = 2_660      # 小形包装物 航空, <=2kg -- filters, knobs, caps, electronics
BAND_MED = 7_300        # 国際小包 航空 5kg -- boxed intake kits, adapters, panels
BAND_HEAVY = 18_954     # measured courier quote, ~15kg -- coolers, radiators, calipers
BAND = {
    "DAMPER ZZ-R": ("coilover", {"TH": 10_423, "MY": 10_423, "HK": 10_165, "SG": 15_512}),
    "NUR-SPEC Exhaust System": ("exhaust", {"TH": 36_579, "MY": 36_579, "HK": 33_525, "SG": 36_579}),
    "BIG CALIPER KIT II": ("heavy", None),
    "RACING RADIATOR TypeZS": ("heavy", None), "RACING OIL COOLER KIT BR": ("heavy", None),
    "AERO SPEED": ("exhaust", None),       # FRP body panels: bulky, courier-only, same band
    "CARBON INTAKE SYSTEM": ("med", None), "SUCTION KIT": ("med", None),
    "DRY CARBON SUCTION KIT": ("med", None), "CORE TYPE AIR CLEANER": ("med", None),
    "RACING RADIATOR HOSE KIT": ("med", None), "RACING METER PANEL": ("med", None),
    "STRUT TOWER BAR": ("med", None), "TRUSS BAR": ("med", None),
    "SUSPENSION ARM": ("med", None), "ENGINE HOOD DAMPER": ("med", None),
    "HAND BRAKE LEVER": ("med", None), "BIG CALIPER KIT II ": ("heavy", None),
}
FLAT = {"coilover": None, "exhaust": None, "heavy": BAND_HEAVY, "med": BAND_MED, "small": BAND_SMALL}


def ex_tax(price):
    """'￥205,700 | (￥187,000)' -> 187000, the ex-consumption-tax MSRP."""
    n = [int(x.replace(",", "")) for x in re.findall(r"￥([\d,]+)", price or "")]
    return n[1] if len(n) > 1 else (round(n[0] / 1.1) if n else None)


def ratios(groups):
    """Per-product-line ratio, averaged over whatever BHJ actually lists there.
    Returns {line: (ratio, [evidence strings])}."""
    seen = {}
    for g in groups:
        for it in g["items"]:
            bhj = OBSERVED.get(it["code"])
            xt = ex_tax(it["price"])
            if bhj and xt:
                seen.setdefault(g["line"], []).append((it["code"], bhj, xt, bhj / xt))
    return {line: (sum(r for *_, r in obs) / len(obs), obs) for line, obs in seen.items()}


def landed(item, freight, rates):
    out = {}
    for cc in ("HK", "SG", "TH", "MY"):
        cif = item + freight[cc]
        if cc == "HK":
            out[cc] = cif
        elif cc == "SG":
            out[cc] = cif if item <= 400 * rates["SGD"] else cif * 1.09 + 3.19 * rates["SGD"]
        elif cc == "TH":
            out[cc] = cif * 1.30 * 1.07
        elif cc == "MY":
            out[cc] = cif if cif <= 500 * rates["MYR"] else cif * 1.30 * 1.10
    return out


def main():
    d = json.load(open(LOCAL))
    rates = d["meta"]["rates"]
    cur = {"HK": "HKD", "SG": "SGD", "TH": "THB", "MY": "MYR"}
    grey, tiers = {}, {"實報": 0, "公式": 0}
    groups = json.load(open(DATA))
    derived = ratios(groups)

    for group in groups:
        line = group["line"]
        band_key, per_country = BAND.get(line, ("small", None))
        ratio = derived.get(line, (None, None))[0]
        for it in group["items"]:
            code, xt = it["code"], ex_tax(it["price"])
            if not xt:
                continue
            if code in MEASURED:
                item, kl, hk, sg = MEASURED[code]
                freight = {"TH": kl, "MY": kl, "HK": hk or kl, "SG": sg or kl}
                tier, basis = "實報", f"RHDJapan 實際購物車報價：品項 ￥{item:,}"
            else:
                item = round(xt * (ratio or DEFAULT_RATIO))
                f = per_country or ({c: FLAT[band_key] for c in cur} if FLAT[band_key]
                                    else BAND["DAMPER ZZ-R"][1] if band_key == "coilover"
                                    else BAND["NUR-SPEC Exhaust System"][1])
                freight = {c: f[c] for c in cur}
                tier = "公式"
                if ratio:
                    ev = derived[line][1]
                    src = "、".join(f"{c} 上架價 ￥{b:,} ÷ 未稅定價 ￥{x:,} ＝ {r:.3f}"
                                   for c, b, x, r in ev[:2])
                    how = (f"比率 {ratio:.2f} 由本產品線 {len(ev)} 筆 Black Hawk Japan 實際上架價推得"
                           f"（{src}{'…' if len(ev) > 2 else ''}）")
                else:
                    how = (f"此產品線 Black Hawk Japan 沒有上架，無實價可推，"
                           f"借用觀測到最常見的比率 {DEFAULT_RATIO:.2f}")
                basis = f"{how}；未稅定價 ￥{xt:,} × {ratio or DEFAULT_RATIO:.2f} ＝ ￥{item:,}"
            for cc, jpy in landed(item, freight, rates).items():
                grey.setdefault(code, {})[cc] = {
                    "amount": round(jpy / rates[cur[cc]]),
                    "kind": f"試算·{tier}",
                    "note": (f"{basis}，運費 ￥{freight[cc]:,}，CIF ￥{item + freight[cc]:,}，"
                             f"加當地關稅與稅金後 ￥{jpy:,.0f}。依已查證數字計算，非任何業者報價。"),
                }
            tiers[tier] += 1

    d["grey"] = grey
    # Publish the derivation alongside the numbers. Written from here rather than
    # kept as prose in the JSON so the page can never quote a ratio the maths no
    # longer uses.
    d.setdefault("greyNote", {})["ratioTable"] = {
        "head": ["產品線", "比率", "怎麼推得的"],
        "rows": [[line, f"×{r:.3f}",
                  "、".join(f"{c} ￥{b:,} ÷ ￥{x:,}" for c, b, x, _ in obs)]
                 for line, (r, obs) in sorted(derived.items(), key=lambda kv: -kv[1][0])]
        + [["（其餘產品線）", f"×{DEFAULT_RATIO:.2f}", "BHJ 未上架，借用觀測到最常見的比率"]],
    }
    json.dump(d, open(LOCAL, "w"), ensure_ascii=False, indent=2)
    print(f"{len(grey)} 個料號 × 4 地 = {sum(tiers.values()) * 4} 格試算"
          f"（實報 {tiers['實報']} 料號 / 公式 {tiers['公式']} 料號）")
    print("由 BHJ 實價推得的產品線比率：")
    for line, (r, obs) in sorted(derived.items(), key=lambda kv: -kv[1][0]):
        print(f"  ×{r:.3f}  {line:30} （{len(obs)} 筆）")


if __name__ == "__main__":
    main()
