# Reference data

Research that took real effort to gather and that the builders depend on.
Keep it here rather than in a chat log, and cite it from `parts.js` notes.

## `jb74-wheel-atlas.json`

Every Japanese and Taiwanese aftermarket wheel that physically fits a JB74,
compiled 2026-09-21 — 117 entries across 30-odd makers, each with the sizes
and offsets that fit, finishes, what the centre cap does, price, and a
paragraph of modelling cues (spoke count and shape, face profile, lip, fake
bolts, where the branding sits). Grouped by `face` so one piece of geometry
serves a family: `round`, `slot`, `spoke`, `mesh`, `dish`, `beadlock`.

Four things in `rules` change how the configurator has to be built:

- **Hub bore is not a constant.** Larger than 108.1 fits (it seats on the
  tapered nuts); smaller cannot fit at all and no ring corrects it. Published
  bores run 108.2 (Enkei) to 110.5 (Hayashi, BRADLEY, older Weds).
- **Exposed lug nuts are the default.** PCD 139.7 puts the nuts at r = 69.9,
  beyond the reach of a typical 108–110 mm cap. Only five wheels here cover
  them; APIO Ventura and SR+ need two face states.
- **Offset −5 or deeper protrudes past the fender**, hence `needsFlares` on
  the catalogue entries. +20/+22 is the kei JB64 fitment and tucks in.
- **16×6.5J and 16×7J barely exist** in 5×139.7, and genuine 15×5.5J is
  rarer still — most 15-inch options are 6.0J.

`corrections` records names that turn out not to exist or not to fit (BRAID,
XJ06, APACHE II, FDX F7, the "DAMD little D wheel"), so nobody re-researches
them. Source artifact: <https://claude.ai/artifact/VARATv6R47Xn2ucasL2XSe>

Prices are maker list unless the entry says otherwise; Japanese street runs
60–70% of list for cast wheels, and Taiwanese sellers add roughly 40–70% on
top of Japanese list.
