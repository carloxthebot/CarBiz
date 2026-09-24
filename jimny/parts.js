// Real JB74 parts catalogue. Every entry is a product that exists; prices are
// approximate and in the currency the maker quotes. `uncertain: true` marks
// anything research could not pin down — shown in the UI rather than hidden,
// because a configurator that invents specs is worse than one that admits gaps.
//
// The geometry each option drives lives in `fit`: lift in mm, tyre outer
// diameter in mm, rim diameter in inches. Those three are what move the model.

// Taiwan sells one trim (JIMNY GLX) in eight colours. Suzuki Taiwan has never
// published a paint code for any of them, so the codes below are the Japanese
// equivalents matched against the official Taiwanese swatches and catalogue —
// docs/jb74-colors-tw.json records the sampled values behind each one.
//
// `hex` is a daylight albedo for the renderer, not a paint chip: Suzuki's own
// web chips for Chiffon Ivory (#f1e4af) and Medium Gray (#94989a) are far
// lighter than the real paint and were rejected. `name` leads with the name
// Taiwan actually sells the colour under.
//
// 黃色 and 藍色 reach Taiwan only as the black-roof two-tone, so switch the
// 雙色車頂 toggle on for them; 米黑色 is 米色 with the same toggle.
export const COLORS = [
  { code: 'ZJ3', name: '黑色（Bluish Black Pearl 3）',        hex: 0x16191c, twoTone: false, tw: true,
    note: '台灣 2022 年才加入；深藍調珍珠黑' },
  { code: 'ZVL', name: '灰色（Medium Gray）',                 hex: 0x63645f, twoTone: false, tw: true,
    note: '台灣自 2019 年連續供應的素色灰' },
  { code: 'ZVR', name: '白色（Pure White Pearl）',            hex: 0xf2f3f0, twoTone: false, tw: true,
    note: '台灣官方只寫「白色」未標代碼，珍珠白 ZVR 與素白 26U 兩者色相幾乎相同' },
  { code: 'ZZC', name: '軍綠色（Jungle Green）',              hex: 0x444a3a, twoTone: false, tw: true,
    note: '台灣自 2019 年連續供應' },
  { code: 'ZVG', name: '米色（Chiffon Ivory Metallic）',      hex: 0xc3b79c, twoTone: '2BW', tw: true,
    note: '2025 年才單獨上市；開雙色車頂即為台灣的「米黑色」' },
  { code: 'ZZB', name: '黃色（Kinetic Yellow）',              hex: 0xcbd232, twoTone: 'DG5', tw: '雙色',
    note: '台灣只進雙色的「黃黑色」，日規才有純黃' },
  { code: 'ZWY', name: '藍色（Brisk Blue Metallic）',         hex: 0x0f74a8, twoTone: 'CZW', tw: '雙色',
    note: '台灣只進雙色的「藍黑色」，2022–2024 曾停售' },
  { code: 'Z2S', name: '絲光銀（Silky Silver Metallic）',     hex: 0xc6c8c7, twoTone: false, tw: false,
    note: '日規全期間都有，台灣從未導入' },
];
export const ROOF_BLACK = 0x16191c;   // ZJ3 — the only two-tone roof Suzuki offers

// Suspension lifts, grouped by the inch class the trade uses. `lift` is the
// static height gain in mm that moves the model; `inch` is the class label.
// Beyond 50mm the front propshaft meets the stock crossmember, so every kit
// from 2" up needs a drop bracket; 3"+ needs caster correction; 4" is in
// practice 2–3" of suspension plus a body lift.
export const LIFTS = [
  { id: 'stock', label: '原廠', inch: '原廠', lift: 0, body: 0, price: 0, brand: 'SUZUKI',
    note: '原廠離地 210mm；原廠高度最大可裝 215/70R16' },
  // ---- 1 吋 (20–30mm)
  { id: 'klc30', url: 'https://www.klc-div.com/heritage/product/suspension/lift-upspringtodoroki/', label: 'Heritage 轟 升高彈簧', inch: '1"', lift: 30, body: 0, price: 38500, cur: 'JPY',
    brand: 'KLC', note: '只換彈簧，沿用原廠避震；車檢 OK' },
  { id: 'sg25', url: 'https://www.showa-garage.shop/shopdetail/000000000529/', label: '1 吋升高彈簧', inch: '1"', lift: 25, body: 0, price: 40700, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00350', note: '只換彈簧；建議加橫拉桿組（含拉桿 ¥90,200）' },
  { id: 'ms20', url: 'https://www.monster-sport.com/product/parts/sus/jb64w_hisusset_2/', label: 'type-2 20mm 懸吊組', inch: '1"', lift: 20, body: 0, price: 94600, cur: 'JPY',
    brand: 'MONSTER SPORT', part: '510502-5600ML', note: '彈簧＋14 段避震＋後大燈水平感應器支架' },
  { id: 'apio20', url: 'https://www.apio.jp/parts/1028-1aa.html', label: '7420SA 懸吊組', inch: '1"', lift: 20, body: 0, price: 126500, cur: 'JPY', brand: 'APIO',
    part: '1028-1AA', note: '彈簧＋14 段避震；免換煞車油管；車檢 OK' },
  { id: 'es30', url: 'https://www.4x4es.co.jp/2021/02/19/', label: 'Country 30mm 懸吊組', inch: '1"', lift: 30, body: 0, price: 123000, cur: 'JPY',
    brand: '4x4 Engineering', part: '74743-31', note: '彈簧＋Harmoflex 14 段避震；沿用原廠煞車油管' },
  // ---- 1.5 吋 (40mm)
  { id: 'jaos40', url: 'https://www.jaos.co.jp/product/A734518Z/3218/', label: 'BATTLEZ VFS ver.A 40mm 全套組', inch: '1.5"', lift: 40, body: 0, price: 184800,
    cur: 'JPY', brand: 'JAOS', part: 'A734518Z', note: '彈簧、避震、長煞車油管、前後橫拉桿、Caster 襯套' },
  { id: 'apio40', url: 'https://www.apio.jp/parts/1034-1ae.html', label: '7440Ti 懸吊全套組', inch: '1.5"', lift: 40, body: 0, price: 276100, cur: 'JPY', brand: 'APIO',
    part: '1034-1AE', note: '全套：長行程避震、前後橫拉桿、Caster 襯套、長煞車油管。⚠ 僅支援右駕' },
  { id: 'omr40', url: 'https://megajimny.com/products/arb-old-man-emu-40mm-lift-kit-2018-jimny', label: 'Old Man Emu 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 2410, cur: 'AUD', brand: 'ARB',
    note: '含橫樑補強、Panhard 座、煞車油管延長、Caster 襯套；彈簧依保桿／絞盤重量選' },
  { id: 'dob40', url: 'https://megajimny.com/products/dobinsons-ims-monotube-40mm-lift-kit', label: 'IMS Monotube 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 1949, cur: 'AUD',
    brand: 'Dobinsons' },
  { id: 'td40', url: 'https://www.toughdog.com.au/Products/SuzukiJimnyJB74.aspx', refs: ['https://www.directsuspensions.com.au/products/tough-dog-40mm-lift-kit-for-suzuki-jimny-jb74-3-door-2019-on'], label: 'Foam Cell 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 1467, cur: 'AUD',
    brand: 'Tough Dog' },
  // ---- 2 吋 (50mm)
  { id: 'sg50', url: 'https://www.showa-garage.shop/shopbrand/I84526', label: 'SG Custom 50 Ennepetal 懸吊組', inch: '2"', lift: 50, body: 0, price: 323400,
    cur: 'JPY', brand: 'SHOWA GARAGE', part: 'S00853', note: 'BA 全套 ¥480,700（加長煞車油管＋橫拉桿）' },
  { id: 'cusco50', url: 'https://shop.nstparts.com/products/cusco-2-inch-lift-suspension-kit-suzuki-jimny-jb74', label: '2 吋懸吊組（50–75mm 可調）', inch: '2"', lift: 50, body: 0, price: null, cur: 'JPY',
    brand: 'CUSCO', part: '60N-6JS-U20', uncertain: true, note: '14 段避震、螺牙墊高可調、延長煞車油管；日本售價未查證' },
  { id: 'im50', url: 'https://ozjimny.com/products/ironman-4x4-50mm-suspension-lift-kit-constant-front-load-with-gas-shock-absorbers', label: 'Nitro Gas 50mm 懸吊組', inch: '2"', lift: 50, body: 0, price: 1757, cur: 'AUD',
    brand: 'Ironman 4x4', part: 'SUZ010BKG', note: '含延長煞車油管、橫樑下降座、2° Caster 襯套、延長緩衝塊' },
  // ---- 2.5 吋 (60mm)
  { id: 'tg60', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_suspension/', label: 'SOLVE ACE60 懸吊組', inch: '2.5"', lift: 60, body: 0, price: 216040, cur: 'JPY',
    brand: 'TANIGUCHI', note: '彈簧、避震、長油管、Caster 襯套、橫拉桿；另需 SOLVE 橫樑（+¥27,500）' },
  { id: 'td60', url: 'https://www.toughdog.com.au/Products/SuzukiJimnyJB74.aspx', refs: ['https://ozjimny.com/products/tough-dog-4wd-suspension-60mm-suspension-lift-kit-with-braided-brake-lines-steel-bullbar-no-winch'], label: 'Foam Cell 60mm 懸吊組', inch: '2.5"', lift: 60, body: 0, price: null, cur: 'AUD',
    brand: 'Tough Dog', uncertain: true, note: '含編織煞車油管；報價制' },
  // ---- 3 吋 (75mm)
  { id: 'sg75', url: 'https://www.showa-garage.shop/shopbrand/I84527/', label: 'SG Custom 75 X-SHOCK 懸吊組', inch: '3"', lift: 75, body: 0, price: 253000, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00472', note: 'BA 全套 ¥394,900；需另購 Caster 修正臂' },
  { id: 'es70', url: 'https://www.4x4es.co.jp/2025/04/08/', label: 'Country 70mm 懸吊組', inch: '3"', lift: 70, body: 0, price: 315000, cur: 'JPY',
    brand: '4x4 Engineering', uncertain: true, note: '全套含橫樑下降、傳動軸墊片、油管、橫拉桿、轉向阻尼' },
  { id: 'dob75', url: 'https://megajimny.com/products/dobinsons-ims-monotube-75mm-lift-kit', label: 'IMS 遠端氣瓶 75mm 懸吊組', inch: '3"', lift: 75, body: 0, price: 3699, cur: 'AUD',
    brand: 'Dobinsons', note: '含橫樑下降、前後可調橫拉桿、Caster 襯套、大燈水平支架、延長油管' },
  { id: 'br75', url: 'https://www.jimnybits.com/3-75mm-suzuki-jimny-black-raptor-full-suspension-lift-kit-2019-on.html', label: 'Black Raptor 3 吋懸吊全套', inch: '3"', lift: 75, body: 0, price: null, cur: 'GBP',
    brand: 'JimnyBits', uncertain: true, note: '含 Caster 修正拉桿臂＋可調 Panhard' },
  // ---- 4 吋 (100mm)
  { id: 'br100', url: 'https://www.jimnybits.com/4-100mm-suzuki-jimny-black-raptor-full-suspension-lift-kit-2019-on.html', label: 'Black Raptor 4 吋懸吊全套', inch: '4"', lift: 100, body: 0, price: 1586, cur: 'GBP',
    brand: 'JimnyBits', note: '彈簧、避震、4 支 Caster 修正臂、2 支可調 Panhard、編織油管、橫樑下降；左右駕彈簧不同' },
  { id: 'sg50bl', label: '50mm 懸吊＋25mm 車身舉升', inch: '3"', lift: 50, body: 25, price: null, cur: 'JPY',
    brand: 'SHOWA GARAGE / JimnyBits', uncertain: true, note: '2 吋懸吊加車身墊高，31 吋胎的常見組合' },
  { id: 'combo100', url: 'https://www.zookoffroad.com.au/product-page/jimny-4-100mm-black-raptor-full-suspension-lift-kit-jb', label: '2 吋懸吊＋2 吋車身舉升', inch: '4"', lift: 50, body: 50, price: null, cur: 'AUD',
    brand: 'Black Raptor / ZOOK', uncertain: true, note: '用車身舉升取代 Caster 修正臂與 Panhard 的組合路線' },
];


export const BODY_LIFTS = [
  { id: 'none', label: '不裝', body: 0, price: 0 },
  { id: 'bl25', label: '25mm 車身舉升組', body: 25, price: null, cur: 'GBP', brand: 'JimnyBits',
    note: '墊高車身本體，真正增加輪拱空間，免切割。31 吋的標準搭配' },
];

export const WHEELS = [
  { id: 'oem', label: '原廠鋁圈', rim: 15, width: 5.5, offset: 5, style: 'stock',
    price: 0, brand: 'SUZUKI', note: 'ET+5／5×139.7／中心孔 108mm' },
  { id: 'oemsteel', label: '原廠鋼製輪框（JL）', rim: 15, width: 5.5, offset: 5, style: 'steel',
    price: 0, brand: 'SUZUKI' },
  { id: 'wildboar', label: 'WILDBOAR X 八輻輪框', rim: 15, width: 6.0, offset: -5, needsFlares: true, style: 'eight',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true, note: '15×6.0J −5' },
  { id: 'wildboar16', label: 'WILDBOAR SR 16 吋輪框', rim: 16, width: 5.5, offset: 20, style: 'eight',
    price: null, cur: 'JPY', brand: 'APIO', uncertain: true },
  { id: 'bradley', label: 'Bradley V 六輻輪框', rim: 16, width: 5.5, offset: 22, style: 'six',
    price: 37400, cur: 'JPY', brand: '4x4 Engineering', note: '每顆單價；另有 +0 Jimny spec' },
  { id: 'xtremej', label: 'XTREME-J XJ04 輪框', rim: 16, width: 5.5, offset: 22, style: 'eight',
    price: null, cur: 'JPY', brand: 'MLJ', uncertain: true },
  { id: 'te37xt', label: 'TE37XT M-SPEC for J 鍛造輪框', rim: 16, width: 5.5, offset: 20, style: 'six',
    price: null, cur: 'JPY', brand: 'RAYS', note: '鍛造一件式，2025 年起；Bronze／Blast Black' },
  { id: 'maxx', photo: true, label: '旋壓 10 輻輪框', rim: 16, width: 6.0, offset: 0, style: 'ten',
    price: 4100, cur: 'TWD', brand: 'MAXX（台灣）',
    note: '台灣賣的是 16×6.0J ±0，不需要爆龜。消光黑／古銅／槍灰／黑底亮唇；超前輪業、真便宜輪胎館等多家現貨 NT$4,000–4,200 一顆。車主實車配置' },
  // ---- 復古框（2026-09 調查）。JB74 中心孔 108.1mm，日規 5×139.7 一律 108.25-108.8 可用；
  // Cragar S/S（91.44）與 American Racing TT-O（83.06）孔徑太小，無法用轉接環補救，故未收錄
  { id: 'dean_cross', photo: false, url: 'https://www.dean-wheels.com/', label: 'Cross Country 五槽鋼圈臉', rim: 16, width: 6.0, offset: -5, needsFlares: true, style: 'slot5',
    price: 10500, cur: 'TWD', brand: 'DEAN', note: '水平五槽鋼圈臉，中心鍍鉻板可拆，拆掉即露出 5 幅。台灣 MRK 4X4 現貨 NT$10,500 一顆，Marguerite White／Mat Black' },
  { id: 'showa_eight', photo: false, url: 'https://showa-garage.shop/shopbrand/I1582', label: 'IGNITION EIGHT 八柱輪框', rim: 16, width: 6.0, offset: 0, style: 'eightpin',
    price: 37400, cur: 'JPY', brand: 'SHOWA GARAGE', uncertain: true,
    note: '8 根支柱＋亮面 pin bolt＋側唇一圈鉚釘，霧黑／霧銅。日本定價 ¥37,400 一顆；台灣通路未查證到現貨' },
  { id: 'daytona_ss', photo: false, url: 'https://www.mljinc.co.jp/product/daytona_ss/daytona_ss', label: 'DAYTONA SS 兩件式鋼圈', rim: 16, width: 6.0, offset: 0, style: 'daytona',
    price: 29700, cur: 'JPY', brand: 'MLJ', note: '10 孔 rally 鋼圈、全平面零凹陷、螺帽全露；5×139.7 不附中心蓋。街價約 ¥13,360。白色版只有 16×5.5J +20' },
  { id: 'super_moon', photo: false, url: 'https://shop.beyond-jpn.com/collections/%E3%83%9B%E3%82%A4%E3%83%BC%E3%83%AB', label: 'SUPER MOON 月亮盤', rim: 16, width: 6.0, offset: -5, needsFlares: true, style: 'moon',
    price: 19800, cur: 'JPY', brand: 'Beyond Japan', note: '完全無孔的光滑碟盤，最極端的 moon disc 語彙。黑／白 ¥19,800、鍍鉻 ¥23,100' },
  { id: 'watanabe_f8', photo: false, url: 'https://www.rs-watanabe.co.jp/jimny/', label: 'F8 八輻輪框', rim: 16, width: 5.5, offset: 0, style: 'watanabe',
    price: 45000, cur: 'JPY', brand: 'RS Watanabe', note: 'Sierra 專用 ±0；正統 8 幅、幅面平薄、中心開放（蓋另購）。黑色標配，銀／金／鎂／紅／藍／白 +¥3,000。台灣無代理' },
  { id: 'mrk_retro', photo: false, url: 'https://www.mrk.com.tw/', label: '復古輪框（陶瓷白）', rim: 16, width: 5.5, offset: 20, style: 'daytona',
    price: 5500, cur: 'TWD', brand: 'MRK', note: '台製現貨、中心孔 108.1 正確；陶瓷白／銀／消光黑。15×6.0J −5 為 NT$3,980' },
  // ---- 2026-09 依各家型錄補齊。輪轂孔徑各家不同（Enkei 108.2、MLJ/Watanabe 108.5、
  // DEAN/RAYS 108.8、Hayashi/BRADLEY 110-110.5 靠螺帽定心）；小於 108.1 裝不上且無法用轉接環補救。
  // offset 低於 -5 會凸出葉子板，需搭配爆龜（needsFlares）
  { id: 'wildboar_d', url: 'https://apio.jp/parts/7200-60.html', label: 'WILDBOAR D 蓮根紋輪框', rim: 16, width: 6.0, offset: -5, style: 'renkon',
    price: 48400, cur: 'JPY', brand: 'APIO', needsFlares: true,
    note: '碟面內凹，單圈 16 個錐形沉孔（蓮根紋），輪唇有對比色飾帶（煙燻透明或木紋銅）。無中心蓋、螺帽外露。2026-04 新品' },
  { id: 'wildboar_sr', url: 'https://apio.jp/parts/7200-28.html', label: 'WILDBOAR SR 四弧槽輪框', rim: 16, width: 6.0, offset: -5, style: 'arc4',
    price: 48400, cur: 'JPY', brand: 'APIO', needsFlares: true,
    note: '復古壓鋼圈造型：外圈平帶＋內凹中央盤，四道細長弧槽在 1:30／4:30／7:30／10:30，槽緣有滾邊。Iron Black／Iron Grey／Cotton White' },
  { id: 'xj07', url: 'https://www.mljinc.co.jp/product/xtreme-j/xj07/', label: 'XTREME-J XJ07 梯形窗輪框', rim: 16, width: 6.0, offset: -5, style: 'dwindow',
    price: 67100, cur: 'JPY', brand: 'MLJ', needsFlares: true,
    note: '8 個梯形 D 窗；官方標示 16×6.0J −5 為 ULTRA DEEP CONCAVE（全系列最深）。無鉚釘、無假 beadlock。孔徑 φ108.5' },
  { id: 'dean_california', url: 'https://www.dean-wheels.com/california/', label: 'California 渦輪面輪框', rim: 16, width: 6.0, offset: -5, style: 'turbine',
    price: 46200, cur: 'JPY', brand: 'DEAN', needsFlares: true,
    note: '24 道細長放射槽、實虛各半；中央三層鍍鉻（外盤＋繩紋環＋子彈蓋），**會蓋住螺帽**——全 117 款裡只有 5 款如此。孔徑 φ108.8' },
  // ---- 台灣現貨（2026-09 調查，每一筆都有查到賣場頁）。台灣買得到的就這幾款，
  //      其餘日規款要靠代購，價格另計運費與關稅
  { id: 'nitro_h12', url: 'https://www.mrk.com.tw/', label: 'NITRO POWER H12 SHOTGUN 輪框', rim: 16, width: 6.0, offset: -5, style: 'eightpin',
    price: 8950, cur: 'TWD', brand: 'SHOWA GARAGE × NITRO POWER', needsFlares: true,
    note: '霧古銅（台灣賣場色）。中心蓋只蓋到輪轂孔，螺帽外露。MRK 4X4 現貨' },
  { id: 'dean_colorado', url: 'https://www.dean-wheels.com/colorado/', label: 'Colorado 仿珠圈輪框', rim: 16, width: 5.5, offset: 20, style: 'beadlock',
    price: 10200, cur: 'TWD', brand: 'DEAN',
    note: '仿珠圈臉，黑色中心板用 8 顆 Torx 固定，會蓋住螺帽。鋼灰／霧炭黑。MRK 4X4 現貨' },
  { id: 'mrk_retro15', url: 'https://www.mrk.com.tw/', label: 'JIMNY 專用復古鋁圈 15 吋', rim: 15, width: 6.0, offset: -5, style: 'daytona',
    price: 3980, cur: 'TWD', brand: 'MRK（台灣）',
    note: '台灣最便宜的復古框，15×6.0J −5。MRK 自有品牌' },
  { id: 'mrk_retro165', url: 'https://www.mrk.com.tw/', label: 'JIMNY 專用復古鋁圈 16×6.5J', rim: 16, width: 6.5, offset: -5, style: 'daytona',
    price: 6500, cur: 'TWD', brand: 'MRK（台灣）', needsFlares: true,
    note: '16×6.5J −5，是台灣現貨裡最寬的一款；配寬胎時輪拱要留意' },
  { id: 'yaochi_h598', label: 'H598 五輻輪框', rim: 15, width: 7.0, offset: 0, style: 'slot5',
    price: 4550, cur: 'TWD', brand: '耀麒（台灣）', needsFlares: true,
    note: '15×7.0J ±0，台灣自有品牌，NT$4,400–4,700 一顆' },
  { id: 'beadlock', label: 'Beadlock 造型輪框', rim: 16, width: 7.0, offset: -20, style: 'beadlock',
    price: null, brand: '多家', uncertain: true, note: '深 offset，需搭配大幅輪拱修改' },
];

export const TYRES = [
  { id: 't195', label: '195/80R15', dia: 693, width: 195, rim: 15, price: 0,
    needLift: 0, needBody: 0, legal: true, note: '原廠配置' },
  { id: 't215r15', label: '215/75R15', dia: 710, width: 215, rim: 15, needLift: 0, needBody: 0,
    legal: true, note: '+2.4%，原廠框可裝、免修改。最安全的升級' },
  { id: 't215r16', label: '215/70R16', dia: 707, width: 215, rim: 16, needLift: 0, needBody: 0,
    legal: true, note: '+2%，可能需輕微修內輪弧' },
  { id: 't225r16', label: '225/75R16', dia: 744, width: 225, rim: 16, needLift: 40, needBody: 0,
    legal: true, note: '+7.4%，需 40–60mm 舉升與修內襯；車主實車配置（MAXX 16×7）' },
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
  { id: 'toyo_at3', photo: true, pattern: 'at', brand: 'TOYO TIRES', model: 'OPEN COUNTRY A/T III', owl: true,
    owlSizes: ['t215r16', 't235', 't30', 't31'],
    mask: { file: 'toyo_at3.png', repeatMM: 184 },
    label: 'Open Country A/T III 全地形胎', note: '白字：日規 215/70R16、美規 235/75R15、30×9.5、31×10.5' },
  { id: 'bfg_ko2', pattern: 'at', brand: 'BFGoodrich', model: 'ALL-TERRAIN T/A KO2', owl: true, owlSizes: 'some',
    label: 'All-Terrain T/A KO2 全地形胎', note: '多數尺寸有白字（RWL）' },
  { id: 'yk_g015', pattern: 'at', brand: 'YOKOHAMA', model: 'GEOLANDAR A/T G015', owl: false,
    label: 'GEOLANDAR A/T G015 全地形胎', note: '**日規目錄沒有 195/80R15 也沒有 215/70R16**，實際可用的是 185/85R16（單面白字）；台灣不賣，已被 A/T4 G018 取代。部分尺寸白字' },
  { id: 'fk_at3w', pattern: 'at', brand: 'FALKEN', model: 'WILDPEAK A/T3W', owl: false,
    label: 'WILDPEAK A/T3W 全地形胎', note: '僅黑字' },
  { id: 'toyo_rt', photo: true, pattern: 'rt', brand: 'TOYO TIRES', model: 'OPEN COUNTRY R/T', owl: false,
    mask: { file: 'toyo_rt.png', repeatMM: 156 },
    label: 'Open Country R/T 複合越野胎', note: '白字**不在 JB74 主力尺寸**：官方表列 195/80R15 與 215/70R16 皆無 WL，白字在 185/85R16、LT225/70R16、235/70R16（零售 SKU 命名與官方表有衝突，待實車確認）。日規單面白字' },
  { id: 'yk_xat', pattern: 'rt', brand: 'YOKOHAMA', model: 'GEOLANDAR X-AT G016', owl: true, owlSizes: ['t195'],
    label: 'GEOLANDAR X-AT G016 複合越野胎', note: '白字的 JB74 尺寸是 **195/80R15（雙面白字）與 185/85R16**；LT215/70R16 是黑字。注意 195/80R15 是 **G016A**，兩面側壁設計與行銷照的 G016 不同。白字：195R16C、215/70R16' },
  { id: 'nt_ridge', unavailable: true, pattern: 'rt', brand: 'NITTO', model: 'RIDGE GRAPPLER', owl: false,
    label: 'Ridge Grappler 複合越野胎', note: '**JB74 裝不上**：最小 265/70R16、最小輪圈 7.0J，原廠 5.5J 不合規。全 Grappler 系列也都沒有白字。留著僅供參考。僅黑字；JB74 常用尺寸較少' },
  { id: 'kd_rt', pattern: 'rt', brand: 'KENDA', model: 'KLEVER R/T', owl: true, owlSizes: 'some',
    label: 'Klever R/T KR601 複合越野胎', note: '部分尺寸白字' },
  { id: 'toyo_mt', photo: true, pattern: 'mt', brand: 'TOYO TIRES', model: 'OPEN COUNTRY M/T', owl: true,
    owlSizes: ['t30', 't225r16'],
    mask: { file: 'toyo_mt.png', repeatMM: 246 },
    label: 'Open Country M/T 泥地胎', note: '白字依尺寸：**30×9.50R15 有、31×10.50R15 沒有**，美規全 BSW。JB74 可用尺寸全是 LT，都需要舉升。日規單面白字；LT 規格' },
  { id: 'bfg_km3', pattern: 'mt', brand: 'BFGoodrich', model: 'MUD-TERRAIN T/A KM3', owl: false,
    label: 'Mud-Terrain T/A KM3 泥地胎', note: '僅黑字' },
  { id: 'yk_g003', pattern: 'mt', brand: 'YOKOHAMA', model: 'GEOLANDAR M/T G003', owl: false,
    label: 'GEOLANDAR M/T G003 泥地胎', note: '**無白字**：Yokohama 明載「G003は全サイズ、レイズドブラックレター、リムプロテクトバー付」——任何市場任何尺寸都沒有白字。日規 215/70R16 有白字' },
  { id: 'cp_stt', pattern: 'mt', brand: 'COOPER', model: 'DISCOVERER STT PRO', owl: true, owlSizes: ['t31'],
    label: 'Discoverer STT Pro 泥地胎', note: 'JB74 只有 31×10.50R15 一個尺寸可用。31×10.5R15 白字' },
];


// Front bumpers and grilles are modelled parts (blender/build_parts.py);
// `id` is the part name suffix in parts.glb. Choosing one hides the stock
// bumper (with its fog lamps) or the stock grille panel on the model.
export const FRONT_BUMPERS = [
  // ---- URNIETA 全車套件專用前保桿（urnieta.com）
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-front-bumper-for-jimny-jb74-jc74/', label: 'SALADO 絞盤前保桿', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-001：1426×670（含 U 型防撞桿）。42.8kg，內藏 8000lb 絞盤艙與導索器，兩端內嵌燈窩加鋼網護罩，U 桿與防撞桿可互換、下護板可拆。官網不標價' },
  // ---- DAMD 全車套件專用前保桿（damd.co.jp）
  { id: 'damd_little_d', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-d/', label: 'little D. 前保桿', price: 63800, cur: 'JPY', brand: 'DAMD', kit: 'little_d',
    note: '平直鋼板風橫樑、方形端板假螺絲，內側小圓霧燈，中央黑網＋偏置車牌，下方銀色凹坑護板。ABS，裝車要切輪拱內襯' },
  { id: 'damd_little_g_trad', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-g_traditional/', label: 'little G. TRADITIONAL 前保桿', price: 96800, cur: 'JPY', brand: 'DAMD', kit: 'little_g_trad',
    note: '鋼板橫樑＋密集縱向壓紋，兩顆鍍鉻框方形琥珀霧燈架在保桿上緣，車牌偏一側' },
  { id: 'damd_roots', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'JIMNY the ROOTS. 前保桿', price: 63800, cur: 'JPY', brand: 'DAMD', kit: 'roots',
    note: '雙層：上層象牙色鋼板橫樑帶一排細縫，下層黑色裙板置中掛牌，兩側小圓鍍鉻霧燈' },
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  // ---- 台灣有售
  { id: 'tube_heritage', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_2_bk/', refs: ['https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_2_iv/', 'https://www.mrk.com.tw/product_ii.html?ID=561'], label: 'Traditional 雙管前保桿（黑）', price: 99000, cur: 'JPY', brand: 'KLC Heritage', part: '162070313', photo: true,
    note: '上下雙圓管、車牌跨兩管、Heritage 護板。全不鏽鋼製；無霧燈架 ¥99,000（162070313）、含霧燈架 ¥110,000（162070297），皆稅込。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝。車主實車配置（霧燈改 KC FLEX ERA 4）' },
  { id: 'armando', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1542', label: 'PRIME 鋼製前保桿', price: 29000, cur: 'TWD', brand: 'ARMANDO',
    part: 'AR-SU-FB-PRM', note: '全寬鋼板保桿、中央燈架、圓霧燈孔、下護板' },
  { id: 'urnieta_1970', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=2210', label: '1970 復古前保桿', price: 20600, cur: 'TWD', brand: 'URNIETA', part: 'UR010',
    note: '工程圖 UN-JIMNY-FB-027：1547×331，兩端上揚翼形角＋三道散熱縫，中央百葉面板配 URNIETA 與 1970 SERIES 銘牌，下方平板配兩顆拖車環。21kg。短版復古、兩側上折收窄，保留原廠霧燈與洗燈' },
  { id: 'beyond_liberte', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=2114', label: 'Liberte 復古前保桿', price: 28000, cur: 'TWD', brand: 'Beyond Japan',
    note: '硬邊鋼製、霧燈架＋下護板；MRK 代理' },
  { id: 'maverick', photo: true, url: 'https://i-pickup.com.tw/product/df0001/', label: '短版金屬前保桿', price: 29000, cur: 'TWD', brand: 'Maverick',
    part: 'DF0001', note: '鍍鋅鋼 NT$29,000／鋁合金 NT$35,000，塗裝 +9,000' },
  { id: 'mrk_abs', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1948', label: '短版 ABS 前保桿（消光黑）', price: 9500, cur: 'TWD', brand: 'MRK', part: 'JMY-FB-L',
    note: '原廠造型縮短版、ABS' },
  { id: 'wmd_winch', photo: true, url: 'https://www.ruten.com.tw/item/show?22105872751291', label: '絞盤短版前保桿', price: 18000, cur: 'TWD', brand: 'WMD（台灣）',
    note: '台製鋼板、絞盤座、Ø50 護弓' },
  { id: 'jaos_cowl', photo: true, url: 'https://www.jaos.co.jp/product/B040518/2866', label: 'Front Sport Cowl 前下擾流', price: 18700, cur: 'TWD', brand: 'JAOS', part: 'B040518',
    note: 'PU 材質＋鋁網，下緣 −80mm；日本 ¥66,000 起' },
  // ---- 日本
  { id: 'klc_short', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/frontshortbumper74/', photo: true, label: 'Front Short Bumper 74 前保桿', price: 102300, cur: 'JPY', brand: 'KLC Heritage',
    note: 'ABS 樹脂、原廠高度縮短版，中央鋁網開口（銀色）、保留原廠霧燈。塗裝色只有皺紋黑：塗裝完成品 ¥102,300、未塗裝素材 ¥69,300，皆稅込。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝' },
  { id: 'showa_iron', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000842/', photo: true, label: 'Iron Bumper 鋼管前保桿', price: 128700, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00900', note: 'Ø60 鋼管、兩端 45° 後彎；含 3mm 鋁下護板與霧燈架（本體單售 ¥90,750）' },
  { id: 'klc_trad', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_2_iv/', photo: true, label: 'Traditional 雙管前保桿（象牙白）', price: 99000, cur: 'JPY', brand: 'KLC Heritage',
    note: '與黑色同一支、象牙白塗裝。全不鏽鋼製，無霧燈架 ¥99,000、含霧燈架 ¥110,000，皆稅込。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝。（原本連到的是 JB64 的頁面，¥104,500 是那台的價）' },
  { id: 'outclass_t2', photo: true, url: 'https://outclass.ocnk.net/product/1095', photo: true, label: 'TYPE2 絞盤鋼製前保桿', price: 140800, cur: 'JPY', brand: 'OUTCLASS',
    note: '鐵製、含絞盤床與 4 顆 LED 方燈；出廠未烤漆（可選 Raptor 塗層）' },
  { id: 'taniguchi_square', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: '角形前保桿', price: 58300, cur: 'JPY', brand: 'TANIGUCHI',
    note: '2mm 方管、粉體黑；不鏽鋼版 ¥107,800' },
  { id: 'taniguchi_double', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: '雙管前保桿', price: 77000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '上下兩支 Ø48 圓管' },
  { id: 'toc_extreme', photo: true, url: 'https://tocbw.thebase.in/items/82110724', label: 'Extreme Bumper 74 前保桿', price: 54780, cur: 'JPY', brand: 'TOC BODYWORKS',
    note: 'FRP 仿鐵保桿、原廠寬度、LED 燈條槽' },
];

export const REAR_BUMPERS = [
  // ---- URNIETA 全車套件專用後保桿（urnieta.com）
  { id: 'urnieta_salado_rear', url: 'https://urnieta.com/product/salado-rear-bumper-for-jimny-jb74-jc74/', label: 'SALADO 後保桿', price: 27000, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', ownLamps: true,
    refs: ['https://shopee.tw/product/7996649/54712201643'],
    note: '工程圖 UN-JIMNY-FB-002：高 216mm、展開全長 1816。半高式、兩端包覆轉角，左右各一組燈窗（一側 Salado、一側 URNIETA 銘牌），下方兩片腳踏板。16.4kg。台灣蝦皮 NT$27,000' },
  // ---- DAMD 全車套件專用後保桿（damd.co.jp）
  { id: 'damd_little_d_rear', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-d/', label: 'little D. 後保桿', price: 81400, cur: 'JPY', brand: 'DAMD', kit: 'little_d', ownLamps: true,
    note: '雙層結構、全寬 1656mm。原廠尾燈整組拆除，改用套件自帶的凸圓頂圓燈（沿用原廠線束）：每側琥珀方向燈、紅色尾／煞車燈、角板上的透明倒車燈，下橫樑再加一片紅色反光片。DAMD 展示車多半加購 ¥10,780 的車牌移設套件改掛後門；有倒車雷達要鑽孔，原廠車牌需重新封印' },
  { id: 'damd_little_g_trad_rear', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-g_traditional/', label: 'little G. TRADITIONAL 後保桿', price: 85800, cur: 'JPY', brand: 'DAMD', kit: 'little_g_trad', ownLamps: true,
    note: '全寬 1650mm，外露面粗目消光黑、凹陷階面鋼琴黑。每側一顆卡車式方形尾燈（DAMD 料號 E-476，215×68mm，中心距中線 ±540），由外而內為琥珀方向燈、紅色反光片、紅色尾／煞車燈、透明倒車燈；無後霧燈。車牌置中掛在下段橫樑' },
  { id: 'damd_roots_rear', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'JIMNY the ROOTS. 後保桿＋延伸片', price: 96800, cur: 'JPY', brand: 'DAMD', kit: 'roots', ownLamps: true,
    note: '象牙色橫樑＋延伸片；烤漆版延伸片一律消光黑' },
  { id: 'stock', label: '原廠', price: 0, brand: 'SUZUKI' },
  // ---- 台灣有售
  { id: 'tube', photo: true, label: '管狀後保桿（含尾燈座）', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: 'Ø76 直管、方形封板、尾燈座板、右側排氣尾管、拖鉤' },
  { id: 'klc_heritage_rear', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperrear_2_bk/', refs: ['https://www.mrk.com.tw/product_ii.html?ID=2059'], ownLamps: false, label: 'Traditional 雙管後保桿（黑）', price: 88000, cur: 'JPY', brand: 'KLC Heritage', photo: true,
    note: '粗直管＋兩端梯形尾燈座板、車牌下吊。全不鏽鋼製（不是粉體鋼），¥88,000 稅込，沿用原廠尾燈。裝的時候原廠備胎必須移位。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝。車主實車配置' },
  { id: 'urnieta_1970_rear', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=2219', ownLamps: true, label: '1970 復古後保桿', price: 20400, cur: 'TWD', brand: 'URNIETA', part: 'UR015',
    note: '工程圖 UN-JIMNY-FB-028：1617×265，每側兩顆圓形尾燈（官方寫致敬 Nissan GT-R）＋方形凹窗，右側 URNIETA 燈條銘牌，車牌置中。8.4kg。半高、兩端上折、圓形尾燈，8.4kg' },
  { id: 'beyond_rear', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=2112', label: 'Liberte 復古後保桿', price: 21000, cur: 'TWD', brand: 'Beyond Japan',
    note: '精簡鋼桿、消光黑' },
  { id: 'jaos_rear_cowl', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1176', ownLamps: true, label: 'Rear Sport Cowl 後下擾流', price: 26500, cur: 'TWD', brand: 'JAOS', part: 'B042518',
    note: 'PU 材質、4 顆圓形尾燈、倒車攝影機架' },
  // ---- 日本
  { id: 'wildgoose_crawler_rear', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1103.html', label: 'Crawler 圓管後保桿 JM-1103', price: 66000, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: 'Ø76.3 直管 1330×200×225、尾燈座 4.5mm 板、Ø50 拖環' },
  { id: 'wildgoose_box_rear', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1101.html', label: '角管越野後保桿 JM-1101', price: 95700, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: '1410×100×100 角形箱桿 3.2mm，13.2kg' },
  { id: 'showa_iron_rear', photo: true, url: 'https://www.showa-garage.shop/shopbrand/ct343/', label: 'Iron Bumper 鋼管後保桿', price: 62150, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00930', note: 'Ø60 主管＋Ø42 尾燈管翼；LED 倒車燈版 ¥127,930' },
  { id: 'taniguchi_rear_pipe', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_rear/', label: '鋼管越野後保桿', price: 63800, cur: 'JPY', brand: 'TANIGUCHI',
    note: '2.3mm 鋼管；角形版 ¥63,800、拖車鉤版 ¥128,700' },
  { id: 'apio_tactical_rear', photo: true, url: 'https://apio.jp/parts/3032-71.html', label: 'Tactical 後保桿', price: 140800, cur: 'JPY', brand: 'APIO', part: '3032-71',
    note: 'ABS 真空成形 1660×280×460，含燈殼與反光片；烤漆 +¥33,000' },
  { id: 'outclass_rear_abs', photo: true, url: 'https://outclass.ocnk.net/product/1094', ownLamps: true, label: 'TYPE2 ABS 後保桿', price: 45760, cur: 'JPY', brand: 'OUTCLASS',
    note: '精簡 ABS、小型尾燈' },
  { id: 'hamer_mx208', photo: true, url: 'https://www.hamer4x4.com/mx208-jimny-rear-bumper/', label: 'MX208 鋼製後保桿', price: 1590, cur: 'AUD', brand: 'Hamer 4x4',
    note: '1830×650×340 包覆式鋼板、角落踏板、燈條槽，50kg' },
];

export const GRILLES = [
  // ---- URNIETA 全車套件專用面板（urnieta.com，工程圖有標註尺寸）
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-grille-for-jimny-jb74-jc74/', label: 'SALADO 水箱護罩', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-004：1337×241，中央開口 592×126，橫向百葉＋URNIETA 立體字。ABS、1.2kg、45° 下傾進氣。官網不標價' },
  // ---- DAMD 全車套件專用面板（damd.co.jp）
  { id: 'damd_little_d', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-d/', label: 'little D. 水箱護罩（消光黑）', price: 52800, cur: 'JPY', brand: 'DAMD', kit: 'little_d',
    note: '致敬舊款 Land Rover Defender；六道橫肋＋綠色橢圓徽章，頭燈外側加兩顆小圓燈。素地出貨但水箱罩一律附消光黑' },
  { id: 'damd_little_g_trad', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-g_traditional/', label: 'little G. TRADITIONAL 水箱護罩', price: 75900, cur: 'JPY', brand: 'DAMD', kit: 'little_g_trad',
    note: '致敬初代 G-Wagen W460；12 道水平百葉＋中央圓形 dd 徽章。只有消光黑' },
  { id: 'damd_roots', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'JIMNY the ROOTS. 水箱護罩', price: 52800, cur: 'JPY', brand: 'DAMD', kit: 'roots',
    note: '與 APIO 共同開發，致敬初代 LJ10；車身色面板、開口被四根直肋分成五格，上緣 SUZUKI 鍍鉻立體字' },
  { id: 'stock', label: '原廠水箱護罩', price: 0, brand: 'SUZUKI', note: '5 道直立柵欄，中央 S 標' },
  // ---- 台灣有售
  { id: 'hbar_suzuki', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrillenostalgic/', refs: ['https://shopee.tw/product/47473069/5556354773'], label: 'Face Grille Nostalgic 水箱護罩', price: 93500, cur: 'JPY', brand: 'KLC Heritage', photo: true,
    note: 'ABS 烤漆 ¥93,500／ABS 素材 ¥60,500／FRP ¥55,000；方形大燈座、三道橫柵＋細網；車主實車配置。南國吉米有仿製品 NT$2,750' },
  { id: 'taishan_retro', photo: true, url: 'https://www.ruten.com.tw/item/show?22105865989825', label: '復古水箱護罩（黑／銀）', price: 17500, cur: 'TWD', brand: '泰山美研社（台灣）',
    note: 'KLC 風格樹脂復古罩' },
  { id: 'urnieta_1970', photo: true, url: 'https://www.heekis.com/products/urnieta-1970-jimny-jb74-jc74-grille', label: '1970 水箱護罩', price: 8400, cur: 'TWD', brand: 'URNIETA',
    note: '工程圖 UN-JIMNY-FB-026：1337×241，中央開口 592×126 細網＋URNIETA 立體字與 UNT 小徽。1.6kg。沖壓金屬網＋極簡框，1.6kg；Heekis 代理' },
  { id: 'mrk_angry', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1670', label: '憤怒鳥款水箱護罩', price: 5500, cur: 'TWD', brand: 'MRK', part: 'JB089',
    note: '3 道粗橫條、外端斜切、卡扣安裝' },
  { id: 'klc_sj', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrillesj.html', photo: true, label: 'Face Grille SJ 水箱護罩', price: 16000, cur: 'TWD', brand: 'KLC Heritage',
    note: 'FRP 素材 NT$16,000（藤井74）；日本 ABS 烤漆 ¥93,500。顯示為車身同色' },
  // ---- 日本
  { id: 'klc_ja', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrilleja/', label: 'Face Grille JA 水箱護罩', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '大燈旁雙燈座、中央開放網；ABS 素材 ¥60,500／FRP ¥55,000' },
  { id: 'klc_nanaketsu', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrillnanaketsu/', label: 'Face Grille NANAKETSU 水箱護罩', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '7 個圓角方孔、銀色鋁網' },
  { id: 'klc_forty', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrillforty/', label: 'Face Grille FORTY 水箱護罩', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '大燈周圍肋條、中央網＋S 標' },
  { id: 'apio_sj', photo: true, url: 'https://apio.jp/parts/3033-58g.html', label: 'SJ Grille 鋼板水箱護罩', price: 58300, cur: 'JPY', brand: 'APIO', part: '3033-58G',
    note: 'SJ30 直縫沖壓鋼板、槍灰、黑鋁網' },
  { id: 'apio_marker', photo: true, url: 'https://apio.jp/parts/3033-59.html', label: 'Marker Vintage Iron 水箱護罩', price: 75900, cur: 'JPY', brand: 'APIO', part: '3033-59',
    note: '鋼製橫柵＋4 顆 IPF 標誌燈，半光黑或淺古銅' },
  { id: 'showa_hex', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000205/', photo: true, label: 'ABS 蜂巢水箱護罩', price: 16500, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00500', note: 'ABS 素材黑（烤漆版 E00502 ¥31,900）；中央蜂巢網開口' },
  { id: 'outclass_g', photo: true, url: 'https://outclass.ocnk.net/product/1071', photo: true, label: 'Vintage G 水箱護罩', price: 57750, cur: 'JPY', brand: 'OUTCLASS',
    note: 'ASA 樹脂紋理黑；4 道橫柵＋中央直柱，後方細網' },
  { id: 'taniguchi_washer', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: 'FRP Washer 水箱護罩', price: 44000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '原廠造型 FRP、中央網狀開口、洗燈噴嘴移入大燈' },
  { id: 'kpro_folksy', photo: true, url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'Folksy Style 橫鰭水箱護罩', price: 30000, cur: 'JPY', brand: 'K-PRODUCTS', uncertain: true,
    note: 'FRP 白膠殼、橫向鰭片' },
  { id: 'prostaff_minig', photo: true, url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'miniG 水箱護罩', price: 38000, cur: 'JPY', brand: 'Pro Staff', uncertain: true,
    note: 'G-Class 直縫' },
  { id: 'sixsense_explosion', photo: true, url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'Explosion Classic 水箱護罩', price: 80000, cur: 'JPY', brand: 'Six Sense', uncertain: true,
    note: 'Bronco 風：車身同色面板、多道細橫桿＋SUZUKI 字' },
];


// Snorkel kits sold for the JB74; all mount on the right (1.5L airbox side).
export const SNORKELS = [
  { id: 'none', label: '不裝', price: 0 },
  // Corrected 2026-09-22 against every maker's own page (docs/jb74-snorkels.json).
  // Safari, ARB's own line, Rival, Dobinsons and APIO make NOTHING for a JB74 --
  // the part filed here under Safari is Ironman's. The airbox is on the right,
  // so every one of these runs the right A-pillar.
  { id: 'safari', photo: true, url: 'https://www.ironman4x4.com.au/products/4x4-snorkel-for-suzuki-jimny-jb74w',
    label: '圓管呼吸管 ISNORKEL070', price: 451, cur: 'AUD', brand: 'Ironman 4x4', part: 'ISNORKEL070',
    note: '前向六角網格 ram 進氣頭，束環固定可轉向。管徑與材質 Ironman 未公布（先前記的 Ø89／LLDPE／需切葉子板三項都沒有出處）。原本掛在 Safari 名下是錯的——Safari 從來沒做過 JB74' },
  { id: 'bravo', photo: true, url: 'https://bravosnorkel.com/en/suzuki/174-suzuki-jimny-jb74-2018-.html',
    label: 'SSJN 呼吸管', price: 18800, cur: 'TWD', brand: 'Bravo Snorkel', part: 'SSJN',
    note: '西班牙 Girona 製。頭部正圓 Ø89、前向彎頭用束環固定可 360° 轉向；要鑽孔也要切葉子板（原廠手冊印著 Drill／Cut，還要拆引擎蓋，附兩顆 M6 鉚帽）——「免鑽孔」是經銷商的說法不是廠方的。台灣 MRK／希琦 NT$18,800，歐洲 EUR 399' },
  { id: 'urnieta', url: 'https://urnieta.com/product/salado-snorkel-kit-for-jimny-jb74-jc74/', photo: true,
    label: 'SALADO 呼吸管', price: 14000, cur: 'TWD', brand: 'URNIETA', part: '0702021',
    refs: ['https://shopee.tw/product/7996649/29595052138'],
    note: '原廠圖 UN-JIMNY-FB-006：全長 1048×全高 675mm、2.3kg，JB64 不相容。這顆是整圈 360° 百葉的圓鼓頭；同一組套件附兩顆頭可互換（URNIETA 官網稱 Standard 與 Pre-Cleaner，沒有寫形狀）。取代原廠引擎蓋飾板。台灣蝦皮 NT$14,000' },
  { id: 'urnieta_ram', url: 'https://urnieta.com/product/salado-snorkel-kit-for-jimny-jb74-jc74/', photo: true,
    label: 'SALADO 呼吸管（前向進氣頭）', price: 14000, cur: 'TWD', brand: 'URNIETA', part: '0702021',
    refs: ['https://shopee.tw/product/7996649/29595052138'],
    note: '同一組 SALADO 套件換上方形頭：一顆往前伸的方盒，橫柵開口正對車頭，外側有 UNT 銘牌。進氣口離開車身側面、朝迎風面，灰塵與濺水的條件跟圓鼓頭不一樣。頭部形狀取自台灣賣家實照，URNIETA 官網未描述兩顆頭的外形' },
  { id: 'precleaner', photo: true, url: 'https://www.jimnybits.com/snorkel-air-pre-filter-pre-cleaner-head-for-3-snorkels-1.html',
    label: '旋風前濾頭（Ø180）', price: 20, cur: 'GBP', brand: 'jimnybits', part: 'PC35',
    note: 'Ø180 透明旋風碗，先把粉塵甩掉再進濾芯。配 3.5 吋（89mm）管口，不是 3 吋。PC35 是 jimnybits 的店內貨號，該商品頁沒有標廠牌——先前記成「Safari + PC35」是掛錯' },
  { id: 'sleek', photo: true, url: 'https://megajimny.com/products/supa-sleek-snorkel-system',
    label: 'Supa-Sleek V4 隱藏式', price: 649, cur: 'AUD', brand: 'Mega Jimny',
    note: '2 吋不鏽鋼管完全藏在黑色飾板裡看不到，進氣是 A 柱頂端朝「外」的百葉面板，不是朝後的進氣口。免鑽孔' },
  { id: 'tw_frp', label: 'FRP 呼吸管（巴西式樣）', price: 10000, cur: 'TWD', brand: '台灣店家自售', uncertain: true,
    note: '台灣多家店自售、沒有一家標示製造商：機油倉庫 NT$10,000（另加工資 3,500）、南國吉米 10,500、台中烏日 12,000–18,000。葉子板開孔約 83–110mm、A 柱另鑽四個 8mm 固定孔' },
  { id: 'tw_nodrill', label: '免鑽孔呼吸管', price: 8350, cur: 'TWD', brand: '台灣店家自售', uncertain: true,
    note: 'JIMNY74 風格選物；規格未公布' },
];

export const MIRRORS = [
  { id: 'stock', label: '原廠電動折疊後照鏡', price: 0, brand: 'SUZUKI' },
  { id: 'urnieta', url: 'https://urnieta.com/product/salado-side-mirror-kit-for-jimny-jb74-jc74/', photo: true, label: 'SALADO 後照鏡組', price: 17800, cur: 'TWD', brand: 'URNIETA', part: '0702022',
    refs: ['https://shopee.tw/product/7996649/53462197780'], note: '台灣蝦皮 GOAT Wild explorer NT$17,800。URNIETA 為中國東莞斯塔克工業品牌（中文名歐尼塔），非日系；只支援 JB74／JC74，JB64 官方列為不相容。官方工程圖 UN-JIMNY-FB-014：總高 411mm、總寬 237mm。圓角矩形鏡座 187×231，單支圓管由門框上前角的關節繞出、沿鏡座內側往下再回到下關節，鏡座以四螺栓夾塊固定在管上，外緣有 URNIETA 銘牌' },
  { id: 'damd', photo: true, url: 'https://www.pp-performance.net/products/damd-jimny-sierra-truck-mirror', refs: ['https://easycars.jp/product/damd-truck-side-mirror-for-jimny-jb64-jb74/'], label: 'Truck Mirror 卡車式後照鏡', price: 19800, cur: 'TWD', brand: 'DAMD', photo: true,
    note: '直式卡車鏡＋U 型管臂，消光黑或鍍鉻；含加熱，失去電動折疊' },
];

// Roof racks, awnings, side steps and ladders are modelled parts named
// roofRack_<id>, awning_<id>_<left|right>, sideStep_<id>, ladder_<id>.
export const ROOF_RACKS = [
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-roof-rack-for-jimny-jb74-jc74/', label: 'SALADO 全頂行李架', price: 30900, cur: 'TWD', brand: 'URNIETA', part: '0702024',
    note: '1890×1366mm 平板式：7 根橫向 50mm 滑槽條（中段 220mm 間距）、中央縱向脊樑、外圍矮圓管框、前方鋁沖壓導風板。原廠雨槽每側一根長軌、每側 3 個腳座。尺寸取自原廠圖 UN-JIMNY-FB-012；離車頂高度原廠未公布' },
  { id: 'urnieta_salado_half', url: 'https://urnieta.com/product/salado-roof-rack-for-jimny-jb74-jc74/', label: 'SALADO 半頂行李架', price: 25200, cur: 'TWD', brand: 'URNIETA', part: '0702034', uncertain: true,
    note: '同款的短版，每側 2 個腳座。原廠沒有公布半頂的長度，模型長度為依照片推估' },
  { id: 'wood', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'trip basket 復古車頂架（半長）', price: 56000, cur: 'JPY', brand: 'DAMD', part: 'TB-HR1',
    refs: ['https://www.sunvigor.com.hk/onlineshop/tw/damd/2605-suzukijimny-jimnysierre-damd-roofrack-tripbacket-djbtbdrr1.html'],
    note: '1350×600×160mm、13.5kg。黑色鋼製鐵線籃，木料是紐西蘭輻射松乙醯化處理的高耐久「Accoya」，做成包覆前緣的弧形擋板與兩側木塊，不是木地板。裝在車頂前段的橫桿上。日本仍在售 ¥56,000／¥61,600 稅込；＋TERZO 基座組 TB-HRKJB ¥74,000' },
  { id: 'wood_full', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'trip basket 復古車頂架（全長）', price: 19800, cur: 'TWD', brand: 'DAMD', part: 'TB-RR1',
    refs: ['https://www.damd.co.jp/products/suzuki/jimny_theroots/'],
    note: '1350×1000×160mm、16kg，與半長款同款式。日本 ¥59,000／¥64,900 稅込；＋TERZO 基座組 TB-RRKJB ¥77,000。台灣蝦皮「藤井74」NT$19,800' },
  { id: 'none', label: '不裝', price: 0 },
  // ---- 台灣有售
  { id: 'arb', photo: true, url: 'https://www.ruten.com.tw/item/show?22438729095708', photo: true, label: 'BASE Rack 車頂架 1545×1285', price: 45000, cur: 'TWD', brand: 'ARB', part: '1770020 + 17900020',
    note: '鋁擠型平台、燕尾槽側軌、4 支雨槽腳；平台單品 NT$15,000（MRK）；車主實車配置' },
  { id: 'yakima', photo: true, url: 'https://www.yakima.com.tw/products/locknload-platform', label: 'LockNLoad 平台車頂架 1520×1370', price: 23000, cur: 'TWD', brand: 'Yakima', part: '8005045',
    note: '橫向板條 T 槽、4 支雨槽腳（110／150／210mm）；Yakima 台灣售價' },
  { id: 'pioneer', photo: true, url: 'https://www.ruten.com.tw/item/show?22441909928235', label: 'Pioneer LT 平台車頂架', price: 58300, cur: 'TWD', brand: 'Rhino-Rack',
    part: 'ROLS1', note: '1453×1339、5 道縱向板條、Backbone 橫樑固定；黑四驅售價' },
  { id: 'ipf', photo: true, url: 'https://www.ipf.co.jp/ipfEc/products/detail/159', label: 'EXP Roof Rack type-A 車頂架', price: 32000, cur: 'TWD', brand: 'IPF', part: 'EXR-01',
    note: '1400×1250×38.8、12.5kg；日本 ¥85,800、MRK 台灣售價' },
  { id: 'tw_generic', photo: true, url: 'https://tw.bid.yahoo.com/item/100868689053', label: '鋁合金平頂車頂架', price: 13000, cur: 'TWD', brand: '機油倉庫（台灣）',
    note: '1600×1260、6 支雨槽腳、前導流板；安裝 +NT$1,000' },
  // ---- 進口
  { id: 'platform', photo: true, url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-current-slii', photo: true, label: 'Slimline II 全長車頂架', price: 1579, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ003T',
    note: '1560×1345、6 支雨槽腳、前導流板，31kg' },
  { id: 'fr34', photo: true, url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-curr-slii-3-4-roof-rack-kit', label: 'Slimline II 3/4 車頂架', price: 1451, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ006T',
    note: '1156×1345、4 支腳' },
  { id: 'jaos', photo: true, url: 'https://www.jaos.co.jp/product/B411611NS/3848', label: 'Flat Rack type-B 車頂架', price: 140800, cur: 'JPY', brand: 'JAOS', part: 'B411611NS',
    note: '1400×1250×32、6 道 T 槽底桿、前導流板；type-A ¥116,600' },
  { id: 'apio', photo: true, url: 'https://apio.jp/parts/3630-50.html', label: 'Mighty Smart Rack 車頂架', price: 231000, cur: 'JPY', brand: 'APIO', part: '3630-50',
    note: '1420×1270、前軌前傾兼導流、船用鋁粉體' },
  { id: 'showa_foot', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000001017/I59728/', label: 'A-x Roof Rack 1512 車頂架', price: 92400, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20080', note: '1500×1250×40 噴砂鋁面' },
  { id: 'basket', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000111/I59728/', label: 'A-x Full Rack M 籃式車頂架', price: 68200, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20008', note: '1400×1250×130、側籃可拆，直鎖雨槽' },
];

export const AWNINGS = [
  { id: 'none', label: '不裝', price: 0 },
  // ---- 台灣有售
  { id: 'yakima_s', photo: true, url: 'https://www.yakima.com.tw/products/slimshady-%E8%BB%8A%E9%82%8A%E5%B8%B3-2-2-5m', photo: true, label: 'OverNOut S 車邊帳 2×2.5m', price: 8500, cur: 'TWD', brand: 'Yakima', part: 'KT8007508',
    note: '軟袋 2100 長、12kg；Yakima 台灣售價' },
  { id: 'yakima_l', photo: true, url: 'https://www.yakima.com.tw/products/overnout_l', label: 'OverNOut L 車邊帳 2.5×2.5m', price: 11700, cur: 'TWD', brand: 'Yakima', part: 'KTHB0019',
    note: '軟袋 2600 長、18kg' },
  { id: 'yakima_270', photo: true, url: 'https://www.yakima.com.tw/products/overnout-270', label: 'OverNOut 270 蝙蝠車邊帳', price: 21600, cur: 'TWD', brand: 'Yakima', part: '8007462/3',
    note: '2286×216×254、後端旋轉、四支臂自撐；左＝駕駛側' },
  { id: 'yakima_270s', photo: true, url: 'https://www.yakima.com.tw/products/overnout-270', photo: true, label: 'OverNOut 270 蝙蝠車邊帳 1.8m', price: 19800, cur: 'TWD', brand: 'Yakima', part: '8007538/9',
    note: '短版 270°，收納約 1850×216×254；架在車頂架側緣上方（車主實車配置）' },
  { id: 'yakima_180', photo: true, url: 'https://www.yakima.com.tw/products/overnout-180-%E5%81%B4%E9%82%8A%E5%B8%B3', label: 'OverNOut 180 車邊帳', price: 21600, cur: 'TWD', brand: 'Yakima', part: '8007516',
    note: '2260×229×178、8.7m²、三支臂' },
  { id: 'rhino_compact', photo: true, url: 'https://www.ruten.com.tw/item/22445161058255/', label: 'Batwing Compact 蝙蝠車邊帳', price: 33920, cur: 'TWD', brand: 'Rhino-Rack',
    part: '33120/33121', note: '2000 長、6m²、18kg；黑四驅售價' },
  { id: 'rhino_270', url: 'https://www.rhinorack.com/en-au/products/sport-awnings/awnings/awnings/batwing-compact-awning-left-_33120', label: 'Batwing 270 蝙蝠車邊帳', price: 38160, cur: 'TWD', brand: 'Rhino-Rack', part: '33118/33119',
    note: '2500 長、10m²、20.5kg' },
  { id: 'allblack_270', photo: true, url: 'https://www.ruten.com.tw/item/22245661385396/', label: 'ALL BLACK 270° 車邊帳 gen3', price: 18000, cur: 'TWD', brand: '黑四驅（台灣）',
    note: '2m／2.5m 兩種、左開／右開；含 LED 燈條' },
  // ---- 進口
  { id: 'arb_touring_2', photo: true, url: 'https://www.arb.com.au/product/814406-arb-touring-awning-2000mm-x-2500mm-with-led-light', label: 'Touring 車邊帳 2000×2500 LED', price: null, cur: 'AUD', brand: 'ARB', part: '814406', uncertain: true,
    note: 'PVC 軟袋約 2200 長，12.9kg；經銷商報價' },
  { id: 'arb_touring_25', photo: true, url: 'https://www.arb.com.au/product/814407-arb-touring-awning-with-light-2500mm-x-2500mm', label: 'Touring 車邊帳 2500×2500 LED', price: null, cur: 'AUD', brand: 'ARB', part: '814407', uncertain: true,
    note: '約 2700 長，14.3kg' },
  { id: 'arb_alu', photo: true, url: 'https://www.arb.com.au/product/814412-arb-awning-2500mm-x-2500mm-black-aluminium-housing-and-light', label: '鋁殼車邊帳 2500×2500', price: null, cur: 'AUD', brand: 'ARB', part: '814412', uncertain: true,
    note: '矩形鋁殼、外側掀蓋，17.8kg' },
  { id: 'darche_270', photo: true, url: 'https://darche.com.au/products/eclipse-270-g2-right-us-eu-p', label: 'Eclipse 270 G2 車邊帳', price: 1499, cur: 'AUD', brand: 'Darche', part: 'T050801743',
    note: '11.5m²、1000D PVC，後端鋁合金旋軸' },
  { id: 'darche_slim', photo: true, url: 'https://darche.com.au/products/eclipse-slimline-2-5m-x-2-5m', label: 'Eclipse Slimline 車邊帳', price: 579, cur: 'AUD', brand: 'Darche', part: 'T050801793',
    note: '820D 軟袋，14kg' },
  { id: 'ikamper', photo: true, url: 'https://ikamper.com/products/exoshell-270-awning', label: 'ExoShell 270 硬殼車邊帳', price: 1950, cur: 'USD', brand: 'iKamper', part: 'MB011-002',
    note: '2630×180×184 硬殼鋁盒、11.2m²，30kg' },
];

export const SIDE_STEPS = [
  // ---- URNIETA 全車套件專用（urnieta.com，工程圖有標註尺寸）
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-side-bar-kit-for-jimny-jb74-jc74/', label: 'SALADO 管狀側踏', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-009：三門 1270×460（五門 1687×460）。外側圓管兩端內收，內側鎖一片開槽踏板，每側兩支支架進大樑＋前方一支斜撐，中央一組夾具踏墊。27kg／組。官網不標價' },
  { id: 'urnieta_1970', url: 'https://urnieta.com/product/1970-side-skirt-kit-for-jimny-jb74-jc74/', label: '1970 側裙飾板', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_1970', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-030：1433×176。一體成型側裙，沿長度一道凸起飾條、上緣三顆螺栓、兩端向上收尾接輪拱。4.6kg／組。官網不標價' },
  { id: 'none', label: '不裝', price: 0 },
  // ---- 台灣
  { id: 'wlm', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1905', photo: true, label: 'WLM001 側踏', price: 13800, cur: 'TWD', brand: 'WLM 4x4',
    note: 'Ø50 圓管貼門檻、兩片踏板、鍍鋅粉體黑；用原廠孔位免鑽孔' },
  { id: 'jst', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=1580', label: 'JB74001 側踏', price: 9000, cur: 'TWD', brand: 'JST 吉米工坊', photo: true,
    note: '直管＋兩片平踏板，兩端上翹；加強型／特仕版至 NT$11,700；車主實車配置' },
  { id: 'tjm', photo: true, url: 'https://www.mrk.com.tw/product_ii.html?ID=915', photo: true, label: '735STRSA57X 岩石滑桿', price: 18000, cur: 'TWD', brand: 'TJM',
    part: '735STRSA57X', note: 'Ø51 大樑固定、焊接踏板；支架另購 NT$3,000' },
  // ---- 日本
  { id: 'outclass', photo: true, url: 'https://outclass.ocnk.net/product/1124', label: '管架式側踏', price: 88000, cur: 'JPY', brand: 'OUTCLASS',
    note: '低矮管架＋平板踏面，兼門檻保護；消光黑或 Raptor 塗層' },
  { id: 'apio_guard', photo: true, url: 'https://apio.jp/parts/3102-69.html', label: 'H.D 硬鋁門檻護甲', price: 132000, cur: 'JPY', brand: 'APIO', part: '3102-69',
    note: '1350×185 雙層 3mm 硬鋁門檻護甲（無踏板）；窄體限定' },
  { id: 'jaos', photo: true, url: 'https://www.jaos.co.jp/product/B172522BK/3882', label: '粗管側踏', price: 121000, cur: 'JPY', brand: 'JAOS', part: 'B172522BK',
    note: 'Ø76.3 粗管＋樹脂踏墊，16.7kg；規格表標 JC74，請確認適用' },
  { id: 'taniguchi_bar', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: '長管側踏（高度可調）', price: 53900, cur: 'JPY', brand: 'TANIGUCHI',
    note: '長管＋550×145 網狀踏板，兩段高度可調；左 ¥50,600' },
  { id: 'taniguchi_short', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: '兩段可調短側踏', price: 41250, cur: 'JPY', brand: 'TANIGUCHI',
    note: '車門下短網踏 550×145；不鏽鋼版 ¥59,400' },
  { id: 'showa', photo: true, url: 'https://store.shopping.yahoo.co.jp/showa-garage/e00173.html', label: '長版側踏 Type2', price: 69300, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00173', note: '純圓管、皺紋黑；JB74 需另購飾板 E00207' },
  { id: 'wildgoose_fold', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/exterior_64/jm-2262l-jm-2262r.html', label: '折疊式側踏 JM-2262', price: 35200, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: '單邊價；510mm 寬 4.2mm 鋼板、可上翻' },
  { id: 'wildgoose_guard', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/protection_64/jm-2409.html', label: '門檻護甲側踏 JM-2409', price: 110000, cur: 'JPY',
    brand: 'RV4 Wild Goose', note: '1292 長、外凸 55mm 的門檻護甲，可踩；14.5kg' },
  { id: 'customwagon', photo: true, url: 'https://www.custom-wagon.com/c/557/jim661', label: '出幅可調側踏', price: 57200, cur: 'JPY', brand: 'Custom Wagon',
    note: '弧形圓管＋花紋踏板，出幅約 50mm 可調' },
  { id: 'spieler', photo: true, url: 'https://spieler.jp/products/jb64jb74sidestep7575', label: '7575 方管側踏', price: 88000, cur: 'JPY', brand: 'SPIELER',
    note: '75×75 方管＋鋁面板，用車廂固定孔免鑽' },
  // ---- 澳洲
  { id: 'arb', photo: true, url: 'https://www.arb.com.au/product/4424010-arb-rock-sliders-with-textured-black-finish-suzuki-jimny', label: 'Rock Slider 岩石滑桿', price: 891, cur: 'AUD', brand: 'ARB', part: '4424010',
    note: 'Ø60.3 主管、3 支支撐管接大樑、紋理黑，18kg' },
  { id: 'ironman', photo: true, url: 'https://doubleblackoffroad.com/products/ironman-suzuki-jimny-rock-sliders-2018', label: 'Rock Slider SS070 岩石滑桿', price: 699, cur: 'AUD', brand: 'Ironman 4x4',
    note: 'Ø50.8×2.6、1280mm、緞面黑' },
  { id: 'hamer', url: 'https://www.hamer4x4.com/product/sm104-rock-slider-for-suzuki-jimny-jb74-2018/', label: 'SM104 岩石滑桿', price: null, cur: 'AUD', brand: 'Hamer 4x4', uncertain: true,
    note: '圓管＋格柵踏板，25kg，報價制' },
];

export const LADDERS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'fr', photo: true, url: 'https://ozjimny.com/products/front-runner-ladder-jimny-models-2023-current-xl', label: '尾門後爬梯', price: null, cur: 'AUD', brand: 'Front Runner', part: 'LASJ004', uncertain: true,
    note: '4 階、鉸鏈側、勾尾門上緣' },
  { id: 'jst', photo: true, url: 'https://shopee.tw/search?keyword=JST%20%E5%B0%BE%E9%96%80%E6%A2%AF%20Jimny', label: '標準版尾門後爬梯', price: 5180, cur: 'TWD', brand: 'JST 吉米工坊',
    note: 'Ø25 圓管封閉橢圓環、內寬 27cm（窄版 22cm）、四階，兩座片鎖尾門鉸鏈側；台灣製' },
  { id: 'urnieta', url: 'https://urnieta.com/product/salado-rear-ladder-kit-for-jimny-jb74-jc74-jb64/', label: 'SALADO 後爬梯', price: 19500, cur: 'TWD', brand: 'URNIETA', part: '0702026',
    note: '1015×390mm、Ø34 主管＋Ø28 四階（離底 158／378／603／862mm，間距不等）。上端勾尾門上緣、下端夾尾門下鉸鍊，不動車頂。中段有 91mm 往外的 S 形偏移閃備胎，可上到 235/75。附旗桿座、天線座與兩個輔助燈點。尺寸取自原廠圖 UN-JIMNY-FB-013' },
  { id: 'tube', photo: true, label: '管狀環形後爬梯', price: null, cur: 'TWD', brand: '多家', uncertain: true,
    note: 'Ø32 管環、勾車頂架後緣、附滅火器座（車主實車配置）' },
];

export const SIMPLE = {
  snorkel:      { label: '呼吸管', brands: 'Safari / Ironman 4x4 / ARB / Rival / APIO',
                  note: '注意左右側別；部分需切葉子板', uncertain: true },
  roofRack:     { label: '車頂架', options: [
                    { id: 'none', label: '不裝' },
                    { id: 'platform', photo: true, url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-current-slii', label: '平台式', brand: 'Rhino-Rack Pioneer / Front Runner Slimline II' },
                    { id: 'basket', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000111/I59728/', label: '籃式', brand: 'APIO / JAOS / Ironman 4x4' }] },
  awning:       { label: '車邊帳', options: [
                    { id: 'none', label: '不裝' },
                    { id: 'left', label: '左側' },
                    { id: 'right', label: '右側' }],
                  brands: 'Rhino-Rack Batwing / ARB / Front Runner / Darche / 23Zero' },
  windowGuards: { label: '鐵窗', brands: 'APIO / SHOWA GARAGE / Bunker', uncertain: true },
  ladder:       { label: '後爬梯', brands: '多家', note: '可鎖車身或與備胎架整合', uncertain: true },
  rockSliders:  { label: '側踏／岩石滑桿', brands: 'APIO / SHOWA GARAGE / Ironman 4x4', uncertain: true },
  lightBar:     { label: '車頂燈條', brands: '多家' },
  spareBag:     { label: '備胎書包', brands: '多家', uncertain: true },
};

// Auxiliary lighting (docs/jb74-lighting.json, compiled 2026-09-21 from maker
// spec sheets). Sizes there are what the 3D parts are built to. Note STEDI
// makes no behind-the-grille bracket for a Jimny -- the Rally Bar sits in
// FRONT of the grille, and the true behind-the-grille bar is Bushranger's.
export const LIGHT_BARS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'ipf', url: 'https://www.ipf-light.com/catalog/642jm2.php', label: '600 S-Series 40 吋燈條', brand: 'IPF',
    part: '642SD + 642JM2', price: null, cur: 'JPY', uncertain: true, note: '白光；A 柱專用支架 642JM2' },
  { id: 'stedi_st3k', url: 'https://www.stedi.com.au/', label: 'ST3K 51.5 吋（琥珀濾片）', brand: 'STEDI',
    price: 394, cur: 'AUD', note: '1300×51mm、50 顆；濾片可拆，裝上由 5700K 變 2500K 琥珀。4.25kg，是唯一不吃掉車頂 30kg 載重的全寬選項。台灣經銷 Jimny Plus' },
  { id: 'stedi_st4k', url: 'https://www.stedi.com.au/', label: 'ST4K 52 吋（琥珀濾片）', brand: 'STEDI',
    price: 519, cur: 'AUD', note: '1320×110×105mm、雙排 100 顆、6.62kg；加車頂架後接近 30kg 上限' },
  { id: 'stedi_st1k', url: 'https://www.stedi.com.au/', label: 'ST1K 21.5 吋 黃光', brand: 'STEDI',
    price: 219, cur: 'AUD', note: '546×38×80mm、20 顆；原廠黏合黃色鏡片，熄燈也是黃的（全系列唯一原生上色）' },
  { id: 'stedi_st2k', url: 'https://www.stedi.com.au/', label: 'ST2K TOUCH 40 吋 白／琥珀', brand: 'STEDI',
    price: 649, cur: 'AUD', note: '1016mm、16 段；白／琥珀雙色 DRL 觸控切換。斷面未公布' },
];

// Round spot lights on the rack's front rail. The KC "smiley" look is the
// black-and-yellow logo cover, not a different lamp.
export const ROOF_LIGHTS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'round', label: '車頂圓燈（一對）', brand: '多家', price: null, uncertain: true, note: '一般 7 吋圓燈一對，鎖在車頂架前橫桿' },
  { id: 'kc_pro6', url: 'https://www.kchilites.com/', label: 'Pro6 六燈排燈（微笑燈罩）', brand: 'KC HiLiTES',
    part: '91307', price: 1615, cur: 'USD',
    note: '994×154×85mm、六顆 152.4mm、間距 156.6mm，附黑底黃 KC 燈罩。11.34kg，加平盤車頂架已超過 JB74 車頂 30kg 動態載重。台灣 MRK 代理，燈罩單買 NT$600' },
];

// Nose lighting. Sits in front of, in, or behind the grille -- three quite
// different looks from the outside.
export const GRILLE_LIGHTS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'rally', url: 'https://www.stedi.com.au/', label: 'Rally Bar ＋ ST1K 黃光', brand: 'STEDI',
    part: 'ST-11-JMN-001', price: 544, cur: 'AUD',
    note: '63mm 白鐵管橫過水箱罩「前方」，燈條鎖在管上。STEDI 沒有 Jimny 的格柵內支架，這是他們唯一的 Jimny 車頭件（管 A$325 ＋ ST1K A$219）' },
  { id: 'lower', url: 'https://www.stedi.com.au/', label: 'ST1K 21.5 吋 下氣壩', brand: 'STEDI',
    price: 219, cur: 'AUD', note: '546mm 黃光條塞在下保桿開口，最常見的 DIY 解法' },
  { id: 'bushranger', label: 'Night Hawk 28 吋（格柵後）', brand: 'Bushranger', part: 'NHBGS450LB',
    price: 600, cur: 'AUD', note: '717mm 單排 21 顆 OSRAM；原廠文案明寫裝在下水箱罩「後方」，需修下護板' },
];

// Tail pipes (docs/jb74-exhaust.json). What matters here is what shows from
// outside: JB74 exits on the RIGHT from the factory, and only a few systems
// change the silhouette at all.
export const EXHAUSTS = [
  { id: 'stock', label: '原廠', brand: 'SUZUKI', price: 0, note: '右側出，管口與保桿幾乎切齊，從外面幾乎看不到' },
  { id: 'tw_tip', label: '裝飾尾飾管（套接）', brand: '台灣市售', price: 675, cur: 'TWD',
    note: '套在原廠管上，往後多伸 50–80mm；底下完全不動。台灣 JB74 最常見的改法' },
  { id: 'fujitsubo_ak', url: 'https://www.fujitsubo.co.jp/', label: 'AUTHORIZE K', brand: 'FUJITSUBO', part: '750-81927',
    price: 72380, cur: 'JPY', note: 'φ70 斜切 21°、離地 320mm，原廠位置最斯文的一套；原廠土除需拆或裁。另有燒色尾管選項' },
  { id: 'monster_sp_x', url: 'https://www.monster-sport.com/', label: 'TYPE Sp-X', brand: 'MONSTER SPORT', part: '241590-5600M',
    price: 68200, cur: 'JPY', note: 'φ76.3 斜切捲邊、子彈型消音筒 3.6kg，右側原廠位置免修保桿' },
  { id: 'jaos_zs', url: 'https://www.jaos.co.jp/', label: 'BATTLEZ ZS', brand: 'JAOS', part: 'B702518B',
    price: 74800, cur: 'JPY', note: 'φ101 正圓管口（全表最大單出）＋BATTLEZ 壓字，需局部修保桿。台灣 MyRack 約 NT$22,000，是台灣最買得到的真系統' },
  { id: 'kakimoto_kr_lr', url: 'https://www.kakimoto.co.jp/', label: 'Class KR 左右出', brand: '柿本改', part: 'S71355S',
    price: 170500, cur: 'JPY', note: 'φ96 雙出、左右保桿下角各一，是車尾正面視角最搶眼的一套；沒有胖消音筒，取而代之是扁平共鳴箱' },
  { id: 'apio_yoshimura_ti', url: 'https://apio.jp/', label: '突擊 R-77J 鈦砲管', brand: 'APIO × YOSHIMURA', part: '2004-7T',
    price: 363000, cur: 'JPY', note: '重點是消音筒本身：550×115mm 鈦砲管橫躺在後保桿下，手工燒藍，辨識度全表最高' },
  { id: 'taniguchi_compe_r', url: 'https://www.ors-taniguchi.co.jp/', label: 'Compe Muffler R', brand: 'TANIGUCHI',
    price: 102300, cur: 'JPY', note: '唯一會動到保桿本體：管口從右後角「側向」穿出、離地約 560mm，涉水用。原廠保桿要開孔' },
  { id: 'hks_legal', url: 'https://www.hks-power.co.jp/', label: 'LEGAL Muffler K-1', brand: 'HKS', part: '31013-AS017',
    price: 13800, cur: 'TWD',
    note: 'φ74.7 單出、拋光 SUS304、右側後出（與原廠同側同位置），伸出保桿約 45mm。消音鼓只有 4.0kg 藏在後軸上方，側面幾乎看不到；近接排氣音 83dB（原廠 81），免切保桿。台灣唯一有公司貨標價的 HKS 吉姆尼排氣，日本 ¥49,500。車主實車配置' },
  { id: 'hks_legal_ti', url: 'https://www.hks-power.co.jp/', label: 'LEGAL Muffler K-1（鈦燒色尾管）', brand: 'HKS', part: '31013-AS020',
    price: 16900, cur: 'TWD', note: '與 K-1 同一支，尾管換成鈦燒色；日本 ¥71,500' },
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-exhaust-kit-for-jimny-jb74-jc74/', label: 'SALADO 四出排氣', brand: 'URNIETA', part: '0702019',
    price: 44800, cur: 'TWD',
    note: '真的四根管：一顆中央消音器分兩路，每側兩根 Ø80 尾管（離中線 279／368mm，同側相距 89mm 幾乎相貼，共用一個方形外罩），全部朝後。電子閥門＋無線遙控，中尾段 cat-back，不需切保桿——SALADO 後保桿是半高的，本來就露出這一區。尺寸取自原廠圖 UN-JIMNY-FB-010' },
  { id: 'hks_trailmaster', url: 'https://www.hks-power.co.jp/', label: 'LEGAMAX TRAILMASTER', brand: 'HKS', part: '32018-AS006',
    price: 150700, cur: 'JPY',
    note: '左側出雙管 φ75 燒藍鈦色，整組藏在左側門檻下、後輪前方，後保桿完全不動。HKS 給 JB74 的另一條路線，與 LEGAL 的右側後出完全不同' },
];

// Where a fire extinguisher hangs. No maker sells a JB74 ladder bracket --
// the owner's car wears a pair of band clamps on the ladder rail, and the
// guard positions strap to the MOLLE panel (2-5 kg rated, so a 1 kg bottle).
export const EXTINGUISHERS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'ladder', label: '掛尾梯', brand: '雙環快拆', price: null, uncertain: true,
    note: '圓管專用雙環架；車主實車配置。市面沒有 JB74 尾梯專用架' },
  { id: 'left', label: '左鐵窗', brand: 'MOLLE 板', price: null, uncertain: true, note: '鐵窗板載重僅 2–5kg，只能綁 1kg 瓶並垂直固定' },
  { id: 'right', label: '右鐵窗', brand: 'MOLLE 板', price: null, uncertain: true, note: '同左側' },
];


// Extras that map to configurator toggles (`key`) rather than a select list
export const OTHERS = [
  { id: 'showa_skirt', url: 'https://www.heekis.com/products/showasidecover', refs: ['https://www.showa-garage.shop/'], label: 'AES 車門下側裙飾板', price: 14500, cur: 'TWD', brand: 'SHOWA GARAGE', photo: true, key: 'sideSkirt',
    note: '消光黑 AES 門檻下飾蓋，簡約腰線；Heekis 代理；車主實車配置' },
  { id: 'kc_flex4', url: 'https://www.mrk.com.tw/product_ii.html?ID=561', label: 'FLEX ERA 4 霧燈（一對）', price: 23500, cur: 'TWD', brand: 'KC HiLiTES', part: '0289', photo: true, key: 'frontBumper',
    note: '4 燈 LED 方燈、160W 混合光；裝在 KLC 前保桿下管兩端（車主實車配置，前保桿模型已含）' },
  { id: 'wlm_guard', photo: true, key: 'windowGuards', url: 'https://www.buerjitw.com/products/wlm-%E7%AA%97%E6%88%B6%E9%98%B2%E8%AD%B7%E7%B6%B2-jimny-jb74', label: '後側窗鐵窗', price: 5200, cur: 'TWD', brand: 'WLM 4x4', part: 'JB7408 / JB7409',
    note: '每片；795×533 雷射切割方孔板、雨槽夾固定，可掀式；配置器「鐵窗（WLM）」' },
  { id: 'fr_ladder', key: 'ladder', url: 'https://ozjimny.com/products/front-runner-ladder-jimny-models-2023-current-xl', label: 'Jimny 尾門後爬梯', price: null, cur: 'AUD', brand: 'Front Runner', part: 'LASJ004', uncertain: true,
    note: '4 階、鉸鏈側；配置器「後爬梯」' },
  { id: 'suzuki_cover', key: 'spareCover', url: 'https://jdmyamato.com/products/y08-sz0001-00024', label: '原廠硬式備胎蓋', price: null, cur: 'JPY', brand: 'SUZUKI', part: '9923B-77R21-003', uncertain: true,
    note: '硬質樹脂面＋皮革背；配置器「備胎硬殼蓋」' },
  { id: 'trasharoo', key: 'spareBag', url: 'https://agileoffroad.com/products/trasharoo-spare-tire-trash-bag', label: '備胎書包（Trasharoo）', price: null, cur: 'USD', brand: 'Trasharoo', uncertain: true,
    note: '配置器「備胎書包」' },
  { id: 'maxx', photo: true, url: null, key: 'wheel', label: '旋壓 10 輻輪框 16×6.0J ±0', price: 4100, cur: 'TWD', brand: 'MAXX（台灣）', note: '消光黑，配 TOYO Open Country M/T 225/75R16（車主實車配置）' },
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
  if (cfg.extinguisher === 'ladder' && cfg.ladder === 'none') {
    out.push({ level: 'error', msg: '滅火器掛在尾梯上，但目前沒有裝尾梯' });
  }
  if ((cfg.extinguisher === 'left' || cfg.extinguisher === 'right') && !cfg.windowGuards) {
    out.push({ level: 'error', msg: '滅火器綁在鐵窗的 MOLLE 板上，但目前沒有裝鐵窗' });
  }
  // JB74 roof load is 30 kg dynamic. A tray is 14-18 kg on its own, so a
  // heavy light set on top of one is over the limit before anything is
  // strapped down.
  if (cfg.roofRack !== 'none' && (cfg.roofLights === 'kc_pro6' || cfg.lightBar === 'stedi_st4k')) {
    out.push({ level: 'warn',
      msg: 'JB74 車頂動態載重只有 30kg；平盤車頂架 14–18kg 加上這組燈（KC Pro6 11.3kg／ST4K 6.6kg）已經吃滿，不要再放行李' });
  }
  if (cfg.exhaust === 'taniguchi_compe_r' && cfg.rearBumper !== 'stock') {
    out.push({ level: 'warn', msg: 'TANIGUCHI Compe R 的管口要從後保桿右角穿出；社外後保桿沒有任何一家公布相容性，需實車確認' });
  }
  if ((cfg.exhaust === 'jaos_zs' || cfg.exhaust === 'showa_links') && cfg.rearBumper !== 'stock') {
    out.push({ level: 'info', msg: '這套排氣管原廠保桿要局部裁切；換成社外後保桿後是否還需要修改，請向店家確認' });
  }
  return out;
}

export function priceOf(list, id) {
  const it = list.find((x) => x.id === id);
  return it?.price ?? null;
}


// DAMD 全車套件（damd.co.jp）。選一款就同時換掉水箱罩與前後保桿。
// 這三款都保留原廠圓形頭燈，所以只換面板；saudade / little 5. / little Δ
// 會換成方形或四圓頭燈，還沒建模。
export const KITS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'little_d', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-d/', label: 'little D. Defender 風套件', price: 305800, cur: 'JPY', brand: 'DAMD',
    set: { grille: 'damd_little_d', frontBumper: 'damd_little_d', rearBumper: 'damd_little_d_rear' },
    note: 'JB74 車身件套件未塗裝 ¥305,800，烤漆另加 ¥96,800。ABS；水箱罩一律消光黑。台灣無總代理，授權經銷商台中 Fujii74' },
  { id: 'little_g_trad', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_little-g_traditional/', label: 'little G. TRADITIONAL 套件', price: 547800, cur: 'JPY', brand: 'DAMD',
    set: { grille: 'damd_little_g_trad', frontBumper: 'damd_little_g_trad', rearBumper: 'damd_little_g_trad_rear' },
    note: 'JB74 車身件套件未塗裝 ¥547,800，烤漆另加 ¥145,200。含引擎蓋罩與蓋上方向燈（尚未建模）' },
  { id: 'urnieta_salado', url: 'https://urnieta.com/', label: 'SALADO 遠征越野套件', price: null, cur: 'TWD', brand: 'URNIETA', uncertain: true,
    set: { grille: 'urnieta_salado', frontBumper: 'urnieta_salado', rearBumper: 'urnieta_salado_rear', sideStep: 'urnieta_salado', hood: 'urnieta_salado', spareCoverKit: 'urnieta_salado', roofRack: 'urnieta_salado', ladder: 'urnieta', exhaust: 'urnieta_salado' },
    note: '中國東莞斯塔克工業（歐尼塔）；官網不標價，僅後保桿在台灣蝦皮有 NT$27,000。整套另有鋁引擎蓋、管狀側桿、行李架、後梯、四出排氣、涉水管（部分尚未建模）。只支援 JB74／JC74' },
  { id: 'urnieta_1970', url: 'https://urnieta.com/', label: '1970 復古套件（70 年代風）', price: 49400, cur: 'TWD', brand: 'URNIETA',
    set: { grille: 'urnieta_1970', frontBumper: 'urnieta_1970', rearBumper: 'urnieta_1970_rear', sideStep: 'urnieta_1970', hood: 'urnieta_1970', spareCoverKit: 'urnieta_1970' },
    note: '中國東莞斯塔克工業（歐尼塔）品牌，2026/6 上線；官網不標價，此為台灣三件合計。半高式前後保桿＋衝壓金屬網水箱罩，後保桿用圓形尾燈（官方寫致敬 Nissan GT-R）。同系列另有引擎蓋、側裙、備胎蓋、鷗翼窗（尚未建模）。只支援 JB74／JC74' },
  { id: 'roots', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'JIMNY the ROOTS. LJ10 風套件', price: 213400, cur: 'JPY', brand: 'DAMD',
    set: { grille: 'damd_roots', frontBumper: 'damd_roots', rearBumper: 'damd_roots_rear' },
    note: 'JB74 外觀三件組未塗裝 ¥213,400，烤漆另加 ¥99,000。與 APIO 共同開發。露天可見代購 NT$65,000（未烤漆）' },
];


// URNIETA 引擎蓋。套件是整片鋁製引擎蓋（減重約 65%），配置器只畫出在車上
// 看得出來的中央隆起與進氣口，蓋在原廠引擎蓋表面上。
export const HOODS = [
  { id: 'stock', label: '原廠引擎蓋', price: 0, brand: 'SUZUKI' },
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-hood-kit-for-jimny-jb74-jc74/', label: 'SALADO 鋁製引擎蓋', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-003：1408×882。鋁製減重約 65%，中央隆起後段一個大進氣口（三道鰭片＋中肋），沿用原廠鉸鍊／鎖扣／撐桿。6kg。官網不標價' },
  { id: 'urnieta_1970', url: 'https://urnieta.com/product/1970-hood-kit-for-jimny-jb74-jc74/', label: '1970 鋁製引擎蓋', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_1970', uncertain: true,
    note: '工程圖 UN-JIMNY-FB-025：1408×882。進氣口較小且位置偏中段（四道鰭片），右前角另有一組百葉散熱口，正面線條較接近原廠。6kg。官網不標價' },
];

// 套件專用備胎蓋（原廠硬殼蓋仍在「配件」開關裡）
export const SPARE_COVERS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'urnieta_salado', url: 'https://urnieta.com/product/salado-extended-spare-tire-cover-for-jimny-jb74-jc74-jb64/', label: 'SALADO 延伸備胎蓋', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', uncertain: true,
    note: '外蓋可向下翻開變成工作檯，兩顆卡扣＋兩支撐桿。3.4kg，JB64 也能裝。官網不標價' },
  { id: 'urnieta_1970', url: 'https://urnieta.com/product/1970-spare-tire-cover-kit-for-jimny-jb74-jc74-jb64/', label: '1970 備胎蓋', price: null, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_1970', uncertain: true,
    note: 'MOLLE 格帶面板／收納包雙模式。3.4kg，JB64 也能裝。官網不標價' },
];
