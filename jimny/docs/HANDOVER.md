# Handover — Jimny JB74 configurator

Written 2026-09-24, at the end of a session that ran out of web-search budget.
A fresh session has a fresh budget; the list at the bottom is what to spend it
on. Everything described here is committed, pushed and live.

Live: <https://carloxthebot.github.io/CarBiz/jimny/app.html>
Catalogue: <https://carloxthebot.github.io/CarBiz/jimny/parts.html>
Current build: **202609250609** · 247 catalogue entries · 7 styles

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

**Seven styles**, each a preset applied from the first step, listed AFTER the makers' complete kits (`KITS` shown as `kit_<id>` cards, the kit on an otherwise stock car). They are pushed
apart on silhouette — height, roof load, arch width, face, wheel size — not on
which bumper they wear, because cars differing by bumper alone read the same
from ten metres.

| style | what makes it read differently |
|---|---|
| 都會寬體低趴 `street_low` | the only one below stock; RAYS 18" forged, 225/60R18 H/T, WALD +30 mm fenders |
| 都會輕改 `city` | bare roof, low black pinstripe |
| 日系復古 `jp_retro` | sand body, three-band retro stripe, steel look |
| 窄胎高瘦 `narrow` | stock height, 185/85R16 white-letter R/T on white DEAN faces — a real Hamamatsu shop build |
| 軍風 `military` | white stencils (no star — owner removed it 2026-09-25), loaded window guards |
| 露營 `camp` | two-tone roof, body lift, four orange bands |
| 澳洲越野 `au_offroad` | tallest, 31s, lit roof rack, snorkel |

New families this session (all pickable in 外觀, all in `parts.html`):
`FACES` (face kits — hide the stock bumper, grille AND headlamps; rig.js
`stockHeadlamps` / `cfg.hideHeadlamps`), `FENDERS` (wide-body over-fenders laid
over the Sierra arches, `widebody()` in build_parts.py follows `ARCH_HALF_W`),
`SPOILERS` (DAMD wing, ROWEN ducktail). Stripes and the cage finally have their
own pickers. `TYRE_MODELS` has an H/T (road) tab with its own procedural tread
(`PATTERNS.ht` in wheels.js). `COLORS` has one wrap film (3M 2080-G13 red),
flagged `wrap: true` and shown in its own 改色膜 group — never as a Suzuki code.

UI added at the owner's request: on a mouse device the part pickers open a
custom list (`.pmenu`) so the hover card follows the row under the pointer
(a native `<select>` menu reports nothing while open); touch keeps the native
select. Prices now lead with the shop's own currency, NT$ in brackets
(`priceLabel` in fx.js). The roof rack has 往車頭／往車尾 buttons, 50 mm a
press, ±200 mm (`S.rackShift`; shovel, awning and roof lights ride along).

Added 2026-09-25:
- **露營 tab.** `TENTS` (Kamado Canotier J3 roof-mounted, Front Runner
  TENT031 fold-out, Autohome Columbus pop-up), open/closed; every AWNINGS entry
  carries `open` geometry (rect projection or 270° fan radius) so the chosen
  awning unrolls; ARB Deluxe Room 813108 under ARB 2500 awnings; `CAMP_EXTRAS`
  (LX-MODE tailgate tent, Suzuki car tarp ACAZ). Open states are built
  parametrically in `camp.js` (three.js), not Blender. Three example buttons
  apply a whole open set-up. Every roof tent exceeds the 30 kg roof rating
  (Suzuki catalogue, rack included) and `validate()` says so as a warning.
- **ARB BASE Rack accessories** (`ARB_RACK_ACC`, `arbAcc_*` in parts.glb):
  deflector (moved off the rack mesh), front 3/4 rail, side rails, jerry cans,
  gas bottle, MAXTRAX mount, Hi-Lift holder; shown only with the ARB rack,
  slide with `rackShift`. Prices are for the holders; what they hold is extra.
- **Narrow tyres**: 175/80R16, 185/85R16, 195R16C, 205R16C, 6.50R16, 7.00R16
  (docs/jb74-narrow-tyres.json).
- **Official demo cars**: 27 JB74 demo cars from the Japanese makers,
  rendered on parts.html from docs/jb74-demo-cars.json, each matched against
  the catalogue with a link that applies the parts we have. Instagram,
  Threads and X all refuse fetching.

Owner feedback 2026-09-25, applied: picking a style no longer jumps to the
底盤 tab; 外掛籠硬派 removed as a style ("不會有這種車"; the cage part stays);
every style now carries real bumpers and grilles instead of stock; 都會輕改
became the common Japanese owner build (1" lift, bronze 16" + white-letter
KO2, KLC short bumper + JA grille). **Physical plausibility is now checked**:
`node tools/tyre_audit.mjs` must print `{}`; a visual review of every part
shot found floating/unsupported parts (rally-bar legs, fog stalks, awning
bags inside the rail, KLC rear lamps with no mount, tail pipes duplicated
by bumpers, side exhaust outside the body) -- all fixed. Keep both clean.

**Stages (2026-09-25).** The owner found the result "not stunning"; the
diagnosis was the dark void stage, primitive-looking parts, a stock car as the
first thing seen, no transitions, a spreadsheet-like panel and timid colours.
First fix shipped: a bright studio (default; CSS backdrop, studio HDR) and an
outdoor stage (Poly Haven "Goegap Road", CC0, model/env_goegap_2k.hdr,
GroundedSkybox at 1.8 m / 160 m, sun aimed from the brightest pixel, pixels
capped at 24 because the half-float post chain overflowed to a black car).
Next, per docs/jb74-beyond-styles.json: two-tone split paint at the window
line (Beyond's single biggest trick), one finish for all hardware, wheels that
contrast the body. Instagram (KLC, SHOWA) needs the Chrome extension
connected; it was not.

**The owner does not want regulation treated as a gate** — "改裝界會另外處理".
A lift advisory was added and then removed on that instruction. Do not put
legality back in front of the buyer. (The research is still in
`docs/jb74-archetypes.json` under `taiwanRegulation` if it is ever wanted; the
one clause verified first-hand from the official PDF is 附件十五 三、底盤:
「懸吊系統之避震器｜變更後不得超過原核定車身高度」.)

**美式方頭換臉 `bronco_face` and 歐系拉力寬體 `euro_rally` were built and then
removed as styles** — the owner: 「美式方頭換臉跟歐系寬體都先拿掉，不好」
(2026-09-25). Their parts (FACES, FENDERS, SPOILERS, OZ wheel, red wrap,
little Δ rear bumper, centre stripe) are still in the catalogue and pickable.
Do not put the two styles back without asking.

**皮卡工作車 `work_truck` is dropped** — the owner said 「先不要做，這個改太大切車身」.
Do not build it.

---

## 3. What is still open

- **Geometry is from photographs.** BRON55, little Δ, the wing, the ducktail
  and the OZ wheel are drawn from `docs/jb74-face-swap.json` and
  `docs/jb74-rally-geometry.json` (±8–25 %). If a maker drawing turns up,
  redraw against it.
- **Widths nobody publishes.** KUHL, LB and DAMD over-fenders have no per-side
  figure; the entries say so and model 30/35/40 mm. AERO OVER's +35 version has
  no separate price.
- **The KLC lowering spring's JB74 figure.** KLC publish ~40 mm for the JB64
  only; the entry says so and estimates.
- **Bumper "painted in the body colour" as a choice** is still not a toggle;
  parts that ship painted use `BodyPaint` and follow the car.

---

## 4. Research already done — read before searching

| file | what is in it |
|---|---|
| `docs/jb74-gapfill-verified.json` | **the 88 gapfill corrections, each re-checked on the maker page** (63 edit, 24 no change, 1 remove), with the quote and URL. All applied to parts.js on 2026-09-24. Where the gapfill itself was wrong it says so (JAOS brake hoses ARE in the kit; the SHOWA 50 rename was scraper noise). |
| `docs/jb74-jp-gapfill.json` | the original, unverified reading — superseded by the file above |
| `docs/jb74-street-wheels-tyres.json` | 17/18" JB74 wheels (only RAYS A・LAP-07X is real; WedsSport, MLJ, 4x4 Eng., Fuel, Method all stop at 16" on 5×139.7) and road tyres |
| `docs/jb74-face-swap.json` | BRON55 (prices are 税込, not 税抜 as older docs said), CH:AMP, 70YO.70, with BRON55 modelling geometry |
| `docs/jb74-widebody.json` | wide-body fenders; every western brand found fits only the old JB23/JB43 |
| `docs/jb74-rally.json`, `docs/jb74-rally-geometry.json` | red (no JB74 red in any market), four-lamp front, stripes (no product exists), spoilers; plus geometry for little Δ, the wing, OZ, ROWEN |
| `docs/jb74-demo-cars.json` | 27 official JB74 demo cars, parts matched to catalogue ids |
| `docs/jb74-camping.json` | roof tents, awning deployed geometry, rooms, tailgate/side tents; 30 kg roof rating sources |
| `docs/jb74-arb-rack-accessories.json` | 26 BASE Rack accessories with part numbers and prices |
| `docs/jb74-narrow-tyres.json` | narrow sizes, which makers list them, real skinny-tyre builds |
| `docs/jb74-complete-kits.json` | 53 Japanese complete kits with first-party prices |
| `docs/jb74-archetypes.json` | the archetypes, 11 rejected with reasons, and the Taiwan regulation dossier |
| `docs/jb74-chrome-damd.json` | 133 items: 86 chrome (9 negative findings), 47 DAMD |
| `docs/jb74-stripes.json`, `jb74-graphics.json`, `jb74-snorkels.json`, `jb74-wheel-atlas.json`, `jb74-fitment.json`, `jb74-accessory-atlas.json` | earlier dossiers |

---

## 5. Spend the next search budget on these

1. Maker drawings or clean side photos for BRON55 and little Δ, to firm up
   the geometry.
2. A second real 17–18" JB74 wheel, so `street_low` is not a one-product style.
3. A JB74-size road tyre beyond the OE Dueler H/T 684 II (195/80R15) and
   Open Country H/T II (225/60R18 only).
4. Chrome modelling from `docs/jb74-chrome-damd.json` — research is done.

---

## 6. Things that will bite you

- **`S.bodyLift` is decorative.** `validate()` and the rig read the body-lift
  figure off the LIFT entry's own `body` field, not off `S.bodyLift`. A style
  wanting a body lift must choose a kit that carries one (`sg50bl`, `combo100`).
- **White letters switch themselves off.** `owl: true` on a tyre size that the
  tread has no OWL for is silently dropped, and the style then reports a
  phantom "改 1" the instant it is applied. Check `TYRE_MODELS[].owlSizes`.
- **Tyre and wheel rim sizes must match** or `validate()` errors. Wheels are
  15", 16" or 18"; tyre sizes carry their own `rim`.
- **Another session can sweep your work into its commit.** On 2026-09-24 a
  parallel session ran `git add -A jimny` and deployed half-finished edits.
  Stage files by name, and check `git log origin/main` before pushing.
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
