# Handover — Jimny JB74 configurator

Written 2026-09-24, at the end of a session that ran out of web-search budget.
A fresh session has a fresh budget; the list at the bottom is what to spend it
on. Everything described here is committed, pushed and live.

Live: <https://carloxthebot.github.io/CarBiz/jimny/app.html>
Catalogue: <https://carloxthebot.github.io/CarBiz/jimny/parts.html>
Current build: **202609241340** · 239 catalogue entries · 7 styles

---

## 1. How this project works

**The rule that matters most: no number goes in without a first-party source.**
The catalogue's whole value is that its prices, part numbers and dimensions are
real. `uncertain: true` and an honest "官網未公布" beat a plausible guess every
time. When a maker's page contradicts what we wrote, that contradiction is the
finding — say it plainly in the note rather than quietly correcting.

The same applies to geometry: **measure the model before drawing a part.**
Raycast it through `window.__jimny` (see `blender/probe.mjs` for the pattern)
and put the measurements in the docstring. Several parts in here were redrawn
three or four times because the first version was drawn from memory of a photo.

### The loop

```sh
python3 -m http.server 8899 -d .      # in another shell, for every tool below
./build.sh                             # Blender → model/parts.glb + rims.glb, then spec_gate
./stamp.sh                             # new build id into app.html (cache busting)
git add -A jimny && git commit && git push
# then WAIT for Pages and verify on the LIVE url, desktop AND iPhone emulation
```

`./build.sh` refuses to continue on a Blender traceback (Blender exits 0 even
when the script raised, so it greps the log) and gates on
`blender/spec_gate.py`, which measures every part against
`tools/calib/specs.json`.

**A deploy is not done until you have checked the live URL yourself** — build
id, zero page errors, on both a desktop viewport and an iPhone one. Headless
Chrome via `playwright-core`, `--use-angle=swiftshader
--enable-unsafe-swiftshader`. Scripts must be written inside the repo root to
resolve `playwright-core`; write them as `./_x.mjs` and `rm` them after.

Two headless gotchas that have cost real time: `page.screenshot({clip})`
returns **stale** frames while the main thread is blocked (use full-page), and
rAF is starved between `p.evaluate` calls (spin your own rAF loop in-page).
Also `page.click()` times out under swiftshader — use
`p.evaluate(() => el.click())`.

### Working conventions

- Code comments and commit messages in English; chat replies to the owner in
  Traditional Chinese with full-width punctuation, verdict first.
- Commits end with the `Co-Authored-By:` and `Claude-Session:` lines.
- This repo is **public**. Makers' product photos are their copyright — only
  our own renders ship. Real photos stay behind the 看產品頁 link.
- The CC BY 4.0 credit for the base model stays on the page.
- Never mix `~/Personal` with `~/Projects`; secrets only in gitignored
  `bot/.env`.

### File map

| file | what it is |
|---|---|
| `app.html` | the whole configurator: markup, CSS, and the module that drives it |
| `parts.js` | the catalogue — every family, plus `validate()` and `STYLES` |
| `rig.js` | loads the body GLB, hides stock parts, applies ride height and paint |
| `accessories.js` | clones a named node out of `parts.glb` |
| `wheels.js` | builds wheels procedurally per size/offset/tread |
| `fx.js` | currency conversion (`toTWD`), rates are deliberately rough |
| `blender/build_parts.py` | every accessory, ~3000 lines, one function per part |
| `blender/lib.py` | `sweep` `loft` `tube` `box` `prism` `text` `cylinder` |
| `tools/styleshots.mjs` | one render per style, for the style cards |
| `tools/partshots.mjs` | one render per catalogue part, for the hover cards |
| `tools/bootcar.py` | the loading screen's grille drawing |
| `docs/*.json` | research output — see §4 |

**Car frame**: millimetres, +Y up, +Z forward, +X = vehicle LEFT (`RIGHT = -1`).
`lib.P(x,y,z) = Vector((x*MM, -z*MM, y*MM))`.

**Sweep frames parallel-transport**, so a profile's axes turn with the path:
running UP the A-pillar `u` is car X and `v` is fore-aft; running FORWARD along
a fender `u` becomes width across the car. Handing both the same numbers made a
snorkel's skirt come out as a tall thin fin.

---

## 2. What is live

**Seven styles**, each a preset applied from the first step. They are pushed
apart on silhouette — height, roof load, arch width, wheel size — not on which
bumper they wear, because five cars differing by bumper alone read the same
from ten metres.

| style | height | what makes it read differently |
|---|---|---|
| 都會寬體低趴 `street_low` | 1690 | the only one below stock; 18" rims, 55-series |
| 都會輕改 `city` | 1755 | bare roof, low black pinstripe |
| 日系復古 `jp_retro` | 1805 | sand body, three-band retro stripe, steel look |
| 軍風 `military` | 1910 | white star and stencils, loaded window guards |
| 露營 `camp` | 1915 | two-tone roof, body lift, four orange bands |
| 外掛籠硬派 `exo_cage` | 1965 | roll cage over the roof, nothing else up there |
| 澳洲越野 `au_offroad` | 2125 | tallest, 31s, lit roof rack, snorkel |

Also live: the style step itself (first visit lands on it, then remembered in
`localStorage`; the tab keeps score — "澳洲越野・改 3"); style cards carrying a
real render; five side-stripe sets and the military stencil markings; the RV4
Wild Goose outer roll cage; the boot screen drawn as the JB74 grille; the sheet
that opens by dragging up and closes only via the ✕ (a downward swipe is how
LINE's and Facebook's in-app browsers dismiss themselves).

**The owner does not want regulation treated as a gate** — "改裝界會另外處理".
A lift advisory was added and then removed on that instruction. Do not put
legality back in front of the buyer. (The research is still in
`docs/jb74-archetypes.json` under `taiwanRegulation` if it is ever wanted; the
one clause verified first-hand from the official PDF is 附件十五 三、底盤:
「懸吊系統之避震器｜變更後不得超過原核定車身高度」.)

---

## 3. What to build next — the owner said 都做

Three archetypes remain from `docs/jb74-archetypes.json`. Each entry there
carries `silhouette`, `signature`, `parts` (ids verified to exist) and
`missing`.

### 3a. 美式方頭換臉 `bronco_face`
The only one that is unrecognisable as a Jimny from the front. Needs a face
set: round headlamp assemblies, a wide grille with raised lettering, a
body-coloured deep bumper, a silver skid plate. GARAGE ILL's BRON55 is the
reference product — ¥264,000 halogen / ¥297,000 LED, 税抜, supplied unpainted.
Also needs a "painted in the body colour" option for bumpers, which the
accessory pipeline does not have yet (`buildAccessory` already swaps any
material named `BodyPaint`, so the hook exists).

### 3b. 皮卡工作車 `work_truck`
The only one that changes the body itself: everything behind the B-pillar
removed and replaced with a steel bed with drop sides, plus a cab-back hoop.
Biggest modelling job here, and it needs the page to hide a large part of the
body — `rig.js` already has that mechanism (`stockQuarter` / `cfg.hideQuarterGlass`
is the pattern to copy).

### 3c. 歐系拉力寬體 `euro_rally`
Four round headlamps in a row, blistered wide fenders, a roof spoiler, twin
white stripes running front-to-back over the bonnet and roof, red paint. Note
three catalogue gaps it exposes: `COLORS` has no red, `STRIPES` are all
belt-line and none run longitudinally, and `TYRE_MODELS` has no road pattern at
all — twelve entries and every one is A/T, R/T or M/T.

### Also outstanding
- **True wide-body fenders.** `flares` today is a rivet trim on the stock arch
  and does not widen the car. 都會寬體低趴 and 歐系拉力寬體 both want real
  blistered over-fenders.
- **`street18` is a class entry, not a product** — 18×7.0J −20 with a null
  price. First job with a search budget: find a real 17–18" wheel sold for the
  JB74 and replace it.
- **The KLC lowering spring's JB74 figure.** KLC publish ~40 mm for the JB64
  only; the entry says so and estimates. Worth confirming with KLC.

---

## 4. Research already done — read before searching

| file | what is in it |
|---|---|
| `docs/jb74-jp-gapfill.json` | **88 entries, and the big one.** Corrections to the catalogue from the Japanese makers' own pages: wrong chassis, dead part numbers, stale prices, narrower model-year ranges. **Roughly 60 of these are still unapplied** — see below. |
| `docs/jb74-complete-kits.json` | 53 Japanese complete kits (DAMD, AIMGAIN, LIBERTY WALK, KUHL, WALD…) with first-party prices |
| `docs/jb74-archetypes.json` | 6 accepted archetypes, 11 rejected with reasons, plus the Taiwan regulation dossier |
| `docs/jb74-stripes.json` | 26 stripe treatments with modelling geometry; the `modellingNotes` block (three vertical slots, six rear terminations) is the useful part |
| `docs/jb74-graphics.json` | 10 graphic styles with Taiwanese marketplace prices and the 變更登記 answer |
| `docs/jb74-chrome-damd.json` | **may not exist yet** — an agent was writing it when the session ended. Chrome parts + DAMD's full JB74 line. Check for it first. |
| `docs/jb74-snorkels.json`, `jb74-wheel-atlas.json`, `jb74-fitment.json`, `jb74-accessory-atlas.json` | earlier dossiers |

### The unapplied corrections backlog

`docs/jb74-jp-gapfill.json` lists ~70 corrections. Applied so far: the KLC
bumpers, SHOWA GARAGE's front and rear, the JAOS side step, SG 75, the JAOS
roof rack. **The rest are still sitting there**, including entries that would
sell a JB74 owner something that does not fit:

- `wildboar16` / `xtremej` / `bradley` / `te37xt` — all four carry JB64 offsets;
  JB74 needs a different row of each maker's size table
- `apio_guard` — is a JB74 part, but cannot be fitted alongside the factory
  over-fenders, which a standard JB74 has
- `prostaff_minig` — sourced only to a JB64 listing
- ~20 stale or wrong prices (`apio20` ¥126,500 → ¥141,900; `taniguchi_bar` and
  `taniguchi_short` quote one side only; `ipf` double-counts about ¥95,000)
- ~6 entries whose model-year range is narrower than the catalogue implies

Work through them the same way: open the maker's page, confirm, then edit.
Do not batch-apply from the JSON without checking — that file is one agent's
reading, and two of its claims turned out to need correcting when checked
(SHOWA's E00990 is a bracket set, not the bumper; KLC's Traditional pair is
fine and only the Nostalgic pair is JB64-only).

---

## 5. Spend the search budget on these

1. A real 17–18" wheel for the JB74, to replace the `street18` class entry.
2. GARAGE ILL BRON55 and any other JB74 face-swap kit — part numbers, prices,
   and above all photographs clear enough to model the grille and lamps from.
3. Blistered wide-body over-fenders for the JB74: who makes them, how much
   width per side, and whether they bolt on or need the arch cut.
4. A road-pattern tyre for `TYRE_MODELS` — the list has no highway tread.
5. Red, and any colour outside Suzuki's eight, for the rally style. This means
   respray or wrap, so the entry has to be honest that it is not a factory code.
6. Whatever `docs/jb74-chrome-damd.json` turns out to be missing: mirror-polished
   stainless bumpers, chrome grilles, chrome mirror caps, chrome headlamp
   bezels, and DAMD's full JB74 line beyond the complete kits.

---

## 6. Things that will bite you

- **`S.bodyLift` is decorative.** `validate()` and the rig read the body-lift
  figure off the LIFT entry's own `body` field, not off `S.bodyLift`. A style
  wanting a body lift must choose a kit that carries one (`sg50bl`, `combo100`).
- **White letters switch themselves off.** `owl: true` on a tyre size that the
  tread has no OWL for is silently dropped, and the style then reports a
  phantom "改 1" the instant it is applied. Check `TYRE_MODELS[].owlSizes`.
- **Tyre and wheel rim sizes must match** or `validate()` errors. Wheels are
  15" or 16" (plus the new 18"); tyre sizes carry their own `rim`.
- **`.sw` is already taken** by the colour swatch buttons (a 32 px circle).
  The style cards use `.tone` for their chips because of it.
- **The page hides stock parts by name**, matched in `rig.js` by bounding box
  and material. Anything that replaces a stock part needs a matcher there and a
  `cfg.hideX` flag.
- **Blender `box()` size order is (car X, car Y, car Z)** but `prism()` takes
  its polygon in the (y, z) plane. A concave polygon passed to `prism` — a star
  outline, say — triangulates through itself; build it from convex pieces.
- The scratchpad fills up. This machine was at 99% disk during the session;
  `/private/tmp/claude-501/` is where it goes.
