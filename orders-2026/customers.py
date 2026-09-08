#!/usr/bin/env python3
"""Customer de-identification + product-name cleanup.

The ledger's 品名 field mixes three things: the product, who it is for, and
free-form notes. This module pulls the people out (replacing them with stable
codes C01…) and leaves a clean product name behind.

Names were confirmed by eye from the paren-content frequency list; anything not
on the list — 前下, WR BLUE, zd8用, MACHINING Ver — is a spec, not a person, and
must survive intact. Two traps this handles explicitly:

  * `GS-FUJI` is a TWS wheel finish code, not the customer FUJI.
  * `(皓.土.陽+菁*1+豆腐2+預備)` is a per-person quantity split; deleting the
    names one by one leaves `1+2+預備`, so a paren group that is mostly names
    gets dropped whole.
"""
import re

CUSTOMERS = [
    "桃園政昌", "李小緯", "惟恩", "皓哥", "藤井", "宏沅", "駿達", "漢特", "聖陽",
    "政昌", "中壢", "FUJI", "豆腐", "菁", "均", "皓", "土", "陽",
]

# Fixed codes so the page is stable across rebuilds.
CODE = {name: f"C{i:02d}" for i, name in enumerate(
    ["藤井", "宏沅", "政昌", "駿達", "皓哥", "漢特", "聖陽",
     "李小緯", "中壢", "FUJI", "惟恩", "豆腐", "菁", "均", "土", "陽"], start=1)}
CODE["桃園政昌"] = CODE["政昌"]   # same person, with a location prefix
CODE["皓"] = CODE["皓哥"]         # short form

# Spec strings that merely contain a customer substring and must be protected.
PROTECT = [r"GS-FUJI"]

NAME_RE = re.compile("|".join(re.escape(n) for n in sorted(CUSTOMERS, key=len, reverse=True)))
PROTECT_RE = re.compile("|".join(PROTECT), re.I)
SEP = r"[\s.。、,，+*/&＋・]"


def _codes_in(text: str) -> list[str]:
    out, seen = [], set()
    for m in NAME_RE.finditer(text):
        c = CODE[m.group(0)]
        if c not in seen:
            seen.add(c); out.append(c)
    return out


def extract(name: str) -> tuple[str, list[str]]:
    """-> (product name with people removed, [customer codes], sorted)"""
    text = name or ""

    # 1. mask protected spec strings so they survive the name sweep
    masks: list[str] = []
    def _mask(m):
        masks.append(m.group(0))
        return f"\x00{len(masks)-1}\x00"
    text = PROTECT_RE.sub(_mask, text)

    found = _codes_in(text)

    # 2. drop paren groups that are essentially a name list (the split-cost case)
    def _group(m):
        inner = m.group(1)
        stripped = NAME_RE.sub("", inner)
        # mostly names + separators/digits left over -> the group was a name list
        if _codes_in(inner) and len(re.sub(rf"{SEP}|\d|預備", "", stripped)) <= 2:
            return " "
        return m.group(0)
    text = re.sub(r"[(（]([^)）]*)[)）]?", _group, text)

    # 3. remove any remaining bare names
    text = NAME_RE.sub("", text)

    # 4. tidy the wreckage
    text = re.sub(r"[(（]\s*[)）]?", " ", text)
    text = re.sub(r"[)）]", " ", text)
    text = re.sub(rf"(?:{SEP}*[-–]{SEP}*)+$", "", text)
    text = re.sub(r"[.。、+*@]{2,}", " ", text)
    text = re.sub(r"^[\s.,、+*@\-]+|[\s.,、+*@\-]+$", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 5. restore protected strings
    for i, orig in enumerate(masks):
        text = text.replace(f"\x00{i}\x00", orig)
    return text, sorted(found)
