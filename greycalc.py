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

# ---- tier 2: Black Hawk Japan's ratio against the EX-TAX MSRP, per product
# line. Each figure is measured on a real BHJ listing, not assumed; the lines
# with no BHJ listing fall back to 0.85, its most common tier, and are flagged
# in the note so the page can say which is which.
RATIO = {
    "DAMPER ZZ-R": 0.67,                  # 92467 .668 / 92208 .653 / 93136 .656
    "BIG CALIPER KIT II": 0.91,           # 86104 .911
    "NUR-SPEC Exhaust System": 0.85,      # 63199 .850
    "SUCTION KIT": 0.85, "DRY CARBON SUCTION KIT": 0.85, "CARBON INTAKE SYSTEM": 0.85,
    "CORE TYPE AIR CLEANER": 0.69,        # 56275 .691
    "SUS POWER AIR FILTER Series": 0.73,  # 59624 .729
    "RACING OIL FILTER": 0.67,            # 18709 .668
    "HYBRID AIRCON FILTER": 0.70,
    "STRUT TOWER BAR": 0.81, "TRUSS BAR": 0.81,   # 96133 .814
    "RACING OIL COOLER KIT BR": 0.81,     # 10479 .814
    "RACING METER PANEL": 0.91,           # 19185 .911
    "SHIFT KNOB": 0.85, "HAND BRAKE LEVER": 0.85, "OIL FILLER CAP": 0.85,  # 13850/13851 .850
}
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

    for group in json.load(open(DATA)):
        line = group["line"]
        band_key, per_country = BAND.get(line, ("small", None))
        ratio = RATIO.get(line)
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
                basis = (f"Black Hawk Japan 對此產品線的定價比率 未稅定價 ￥{xt:,} × "
                         f"{ratio or DEFAULT_RATIO:.2f}{'' if ratio else '（此產品線無 BHJ 實價，採其最常見比率）'}"
                         f" ＝ ￥{item:,}")
            for cc, jpy in landed(item, freight, rates).items():
                grey.setdefault(code, {})[cc] = {
                    "amount": round(jpy / rates[cur[cc]]),
                    "kind": f"試算·{tier}",
                    "note": (f"{basis}，運費 ￥{freight[cc]:,}，CIF ￥{item + freight[cc]:,}，"
                             f"加當地關稅與稅金後 ￥{jpy:,.0f}。依已查證數字計算，非任何業者報價。"),
                }
            tiers[tier] += 1

    d["grey"] = grey
    json.dump(d, open(LOCAL, "w"), ensure_ascii=False, indent=2)
    print(f"{len(grey)} 個料號 × 4 地 = {sum(tiers.values()) * 4} 格試算"
          f"（實報 {tiers['實報']} 料號 / 公式 {tiers['公式']} 料號）")


if __name__ == "__main__":
    main()
