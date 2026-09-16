// Real JB74 parts catalogue. Every entry is a product that exists; prices are
// approximate and in the currency the maker quotes. `uncertain: true` marks
// anything research could not pin down — shown in the UI rather than hidden,
// because a configurator that invents specs is worse than one that admits gaps.
//
// The geometry each option drives lives in `fit`: lift in mm, tyre outer
// diameter in mm, rim diameter in inches. Those three are what move the model.

export const COLORS = [
  { code: '26U', name: 'Superior White',          hex: 0xffffff, twoTone: false },
  { code: 'ZVR', name: 'Pure White Pearl',        hex: 0xf2f4f3, twoTone: false },
  { code: 'Z2S', name: 'Silky Silver Metallic',   hex: 0xc6c9c8, twoTone: false },
  { code: 'ZVL', name: 'Medium Gray (Solid)',     hex: 0x6a6866, twoTone: false },
  { code: 'ZJ3', name: 'Bluish Black Pearl 3',    hex: 0x1e2326, twoTone: false },
  { code: 'ZZC', name: 'Jungle Green',            hex: 0x3e4135, twoTone: false },
  { code: 'ZZB', name: 'Kinetic Yellow',          hex: 0xdcd037, twoTone: 'DG5' },
  { code: 'ZVG', name: 'Chiffon Ivory Metallic',  hex: 0xd5c29e, twoTone: '2BW' },
  { code: 'ZWY', name: 'Brisk Blue Metallic',     hex: 0x1db1d0, twoTone: 'CZW' },
  { code: 'WAA', name: 'Sizzling Red Metallic',   hex: 0xb9202b, twoTone: false, note: '部分市場' },
];
export const ROOF_BLACK = 0x1e2326;   // ZJ3 — the only two-tone roof Suzuki offers

// Suspension lifts, grouped by the inch class the trade uses. `lift` is the
// static height gain in mm that moves the model; `inch` is the class label.
// Beyond 50mm the front propshaft meets the stock crossmember, so every kit
// from 2" up needs a drop bracket; 3"+ needs caster correction; 4" is in
// practice 2–3" of suspension plus a body lift.
export const LIFTS = [
  { id: 'stock', label: '原廠', inch: '原廠', lift: 0, body: 0, price: 0, brand: 'SUZUKI',
    note: '原廠離地 210mm；原廠高度最大可裝 215/70R16' },
  // ---- 1 吋 (20–30mm)
  { id: 'klc30', url: 'https://www.klc-div.com/heritage/product/suspension/lift-upspringtodoroki/', label: 'KLC Heritage 轟 彈簧', inch: '1"', lift: 30, body: 0, price: 38500, cur: 'JPY',
    brand: 'KLC', note: '只換彈簧，沿用原廠避震；車檢 OK' },
  { id: 'sg25', url: 'https://www.showa-garage.shop/shopdetail/000000000529/', label: 'SHOWA GARAGE 1 吋彈簧', inch: '1"', lift: 25, body: 0, price: 40700, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00350', note: '只換彈簧；建議加橫拉桿組（含拉桿 ¥90,200）' },
  { id: 'ms20', url: 'https://www.monster-sport.com/product/parts/sus/jb64w_hisusset_2/', label: 'MONSTER SPORT type-2 20mm', inch: '1"', lift: 20, body: 0, price: 94600, cur: 'JPY',
    brand: 'MONSTER SPORT', part: '510502-5600ML', note: '彈簧＋14 段避震＋後大燈水平感應器支架' },
  { id: 'apio20', url: 'https://www.apio.jp/parts/1028-1aa.html', label: 'APIO 7420SA', inch: '1"', lift: 20, body: 0, price: 126500, cur: 'JPY', brand: 'APIO',
    part: '1028-1AA', note: '彈簧＋14 段避震；免換煞車油管；車檢 OK' },
  { id: 'es30', url: 'https://www.4x4es.co.jp/2021/02/19/', label: '4x4 Engineering Country 30mm', inch: '1"', lift: 30, body: 0, price: 123000, cur: 'JPY',
    brand: '4x4 Engineering', part: '74743-31', note: '彈簧＋Harmoflex 14 段避震；沿用原廠煞車油管' },
  // ---- 1.5 吋 (40mm)
  { id: 'jaos40', url: 'https://www.jaos.co.jp/product/A734518Z/3218/', label: 'JAOS BATTLEZ VFS ver.A(40) Complete', inch: '1.5"', lift: 40, body: 0, price: 184800,
    cur: 'JPY', brand: 'JAOS', part: 'A734518Z', note: '彈簧、避震、長煞車油管、前後橫拉桿、Caster 襯套' },
  { id: 'apio40', url: 'https://www.apio.jp/parts/1034-1ae.html', label: 'APIO 7440Ti', inch: '1.5"', lift: 40, body: 0, price: 276100, cur: 'JPY', brand: 'APIO',
    part: '1034-1AE', note: '全套：長行程避震、前後橫拉桿、Caster 襯套、長煞車油管。⚠ 僅支援右駕' },
  { id: 'omr40', url: 'https://megajimny.com/products/arb-old-man-emu-40mm-lift-kit-2018-jimny', label: 'ARB Old Man Emu 40mm', inch: '1.5"', lift: 40, body: 0, price: 2410, cur: 'AUD', brand: 'ARB',
    note: '含橫樑補強、Panhard 座、煞車油管延長、Caster 襯套；彈簧依保桿／絞盤重量選' },
  { id: 'dob40', url: 'https://megajimny.com/products/dobinsons-ims-monotube-40mm-lift-kit', label: 'Dobinsons IMS Monotube 40mm', inch: '1.5"', lift: 40, body: 0, price: 1949, cur: 'AUD',
    brand: 'Dobinsons' },
  { id: 'td40', url: 'https://www.directsuspensions.com.au/products/tough-dog-40mm-lift-kit-for-suzuki-jimny-jb74-3-door-2019-on', label: 'Tough Dog Foam Cell 40mm', inch: '1.5"', lift: 40, body: 0, price: 1467, cur: 'AUD',
    brand: 'Tough Dog' },
  // ---- 2 吋 (50mm)
  { id: 'sg50', url: 'https://www.showa-garage.shop/shopbrand/I84526', label: 'SHOWA GARAGE SG Custom 50 Ennepetal E-12', inch: '2"', lift: 50, body: 0, price: 323400,
    cur: 'JPY', brand: 'SHOWA GARAGE', part: 'S00853', note: 'BA 全套 ¥480,700（加長煞車油管＋橫拉桿）' },
  { id: 'cusco50', url: 'https://shop.nstparts.com/products/cusco-2-inch-lift-suspension-kit-suzuki-jimny-jb74', label: 'CUSCO 2 吋套件（50–75 可調）', inch: '2"', lift: 50, body: 0, price: null, cur: 'JPY',
    brand: 'CUSCO', part: '60N-6JS-U20', uncertain: true, note: '14 段避震、螺牙墊高可調、延長煞車油管；日本售價未查證' },
  { id: 'im50', url: 'https://ozjimny.com/products/ironman-4x4-50mm-suspension-lift-kit-constant-front-load-with-gas-shock-absorbers', label: 'Ironman 4x4 Nitro Gas 50mm', inch: '2"', lift: 50, body: 0, price: 1757, cur: 'AUD',
    brand: 'Ironman 4x4', part: 'SUZ010BKG', note: '含延長煞車油管、橫樑下降座、2° Caster 襯套、延長緩衝塊' },
  // ---- 2.5 吋 (60mm)
  { id: 'tg60', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_suspension/', label: 'TANIGUCHI SOLVE ACE60', inch: '2.5"', lift: 60, body: 0, price: 216040, cur: 'JPY',
    brand: 'TANIGUCHI', note: '彈簧、避震、長油管、Caster 襯套、橫拉桿；另需 SOLVE 橫樑（+¥27,500）' },
  { id: 'td60', url: 'https://ozjimny.com/products/tough-dog-4wd-suspension-60mm-suspension-lift-kit-with-braided-brake-lines-steel-bullbar-no-winch', label: 'Tough Dog Foam Cell 60mm', inch: '2.5"', lift: 60, body: 0, price: null, cur: 'AUD',
    brand: 'Tough Dog', uncertain: true, note: '含編織煞車油管；報價制' },
  // ---- 3 吋 (75mm)
  { id: 'sg75', url: 'https://www.showa-garage.shop/shopbrand/I84527/', label: 'SHOWA GARAGE SG Custom 75 X-SHOCK', inch: '3"', lift: 75, body: 0, price: 253000, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00472', note: 'BA 全套 ¥394,900；需另購 Caster 修正臂' },
  { id: 'es70', url: 'https://www.4x4es.co.jp/2025/04/08/', label: '4x4 Engineering Country 70mm', inch: '3"', lift: 70, body: 0, price: 315000, cur: 'JPY',
    brand: '4x4 Engineering', uncertain: true, note: '全套含橫樑下降、傳動軸墊片、油管、橫拉桿、轉向阻尼' },
  { id: 'dob75', url: 'https://megajimny.com/products/dobinsons-ims-monotube-75mm-lift-kit', label: 'Dobinsons IMS 遠端氣瓶 75mm', inch: '3"', lift: 75, body: 0, price: 3699, cur: 'AUD',
    brand: 'Dobinsons', note: '含橫樑下降、前後可調橫拉桿、Caster 襯套、大燈水平支架、延長油管' },
  { id: 'br75', url: 'https://www.jimnybits.com/3-75mm-suzuki-jimny-black-raptor-full-suspension-lift-kit-2019-on.html', label: 'Black Raptor 3" 全套', inch: '3"', lift: 75, body: 0, price: null, cur: 'GBP',
    brand: 'JimnyBits', uncertain: true, note: '含 Caster 修正拉桿臂＋可調 Panhard' },
  // ---- 4 吋 (100mm)
  { id: 'br100', url: 'https://www.jimnybits.com/4-100mm-suzuki-jimny-black-raptor-full-suspension-lift-kit-2019-on.html', label: 'Black Raptor 4" 全套', inch: '4"', lift: 100, body: 0, price: 1586, cur: 'GBP',
    brand: 'JimnyBits', note: '彈簧、避震、4 支 Caster 修正臂、2 支可調 Panhard、編織油管、橫樑下降；左右駕彈簧不同' },
  { id: 'sg50bl', label: 'SHOWA GARAGE 50 + 25mm 車身舉升', inch: '3"', lift: 50, body: 25, price: null, cur: 'JPY',
    brand: 'SHOWA GARAGE / JimnyBits', uncertain: true, note: '2 吋懸吊加車身墊高，31 吋胎的常見組合' },
  { id: 'combo100', url: 'https://www.zookoffroad.com.au/product-page/jimny-4-100mm-black-raptor-full-suspension-lift-kit-jb', label: '2" 懸吊 + 2" 車身舉升', inch: '4"', lift: 50, body: 50, price: null, cur: 'AUD',
    brand: 'Black Raptor / ZOOK', uncertain: true, note: '用車身舉升取代 Caster 修正臂與 Panhard 的組合路線' },
];


export const BODY_LIFTS = [
  { id: 'none', label: '無', body: 0, price: 0 },
  { id: 'bl25', label: '25mm 車身舉升', body: 25, price: null, cur: 'GBP', brand: 'JimnyBits',
    note: '墊高車身本體，真正增加輪拱空間，免切割。31 吋的標準搭配' },
];

export const WHEELS = [
  { id: 'oem', label: '原廠 15×5.5J', rim: 15, width: 5.5, offset: 5, style: 'stock',
    price: 0, brand: 'SUZUKI', note: 'ET+5／5×139.7／中心孔 108mm' },
  { id: 'oemsteel', label: '原廠鐵圈（JL）', rim: 15, width: 5.5, offset: 5, style: 'steel',
    price: 0, brand: 'SUZUKI' },
  { id: 'wildboar', label: 'APIO WILDBOAR X', rim: 15, width: 6.0, offset: -5, style: 'eight',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true, note: '15×6.0J −5' },
  { id: 'wildboar16', label: 'APIO WILDBOAR SR 16', rim: 16, width: 5.5, offset: 20, style: 'eight',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true },
  { id: 'bradley', label: 'Bradley V', rim: 16, width: 5.5, offset: 22, style: 'six',
    price: 37400, cur: 'JPY', brand: '4x4 Engineering', note: '每顆單價；另有 +0 Jimny spec' },
  { id: 'xtremej', label: 'MLJ XTREME-J XJ04', rim: 16, width: 5.5, offset: 22, style: 'eight',
    price: null, cur: 'JPY', brand: 'MLJ', uncertain: true },
  { id: 'te37xt', label: 'RAYS TE37XT M-SPEC for J', rim: 16, width: 5.5, offset: 20, style: 'six',
    price: null, cur: 'JPY', brand: 'RAYS', note: '鍛造一件式，2025 年起；Bronze／Blast Black' },
  { id: 'maxx', label: 'MAXX Flowforged 8 輻', rim: 16, width: 7.0, offset: -10, style: 'eight',
    price: null, brand: 'MAXX', uncertain: true, note: '消光黑，車主實車配置' },
  { id: 'beadlock', label: 'Beadlock 造型輪圈', rim: 16, width: 7.0, offset: -20, style: 'beadlock',
    price: null, brand: '多家', uncertain: true, note: '深 offset，需搭配大幅輪拱修改' },
];

export const TYRES = [
  { id: 't195', label: '195/80R15（原廠）', dia: 693, width: 195, rim: 15, price: 0,
    needLift: 0, needBody: 0, legal: true, note: '原廠配置' },
  { id: 't215r15', label: '215/75R15', dia: 710, width: 215, rim: 15, needLift: 0, needBody: 0,
    legal: true, note: '+2.4%，原廠框可裝、免修改。最安全的升級' },
  { id: 't215r16', label: '215/70R16', dia: 707, width: 215, rim: 16, needLift: 0, needBody: 0,
    legal: true, note: '+2%，可能需輕微修內輪弧' },
  { id: 't225', label: '225/75R15', dia: 719, width: 225, rim: 15, needLift: 20, needBody: 0,
    legal: true, uncertain: true, note: '+3.7%，約需 20mm 舉升' },
  { id: 't235', label: '235/75R15', dia: 741, width: 235, rim: 15, needLift: 40, needBody: 0,
    legal: true, note: '+6.9%，需 40–50mm 舉升＋修內襯與保桿；滿舵與扭曲時會磨。澳洲法規上限' },
  { id: 't205r16', label: '205R16', dia: 741, width: 205, rim: 16, needLift: 40, needBody: 0,
    legal: true, note: '與 235/75R15 同外徑但較輕' },
  { id: 't30', label: '30×9.50R15', dia: 762, width: 241, rim: 15, needLift: 50, needBody: 0,
    legal: false, note: '+10%，需 50mm 舉升＋修改。超出澳洲法規' },
  { id: 't31', label: '31×10.50R15', dia: 787, width: 267, rim: 15, needLift: 50, needBody: 25,
    legal: false, note: '+13.5%，標準解是 50mm 懸吊＋25mm 車身舉升＋修改' },
  { id: 't33', label: '33 吋', dia: 838, width: 285, rim: 15, needLift: 100, needBody: 25,
    legal: false, severe: true,
    note: '+21%，需 4 吋舉升、−30 offset、大幅切割輪拱與保桿、17/87 減速齒輪' },
];

// Tread patterns drawn by wheels.js. `pattern` picks the procedural geometry
// (at / rt / mt); `mask` names a strip traced from the maker's tread photo
// (blender/trace_tread.py) that replaces it, `repeatMM` being the strip's
// length along the circumference; `owl` says whether the maker sells a white-letter sidewall in JB74
// sizes, so the toggle can be offered honestly.
export const TYRE_MODELS = [
  { id: 'toyo_at3', pattern: 'at', brand: 'TOYO TIRES', model: 'OPEN COUNTRY A/T III', owl: true,
    mask: { file: 'toyo_at3.png', repeatMM: 184 },
    label: 'TOYO Open Country A/T III', note: '白字：日規 215/70R16、美規 235/75R15、30×9.5、31×10.5' },
  { id: 'bfg_ko2', pattern: 'at', brand: 'BFGoodrich', model: 'ALL-TERRAIN T/A KO2', owl: true,
    label: 'BFGoodrich All-Terrain T/A KO2', note: '多數尺寸有白字（RWL）' },
  { id: 'yk_g015', pattern: 'at', brand: 'YOKOHAMA', model: 'GEOLANDAR A/T G015', owl: true,
    label: 'Yokohama GEOLANDAR A/T G015', note: '部分尺寸白字' },
  { id: 'fk_at3w', pattern: 'at', brand: 'FALKEN', model: 'WILDPEAK A/T3W', owl: false,
    label: 'Falken WILDPEAK A/T3W', note: '僅黑字' },
  { id: 'toyo_rt', pattern: 'rt', brand: 'TOYO TIRES', model: 'OPEN COUNTRY R/T', owl: true,
    mask: { file: 'toyo_rt.png', repeatMM: 156 },
    label: 'TOYO Open Country R/T', note: '日規單面白字' },
  { id: 'yk_xat', pattern: 'rt', brand: 'YOKOHAMA', model: 'GEOLANDAR X-AT G016', owl: true,
    label: 'Yokohama GEOLANDAR X-AT', note: '白字：195R16C、215/70R16' },
  { id: 'nt_ridge', pattern: 'rt', brand: 'NITTO', model: 'RIDGE GRAPPLER', owl: false,
    label: 'Nitto Ridge Grappler', note: '僅黑字；JB74 常用尺寸較少' },
  { id: 'kd_rt', pattern: 'rt', brand: 'KENDA', model: 'KLEVER R/T', owl: true,
    label: 'Kenda Klever R/T KR601', note: '部分尺寸白字' },
  { id: 'toyo_mt', pattern: 'mt', brand: 'TOYO TIRES', model: 'OPEN COUNTRY M/T', owl: true,
    mask: { file: 'toyo_mt.png', repeatMM: 246 },
    label: 'TOYO Open Country M/T', note: '日規單面白字；LT 規格' },
  { id: 'bfg_km3', pattern: 'mt', brand: 'BFGoodrich', model: 'MUD-TERRAIN T/A KM3', owl: false,
    label: 'BFGoodrich Mud-Terrain T/A KM3', note: '僅黑字' },
  { id: 'yk_g003', pattern: 'mt', brand: 'YOKOHAMA', model: 'GEOLANDAR M/T G003', owl: true,
    label: 'Yokohama GEOLANDAR M/T G003', note: '日規 215/70R16 有白字' },
  { id: 'cp_stt', pattern: 'mt', brand: 'COOPER', model: 'DISCOVERER STT PRO', owl: true,
    label: 'Cooper Discoverer STT Pro', note: '31×10.5R15 白字' },
];


// Front bumpers and grilles are modelled parts (blender/build_parts.py);
// `id` is the part name suffix in parts.glb. Choosing one hides the stock
// bumper (with its fog lamps) or the stock grille panel on the model.
export const FRONT_BUMPERS = [
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  // ---- 台灣有售
  { id: 'tube_heritage', url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_iv/', label: 'KLC Heritage Traditional 圓管保桿（MRK 代理）', price: 104500, cur: 'JPY', brand: 'KLC Heritage',
    note: '不鏽鋼圓管＋Heritage 護板、車牌鎖管上、LED 方燈（車主實車配置）；台灣 MRK 4X4 代理' },
  { id: 'armando', url: 'https://www.mrk.com.tw/product_ii.html?ID=1542', label: 'ARMANDO PRIME 前鐵保桿（MRK）', price: 29000, cur: 'TWD', brand: 'ARMANDO',
    part: 'AR-SU-FB-PRM', note: '全寬鋼板保桿、中央燈架、圓霧燈孔、下護板' },
  { id: 'urnieta_1970', url: 'https://www.mrk.com.tw/product_ii.html?ID=2210', label: 'URNIETA 1970 前保桿', price: 20600, cur: 'TWD', brand: 'URNIETA', part: 'UR010',
    note: '短版復古、兩側上折收窄，保留原廠霧燈與洗燈' },
  { id: 'beyond_liberte', url: 'https://www.mrk.com.tw/product_ii.html?ID=2114', label: 'Beyond Japan Liberte 復古前保桿', price: 28000, cur: 'TWD', brand: 'Beyond Japan',
    note: '硬邊鋼製、霧燈架＋下護板；MRK 代理' },
  { id: 'maverick', url: 'https://i-pickup.com.tw/product/df0001/', label: 'Maverick 短版金屬前保桿（i-PICKUP）', price: 29000, cur: 'TWD', brand: 'Maverick',
    part: 'DF0001', note: '鍍鋅鋼 NT$29,000／鋁合金 NT$35,000，塗裝 +9,000' },
  { id: 'jst', url: 'https://www.mrk.com.tw/product_ii.html?ID=1580', label: 'JST 前保桿（黑四驅）', price: null, cur: 'TWD', brand: 'JST', uncertain: true,
    note: '短鋼板＋管狀護弓；報價制（估 NT$25–30k）' },
  { id: 'mrk_abs', url: 'https://www.mrk.com.tw/product_ii.html?ID=1948', label: 'MRK 短版 ABS 前保桿 消光黑', price: 9500, cur: 'TWD', brand: 'MRK', part: 'JMY-FB-L',
    note: '原廠造型縮短版、ABS' },
  { id: 'wmd_winch', url: 'https://www.ruten.com.tw/item/show?22105872751291', label: 'WMD 前絞盤短保桿（機油倉庫）', price: 18000, cur: 'TWD', brand: 'WMD（台灣）',
    note: '台製鋼板、絞盤座、Ø50 護弓' },
  { id: 'jaos_cowl', url: 'https://www.jaos.co.jp/product/B040518/2866', label: 'JAOS Front Sport Cowl', price: 18700, cur: 'TWD', brand: 'JAOS', part: 'B040518',
    note: 'PU 材質＋鋁網，下緣 −80mm；日本 ¥66,000 起' },
  // ---- 日本
  { id: 'klc_nostalgic', url: 'https://www.klc-div.com/heritage/product/bumper/nostalgicfrontbumper/', label: 'KLC Heritage Nostalgic 前保桿', price: 74800, cur: 'JPY', brand: 'KLC Heritage', uncertain: true,
    note: 'JA11 風壓鋼箱型桿、烤漆（顯示為車身同色），下方黑色飾板含圓霧燈；¥74,800–96,800 依塗裝' },
  { id: 'klc_short', url: 'https://www.klc-div.com/heritage/product/bumper/frontshortbumper74/', label: 'KLC Heritage Front Short Bumper 74', price: 96800, cur: 'JPY', brand: 'KLC Heritage', uncertain: true,
    note: 'ABS 原廠高度縮短版、中央網狀開口、保留原廠霧燈；素材 ¥63,800' },
  { id: 'showa_iron', url: 'https://www.showa-garage.shop/shopdetail/000000000842/', label: 'SHOWA GARAGE Iron Bumper', price: 128700, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00900', note: 'Ø60 鋼管、兩端 45° 後彎；含 3mm 鋁下護板與霧燈架（本體單售 ¥90,750）' },
  { id: 'klc_trad', url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_iv/', label: 'KLC Heritage Traditional（象牙白）', price: 104500, cur: 'JPY', brand: 'KLC Heritage',
    note: '全不鏽鋼雙管，象牙白／黑／拋光；顯示為車身同色' },
  { id: 'outclass_t2', url: 'https://outclass.ocnk.net/product/1095', label: 'OUTCLASS TYPE2 絞盤鐵保桿', price: 140800, cur: 'JPY', brand: 'OUTCLASS',
    note: '鐵製、含絞盤床與 4 顆 LED 方燈；出廠未烤漆（可選 Raptor 塗層）' },
  { id: 'taniguchi_square', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: 'TANIGUCHI 角形前保桿', price: 58300, cur: 'JPY', brand: 'TANIGUCHI',
    note: '2mm 方管、粉體黑；不鏽鋼版 ¥107,800' },
  { id: 'taniguchi_double', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: 'TANIGUCHI 雙管前保桿', price: 77000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '上下兩支 Ø48 圓管' },
  { id: 'toc_extreme', url: 'https://tocbw.thebase.in/items/82110724', label: 'TOC BODYWORKS Extreme Bumper 74', price: 54780, cur: 'JPY', brand: 'TOC BODYWORKS',
    note: 'FRP 仿鐵保桿、原廠寬度、LED 燈條槽' },
];

export const REAR_BUMPERS = [
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  // ---- 台灣有售
  { id: 'tube', label: '車主實車 管狀後保桿（含尾燈座）', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: 'Ø76 直管、方形封板、尾燈座板、右側排氣尾管、拖鉤' },
  { id: 'klc_heritage_rear', url: 'https://www.mrk.com.tw/product_ii.html?ID=2059', label: 'KLC Heritage 經典復古後保桿（MRK）', price: 26000, cur: 'TWD', brand: 'KLC Heritage', part: 'HTRBBK',
    note: '粗直管＋兩端梯形尾燈座板、車牌下吊；粉體黑／銀／象牙白（車主實車配置）' },
  { id: 'klc_nostalgic_rear', url: 'https://www.klc-div.com/heritage/product/bumper/nostalgicrearbumper/', ownLamps: true, label: 'KLC Heritage Nostalgic 後保桿', price: 96800, cur: 'JPY', brand: 'KLC Heritage', uncertain: true,
    note: '烤漆箱型桿（顯示為車身同色）、上緣橡膠條、兩端內嵌三色矩形尾燈' },
  { id: 'urnieta_1970_rear', url: 'https://www.mrk.com.tw/product_ii.html?ID=2219', ownLamps: true, label: 'URNIETA 1970 後保桿', price: 20400, cur: 'TWD', brand: 'URNIETA', part: 'UR015',
    note: '半高、兩端上折、圓形尾燈，8.4kg' },
  { id: 'beyond_rear', url: 'https://www.mrk.com.tw/product_ii.html?ID=2112', label: 'Beyond Japan Liberte 復古後保桿', price: 21000, cur: 'TWD', brand: 'Beyond Japan',
    note: '精簡鋼桿、消光黑' },
  { id: 'jaos_rear_cowl', url: 'https://www.mrk.com.tw/product_ii.html?ID=1176', ownLamps: true, label: 'JAOS Rear Sport Cowl', price: 26500, cur: 'TWD', brand: 'JAOS', part: 'B042518',
    note: 'PU 材質、4 顆圓形尾燈、倒車攝影機架' },
  // ---- 日本
  { id: 'wildgoose_crawler_rear', url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1103.html', label: 'Wild Goose Crawler 後保桿 JM-1103', price: 66000, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: 'Ø76.3 直管 1330×200×225、尾燈座 4.5mm 板、Ø50 拖環' },
  { id: 'wildgoose_box_rear', url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1101.html', label: 'Wild Goose クロカン後保桿 JM-1101', price: 95700, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: '1410×100×100 角形箱桿 3.2mm，13.2kg' },
  { id: 'showa_iron_rear', url: 'https://www.showa-garage.shop/shopbrand/ct343/', label: 'SHOWA GARAGE Iron Bumper Rear', price: 62150, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00930', note: 'Ø60 主管＋Ø42 尾燈管翼；LED 倒車燈版 ¥127,930' },
  { id: 'taniguchi_rear_pipe', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_rear/', label: 'TANIGUCHI 越野後保桿（鋼管）', price: 63800, cur: 'JPY', brand: 'TANIGUCHI',
    note: '2.3mm 鋼管；角形版 ¥63,800、拖車鉤版 ¥128,700' },
  { id: 'apio_tactical_rear', url: 'https://apio.jp/parts/3032-71.html', label: 'APIO Tactical 後保桿', price: 140800, cur: 'JPY', brand: 'APIO', part: '3032-71',
    note: 'ABS 真空成形 1660×280×460，含燈殼與反光片；烤漆 +¥33,000' },
  { id: 'outclass_rear_abs', url: 'https://outclass.ocnk.net/product/1094', ownLamps: true, label: 'OUTCLASS Rear Bumper TYPE2 ABS', price: 45760, cur: 'JPY', brand: 'OUTCLASS',
    note: '精簡 ABS、小型尾燈' },
  { id: 'hamer_mx208', url: 'https://www.hamer4x4.com/mx208-jimny-rear-bumper/', label: 'Hamer 4x4 MX208 後保桿', price: 1590, cur: 'AUD', brand: 'Hamer 4x4',
    note: '1830×650×340 包覆式鋼板、角落踏板、燈條槽，50kg' },
];

export const GRILLES = [
  { id: 'stock', label: '原廠五格柵', price: 0, brand: 'SUZUKI', note: '5 道直立柵欄，中央 S 標' },
  // ---- 台灣有售
  { id: 'hbar_suzuki', url: 'https://shopee.tw/product/47473069/5556354773', label: '南國吉米 JB74 復古水箱罩（5 橫柵＋SUZUKI 白字）', price: 2750, cur: 'TWD', brand: '南國吉米（台灣）',
    note: 'ABS 消光黑；客製色 NT$4,500、草寫字版 NT$5,000（車主實車配置）' },
  { id: 'taishan_retro', url: 'https://www.ruten.com.tw/item/show?22105865989825', label: '泰山美研社 復古水箱罩 黑／銀', price: 17500, cur: 'TWD', brand: '泰山美研社（台灣）',
    note: 'KLC 風格樹脂復古罩' },
  { id: 'urnieta_1970', url: 'https://www.heekis.com/products/urnieta-1970-jimny-jb74-jc74-grille', label: 'URNIETA 1970 水箱護罩', price: 8400, cur: 'TWD', brand: 'URNIETA',
    note: '沖壓金屬網＋極簡框，1.6kg；Heekis 代理' },
  { id: 'mrk_angry', url: 'https://www.mrk.com.tw/product_ii.html?ID=1670', label: 'MRK 憤怒鳥款水箱罩', price: 5500, cur: 'TWD', brand: 'MRK', part: 'JB089',
    note: '3 道粗橫條、外端斜切、卡扣安裝' },
  { id: 'klc_sj', url: 'https://www.klc-div.com/heritage/product/grille/facegrillesj.html', label: 'KLC Face Grille SJ（七孔＋SUZUKI 字）', price: 16000, cur: 'TWD', brand: 'KLC Heritage',
    note: 'FRP 素材 NT$16,000（藤井74）；日本 ABS 烤漆 ¥93,500。顯示為車身同色' },
  // ---- 日本
  { id: 'klc_ja', url: 'https://www.klc-div.com/heritage/product/grille/facegrilleja/', label: 'KLC Face Grille JA（JA22 風）', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '大燈旁雙燈座、中央開放網；ABS 素材 ¥60,500／FRP ¥55,000' },
  { id: 'klc_nanaketsu', url: 'https://www.klc-div.com/heritage/product/grille/facegrillnanaketsu/', label: 'KLC Face Grille NANAKETSU（七穴）', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '7 個圓角方孔、銀色鋁網' },
  { id: 'klc_forty', url: 'https://www.klc-div.com/heritage/product/grille/facegrillforty/', label: 'KLC Face Grille FORTY（FJ40 風）', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '大燈周圍肋條、中央網＋S 標' },
  { id: 'apio_sj', url: 'https://apio.jp/parts/3033-58g.html', label: 'APIO SJ Grille', price: 58300, cur: 'JPY', brand: 'APIO', part: '3033-58G',
    note: 'SJ30 直縫沖壓鋼板、槍灰、黑鋁網' },
  { id: 'apio_marker', url: 'https://apio.jp/parts/3033-59.html', label: 'APIO Marker Vintage Iron Grille', price: 75900, cur: 'JPY', brand: 'APIO', part: '3033-59',
    note: '鋼製橫柵＋4 顆 IPF 標誌燈，半光黑或淺古銅' },
  { id: 'showa_hex', url: 'https://www.showa-garage.shop/shopdetail/000000000205/', label: 'SHOWA GARAGE ABS 蜂巢護罩', price: 16500, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00500', note: 'ABS 素材黑（烤漆版 E00502 ¥31,900）；中央蜂巢網開口' },
  { id: 'outclass_g', url: 'https://outclass.ocnk.net/product/1071', label: 'OUTCLASS Vintage G Grille', price: 57750, cur: 'JPY', brand: 'OUTCLASS',
    note: 'ASA 樹脂紋理黑；4 道橫柵＋中央直柱，後方細網' },
  { id: 'taniguchi_washer', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: 'TANIGUCHI FRP Washer Grille', price: 44000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '原廠造型 FRP、洗燈噴嘴移入大燈' },
  { id: 'kpro_folksy', url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'K-PRODUCTS Folksy Style 橫鰭護罩', price: 30000, cur: 'JPY', brand: 'K-PRODUCTS', uncertain: true,
    note: 'FRP 白膠殼、橫向鰭片' },
  { id: 'prostaff_minig', url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'Pro Staff miniG Grille', price: 38000, cur: 'JPY', brand: 'Pro Staff', uncertain: true,
    note: 'G-Class 直縫' },
  { id: 'sixsense_explosion', url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'Six Sense Explosion Classic', price: 80000, cur: 'JPY', brand: 'Six Sense', uncertain: true,
    note: 'Bronco 風橫桿＋SUZUKI 字' },
];


// Snorkel kits sold for the JB74; all mount on the right (1.5L airbox side).
export const SNORKELS = [
  { id: 'none', label: '無', price: 0 },
  { id: 'safari', url: 'https://www.ironman4x4.com.au/products/4x4-snorkel-for-suzuki-jimny-jb74w', label: 'Safari / Ironman 圓管進氣頭', price: 451, cur: 'AUD', brand: 'Ironman 4x4', part: 'ISNORKEL070',
    note: 'Ø89 LLDPE 圓管、前向進氣頭；需切葉子板' },
  { id: 'bravo', url: 'https://bravosnorkel.com/en/suzuki/106-suzuki-jimny-2018-.html', label: 'Bravo Snorkel SSJN', price: 399, cur: 'EUR', brand: 'Bravo Snorkel',
    note: '西班牙製、方形管身貼 A 柱、彎頭側向網狀進氣；免鑽孔（換掉葉子板角飾板）' },
  { id: 'urnieta', url: 'https://urnieta.com/product/salado-snorkel-kit-for-jimny-jb74-jc74/', label: 'URNIETA Salado', price: 839, cur: 'AUD', brand: 'URNIETA', part: '0702021',
    note: 'ABS 方管、矩形百葉進氣頭、側面開槽；免鑽孔，另附旋風前濾頭' },
  { id: 'precleaner', url: 'https://www.jimnybits.com/snorkel-air-pre-filter-pre-cleaner-head-for-3-snorkels-1.html', label: 'Safari 管身＋旋風前濾頭', price: null, cur: 'GBP', brand: 'Safari + PC35', uncertain: true,
    note: 'Ø180 透明旋風碗，先甩掉粉塵' },
  { id: 'sleek', url: 'https://megajimny.com/products/supa-sleek-snorkel-system', label: 'Mega Jimny Supa-Sleek', price: 649, cur: 'AUD', brand: 'Mega Jimny',
    note: '2 吋不鏽鋼細管貼 A 柱、後向小進氣口；免鑽孔、幾乎看不見' },
];

export const MIRRORS = [
  { id: 'stock', label: '原廠電動折疊鏡', price: 0, brand: 'SUZUKI' },
  { id: 'urnieta', url: 'https://urnieta.com/product/salado-side-mirror-kit-for-jimny-jb74-jc74/', label: 'URNIETA Salado 環管後照鏡', price: 949, cur: 'AUD', brand: 'URNIETA', part: '0702022',
    note: '方形鏡頭＋圓管環臂，沿用原廠門上三角座；手動調整，附相機孔' },
  { id: 'damd', url: 'https://easycars.jp/product/damd-truck-side-mirror-for-jimny-jb64-jb74/', label: 'DAMD Truck Mirror', price: 88000, cur: 'JPY', brand: 'DAMD',
    note: '直式卡車鏡＋U 型管臂，消光黑或鍍鉻；含加熱，失去電動折疊' },
];

// Roof racks, awnings, side steps and ladders are modelled parts named
// roofRack_<id>, awning_<id>_<left|right>, sideStep_<id>, ladder_<id>.
export const ROOF_RACKS = [
  { id: 'none', label: '無', price: 0 },
  // ---- 台灣有售
  { id: 'arb', url: 'https://www.ruten.com.tw/item/show?22438729095708', label: 'ARB BASE Rack 1545×1285', price: 45000, cur: 'TWD', brand: 'ARB', part: '1770020 + 17900020',
    note: '鋁擠型平台、燕尾槽側軌、4 支雨槽腳；平台單品 NT$15,000（MRK）；車主實車配置' },
  { id: 'yakima', url: 'https://www.yakima.com.tw/products/locknload-platform', label: 'Yakima LockNLoad 平台 B 1520×1370', price: 23000, cur: 'TWD', brand: 'Yakima', part: '8005045',
    note: '橫向板條 T 槽、4 支雨槽腳（110／150／210mm）；Yakima 台灣售價' },
  { id: 'pioneer', url: 'https://www.ruten.com.tw/item/show?22441909928235', label: 'Rhino-Rack Jimny Overlanding Kit（Pioneer LT）', price: 58300, cur: 'TWD', brand: 'Rhino-Rack',
    part: 'ROLS1', note: '1453×1339、5 道縱向板條、Backbone 橫樑固定；黑四驅售價' },
  { id: 'ipf', url: 'https://www.ipf.co.jp/ipfEc/products/detail/159', label: 'IPF EXP Roof Rack type-A', price: 32000, cur: 'TWD', brand: 'IPF', part: 'EXR-01',
    note: '1400×1250×38.8、12.5kg；日本 ¥85,800、MRK 台灣售價' },
  { id: 'tw_generic', url: 'https://tw.bid.yahoo.com/item/100868689053', label: '機油倉庫 鋁合金平頂行李架', price: 13000, cur: 'TWD', brand: '機油倉庫（台灣）',
    note: '1600×1260、6 支雨槽腳、前導流板；安裝 +NT$1,000' },
  // ---- 進口
  { id: 'platform', url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-current-slii', label: 'Front Runner Slimline II 全長', price: 1579, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ003T',
    note: '1560×1345、6 支雨槽腳、前導流板，31kg' },
  { id: 'fr34', url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-curr-slii-3-4-roof-rack-kit', label: 'Front Runner Slimline II 3/4', price: 1451, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ006T',
    note: '1156×1345、4 支腳' },
  { id: 'jaos', url: 'https://www.jaos.co.jp/product/B411611NS/3848', label: 'JAOS Flat Rack type-B', price: 140800, cur: 'JPY', brand: 'JAOS', part: 'B411611NS',
    note: '1400×1250×32、6 道 T 槽底桿、前導流板；type-A ¥116,600' },
  { id: 'apio', url: 'https://apio.jp/parts/3630-50.html', label: 'APIO Mighty Smart Rack', price: 231000, cur: 'JPY', brand: 'APIO', part: '3630-50',
    note: '1420×1270、前軌前傾兼導流、船用鋁粉體' },
  { id: 'showa_foot', url: 'https://www.showa-garage.shop/shopdetail/000000001017/I59728/', label: 'SHOWA GARAGE A-x Roof Rack 1512', price: 92400, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20080', note: '1500×1250×40 噴砂鋁面' },
  { id: 'basket', url: 'https://www.showa-garage.shop/shopdetail/000000000111/I59728/', label: 'SHOWA GARAGE A-x Full Rack M（籃式）', price: 68200, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20008', note: '1400×1250×130、側籃可拆，直鎖雨槽' },
];

export const AWNINGS = [
  { id: 'none', label: '無', price: 0 },
  // ---- 台灣有售
  { id: 'yakima_s', url: 'https://www.yakima.com.tw/products/slimshady-%E8%BB%8A%E9%82%8A%E5%B8%B3-2-2-5m', label: 'Yakima OverNOut S 2×2.5m', price: 8500, cur: 'TWD', brand: 'Yakima', part: 'KT8007508',
    note: '軟袋 2100 長、12kg；Yakima 台灣售價' },
  { id: 'yakima_l', url: 'https://www.yakima.com.tw/products/overnout_l', label: 'Yakima OverNOut L 2.5×2.5m', price: 11700, cur: 'TWD', brand: 'Yakima', part: 'KTHB0019',
    note: '軟袋 2600 長、18kg' },
  { id: 'yakima_270', url: 'https://www.yakima.com.tw/products/overnout-270', label: 'Yakima OverNOut 270 蝙蝠帳', price: 21600, cur: 'TWD', brand: 'Yakima', part: '8007462/3',
    note: '2286×216×254、後端旋轉、四支臂自撐；左＝駕駛側' },
  { id: 'yakima_270s', url: 'https://www.yakima.com.tw/products/overnout-270', label: 'Yakima OverNOut 270 1.8M 蝙蝠帳', price: 19800, cur: 'TWD', brand: 'Yakima', part: '8007538/9',
    note: '短版 270°，收納約 1850×216×254；架在車頂架側緣上方（車主實車配置）' },
  { id: 'yakima_180', url: 'https://www.yakima.com.tw/products/overnout-180-%E5%81%B4%E9%82%8A%E5%B8%B3', label: 'Yakima OverNOut 180', price: 21600, cur: 'TWD', brand: 'Yakima', part: '8007516',
    note: '2260×229×178、8.7m²、三支臂' },
  { id: 'rhino_compact', url: 'https://www.ruten.com.tw/item/22445161058255/', label: 'Rhino-Rack Batwing Compact 蝙蝠帳', price: 33920, cur: 'TWD', brand: 'Rhino-Rack',
    part: '33120/33121', note: '2000 長、6m²、18kg；黑四驅售價' },
  { id: 'rhino_270', url: 'https://www.rhinorack.com/en-au/products/sport-awnings/awnings/awnings/batwing-compact-awning-left-_33120', label: 'Rhino-Rack Batwing 270', price: 38160, cur: 'TWD', brand: 'Rhino-Rack', part: '33118/33119',
    note: '2500 長、10m²、20.5kg' },
  { id: 'allblack_270', url: 'https://www.ruten.com.tw/item/22245661385396/', label: '黑四驅 ALL BLACK 270° 車邊帳 gen3', price: 18000, cur: 'TWD', brand: '黑四驅（台灣）',
    note: '2m／2.5m 兩種、左開／右開；含 LED 燈條' },
  // ---- 進口
  { id: 'arb_touring_2', url: 'https://www.arb.com.au/product/814406-arb-touring-awning-2000mm-x-2500mm-with-led-light', label: 'ARB Touring 2000×2500 LED', price: null, cur: 'AUD', brand: 'ARB', part: '814406', uncertain: true,
    note: 'PVC 軟袋約 2200 長，12.9kg；經銷商報價' },
  { id: 'arb_touring_25', url: 'https://www.arb.com.au/product/814407-arb-touring-awning-with-light-2500mm-x-2500mm', label: 'ARB Touring 2500×2500 LED', price: null, cur: 'AUD', brand: 'ARB', part: '814407', uncertain: true,
    note: '約 2700 長，14.3kg' },
  { id: 'arb_alu', url: 'https://www.arb.com.au/product/814412-arb-awning-2500mm-x-2500mm-black-aluminium-housing-and-light', label: 'ARB 鋁殼車邊帳 2500×2500', price: null, cur: 'AUD', brand: 'ARB', part: '814412', uncertain: true,
    note: '矩形鋁殼、外側掀蓋，17.8kg' },
  { id: 'darche_270', url: 'https://darche.com.au/products/eclipse-270-g2-right-us-eu-p', label: 'Darche Eclipse 270 G2', price: 1499, cur: 'AUD', brand: 'Darche', part: 'T050801743',
    note: '11.5m²、1000D PVC，後端鋁合金旋軸' },
  { id: 'darche_slim', url: 'https://darche.com.au/products/eclipse-slimline-2-5m-x-2-5m', label: 'Darche Eclipse Slimline 2.5×2.5', price: 579, cur: 'AUD', brand: 'Darche', part: 'T050801793',
    note: '820D 軟袋，14kg' },
  { id: 'ikamper', url: 'https://ikamper.com/products/exoshell-270-awning', label: 'iKamper ExoShell 270', price: 1950, cur: 'USD', brand: 'iKamper', part: 'MB011-002',
    note: '2630×180×184 硬殼鋁盒、11.2m²，30kg' },
];

export const SIDE_STEPS = [
  { id: 'none', label: '無', price: 0 },
  // ---- 台灣
  { id: 'wlm', url: 'https://www.mrk.com.tw/product_ii.html?ID=1905', label: 'WLM 4x4 側踏保桿 WLM001', price: 13800, cur: 'TWD', brand: 'WLM 4x4',
    note: 'Ø50 圓管貼門檻、兩片踏板、鍍鋅粉體黑；用原廠孔位免鑽孔' },
  { id: 'jst', url: 'https://www.mrk.com.tw/product_ii.html?ID=1580', label: 'JST 吉米工坊 側踏保桿 JB74001', price: 8500, cur: 'TWD', brand: 'JST 吉米工坊',
    note: '加強型／特仕版 NT$8,500–11,700；直管＋兩片平踏板' },
  { id: 'tjm', url: 'https://www.mrk.com.tw/product_ii.html?ID=915', label: 'TJM Rock Slider（MRK 代理）', price: 18000, cur: 'TWD', brand: 'TJM',
    part: '735STRSA57X', note: 'Ø51 大樑固定、焊接踏板；支架另購 NT$3,000' },
  // ---- 日本
  { id: 'outclass', url: 'https://outclass.ocnk.net/product/1124', label: 'OUTCLASS サイドステップ', price: 88000, cur: 'JPY', brand: 'OUTCLASS',
    note: '低矮管架＋平板踏面，兼門檻保護；消光黑或 Raptor 塗層' },
  { id: 'apio_guard', url: 'https://apio.jp/parts/3102-69.html', label: 'APIO H.D サイドシルガード', price: 132000, cur: 'JPY', brand: 'APIO', part: '3102-69',
    note: '1350×185 雙層 3mm 硬鋁門檻護甲（無踏板）；窄體限定' },
  { id: 'jaos', url: 'https://www.jaos.co.jp/product/B172522BK/3882', label: 'JAOS サイドステップ', price: 121000, cur: 'JPY', brand: 'JAOS', part: 'B172522BK',
    note: 'Ø76.3 粗管＋樹脂踏墊，16.7kg；規格表標 JC74，請確認適用' },
  { id: 'taniguchi_bar', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: 'TANIGUCHI サイドステップ バータイプ', price: 53900, cur: 'JPY', brand: 'TANIGUCHI',
    note: '長管＋550×145 網狀踏板，兩段高度可調；左 ¥50,600' },
  { id: 'taniguchi_short', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: 'TANIGUCHI 2段調整サイドステップ', price: 41250, cur: 'JPY', brand: 'TANIGUCHI',
    note: '車門下短網踏 550×145；不鏽鋼版 ¥59,400' },
  { id: 'showa', url: 'https://store.shopping.yahoo.co.jp/showa-garage/e00173.html', label: 'SHOWA GARAGE サイドステップ ロング Type2', price: 69300, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00173', note: '純圓管、皺紋黑；JB74 需另購飾板 E00207' },
  { id: 'wildgoose_fold', url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/exterior_64/jm-2262l-jm-2262r.html', label: 'Wild Goose 折疊式踏板 JM-2262', price: 35200, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: '單邊價；510mm 寬 4.2mm 鋼板、可上翻' },
  { id: 'wildgoose_guard', url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/protection_64/jm-2409.html', label: 'Wild Goose サイドシルガードステップ JM-2409', price: 110000, cur: 'JPY',
    brand: 'RV4 Wild Goose', note: '1292 長、外凸 55mm 的門檻護甲，可踩；14.5kg' },
  { id: 'customwagon', url: 'https://www.custom-wagon.com/c/557/jim661', label: 'Custom Wagon 出幅調整サイドステップ', price: 57200, cur: 'JPY', brand: 'Custom Wagon',
    note: '弧形圓管＋花紋踏板，出幅約 50mm 可調' },
  { id: 'spieler', url: 'https://spieler.jp/products/jb64jb74sidestep7575', label: 'SPIELER サイドステップ 7575', price: 88000, cur: 'JPY', brand: 'SPIELER',
    note: '75×75 方管＋鋁面板，用車廂固定孔免鑽' },
  // ---- 澳洲
  { id: 'arb', url: 'https://www.arb.com.au/product/4424010-arb-rock-sliders-with-textured-black-finish-suzuki-jimny', label: 'ARB Rock Slider', price: 891, cur: 'AUD', brand: 'ARB', part: '4424010',
    note: 'Ø60.3 主管、3 支支撐管接大樑、紋理黑，18kg' },
  { id: 'ironman', url: 'https://doubleblackoffroad.com/products/ironman-suzuki-jimny-rock-sliders-2018', label: 'Ironman 4x4 Rock Slider SS070', price: 699, cur: 'AUD', brand: 'Ironman 4x4',
    note: 'Ø50.8×2.6、1280mm、緞面黑' },
  { id: 'hamer', url: 'https://www.hamer4x4.com/product/sm104-rock-slider-for-suzuki-jimny-jb74-2018/', label: 'Hamer 4x4 SM104 Rock Slider', price: null, cur: 'AUD', brand: 'Hamer 4x4', uncertain: true,
    note: '圓管＋格柵踏板，25kg，報價制' },
];

export const LADDERS = [
  { id: 'none', label: '無', price: 0 },
  { id: 'fr', url: 'https://ozjimny.com/products/front-runner-ladder-jimny-models-2023-current-xl', label: 'Front Runner 尾門梯', price: null, cur: 'AUD', brand: 'Front Runner', part: 'LASJ004', uncertain: true,
    note: '4 階、鉸鏈側、勾尾門上緣' },
  { id: 'tube', label: '管狀環形爬梯', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: 'Ø32 管環、勾車頂架後緣、附滅火器座（車主實車配置）' },
];

export const SIMPLE = {
  snorkel:      { label: '呼吸管', brands: 'Safari / Ironman 4x4 / ARB / Rival / APIO',
                  note: '注意左右側別；部分需切葉子板', uncertain: true },
  roofRack:     { label: '車頂架', options: [
                    { id: 'none', label: '無' },
                    { id: 'platform', url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-current-slii', label: '平台式', brand: 'Rhino-Rack Pioneer / Front Runner Slimline II' },
                    { id: 'basket', url: 'https://www.showa-garage.shop/shopdetail/000000000111/I59728/', label: '籃式', brand: 'APIO / JAOS / Ironman 4x4' }] },
  awning:       { label: '側邊帳', options: [
                    { id: 'none', label: '無' },
                    { id: 'left', label: '左側' },
                    { id: 'right', label: '右側' }],
                  brands: 'Rhino-Rack Batwing / ARB / Front Runner / Darche / 23Zero' },
  windowGuards: { label: '鐵窗（窓ガード）', brands: 'APIO / SHOWA GARAGE / Bunker', uncertain: true },
  ladder:       { label: '後爬梯', brands: '多家', note: '可鎖車身或與備胎架整合', uncertain: true },
  rockSliders:  { label: '側踏 / Rock Slider', brands: 'APIO / SHOWA GARAGE / Ironman 4x4', uncertain: true },
  lightBar:     { label: '車頂燈條', brands: '多家' },
  spareBag:     { label: '備胎書包（スペアタイヤバッグ）', brands: '多家', uncertain: true },
};

// Catalogue-only extras (no selectable model variant yet)
export const OTHERS = [
  { id: 'wlm_guard', url: 'https://www.buerjitw.com/products/wlm-%E7%AA%97%E6%88%B6%E9%98%B2%E8%AD%B7%E7%B6%B2-jimny-jb74', label: 'WLM 4x4 後側窗防護網（鐵窗）', price: 5200, cur: 'TWD', brand: 'WLM 4x4', part: 'JB7408 / JB7409',
    note: '每片；795×533 雷射切割方孔板、雨槽夾固定，可掀式；配置器「鐵窗（WLM）」' },
  { id: 'fr_ladder', url: 'https://ozjimny.com/products/front-runner-ladder-jimny-models-2023-current-xl', label: 'Front Runner Jimny 尾門梯', price: null, cur: 'AUD', brand: 'Front Runner', part: 'LASJ004', uncertain: true,
    note: '4 階、鉸鏈側；配置器「後爬梯」' },
  { id: 'ipf_bar', url: 'https://www.ipf-light.com/catalog/642jm2.php', label: 'IPF 600 S-Series 40" 燈條＋A 柱支架', price: null, cur: 'JPY', brand: 'IPF', part: '642SD + 642JM2', uncertain: true,
    note: '配置器「車頂燈條」' },
  { id: 'suzuki_cover', url: 'https://jdmyamato.com/products/y08-sz0001-00024', label: 'Suzuki 原廠硬式備胎蓋', price: null, cur: 'JPY', brand: 'SUZUKI', part: '9923B-77R21-003', uncertain: true,
    note: '硬質樹脂面＋皮革背；配置器「備胎硬殼蓋」' },
  { id: 'trasharoo', url: 'https://agileoffroad.com/products/trasharoo-spare-tire-trash-bag', label: 'Trasharoo 備胎書包', price: null, cur: 'USD', brand: 'Trasharoo', uncertain: true,
    note: '配置器「備胎書包」' },
  { id: 'maxx', url: null, label: 'MAXX Flowforged 8 輻 16×7', price: null, cur: 'TWD', brand: 'MAXX', uncertain: true, note: '消光黑（車主實車配置）' },
];

export const SPARE_COVERS = [
  { id: 'soft', label: '軟式備胎套' },
  { id: 'hard', label: '硬殼備胎蓋' },
  { id: 'none', label: '裸露備胎' },
];

/** Which warnings apply to a configuration. Pure function so the UI and any
 *  future export share one source of truth. */
export function validate(cfg, { tyre, lift, bodyLift, wheel }) {
  const out = [];
  const totalLift = (lift?.lift ?? 0) + (bodyLift?.body ?? 0);
  if (tyre.needLift > totalLift) {
    out.push({ level: 'error',
      msg: `${tyre.label} 需要約 ${tyre.needLift}mm 舉升，目前只有 ${totalLift}mm` });
  }
  if (tyre.needBody > (bodyLift?.body ?? 0)) {
    out.push({ level: 'error',
      msg: `${tyre.label} 實務上需要 ${tyre.needBody}mm 車身舉升才有足夠輪拱空間` });
  }
  if (tyre.rim !== wheel.rim) {
    out.push({ level: 'error', msg: `${tyre.label} 是 ${tyre.rim} 吋胎，但輪框是 ${wheel.rim} 吋` });
  }
  if (tyre.legal === false) {
    out.push({ level: 'warn', msg: `${tyre.label} 超出澳洲法規上限（235/75R15）；各地法規請自行確認` });
  }
  if (tyre.severe) {
    out.push({ level: 'warn', msg: '33 吋需要減速齒輪（17/87），否則一檔起步與油耗會明顯惡化' });
  }
  if ((lift?.lift ?? 0) >= 75) {
    out.push({ level: 'info', msg: '75mm 以上需 Caster 修正、可調橫拉桿、延長煞車油管與緩衝塊' });
  }
  if ((lift?.lift ?? 0) > 0 && (lift?.lift ?? 0) <= 50 && tyre.needBody > 0) {
    out.push({ level: 'info', msg: '懸吊舉升只抬靜態高度，壓縮行程時輪拱空間不變 — 這是要加車身舉升的原因' });
  }
  if (lift?.id === 'apio40') {
    out.push({ level: 'warn', msg: 'APIO 7440Ti 僅支援右駕（後彈簧左右不等長）' });
  }
  if (wheel.offset <= -20) {
    out.push({ level: 'info', msg: `offset ${wheel.offset} 會明顯外擴輪距，需確認輪拱覆蓋與法規` });
  }
  return out;
}

export function priceOf(list, id) {
  const it = list.find((x) => x.id === id);
  return it?.price ?? null;
}
