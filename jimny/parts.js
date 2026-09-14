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

export const LIFTS = [
  { id: 'stock', label: '原廠', lift: 0, body: 0, price: 0, brand: '—',
    note: '原廠離地 210mm' },
  { id: 'ms20', label: 'MONSTER SPORT 20mm 彈簧', lift: 20, body: 0, price: 37400, cur: 'JPY',
    brand: 'MONSTER SPORT', part: '520500-5600M',
    note: '只換彈簧（23.0/24.5 N/mm），沿用原廠避震與煞車油管' },
  { id: 'apio20', label: 'APIO 7420SA', lift: 20, body: 0, price: 1145, cur: 'USD', brand: 'APIO',
    note: '彈簧＋避震組' },
  { id: 'sg30', label: 'SHOWA GARAGE 30mm', lift: 30, body: 0, price: null, cur: 'JPY',
    brand: 'SHOWA GARAGE', uncertain: true, note: '入門 1 吋套件，價格未查證' },
  { id: 'jaos40', label: 'JAOS Battlez Lift Up Set AJ', lift: 38, body: 0, price: null, cur: 'JPY',
    brand: 'JAOS', part: 'A732518C', uncertain: true,
    note: 'Coil Ti-W 19.8/20.5 N/mm，+35〜40mm' },
  { id: 'apio40', label: 'APIO 7440Ti', lift: 40, body: 0, price: 2142, cur: 'USD', brand: 'APIO',
    note: '含前後橫拉桿、Caster 襯套、緩衝墊片、延長煞車油管。⚠ 僅支援右駕' },
  { id: 'dob40', label: 'Dobinsons Nitro-Gas 40mm', lift: 40, body: 0, price: 1329, cur: 'AUD',
    brand: 'Dobinsons' },
  { id: 'omr40', label: 'ARB Old Man Emu 40mm', lift: 40, body: 0, price: 2410, cur: 'AUD', brand: 'ARB' },
  { id: 'im50', label: 'Ironman 4x4 Nitro Gas Heavy', lift: 50, body: 0, price: 1757, cur: 'AUD',
    brand: 'Ironman 4x4',
    note: '含延長煞車油管、延長緩衝塊、橫樑下降座、偏心 Caster 襯套' },
  { id: 'sg50', label: 'SHOWA GARAGE SG Custom 50 X-SHOCK', lift: 50, body: 0, price: 211200, cur: 'JPY',
    brand: 'SHOWA GARAGE', note: '依避震等級 ¥211,200–370,700' },
  { id: 'sg50b', label: 'SHOWA GARAGE SG Custom 50 Ennepetal E-12', lift: 50, body: 0, price: 323400, cur: 'JPY',
    brand: 'SHOWA GARAGE', note: 'B 規 ¥335,500／BA 規 ¥480,700' },
  { id: 'sg75', label: 'SHOWA GARAGE SG Custom 75 X-SHOCK', lift: 75, body: 0, price: 234300, cur: 'JPY',
    brand: 'SHOWA GARAGE', note: '含緩衝套與蓋；B 規 ¥246,400／BA 規 ¥389,400' },
  { id: 'dob75', label: 'Dobinsons IMS 三向可調 75mm', lift: 75, body: 0, price: 3699, cur: 'AUD',
    brand: 'Dobinsons',
    note: '含橫樑下降、前後強化可調橫拉桿、偏心 Caster 襯套、大燈水平感應器支架' },
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
  { id: 'wildboar', label: 'APIO WILDBOAR X', rim: 15, width: 6.0, offset: -5, style: 'spoke',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true, note: '15×6.0J −5' },
  { id: 'wildboar16', label: 'APIO WILDBOAR SR 16', rim: 16, width: 5.5, offset: 20, style: 'spoke',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true },
  { id: 'bradley', label: 'Bradley V', rim: 16, width: 5.5, offset: 22, style: 'spoke',
    price: 37400, cur: 'JPY', brand: '4x4 Engineering', note: '每顆單價；另有 +0 Jimny spec' },
  { id: 'xtremej', label: 'MLJ XTREME-J XJ04', rim: 16, width: 5.5, offset: 22, style: 'spoke',
    price: null, cur: 'JPY', brand: 'MLJ', uncertain: true },
  { id: 'te37xt', label: 'RAYS TE37XT M-SPEC for J', rim: 16, width: 5.5, offset: 20, style: 'spoke',
    price: null, cur: 'JPY', brand: 'RAYS', note: '鍛造一件式，2025 年起；Bronze／Blast Black' },
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

export const TYRE_MODELS = [
  'BFGoodrich All-Terrain T/A KO2 / KO3', 'Yokohama GEOLANDAR A/T G015',
  'Yokohama GEOLANDAR M/T G003', 'Toyo Open Country A/T III',
  'Falken Wildpeak A/T3W', 'Maxxis AT811 / Bighorn 764',
  'Bridgestone Dueler D697', 'General Grabber AT3', 'Goodyear Wrangler MT/R',
];

export const FRONT_BUMPERS = [
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  { id: 'delete', label: '短保桿 / Bumper Delete', variant: 'delete', price: null, uncertain: true,
    brand: '多家', note: '改善接近角，通常犧牲原廠霧燈與感應器' },
  { id: 'tube', label: '管狀前保桿', variant: 'tube', price: null, uncertain: true, brand: '多家' },
  { id: 'bull', label: 'Bull Bar 前護槓', variant: 'bull', price: null, uncertain: true,
    brand: 'ARB / Ironman 4x4', note: '需確認是否保留原廠感應器' },
  { id: 'winch', label: '絞盤保桿', variant: 'winch', price: null, uncertain: true,
    brand: 'ARB / Rival 4x4', note: '可裝絞盤' },
];

export const REAR_BUMPERS = [
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  { id: 'delete', label: '後保桿 Delete', variant: 'delete', price: null, uncertain: true },
  { id: 'tube', label: '管狀後保桿', variant: 'tube', price: null, uncertain: true, brand: '多家' },
];

export const GRILLES = [
  { id: 'stock', label: '原廠五格柵', price: 0, brand: 'SUZUKI', note: '5 道直立柵欄' },
  { id: 'retro', label: '復古橫柵（JA11 風格）', price: null, uncertain: true,
    brand: 'DAMD / AheadTAKE', note: '把 JB74 的臉改成舊世代橫柵造型' },
  { id: 'mesh', label: '網狀水箱護罩', price: null, uncertain: true, brand: '多家' },
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
