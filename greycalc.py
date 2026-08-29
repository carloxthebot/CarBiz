#!/usr/bin/env python3
"""greycalc.py — compute the 水貨到岸試算 (parallel-import landed cost) block and
write it into data/prices-local.json under "grey".

Everything here is ARITHMETIC on sourced inputs, never a quote. It lives in its
own script so the numbers on the page can be re-derived and audited rather than
typed in by hand.

Inputs, all captured 2026-08-29 and recorded per SKU below:
  item     RHDJapan's item price
  freight  RHDJapan's ACTUAL cart quote to Kuala Lumpur
Item price and freight must come from the SAME exporter -- Black Hawk Japan is
cheaper on 13 of these SKUs, but its freight was never quoted, and pairing one
shop's price with another's shipping would be a number that exists nowhere.

Singapore freight for the coilover band is a measured RHDJapan cart quote to a
Singapore address on a comparable coilover box, not the same SKU -- roughly 50%
above the Kuala Lumpur figure, so reusing KL there would have understated it.

Freight to Hong Kong: Japan Post Zone 2 covers HK/SG/TH/MY at identical rates,
but these parcels exceed postal limits and go by courier, where HK is a slightly
cheaper zone. Where a UPS published-rate ratio was measured for the weight band,
it is applied; otherwise HK reuses the KL figure, which OVERSTATES Hong Kong by
up to ~8%. Erring against the cheapest market is the safe direction.

Tax treatment per destination, from each customs authority:
  HK  no duty on general goods, no GST/VAT. The import declaration charge on a
      HK$10,000-60,000 consignment is HK$0.20-2.00 -- rounds to nothing.
  SG  9% GST on CIF, but CIF <= S$400 by air or post is relieved entirely; over
      that, a TradeNet permit fee of S$3.19 applies.
  TH  30% MFN on the HS 8708 lines, then 7% VAT on CIF + duty. No de minimis
      since 2026-01-01.
  MY  30% MFN for a private consignee who cannot furnish a Form AJ, then 10%
      SST. CIF <= RM500 by air courier is exempt from both.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "data", "prices-local.json")

# code: (RHDJapan item ¥, freight to KL ¥, freight to HK ¥ or None, freight to SG ¥ or None)
# None means "reuse the Kuala Lumpur quote", which is the honest fallback: Japan
# Post Zone 2 covers all four at one rate, and the couriers differ by a few
# percent between these zones.
SKUS = {
    "92467": (124_289, 10_423, 10_165, 15_512),  # DAMPER ZZ-R ~25kg; HK via UPS ratio 0.975,
                                                 # SG measured on a comparable coilover box
    "98208": (218_559, 14_800, None, 15_512),    # ZZ-R BB DSC Plus ~30kg; same SG coilover band
    "86104": (363_579, 18_954, None, None),      # BIG CALIPER KIT II front, 15kg
    "63199": (131_679, 36_579, 33_525, None),    # NUR-SPEC, 150cm long box; HK via UPS ratio 0.916
    "55301": (17_559, 2_830, None, None),        # SUCTION KIT, ~2kg
    "96133": (14_839, 3_353, None, None),        # STRUT TOWER BAR front
    "96101": (14_839, 3_353, None, None),        # STRUT TOWER BAR rear, same price and box
}


def landed(item, freight, rates):
    """CIF -> landed cost in JPY for each destination."""
    out = {}
    for cc in ("HK", "SG", "TH", "MY"):
        cif = item + freight[cc]
        if cc == "HK":
            out[cc] = cif                                  # no duty, no GST
        elif cc == "SG":
            # The low-value test is the ITEM's sales value with shipping excluded
            # -- Singapore Customs' own example: an S$395 item with S$25 shipping
            # is an S$395 sale. Above it, GST is charged on the full CIF.
            if item <= 400 * rates["SGD"]:
                out[cc] = cif                              # air/post relief
            else:
                out[cc] = cif * 1.09 + 3.19 * rates["SGD"]  # GST + TradeNet permit
        elif cc == "TH":
            out[cc] = cif * 1.30 * 1.07                    # 30% duty, then 7% VAT
        elif cc == "MY":
            # Malaysia's de minimis is on CIF, unlike Singapore's.
            out[cc] = cif if cif <= 500 * rates["MYR"] else cif * 1.30 * 1.10
    return out


def main():
    d = json.load(open(LOCAL))
    rates = d["meta"]["rates"]          # JPY per 1 unit of local currency
    cur = {"HK": "HKD", "SG": "SGD", "TH": "THB", "MY": "MYR"}
    grey = {}
    for code, (item, kl, hk, sg) in SKUS.items():
        freight = {"MY": kl, "TH": kl, "HK": hk or kl, "SG": sg or kl}
        for cc, jpy in landed(item, freight, rates).items():
            note = (f"日本出口通路 RHDJapan 品項 ￥{item:,} ＋ 運費 ￥{freight[cc]:,}"
                    f" ＝ CIF ￥{item + freight[cc]:,}，加當地關稅與稅金後 ￥{jpy:,.0f}。"
                    "此為依已查證數字的計算，非任何業者報價。")
            grey.setdefault(code, {})[cc] = {"amount": round(jpy / rates[cur[cc]]), "note": note}
    d["grey"] = grey
    json.dump(d, open(LOCAL, "w"), ensure_ascii=False, indent=2)
    print(f"{len(grey)} 個 SKU × 4 地 → grey")
    for code in SKUS:
        row = " / ".join(f"{cc} ￥{grey[code][cc]['amount'] * rates[cur[cc]]:,.0f}"
                         for cc in ("HK", "SG", "TH", "MY"))
        print(f"  {code}  {row}")


if __name__ == "__main__":
    main()
