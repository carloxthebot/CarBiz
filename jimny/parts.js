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
  { id: 'klc30', label: 'KLC Heritage 轟 彈簧', inch: '1"', lift: 30, body: 0, price: 38500, cur: 'JPY',
    brand: 'KLC', note: '只換彈簧，沿用原廠避震；車檢 OK' },
  { id: 'sg25', label: 'SHOWA GARAGE 1 吋彈簧', inch: '1"', lift: 25, body: 0, price: 40700, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00350', note: '只換彈簧；建議加橫拉桿組（含拉桿 ¥90,200）' },
  { id: 'ms20', label: 'MONSTER SPORT type-2 20mm', inch: '1"', lift: 20, body: 0, price: 94600, cur: 'JPY',
    brand: 'MONSTER SPORT', part: '510502-5600ML', note: '彈簧＋14 段避震＋後大燈水平感應器支架' },
  { id: 'apio20', label: 'APIO 7420SA', inch: '1"', lift: 20, body: 0, price: 126500, cur: 'JPY', brand: 'APIO',
    part: '1028-1AA', note: '彈簧＋14 段避震；免換煞車油管；車檢 OK' },
  { id: 'es30', label: '4x4 Engineering Country 30mm', inch: '1"', lift: 30, body: 0, price: 123000, cur: 'JPY',
    brand: '4x4 Engineering', part: '74743-31', note: '彈簧＋Harmoflex 14 段避震；沿用原廠煞車油管' },
  // ---- 1.5 吋 (40mm)
  { id: 'jaos40', label: 'JAOS BATTLEZ VFS ver.A(40) Complete', inch: '1.5"', lift: 40, body: 0, price: 184800,
    cur: 'JPY', brand: 'JAOS', part: 'A734518Z', note: '彈簧、避震、長煞車油管、前後橫拉桿、Caster 襯套' },
  { id: 'apio40', label: 'APIO 7440Ti', inch: '1.5"', lift: 40, body: 0, price: 276100, cur: 'JPY', brand: 'APIO',
    part: '1034-1AE', note: '全套：長行程避震、前後橫拉桿、Caster 襯套、長煞車油管。⚠ 僅支援右駕' },
  { id: 'omr40', label: 'ARB Old Man Emu 40mm', inch: '1.5"', lift: 40, body: 0, price: 2410, cur: 'AUD', brand: 'ARB',
    note: '含橫樑補強、Panhard 座、煞車油管延長、Caster 襯套；彈簧依保桿／絞盤重量選' },
  { id: 'dob40', label: 'Dobinsons IMS Monotube 40mm', inch: '1.5"', lift: 40, body: 0, price: 1949, cur: 'AUD',
    brand: 'Dobinsons' },
  { id: 'td40', label: 'Tough Dog Foam Cell 40mm', inch: '1.5"', lift: 40, body: 0, price: 1467, cur: 'AUD',
    brand: 'Tough Dog' },
  // ---- 2 吋 (50mm)
  { id: 'sg50', label: 'SHOWA GARAGE SG Custom 50 Ennepetal E-12', inch: '2"', lift: 50, body: 0, price: 323400,
    cur: 'JPY', brand: 'SHOWA GARAGE', part: 'S00853', note: 'BA 全套 ¥480,700（加長煞車油管＋橫拉桿）' },
  { id: 'cusco50', label: 'CUSCO 2 吋套件（50–75 可調）', inch: '2"', lift: 50, body: 0, price: null, cur: 'JPY',
    brand: 'CUSCO', part: '60N-6JS-U20', uncertain: true, note: '14 段避震、螺牙墊高可調、延長煞車油管；日本售價未查證' },
  { id: 'im50', label: 'Ironman 4x4 Nitro Gas 50mm', inch: '2"', lift: 50, body: 0, price: 1757, cur: 'AUD',
    brand: 'Ironman 4x4', part: 'SUZ010BKG', note: '含延長煞車油管、橫樑下降座、2° Caster 襯套、延長緩衝塊' },
  // ---- 2.5 吋 (60mm)
  { id: 'tg60', label: 'TANIGUCHI SOLVE ACE60', inch: '2.5"', lift: 60, body: 0, price: 216040, cur: 'JPY',
    brand: 'TANIGUCHI', note: '彈簧、避震、長油管、Caster 襯套、橫拉桿；另需 SOLVE 橫樑（+¥27,500）' },
  { id: 'td60', label: 'Tough Dog Foam Cell 60mm', inch: '2.5"', lift: 60, body: 0, price: null, cur: 'AUD',
    brand: 'Tough Dog', uncertain: true, note: '含編織煞車油管；報價制' },
  // ---- 3 吋 (75mm)
  { id: 'sg75', label: 'SHOWA GARAGE SG Custom 75 X-SHOCK', inch: '3"', lift: 75, body: 0, price: 253000, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00472', note: 'BA 全套 ¥394,900；需另購 Caster 修正臂' },
  { id: 'es70', label: '4x4 Engineering Country 70mm', inch: '3"', lift: 70, body: 0, price: 315000, cur: 'JPY',
    brand: '4x4 Engineering', uncertain: true, note: '全套含橫樑下降、傳動軸墊片、油管、橫拉桿、轉向阻尼' },
  { id: 'dob75', label: 'Dobinsons IMS 遠端氣瓶 75mm', inch: '3"', lift: 75, body: 0, price: 3699, cur: 'AUD',
    brand: 'Dobinsons', note: '含橫樑下降、前後可調橫拉桿、Caster 襯套、大燈水平支架、延長油管' },
  { id: 'br75', label: 'Black Raptor 3" 全套', inch: '3"', lift: 75, body: 0, price: null, cur: 'GBP',
    brand: 'JimnyBits', uncertain: true, note: '含 Caster 修正拉桿臂＋可調 Panhard' },
  // ---- 4 吋 (100mm)
  { id: 'br100', label: 'Black Raptor 4" 全套', inch: '4"', lift: 100, body: 0, price: 1586, cur: 'GBP',
    brand: 'JimnyBits', note: '彈簧、避震、4 支 Caster 修正臂、2 支可調 Panhard、編織油管、橫樑下降；左右駕彈簧不同' },
  { id: 'combo100', label: '2" 懸吊 + 2" 車身舉升', inch: '4"', lift: 50, body: 50, price: null, cur: 'AUD',
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
  { id: 'showa_iron', label: 'SHOWA GARAGE Iron Bumper', price: 128700, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00900', note: 'Ø60 鋼管、兩端 45° 後彎；含 3mm 鋁下護板與霧燈架（本體單售 ¥90,750）' },
  { id: 'klc_trad', label: 'KLC Heritage Traditional Bumper', price: 104500, cur: 'JPY', brand: 'KLC',
    note: '全不鏽鋼雙管，象牙白／黑／拋光；含霧燈架（無霧燈架 ¥93,500）。顯示為車身同色' },
  { id: 'outclass_t2', label: 'OUTCLASS TYPE2 絞盤鐵保桿', price: 140800, cur: 'JPY', brand: 'OUTCLASS',
    note: '鐵製、含絞盤床與 4 顆 LED 方燈；出廠未烤漆（可選 Raptor 塗層）' },
  { id: 'stubby_led', label: '短版平面鐵保桿＋LED 方燈', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: '兩輪之間的短鐵桿，車牌與兩顆 4 燈 LED 鎖在正面，護罩下方鏤空（車主實車配置）' },
];

export const REAR_BUMPERS = [
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  { id: 'tube', label: '管狀後保桿（含尾燈座）', price: null, cur: 'TWD', brand: 'OUTCLASS / 多家', uncertain: true,
    note: 'Ø76 直管、方形封板、尾燈座板、右側排氣尾管、拖鉤（車主實車配置）' },
];

export const GRILLES = [
  { id: 'stock', label: '原廠五格柵', price: 0, brand: 'SUZUKI', note: '5 道直立柵欄，中央 S 標' },
  { id: 'showa_hex', label: 'SHOWA GARAGE ABS 蜂巢護罩', price: 16500, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00500', note: 'ABS 素材黑（烤漆版 E00502 ¥31,900）；中央蜂巢網開口' },
  { id: 'outclass_g', label: 'OUTCLASS Vintage G Grille', price: 57750, cur: 'JPY', brand: 'OUTCLASS',
    note: 'ASA 樹脂紋理黑；4 道橫柵＋中央直柱，後方細網' },
  { id: 'hbar_suzuki', label: '橫柵護罩＋SUZUKI 白字', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: '7 道橫柵、方形大燈座、白色 SUZUKI 字樣（車主實車配置）' },
  { id: 'klc_sj', label: 'KLC Face Grille SJ（七孔）', price: 93500, cur: 'JPY', brand: 'KLC',
    note: 'SJ10 復古七直孔，含鋁網與反光片；ABS 烤漆版（素材 ¥60,500）。顯示為車身同色' },
];


export const SIMPLE = {
  snorkel:      { label: '呼吸管', brands: 'Safari / Ironman 4x4 / ARB / Rival / APIO',
                  note: '注意左右側別；部分需切葉子板', uncertain: true },
  roofRack:     { label: '車頂架', options: [
                    { id: 'none', label: '無' },
                    { id: 'platform', label: '平台式', brand: 'Rhino-Rack Pioneer / Front Runner Slimline II' },
                    { id: 'basket', label: '籃式', brand: 'APIO / JAOS / Ironman 4x4' }] },
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
