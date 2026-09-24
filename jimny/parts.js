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
// Not a Suzuki colour. No JB74 has ever been sold in red -- Japan, Taiwan,
// Australia and the UK all checked; only the five-door JC74 gets "Sizzling
// Red" -- so the rally red is a wrap film, and says so.
COLORS.push(
  { code: '2080-G13', name: '紅色（3M 2080 Gloss Hot Rod Red 改色膜）', hex: 0xc81b22, twoTone: false, tw: false, wrap: true,
    note: '非原廠色。JB74 在日本、台灣、澳洲、英國都沒有原廠紅，只有五門的 JC74 有 Sizzling Red。這是 3M 改色膜 2080-G13；台灣包膜行的休旅車級距 3M 膜約 NT$115,000（不是 Jimny 專屬報價，車小可能更低）。顏色是照產品照片估的，3M 不公布色碼' });
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
  // The list ran from stock upwards only, which quietly made "modified" mean
  // "taller". Japan's street scene goes the other way and this is the spring
  // it uses.
  { id: 'klc_turtles', url: 'https://www.klc-div.com/heritage/product/suspension/superdownspringturtles/', label: 'SUPER DOWN SPRING TURTLES 降低彈簧', inch: '−1.5"', lift: -40, body: 0, price: 30800, cur: 'JPY',
    brand: 'KLC Heritage', uncertain: true,
    note: '只換彈簧的降低組，適用 JB64W／JB74W／JC74W，¥30,800 稅込。廠方只公布 JB64 的數字「純正比約 40 ミリのローダウン」，JB74 降多少官網沒有單獨寫，這裡先照 40mm 估' },
  { id: 'klc30', url: 'https://www.klc-div.com/heritage/product/suspension/lift-upspringtodoroki/', label: 'Heritage 轟 升高彈簧', inch: '1"', lift: 30, body: 0, price: 38500, cur: 'JPY',
    brand: 'KLC', note: 'KLC Heritage 商品頁：リフトアップサスペンション轟 ¥38,500 稅込，官方僅列「JB64W／JB74W シエラ／JC74W ノマド」共用適用，未單獨標示 JB74 的升高量；頁面上出現的「約 30mm」其實是 JB64 的數字。純彈簧套件，沿用原廠避震、在原廠行程內升高，官方稱免延長煞車油管、裝著狀態可通過車檢。JB74 實際升高量官網未公布，此處沿用 JB64 的數字估算。',
    uncertain: true },
  { id: 'sg25', url: 'https://www.showa-garage.shop/shopdetail/000000000529/', label: '1 吋升高彈簧', inch: '1"', lift: 25, body: 0, price: 40700, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00350', note: '只換彈簧；建議加橫拉桿組（含拉桿 ¥90,200）' },
  { id: 'ms20', url: 'https://www.monster-sport.com/product/parts/sus/jb74w_hisusset/', label: '20mm 懸吊組', inch: '1"', lift: 20, body: 0, price: 99000, cur: 'JPY',
    brand: 'MONSTER SPORT', part: '510500-5600M', note: 'MONSTER SPORT 現行實際在售的 JB74W 專用品為「ハイトアップサスペンションセット」，品番 510500-5600M，¥99,000 稅込（¥90,000 稅抜），前後各升高約 20mm、14 段可調，彈簧常數前 2.3／後 2.5 kgf/mm，官方註明 JB74W 專用、不適用 JB64W。原目錄寫的 type-2（品番 510502-5600ML，¥94,600 稅込）官網仍標示「開発中」、為預定售價，尚未正式開賣，故換成現行實際在賣的品項。' },
  { id: 'apio20', url: 'https://www.apio.jp/parts/1028-1aa.html', label: '7420SA 懸吊組', inch: '1"', lift: 20, body: 0, price: 141900, cur: 'JPY', brand: 'APIO',
    part: '1028-1AA', note: 'アピオ官網現行定價 ¥141,900 稅込，品番 1028-1AA，JB74 專用，升高約 20mm。內容為 JB74 專用 20mm 彈簧、14 段減衰力可調避震器、LED 頭燈水平調整板與螺帽。官方註明為車檢對應品（免結構變更），安裝不需延長煞車油管。' },
  { id: 'es30', url: 'https://www.4x4es.co.jp/2021/02/19/', label: 'Country 30mm 懸吊組', inch: '1"', lift: 30, body: 0, price: 139700, cur: 'JPY',
    brand: '4x4 Engineering', part: '74743-31C', note: '4x4 Engineering 官方報價：JB74 30mm 基本款 74743-31C ¥127,000 稅抜（¥139,700 稅込），內容只有前後彈簧與 14 段可調避震器，不含橫拉桿或轉向阻尼器。同系列另有 74743-31LC（LED 頭燈水平支架版，¥142,560 稅込）、74743-32C（加橫拉桿，¥199,100 稅込）等規格。' },
  // ---- 1.5 吋 (40mm)
  { id: 'jaos40', url: 'https://www.jaos.co.jp/product/A734518Z/3218/', label: 'BATTLEZ VFS ver.A 40mm 全套組', inch: '1.5"', lift: 40, body: 0, price: 184800,
    cur: 'JPY', brand: 'JAOS', part: 'A734518Z', note: 'JAOS 官網定價 ¥184,800 稅込（¥168,000 稅抜），品番 A734518Z，適用 2018.07- JB74 系全等級，官方標示前後升高量為 35〜40mm（並非固定 40mm），產品淨重 24.54kg。內容含鈦合金彈簧、搭載 Harmoflex 的阻尼器、長煞車油管、前後橫拉桿、Assist Kit（前 Caster 襯套與定位治具）與 LED 頭燈車用水平調整長支架；長煞車油管確認是套件內容物之一，不是另購件。' },
  { id: 'apio40', url: 'https://www.apio.jp/parts/1034-1ae.html', label: '7440Ti 懸吊全套組', inch: '1.5"', lift: 40, body: 0, price: 276100, cur: 'JPY', brand: 'APIO',
    part: '1034-1AE', note: 'アピオ官網定價 ¥276,100 稅込，品番 1034-1AE，JB74 專用，升高約 40mm，車檢對應（免結構變更）。內容為 A2000Ti 含鈦彈簧一台份、長行程 14 段可調避震器、前後調整式強化橫拉桿、後緩衝塊墊片、Caster 偏心襯套、延長煞車油管、LED 頭燈水平調整板。官網全文未提及駕駛座方向限制，原本「⚠ 僅支援右駕」查無依據，已拿掉。' },
  { id: 'omr40', url: 'https://megajimny.com/products/arb-old-man-emu-40mm-lift-kit-2018-jimny', label: 'Old Man Emu 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 2410, cur: 'AUD', brand: 'ARB',
    note: '含橫樑補強、Panhard 座、煞車油管延長、Caster 襯套；彈簧依保桿／絞盤重量選' },
  { id: 'dob40', url: 'https://megajimny.com/products/dobinsons-ims-monotube-40mm-lift-kit', label: 'IMS Monotube 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 1949, cur: 'AUD',
    brand: 'Dobinsons' },
  { id: 'td40', url: 'https://www.toughdog.com.au/Products/SuzukiJimnyJB74.aspx', refs: ['https://www.directsuspensions.com.au/products/tough-dog-40mm-lift-kit-for-suzuki-jimny-jb74-3-door-2019-on'], label: 'Foam Cell 40mm 懸吊組', inch: '1.5"', lift: 40, body: 0, price: 1467, cur: 'AUD',
    brand: 'Tough Dog' },
  // ---- 2 吋 (50mm)
  { id: 'sg50', url: 'https://www.showa-garage.shop/shopbrand/I84526', label: 'SG Custom 50 Ennepetal 懸吊組', inch: '2"', lift: 50, body: 0, price: 323400,
    cur: 'JPY', brand: 'SHOWA GARAGE', part: 'S00853', note: 'BA 全套 ¥480,700（加長煞車油管＋橫拉桿）' },
  { id: 'cusco50', url: 'https://shop.nstparts.com/products/cusco-2-inch-lift-suspension-kit-suzuki-jimny-jb74', label: '2 吋懸吊組（50–75mm 可調）', inch: '2"', lift: 50, body: 0, price: 167200, cur: 'JPY',
    brand: 'CUSCO', part: '60N-6JS-U20', note: 'CUSCO 官網定價 ¥167,200 稅込（¥152,000 稅抜），JB74W 品番 60N-6JS-U20（JB64W 為另一品番 60M-6JS-U20，規格相同）。車高調整範圍 +50〜+75mm，前後 14 段減衰力可調。內容含避震器、彈簧、螺牙墊片、大容量緩衝塊各 4 件、延長煞車油管、ABS 線束與自由輪轂油管移位套件。升高 2 吋以上前傳動軸易與原廠橫樑干涉，建議另購下移支架；LED 頭燈自動水平車型需另購調整桿。' },
  { id: 'im50', url: 'https://ozjimny.com/products/ironman-4x4-50mm-suspension-lift-kit-constant-front-load-with-gas-shock-absorbers', label: 'Nitro Gas 50mm 懸吊組', inch: '2"', lift: 50, body: 0, price: 1757, cur: 'AUD',
    brand: 'Ironman 4x4', part: 'SUZ010BKG', note: '含延長煞車油管、橫樑下降座、2° Caster 襯套、延長緩衝塊' },
  // ---- 2.5 吋 (60mm)
  { id: 'tg60', url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_suspension/', label: 'SOLVE ACE60 懸吊組', inch: '2.5"', lift: 60, body: 0, price: 220220, cur: 'JPY',
    brand: 'TANIGUCHI', note: 'オフロードサービスタニグチ官網（2025.2.1 改價後）：SOLVE ACE60 サスペンションキット JB74 用 ¥220,220 稅込，升高約 60mm。內容含彈簧、專用避震器、延長煞車油管、キャスタードリーム、橫拉桿、後橫拉桿補正支架、偏置防傾桿墊片。原廠第三橫樑無法沿用，官方標示「裝著推奨」需另購 SOLVE クロスメンバー ¥29,700；1〜4 型原廠 LED 頭燈車另需調整式水平調整桿。' },
  { id: 'td60', url: 'https://www.toughdog.com.au/Products/SuzukiJimnyJB74.aspx', refs: ['https://ozjimny.com/products/tough-dog-4wd-suspension-60mm-suspension-lift-kit-with-braided-brake-lines-steel-bullbar-no-winch'], label: 'Foam Cell 60mm 懸吊組', inch: '2.5"', lift: 60, body: 0, price: null, cur: 'AUD',
    brand: 'Tough Dog', uncertain: true, note: '含編織煞車油管；報價制' },
  // ---- 3 吋 (75mm)
  { id: 'sg75', url: 'https://www.showa-garage.shop/shopbrand/I84527/', label: 'SG 彈簧 75 X-SHOCK 懸吊組', inch: '3"', lift: 75, body: 0, price: 234300, cur: 'JPY',
    brand: 'SHOWA GARAGE', part: 'S00373', note: 'JB74 適用 1〜5 型。標準組 ¥234,300（S00373）、B 組 ¥246,400（S00374）、BA 全套 ¥389,400（S00375），皆稅込；需另購 Caster 修正臂。原本記的 S00472／¥253,000／BA ¥394,900 三個數字都是五門 JC74 的' },
  { id: 'es70', url: 'https://www.4x4es.co.jp/2025/04/08/', label: 'Country 70mm 懸吊組', inch: '3"', lift: 70, body: 0, price: 217030, cur: 'JPY',
    brand: '4x4 Engineering', note: '4x4 Engineering 官方報價：JB74 70mm 基本款 74745-31B ¥197,300 稅抜（¥217,030 稅込），內容為前後彈簧、Harmoflex 14 段可調避震器、後避震墊片、橫樑下移支架、煞車油管、傳動軸墊片。要橫拉桿需升級 74745-32B（¥303,380 稅込），要轉向阻尼器＋橫拉桿的全配為 74745-32LSB（¥330,110 稅込）。原本標示的 ¥315,000 對不上官方任何一組報價，且套件內容也不屬於基本款。',
    part: '74745-31B' },
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
    price: 47300, cur: 'JPY', brand: 'APIO', note: 'APIO 官網現役商品，15 吋仍在售，¥47,300／本（稅込），鋁合金鑄造一體式、JWL／JWL-T 規格，約 7.35kg，附專用同色輪圈蓋。適合 JB74／JB43／JB33／JB32／JB31。APIO 未公布中心孔徑，JB74 需要 108.1mm，下單前請向 APIO 確認。',
    part: '7200-15R（レイドブラック）／7200-15G（ガンブラック）' },
  { id: 'bradley', label: 'Bradley V 六輻輪框', rim: 16, width: 5.5, offset: 0, style: 'six',
    price: 53900, cur: 'JPY', brand: '4x4 Engineering', note: '4x4 Engineering 官網確認 BRADLEY V 中心孔 110mm、PCD5/139.7。JB74 シエラ／JC74 用 16×5.5J ±0（本目錄採用，¥49,000 稅抜／¥53,900 稅込 每顆）；另有 16×6.0J −6（¥51,000 稅抜／¥56,100 稅込）。16×5.5J +22 是 JB23／JB64 專用，不適用 JB74 シエラ。官網未列材質與重量。' },
  { id: 'xtremej', label: 'XTREME-J XJ04 輪框', rim: 16, width: 5.5, offset: -5, style: 'eight',
    price: 59400, cur: 'JPY', brand: 'MLJ',
    note: 'MLJ 官方尺寸表確認：16×5.5J INSET+22（PCD5/139.7，*3）是 JB23／JB64ジムニー 專用；JB74 シエラ 對應的是同尺寸 16×5.5J INSET−5（*4）。單顆稅込價 サテンブラック ¥59,400、グロスブラックマシーン／スモーククリア與マットブロンズ／ブラックリム皆 ¥62,700。MLJ 未公布中心孔徑；官網對這個 −5 規格沒有特別註記需要爆龜或寬体（offset 比原廠 +5 多凸出約 10mm，實裝前建議自行量測輪拱間隙）。同廠 XJ07 另有 16×6.0J −5（¥62,700〜¥67,100）可選，凹度更深。',
    part: 'XTREME-J XJ04' },
  { id: 'te37xt', label: 'TE37XT for J 鍛造輪框', rim: 16, width: 5.5, offset: 0, style: 'six',
    price: 83600, cur: 'JPY', brand: 'RAYS', note: 'RAYS 官網商品名為「VOLK RACING TE37XT for J」，沒有「M-SPEC」字樣。JB74 シエラ 對應 16×5.5J ±0 或 16×6.0J −5；JB64／一般ジムニー 用的是 16×5.5J +20，本目錄採前者（±0）。鍛造一體式，中心孔 112φ、PCD139.7、5孔。單顆稅込價：16×5.5J（±0 與 +20 同價）標準色 BC 布拉斯特黑 ¥83,600、BR 古銅色 ¥88,000；16×6.0J −5 為 BC ¥84,700、BR ¥89,100。RAYS 未公布重量。',
    part: 'VOLK RACING TE37XT for J（06456550015BC 標準黑）' },
  { id: 'oz_rally', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta/', label: 'Rally Racing 復刻 16 吋輪框', rim: 16, width: 6.0, offset: -5, style: 'oz20', needsFlares: true,
    price: 53900, cur: 'JPY', brand: 'OZ Racing × DAMD',
    note: '80–90 年代拉力賽那顆 Rally Racing 的復刻，OZ 協力、旋壓製法。16×6J −5、5×139.7，單顆 8.584kg，JB74／JC74 用。單顆 ¥53,900、五顆 ¥269,500，稅込。賽車白／深石墨／消光黑／消光古銅。DAMD 官網未公布料號' },
  { id: 'maxx', photo: true, label: '旋壓 10 輻輪框', rim: 16, width: 6.0, offset: 0, style: 'ten',
    price: 4100, cur: 'TWD', brand: 'MAXX（台灣）',
    note: '台灣賣的是 16×6.0J ±0，不需要爆龜。消光黑／古銅／槍灰／黑底亮唇；超前輪業、真便宜輪胎館等多家現貨 NT$4,000–4,200 一顆。車主實車配置' },
  // ---- 復古框（2026-09 調查）。JB74 中心孔 108.1mm，日規 5×139.7 一律 108.25-108.8 可用；
  // Cragar S/S（91.44）與 American Racing TT-O（83.06）孔徑太小，無法用轉接環補救，故未收錄
  { id: 'dean_cross', photo: false, url: 'https://www.dean-wheels.com/', label: 'Cross Country 五槽鋼圈臉', rim: 16, width: 6.0, offset: -5, needsFlares: true, style: 'slot5',
    price: 10500, cur: 'TWD', brand: 'DEAN', note: '水平五槽鋼圈臉，中心鍍鉻板可拆，拆掉即露出 5 幅。台灣 MRK 4X4 現貨 NT$10,500 一顆，Marguerite White／Mat Black' },
  { id: 'showa_eight', photo: false, url: 'https://showa-garage.shop/shopbrand/I1582', label: 'IGNITION EIGHT 八柱輪框', rim: 16, width: 6.0, offset: 0, style: 'eightpin',
    price: 37400, cur: 'JPY', brand: 'SHOWA GARAGE',
    note: 'SHOWA GARAGE 官方商店確認品番 w00235、16×6.0J ±0，商品頁明寫「37,400円（税込）/本」（單顆，非四顆一組），適合車種「ジムニーシエラ JB74／JB43」（含 JC74）。JB64／JB23 用的是另一顆 w00230（16×5.5J +20、¥36,300 稅込）。查詢當下マットブラック色顯示售罄，下單前請先確認庫存。',
    part: 'w00235' },
  { id: 'daytona_ss', photo: false, url: 'https://www.mljinc.co.jp/product/daytona_ss/daytona_ss', label: 'DAYTONA SS 兩件式鋼圈', rim: 16, width: 6.0, offset: 0, style: 'daytona',
    price: 29700, cur: 'JPY', brand: 'MLJ', note: 'MLJ 官方尺寸表 PCD5-139.7 這一列（*9）同時有 15×6.0J INSET±0（¥28,600 稅込）與 16×6.0J（INSET 欄留白、官網未公布數值，¥29,700 稅込），適合車種寫「JB74ジムニーシエラ」；目錄沿用 16×6.0J、¥29,700 稅込／本，offset 暫以 ±0 標示但官網並未證實，下單前需向 MLJ 確認。另一列 16×5.5J INSET+20（黑／全白 ¥29,700 稅込）的適合車種其實是「JA/JBジムニー」（JB64 等軽自動車），不適用 JB74 シエラ——目錄原句「白色版只有16×5.5J+20」數字沒錯，但那個尺寸根本不裝 JB74，白色目前查無適用 JB74 的規格。「街價約¥13,360」查無出處，已刪除。',
    uncertain: true },
  { id: 'super_moon', photo: false, url: 'https://shop.beyond-jpn.com/products/bewl74-smch', label: 'SUPER MOON 月亮盤', rim: 16, width: 6.0, offset: -5, needsFlares: true, style: 'moon',
    price: 23100, cur: 'JPY', brand: 'Beyond Japan', part: 'bewl74-smch',
    note: '完全無孔的光滑碟盤，最極端的 moon disc 語彙。16×6.0J INSET −5、PCD 139.7，品名就寫「スーパームーン【JB74W・クローム】」——JB74W／JC74 專用，JB64 是另一個品番。鍍鉻 ¥23,100（原價 ¥38,500 特價中）、黑／白 ¥19,800，**都是一顆的價**，官網寫明「こちらの商品ページは単品販売となります」' },
  { id: 'watanabe_f8', photo: false, url: 'https://www.rs-watanabe.co.jp/jimny/', label: 'F8 八輻輪框', rim: 16, width: 5.5, offset: 0, style: 'watanabe',
    price: 49500, cur: 'JPY', brand: 'RS Watanabe', note: 'RS Watanabe 官網 Jimny 專頁確認 F8（Eight Spoke）16×5.5J ±0、PCD5×139.7 為 Jimny Sierra（JB74）規格；16×5.5J +22 才是 JB64／JA Jimny 規格，5 孔沒有 6 孔的混淆疑慮。官網價格 ¥45,000／本是「業者様用・税別」（未稅），換算稅込約 ¥49,500／本；標準黑，其餘色（銀／金／鎂／紅／藍／黃／白等）加價 ¥3,000 稅別（約 ¥3,300 稅込）。中心孔徑與重量官網未公布，台灣無代理。' },
  { id: 'mrk_retro', photo: false, url: 'https://www.mrk.com.tw/', label: '復古輪框（陶瓷白）', rim: 16, width: 5.5, offset: 20, style: 'daytona',
    price: 5500, cur: 'TWD', brand: 'MRK', note: '台製現貨、中心孔 108.1 正確；陶瓷白／銀／消光黑。15×6.0J −5 為 NT$3,980' },
  // ---- 2026-09 依各家型錄補齊。輪轂孔徑各家不同（Enkei 108.2、MLJ/Watanabe 108.5、
  // DEAN/RAYS 108.8、Hayashi/BRADLEY 110-110.5 靠螺帽定心）；小於 108.1 裝不上且無法用轉接環補救。
  // offset 低於 -5 會凸出葉子板，需搭配爆龜（needsFlares）
  { id: 'wildboar_d', url: 'https://apio.jp/parts/7200-60.html', label: 'WILDBOAR D 蓮根紋輪框', rim: 16, width: 6.0, offset: -5, style: 'renkon',
    price: 48400, cur: 'JPY', brand: 'APIO', needsFlares: true,
    note: '碟面內凹，單圈 16 個錐形沉孔（蓮根紋），輪唇有對比色飾帶。APIO 官網同一顆輪圈依塗裝分兩種 offset：グロスブラック／スモーククリア是 16×6.0J ±0（7200-62B）；セミグロスブラック／ウッドカッパー（2026-04-20 新色）才是 16×6.0J −5（7200-62F）——本目錄採用的是後者這個新色版本。無中心蓋、螺帽外露，PCD139.7、5孔，約8.62kg，¥48,400／本稅込。APIO 未公布中心孔徑。' },
  { id: 'wildboar_sr', url: 'https://apio.jp/parts/7200-28.html', label: 'WILDBOAR SR 四弧槽輪框', rim: 16, width: 6.0, offset: -5, style: 'arc4',
    price: 48400, cur: 'JPY', brand: 'APIO', needsFlares: true,
    note: '復古壓鋼圈造型：外圈平帶＋內凹中央盤，四道細長弧槽在 1:30／4:30／7:30／10:30，槽緣有滾邊。APIO 官網 16×6.0J −5 這個規格頁只列 Iron Black（7200-47B）與 Cotton White（7200-47W）兩色，查無目錄原寫的 Iron Grey。適合 JB74 シエラ／JC74 ノマド，約 8kg，附專用輪圈蓋。' },
  { id: 'street18', url: 'https://www.rayswheels.co.jp/products/brand/detail/144', label: 'A・LAP-07X 七輻鍛造輪框', rim: 18, width: 7.0, offset: 8, style: 'seven', needsFlares: true,
    price: 97900, cur: 'JPY', brand: 'RAYS', part: '10098700815BD',
    note: '鍛造一件式，七輻深凹面；5×139.7／中心孔 108.8mm，JB64W／JB23W／JB74W 共用。黑／輪緣車亮 ¥97,900、青銅陽極 ¥100,100，皆稅込單顆。同型號另有 −2 offset（品番 10098706215）。RAYS 的實車配置是 18×7.0J +8 配 225/60R18，原廠車高未動懸吊。WedsSport、MLJ XTREME-J、4x4 Engineering Bradley V 官方適合表給 JB74 的都只到 16 吋，這是目前查到唯一 JB74 可用的 18 吋日系現行款' },
  { id: 'xj07', url: 'https://www.mljinc.co.jp/product/xtreme-j/xj07/', label: 'XTREME-J XJ07 梯形窗輪框', rim: 16, width: 6.0, offset: -5, style: 'dwindow',
    price: 67100, cur: 'JPY', brand: 'MLJ', needsFlares: true,
    note: '8 個梯形 D 窗；官方標示 16×6.0J −5（*9，適合車種「JB74ジムニーシエラ」）為 ULTRA DEEP CONCAVE（全系列最深）。無鉚釘、無假 beadlock，孔徑 108.5mm，PCD5/139.7。目錄價 ¥67,100 稅込是マットブロンズ／ブラックリム這個色的價格；基本色サテンブラック是 ¥62,700 稅込／本，這個尺寸不提供グロスブラックマシンインディゴ。' },
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
  { id: 't215r18', label: '215/55R18', dia: 694, width: 215, rim: 18, needLift: 0, needBody: 0,
    legal: true, note: '外徑 694mm，跟原廠 195/80R15 幾乎一樣，所以不必動舉升；差別全在胎壁——55 系列的側面高度只有原廠的一半出頭，輪拱會被輪框而不是被胎填滿' },
  { id: 't225r55', label: '225/55R18', dia: 705, width: 225, rim: 18, needLift: 0, needBody: 0,
    legal: true, note: '+1.7%，比原廠只大一點；TOYO OPEN COUNTRY H/T Ⅱ 官方表有這個尺寸（98H，有白字）' },
  { id: 't225r18', label: '225/60R18', dia: 727, width: 225, rim: 18, needLift: 0, needBody: 0,
    legal: true, note: '+4.9%，RAYS A・LAP-07X 18×7.0J +8 的實車配置就是這個尺寸，原廠車高未動懸吊' },
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
  // highway / road patterns: continuous ribs and straight grooves, no blocks
  { id: 'bs_ht684', pattern: 'ht', url: 'https://tire.bridgestone.co.jp/dueler/equipment/', brand: 'BRIDGESTONE', model: 'DUELER H/T684Ⅱ', owl: false,
    label: 'DUELER H/T684Ⅱ 公路胎', note: 'JB74 Sierra 的原廠配胎：普利司通新車裝著一覽列 195/80R15 96S、品番 PSR16069、¥24,310 稅込。連續直溝加肩部連續肋，低噪音' },
  { id: 'toyo_ht2', pattern: 'ht', url: 'https://www.toyotires.jp/product/opht2/', brand: 'TOYO TIRES', model: 'OPEN COUNTRY H/T Ⅱ', owl: true, owlSizes: ['t225r18', 't225r55'],
    label: 'OPEN COUNTRY H/T Ⅱ 公路胎', note: '官方尺寸表沒有 195/80R15 與 215/70R16；18 吋有 225/60R18、225/55R18、235/60R18，都有白字。肩部連續肋、直線縱溝的低噪音公路胎紋' },
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
    note: 'JAOS 日本官網確認 ¥66,000 稅込／¥60,000 稅抜，品番 B040518，聚氨酯未塗裝黑本體配鋁網，單品 5.05kg。適合年式 2018 年 7 月〜2025 年 11 月、全等級皆可裝；全長 +10mm、下緣 −80mm，寬度在全寬內。官網目前顯示售完，預計 2026 年 11 月上中旬出貨。目錄中的 NT$18,700 是台灣售價，本次查證只找到 JAOS 日本官網資料，MRK 等台灣代理站上未查到這支前下巴的對應頁面，NT$ 數字暫無法對應到第一手來源，先標 uncertain。',
    uncertain: true },
  // ---- 日本
  { id: 'klc_short', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/frontshortbumper74/', photo: true, label: 'Front Short Bumper 74 前保桿', price: 102300, cur: 'JPY', brand: 'KLC Heritage',
    note: 'ABS 樹脂、原廠高度縮短版，中央鋁網開口（銀色）、保留原廠霧燈。塗裝色只有皺紋黑：塗裝完成品 ¥102,300、未塗裝素材 ¥69,300，皆稅込。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝' },
  { id: 'klc_trad', photo: true, url: 'https://www.klc-div.com/heritage/product/bumper/traditionalbumperfront_2_iv/', photo: true, label: 'Traditional 雙管前保桿（象牙白）', price: 99000, cur: 'JPY', brand: 'KLC Heritage',
    note: '與黑色同一支、象牙白塗裝。全不鏽鋼製，無霧燈架 ¥99,000、含霧燈架 ¥110,000，皆稅込。適用 JB74W シエラ 與 JC74W ノマド，シエラ 5 型與 ノマド 2 型不可裝。（原本連到的是 JB64 的頁面，¥104,500 是那台的價）' },
  { id: 'outclass_t2', photo: true, url: 'https://outclass.ocnk.net/product/1095', photo: true, label: 'TYPE2 絞盤鋼製前保桿', price: 140800, cur: 'JPY', brand: 'OUTCLASS',
    note: 'OUTCLASS 官網確認 ¥128,000 稅別／¥140,800 稅込（希望小售價 ¥180,000），品番 JB64JB74JC74-A-FB2UBTETU【260/160サイズ】，鋼製，適用 JB64／JB74／JC74。含絞盤床與四顆 LED（霧燈 ×2、工作燈 ×2），導索器、D 環與絞盤本體另購；官網目前顯示 Raptor 塗層選項「受付中止」，出廠僅提供未烤漆素材。原廠頭燈清洗器無法安裝，重量官網未標示。',
    part: 'JB64JB74JC74-A-FB2UBTETU' },
  { id: 'taniguchi_square', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: '角形前保桿', price: 58300, cur: 'JPY', brand: 'TANIGUCHI',
    note: 'TANIGUCHI 官網確認鋼製粉體烤漆黑 ¥58,300 稅込、不鏽鋼 SUS304 #400 研磨版 ¥107,800 稅込（安裝支架仍為鋼製），適用 JB64・74／JC74，本體約 3kg。「2mm 方管」查無依據——2mm 是同廠後保桿角形版的規格，前保桿頁面只公布材質、塗裝與重量，官網未公布品番與角管尺寸壁厚。' },
  { id: 'taniguchi_double', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: '雙管前保桿', price: 77000, cur: 'JPY', brand: 'TANIGUCHI',
    note: 'TANIGUCHI 官網確認 ¥77,000 稅込，鋼製粉體烤漆黑，管徑 48.6mm、壁厚 2.3mm，本體約 9kg，適用 JB64（XG 除外）／JB74／JC74。官網未公布品番。' },
  { id: 'toc_extreme', photo: true, url: 'https://tocbw.thebase.in/items/82110724', label: 'Extreme Bumper 74 前保桿', price: 54780, cur: 'JPY', brand: 'TOC BODYWORKS',
    note: 'TOC BODYWORKS 官方店確認「エクストリームバンパー74 フロント」¥54,780 稅込，適用 JB74 シエラ 與 JC74 ノマド，FRP 黑膠衣（ゲルコート）處理，出貨即需自行烤漆（官網另提供代烤漆加價選項）。官網明寫「LEDライトバー、スキッドプレートは含まれません」，且沒有內建 LED 燈條凹槽的說明。另有含 TOC スキッドプレート74 的兩件組 ¥82,280 與前後加護板的三件組 ¥137,060。目前為預購品，預計 2026 年 10 月 10 日起陸續出貨。' },
];

export const REAR_BUMPERS = [
  // ---- URNIETA 全車套件專用後保桿（urnieta.com）
  { id: 'urnieta_salado_rear', url: 'https://urnieta.com/product/salado-rear-bumper-for-jimny-jb74-jc74/', label: 'SALADO 後保桿', price: 27000, cur: 'TWD', brand: 'URNIETA', kit: 'urnieta_salado', ownLamps: true,
    refs: ['https://shopee.tw/product/7996649/54712201643'],
    note: '工程圖 UN-JIMNY-FB-002：高 216mm、展開全長 1816。半高式、兩端包覆轉角，左右各一組燈窗（一側 Salado、一側 URNIETA 銘牌），下方兩片腳踏板。16.4kg。台灣蝦皮 NT$27,000' },
  // ---- DAMD 全車套件專用後保桿（damd.co.jp）
  { id: 'damd_delta_rear', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta/', label: 'little 5.／Δ 後保桿（DB 方形尾燈）', price: 74800, cur: 'JPY', brand: 'DAMD', ownLamps: true,
    note: '素地 ¥74,800，little 5. 與 little Δ 共用；嵌德國 DB 的方形尾燈，外側兩塊凸起帶肋，下緣灰色。JB74 Sierra／JC74 用。官網不公布料號；形狀照官方照片估' },
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
    note: 'JAOS 台灣代理 MRK 定價 NT$26,500（未塗裝），日本官方 ¥92,400 稅込／¥84,000 稅抜，品番 B042518，聚氨酯未塗裝本體、不鏽鋼支架，單品 4.65kg。適合 JB74 系 1〜3 型（2018.07〜2024.04），4 型以後官網未列入適合表。四顆圓形 LED 尾燈通過 ECE 認證、可過原廠車檢；套件內附倒車攝影機支架（僅支架，不含攝影機本體）。' },
  // ---- 日本
  { id: 'wildgoose_crawler_rear', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1103.html', label: 'Crawler 圓管後保桿 JM-1103', price: 66000, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: 'RV4 Wild Goose 官網確認品番 JM-1103，¥60,000 稅抜／¥66,000 稅込，重量 9.3kg。鋼製，管徑 76.3mm、壁厚 1.6mm，黑色半消光塗裝，尺寸 W1330×H200×D225mm；尾燈座板厚 4.5mm、鏡片內縮 10mm 防撞設計，拖車環 Ø50mm（附 Ø20mm 鎖點）。官網明寫本體不含尾燈，尾燈是另購的「コンビネーションランプ」需自行選配安裝，原廠尾燈不與本桿共用。適用 ジムニー JB64 與 ジムニーシエラ JB74（JB74 因原廠寬體輪拱，兩側略短）。裝車需移動車牌與備胎。' },
  { id: 'wildgoose_box_rear', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/rear_bumper_64/jm-1101.html', label: '角管越野後保桿 JM-1101', price: 95700, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: 'RV4 Wild Goose 官網確認品番 JM-1101，¥87,000 稅抜／¥95,700 稅込，重量 13.2kg。鋼製，本體斷面 W1410×H100×D100mm，含支架整體尺寸為 W1410×H200×D220mm；本體板厚 3.2mm、安裝托架 9.0mm、補強板 3.2mm，陽離子電著加黑色半消光塗裝。主打 ジムニー JB64，ジムニーシエラ JB74 亦可裝（因原廠寬體輪拱兩側略短）。官網明寫本體不含尾燈，需另購「コンビネーションランプ」自行安裝；裝車需移動車牌與備胎。' },
  { id: 'showa_iron_rear', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000843/', refs: ['https://www.showa-garage.shop/shopbrand/ct343/'], label: 'Iron Bumper 鋼管後保桿', price: 62150, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00930', note: 'Ø60 主管＋Ø42 尾燈管翼，消光黑。¥62,150 稅込。適用 JB74 1〜4 型（5 型不可裝）。附 LED 倒車燈的版本依型式分兩個品番：1〜3 型 E00951 ¥127,160、4 型與 JC74 1 型 E00952 ¥127,930' },
  { id: 'taniguchi_rear_pipe', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_rear/', label: '鋼管越野後保桿', price: 63800, cur: 'JPY', brand: 'TANIGUCHI',
    note: 'TANIGUCHI 官網確認鋼管版（オフロードリアバンパー）¥63,800 稅込、管徑 48.6mm、壁厚 2.3mm，適用 JB64・74／JC74；角形版（リア角バンパー）鋼製同為 ¥63,800（純屬巧合非筆誤）、本體約 4kg、板厚 2mm，另有不鏽鋼 SUS304 #400 研磨版 ¥121,000 稅込；拖車鉤版 ¥128,700 稅込、管徑 48.6mm、壁厚 3.5mm，本體約 15kg 加安裝托架約 5kg，僅適用 JB64・74（不含 JC74）。三款官網皆未公布品番。' },
  { id: 'apio_tactical_rear', photo: true, url: 'https://apio.jp/parts/3032-71.html', label: 'Tactical 後保桿', price: 140800, cur: 'JPY', brand: 'APIO', part: '3032-71',
    note: 'APIO 官網確認 ¥140,800 稅込、品番 3032-71 未塗裝，烤漆版（消光黑）加 ¥33,000 稅込，ジムニーシエラ JB74 專用件（非 JB64 共用），ABS 真空成形。內容含本體、左右寬版延伸片、尾煞車燈殼、方向燈殼、倒車燈殼與反光片；燈殼為專用外殼取代原廠尾燈總成，燈泡／插座／線組沿用原廠零件（倒車燈需接長線組）。1660×280×460mm 為出貨外箱尺寸，並非本體實際寸法，本體寸法與重量官網未公布；部分倒車雷達車型需鑽孔。',
    ownLamps: true },
  { id: 'outclass_rear_abs', photo: true, url: 'https://outclass.ocnk.net/product/1094', ownLamps: false, label: 'TYPE2 ABS 後保桿', price: 45760, cur: 'JPY', brand: 'OUTCLASS',
    note: 'OUTCLASS 官網確認 ¥41,600 稅別／¥45,760 稅込（希望小售價 ¥83,200），品番 JB64JB74JC74-A-RB2ABS【200サイズ】，ABS 製，適用 JB64／JB74／JC74。標準品未塗裝且不含尾燈，尾燈（國產小型尾燈或 LED 燻黑版）、Raptor 黑塗裝、倒車雷達鑽孔皆為加價選配。',
    part: 'JB64JB74JC74-A-RB2ABS' },
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
    note: '七個縱向長孔營造立體感（KLC 原文「縦穴7つ穴で立体感を出す」，並非圓角方孔）、圓形大燈以方形圓角框收邊；ABS 素材 ¥60,500／FRP 素材 ¥55,000（皆稅込）' },
  { id: 'klc_forty', photo: true, url: 'https://www.klc-div.com/heritage/product/grille/facegrillforty/', label: 'Face Grille FORTY 水箱護罩', price: 93500, cur: 'JPY', brand: 'KLC Heritage',
    note: '大燈周圍肋條、中央網＋S 標' },
  { id: 'apio_sj', photo: true, url: 'https://apio.jp/parts/3033-58g.html', label: 'SJ Grille 鋼板水箱護罩', price: 58300, cur: 'JPY', brand: 'APIO', part: '3033-58G',
    note: 'SJ30 直縫沖壓鋼板、槍灰、黑鋁網' },
  { id: 'apio_marker', photo: true, url: 'https://apio.jp/parts/3033-59.html', label: 'Marker Vintage Iron 水箱護罩', price: 75900, cur: 'JPY', brand: 'APIO', part: '3033-59B（半光黑）／3033-59L（淺古銅）',
    note: '鋼製橫柵＋4 顆 IPF 標誌燈，半光黑或淺古銅' },
  { id: 'showa_hex', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000205/', photo: true, label: 'ABS 蜂巢水箱護罩', price: 16500, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00500', note: 'ABS 素材黑，需自行烤漆（官網原文：ABS樹脂は対候性が良くないため紫外線による劣化が早いので塗装してお使いください）；同系列烤漆款分 E00501（槍灰）／E00502（珍珠白）／E00504（藍配白線 ZJ3），烤漆款稅込 ¥37,400，並非目錄原載的 ¥31,900；中央蜂巢網開口' },
  { id: 'outclass_g', photo: true, url: 'https://outclass.ocnk.net/product/1071', photo: true, label: 'Vintage G 水箱護罩', price: 57750, cur: 'JPY', brand: 'OUTCLASS',
    note: 'ASA 樹脂紋理黑；4 道橫柵＋中央直柱，後方細網。¥52,500 稅抜／¥57,750 稅込；廠徽另購、不附安裝說明書，缺貨時約需 3 週',
    part: 'JB6474-A-FG-ASA' },
  { id: 'taniguchi_washer', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_front/', label: 'FRP Washer 水箱護罩', price: 44000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '原廠造型 FRP、中央網狀開口、洗燈噴嘴移入大燈' },
  { id: 'kpro_folksy', photo: true, url: 'http://www.k-products.shop/shopdetail/000000001706/', label: 'Folksy Style 橫鰭水箱護罩', price: 42493, cur: 'JPY', brand: 'K-PRODUCTS', uncertain: true,
    note: 'K-PRODUCTS 官方商店確認適合車種 JB64／JB74／JC74；FRP 材質、含網目件，品番 190604-1，官網標價 ¥42,493（稅別／稅込未標示），目前顯示 SOLD OUT。目錄原列 ¥30,000 是 4x4espoir 轉引的 JB64 舊稅別價，改用廠方頁面為準' },
  { id: 'prostaff_minig', photo: true, url: 'https://www.4x4espoir.com/jb64-frontgrill/', label: 'miniG 水箱護罩', price: 38000, cur: 'JPY', brand: 'Pro Staff', uncertain: true,
    note: '目前唯一可查到的資料來源（4x4espoir 轉載頁）寫適合車種是「新型ジムニーJB64W用」；另一篇同廠 miniG 保桿介紹（64swamp.com）也寫「こちらはJB64用」，兩份資料都指向 JB64 專用，沒有任何一份提到 JB74。プロスタッフ官網（4x4prostaff.com／www.4x4prostaff.com）本次查核仍連不上，無法直接核實。¥38,000（稅別）是 4x4espoir 轉引的舊價、非廠方現行價；JB74 適用性應標示為未確認，而不是目前隱含的「適用」' },
  { id: 'sixsense_explosion', photo: true, url: 'https://sixth-sense.shop-pro.jp/?pid=184181806', label: 'Explosion Classic 水箱護罩', price: 110000, cur: 'JPY', brand: 'Six Sense',
    note: 'シックスセンス 官方商店頁確認同時適用 JB64W 與 JB74W シエラ；材質 FRP 未塗裝需自行烤漆，開口部 240mm，品番 jimex108-nocl，價格 ¥110,000（官網明寫稅別）。目錄原價 ¥80,000 是 4x4espoir 轉引的舊稅別價，已用廠方現價更新；可選 SUZUKI 標準標誌或原廠標誌裝法，另有前格柵蓋加 LED 百葉套件 ¥16,500 選配',
    part: 'jimex108-nocl' },
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
  { id: 'damd', photo: true, url: 'http://www.damd.co.jp/products/suzuki/jimny_sierra_little-g', refs: ['https://easycars.jp/product/damd-truck-side-mirror-for-jimny-jb64-jb74/'], label: 'Truck Mirror 卡車式後照鏡', price: 75900, cur: 'JPY', brand: 'DAMD', photo: true,
    note: 'DAMD 日本官網建議售價：消光黑 ¥69,000 稅抜／¥75,900 稅込、鍍鉻 ¥74,000 稅抜／¥81,400 稅込；U 型管臂＋直式卡車鏡殼，含加熱但喪失電動收折與電動角度調整（官網原文：自動收折、收折開關、角度調整開關均無法使用）。僅適用 JB64／JB74，不可裝 JC74（NOMADE）' },
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
    note: '1350×600×160mm、13.5kg。黑色鋼製鐵線籃，木料是紐西蘭輻射松乙醯化處理的高耐久「Accoya」，做成包覆前緣的弧形擋板與兩側木塊，不是木地板。裝在車頂前段的橫桿上。日本仍在售 ¥56,000／¥61,600 稅込；＋TERZO 基座組 TB-HRKJB ¥74,000 稅抜（¥81,400 稅込），內含 JB64／JB74 專用 PIAA TERZO 腳座 4 個與主橫桿 2 根，另加約 5kg。' },
  { id: 'wood_full', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_theroots/', label: 'trip basket 復古車頂架（全長）', price: 19800, cur: 'TWD', brand: 'DAMD', part: 'TB-RR1',
    refs: ['https://www.damd.co.jp/products/suzuki/jimny_theroots/'],
    note: '1350×1000×160mm、16kg，與半長款同款式。日本 ¥59,000／¥64,900 稅込；＋TERZO 基座組 TB-RRKJB ¥77,000 稅抜（¥84,700 稅込），內含 JB64／JB74 專用 PIAA TERZO 腳座 4 個與主橫桿 2 根，另加約 5kg。台灣蝦皮「藤井74」NT$19,800' },
  { id: 'none', label: '不裝', price: 0 },
  // ---- 台灣有售
  { id: 'arb', photo: true, url: 'https://www.ruten.com.tw/item/show?22438729095708', photo: true, label: 'BASE Rack 車頂架 1545×1285', price: 45000, cur: 'TWD', brand: 'ARB', part: '1770020 + 17900020',
    note: '鋁擠型平台、燕尾槽側軌、4 支雨槽腳；平台單品 NT$15,000（MRK）；車主實車配置' },
  { id: 'yakima', photo: true, url: 'https://www.yakima.com.tw/products/locknload-platform', label: 'LockNLoad 平台車頂架 1520×1370', price: 23000, cur: 'TWD', brand: 'Yakima', part: '8005045',
    note: '橫向板條 T 槽、4 支雨槽腳（110／150／210mm）；Yakima 台灣售價' },
  { id: 'pioneer', photo: true, url: 'https://www.ruten.com.tw/item/show?22441909928235', label: 'Pioneer LT 平台車頂架', price: 58300, cur: 'TWD', brand: 'Rhino-Rack',
    part: 'ROLS1', note: '1453×1339、5 道縱向板條、Backbone 橫樑固定；黑四驅售價' },
  { id: 'ipf', photo: true, url: 'https://www.ipf.co.jp/ipfEc/products/detail/159', label: 'EXP Roof Rack type-A 車頂架', price: 32000, cur: 'TWD', brand: 'IPF', part: 'EXR-01',
    note: '1400×1250×38.8mm（不含腳座高度）、12.5kg，防鏽鋁合金。日本官網 ¥85,800 稅込只是貨架本體，腳座必須另購：ドリップモール用レッグ 低腳 EXR-01L2 ¥50,600、高腳 EXR-02L2 ¥30,800，裝車日本總價實為 ¥116,600〜¥136,400；IPF 官網也沒有公布耐荷重。以下 NT$32,000 為 MRK 台灣售價。' },
  { id: 'tw_generic', photo: true, url: 'https://tw.bid.yahoo.com/item/100868689053', label: '鋁合金平頂車頂架', price: 13000, cur: 'TWD', brand: '機油倉庫（台灣）',
    note: '1600×1260、6 支雨槽腳、前導流板；安裝 +NT$1,000' },
  // ---- 進口
  { id: 'platform', photo: true, url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-current-slii', photo: true, label: 'Slimline II 全長車頂架', price: 1579, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ003T',
    note: '1560×1345、6 支雨槽腳、前導流板，31kg' },
  { id: 'fr34', photo: true, url: 'https://www.dometic.com/en-au/product/suzuki-jimny-2018-curr-slii-3-4-roof-rack-kit', label: 'Slimline II 3/4 車頂架', price: 1451, cur: 'AUD', brand: 'Front Runner', part: 'KRSJ006T',
    note: '1156×1345、4 支腳' },
  { id: 'jaos', photo: true, url: 'https://www.jaos.co.jp/product/B411611NS/3848', label: 'Flat Rack type-B 車頂架', price: 140800, cur: 'JPY', brand: 'JAOS', part: 'B411611NS', uncertain: true,
    note: '1400×1250，鋁框厚 32mm、含四角護蓋 39mm，6 道 T 槽底桿、前導流板，16.4kg，¥140,800 稅込。**適用有疑義**：JAOS 自己的商品頁把適合車種寫成五門 JC74，車種檢索頁卻把它掛在 JB74 下，兩頁互相矛盾，下訂前務必跟 JAOS 確認。貨架自身荷重 50kg，但車頂動態載重仍是 30kg，扣掉 16.4kg 自重行駛中只剩約 13kg' },
  { id: 'apio', photo: true, url: 'https://apio.jp/parts/3630-50.html', label: 'Mighty Smart Rack 車頂架', price: 231000, cur: 'JPY', brand: 'APIO', part: '3630-50',
    note: '1420×1270、前軌前傾兼導流、船用鋁粉體配不鏽鋼零件。本體自重 21.3kg，APIO 官網明寫「積載可能重量：記載無し」不公布耐荷重；在 JB74 屋頂 30kg 動態載重上限下，扣掉自重後行駛中可用載重不到 9kg。' },
  { id: 'showa_foot', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000001017/I59728/', label: 'A-x Roof Rack 1512 車頂架', price: 92400, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20080', note: '收納 1500×1250×40mm，展開 1520×1270×60mm，可在屋頂上直接收折、高度可調約 3cm。含腳座重 27kg，官方耐荷重 50kg，但已吃掉 JB74 屋頂 30kg 動態載重的九成，行駛中幾乎無法再加載，適合靜止露營時使用。固定支架 E20034 另購。' },
  { id: 'basket', photo: true, url: 'https://www.showa-garage.shop/shopdetail/000000000111/I59728/', label: 'A-x Half Rack M 籃式車頂架', price: 68200, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E20008', note: '官方正式名稱是「ハーフサイズ M型」（半頂），不是 Full size——SHOWA GARAGE 另有一款「フルサイズ M型」（E20009）¥57,200 稅込是不同商品，容易搞混。1400×1250mm、折疊高度約 130mm，布料配框架的半硬式構造（不是剛性金屬貨架），可分成兩半、單邊約 7kg，總重 11.4kg，官方耐荷重 30kg，恰好等於 JB74 屋頂動態上限，扣掉自重後行駛中可載約 18kg。' },
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
    note: 'OUTCLASS 官網 [220サイズ] 版 ¥80,000 稅別／¥88,000 稅込，鋼製左右一組，可選粉體消光黑或 Raptor 黑塗裝，對應車檢；重量欄官網直接寫「未計測」，品番與管徑皆未公布，說明書不附。同廠另售電動款「オートサイドステップ [240サイズ]」¥119,000 稅別／¥130,900 稅込，購買時勿混淆兩者。' },
  { id: 'apio_guard', photo: true, url: 'https://apio.jp/parts/3102-69.html', label: 'H.D 硬鋁門檻護甲', price: 132000, cur: 'JPY', brand: 'APIO', part: '3102-69',
    note: 'APIO 官網確認商品名為「JB74 H.Dサイドシルガード」，適合車種明寫ジムニーシエラ JB74，¥132,000 稅込、品番 3102-69。本體為 3.0mm 厚 A5052 杜拉鋁單層板、取付支架為鋼製，左右一組約 8kg（含包裝約 10kg）；1,350×185×210mm 是外箱尺寸，官網未公布本體實際寸法。官網明寫「ナローフェンダー装着車両用」且「純正オーバーフェンダー併用不可」——原廠標準寬體輪拱的 JB74 無法直接裝這件，必須先換裝窄型葉子板。' },
  { id: 'taniguchi_bar', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: '長管側踏（高度可調）', price: 104500, cur: 'JPY', brand: 'TANIGUCHI',
    note: '報價原為單邊右用價，改標左右合計：右用 ¥53,900、左用 ¥50,600，皆稅込，左右都裝合計 ¥104,500 稅込（2025 年 10 月起表面改為シボ加工）。此為 JB74 シエラ 專用鋼管桿式側踏，管徑 42.7mm、壁厚 2.3mm、全長 1200mm、黑色粉體烤漆，踏面即為鋼管本體、並無另外的網狀踏板，高度可兩段調整（側裙下緣下方約 9cm／約 6cm），不超出原廠輪拱、車檢合格。' },
  { id: 'taniguchi_short', photo: true, url: 'https://www.ors-taniguchi.co.jp/parts-cat/jb_exterior_side/', label: '兩段可調短側踏', price: 77000, cur: 'JPY', brand: 'TANIGUCHI',
    note: '報價原為單邊右用價，改標左右合計：鋼製右 ¥41,250／左 ¥35,750，左右合計 ¥77,000 稅込；不鏽鋼版右 ¥59,400／左 ¥56,100，左右合計 ¥115,500 稅込（不鏽鋼版 2026.5.1 調價）。JB74 シエラ 專用、免鑽孔螺栓固定，踏面高度可兩段調整（側裙下緣下方約 9cm／約 6cm），不超出原廠輪拱、車檢合格。550×145 網狀踏板這組尺寸官網只標在 JB64 鋼製版頁面，JB74 頁面未公布踏板尺寸與管徑，全車系不公開品番。' },
  { id: 'showa', photo: true, url: 'https://store.shopping.yahoo.co.jp/showa-garage/e00173.html', label: '長版側踏＋側裙飾板套組（JB74）', price: 127050, cur: 'JPY', brand: 'SHOWA GARAGE',
    part: 'E00173 + E00207', note: '官網查無「Type2」這個型號名，E00173 正式商品名是「サイドステップ ロングタイプ 左右セット」，¥69,300 稅込、左右一組，鋼製皺紋黑烤漆，JB64／JB74 一至五型皆適用。JB74 因原廠側裙擋板無法直接拆除，官網明寫必須另購 E00207「AESサイドガーニッシュ JB74用」（左右一組 ¥57,750 稅込，JB74 專用，不可裝 JC74）取代原廠側裙，兩者合計 JB74 全套實際要價 ¥127,050 稅込。三型以後車款因地板隔音材干涉支架需修剪。' },
  { id: 'wildgoose_fold', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/exterior_64/jm-2262l-jm-2262r.html', label: '折疊式側踏 JM-2262', price: 35200, cur: 'JPY', brand: 'RV4 Wild Goose',
    note: 'RV4 Wild Goose 官網確認單邊 ¥35,200 稅込（¥32,000 稅抜），左右分別為品番 JM-2262L／JM-2262R，左右都裝合計 ¥70,400 稅込；JB74W 專用，JB64 是另一品番 JM-2162，不通用。踏板鋼板 4.2mm、支架 6.0mm，單邊 5kg，可手動上翻收折；官方註明三型以後車款依安裝狀況可能產生接觸異音，需對策。' },
  { id: 'wildgoose_guard', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/protection_64/jm-2409.html', label: '門檻護甲側踏 JM-2409', price: 110000, cur: 'JPY',
    brand: 'RV4 Wild Goose', note: 'RV4 Wild Goose 官網確認 ¥110,000 稅込（¥100,000 稅抜）為左右一組（一台份），不是單邊。材質為鍍鋅鋼板（ボンデ鋼板，鍍鋅＋鉻酸鹽雙層被膜）2.3mm 厚、聚氨酯烤漆黑，長 1292mm、外凸 55mm，JB74 專用品番 JM-2409；JB64 對應品是另一件「サイドシルガード3.2」JM-2408（¥44,000 稅込，非同款護甲踏板）。14.5kg 官網未註明是單邊還是一組。' },
  { id: 'customwagon', photo: true, url: 'https://www.custom-wagon.com/c/557/jim661', label: '出幅可調側踏', price: 57200, cur: 'JPY', brand: 'Custom Wagon',
    note: 'Custom Wagon 官網原文為「調整幅は約50センチあります」，即出幅可調約 50cm，不是目錄原本寫的 50mm——官網白紙黑字，以此為準更正十倍之差。¥57,200 稅込（店售價，非廠商建議售價），鋼管加緞面黑塗裝，JB74W 專用（AT／MT 共用），與 JB64 版支架不同不可混用，2022 年 7 月以後（三型）車輛需切除新增隔音材才能安裝。官網未公布品番、管徑、尺寸與重量。' },
  { id: 'spieler', photo: true, url: 'https://spieler.jp/products/jb64jb74sidestep7575', label: '7575 方管側踏', price: 88000, cur: 'JPY', brand: 'SPIELER',
    note: 'SPIELER 官網查無「75×75 方管」這個規格，商品頁只寫「角パイプ」＋「アルミ天板（バーリング加工滑り止め）」，75×75 只出現在網址代碼 jb64jb74sidestep7575，未經官方文字證實，應標為未確認。¥88,000 稅込（¥80,000 稅抜），JB64 與 JB74 共用本體、支架不同，利用既有車體固定孔免鑽孔，出幅可調、對應車檢。目前 JB64／JB74 兩款官網皆顯示售罄。',
    uncertain: true },
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
  snorkel:      { label: '呼吸管', brands: 'Safari / Ironman 4x4 / ARB / Rival',
                  note: '日系六大改裝廠（APIO、TANIGUCHI、JAOS、RV4 Wild Goose、MONSTER SPORT、SHOWA GARAGE）目前都沒有 JB74 用呼吸管，原本列的 APIO 是誤植；日本市場的涉水對策改走差速器／變速箱通氣管延長與碳罐移位（RV4 Wild Goose 前後差速器呼吸管組 JM-5016 ¥9,350 稅込、A/T 呼吸管 JM-5019 ¥3,300 稅込、碳罐移位套件 JM-5221 ¥19,800 稅込）。呼吸管本身仍以澳洲／南非等海外品牌為主，注意左右側別，部分需切葉子板', uncertain: true },
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
  { id: 'ipf', url: 'https://www.ipf.co.jp/ipfEc/products/detail/122', label: '600 S-Series 40 吋燈條', brand: 'IPF',
    part: '642JM2', price: 118800, cur: 'JPY', note: 'IPF 642JM2 是含燈條的整組套件：642SD 40 吋雙排燈條本體＋繼電器線組＋開關＋A 柱專用托架，適用 JB64／JB74（2018.07 以後，兩車共用同一料號）。官網 ¥118,800 稅込（¥108,000 稅抜）是整組總價；642SD 單體另售 ¥95,480 稅込（¥86,800 稅抜），若把兩者價格相加會重複計算燈條本體，本欄只計整組總價一次。642SD 規格：20,000 流明、273,000cd、210W、6000K、IP68、重 2,900g，白光。' },
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
  { id: 'round', label: '車頂圓燈（一對）', brand: 'IPF', price: 16940, uncertain: true, note: '目錄原寫「一般 7 吋圓燈一對」查無對應的日本一手商品：IPF 唯一成對出貨的圓燈是 968 系列，φ166×D75mm（約 6.5 吋）鹵素燈（H3 12V 55W），不是 7 吋也不是 LED。整組含燈體×2、燈罩×2、繼電器、線組、開關，S-9682（透明）¥16,940 稅込、S-9681（金）¥18,150 稅込。若要 LED，IPF 900XLS φ200mm（約 7.9 吋）、2,200 流明、30W，¥29,700 稅込，但官網註明單顆出貨，一對要買兩顆。',
    part: 'S-9682（透明燈罩）／S-9681（金色燈罩）',
    cur: 'JPY',
    url: 'https://www.ipf.co.jp/ipfEc/products/detail/116' },
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
    price: 74800, cur: 'JPY', note: 'φ101 正圓管口（全表最大單出）＋BATTLEZ 壓字，需局部修保桿。適用 JB74 2018.07〜2025.11，2025.11 後的 5 型不可裝。台灣 MyRack 約 NT$22,000，是台灣最買得到的真系統' },
  { id: 'kakimoto_kr_lr', url: 'https://www.kakimotoracing.co.jp/products/list_carmodel.cgi?rid=266&serieskey=exhaust_class_kr', label: 'Class KR 左右出', brand: '柿本改', part: 'S71355S',
    price: 170500, cur: 'JPY', note: 'φ96 雙出、左右保桿下角各一，是車尾正面視角最搶眼的一套；沒有胖消音筒，取而代之是扁平共鳴箱' },
  { id: 'apio_yoshimura_ti', url: 'https://apio.jp/parts/2004-7.html', label: '突擊 R-77J 鈦砲管', brand: 'APIO × YOSHIMURA', part: '2004-7T',
    price: 363000, cur: 'JPY', note: '重點是消音筒本身：手工燒藍鈦合金消音筒，辨識度全表最高。APIO 官網規格為主管約 φ50.8mm（部分 φ42.7mm）、出口外徑約 φ68mm、重約 4.2kg；目錄原寫的「550×115mm」尺寸官網查無依據，已拿掉。適用 JB74 1〜4 型純正保桿車（MT／AT），5 型不適用。同規格鈦灰色 2004-7TX 便宜約 ¥14,300（¥348,700）' },
  { id: 'taniguchi_compe_r', url: 'https://www.ors-taniguchi.co.jp/', label: 'Compe Muffler R', brand: 'TANIGUCHI',
    price: 102300, cur: 'JPY', note: 'TANIGUCHI 官網價格公告確認稅込 ¥102,300（2026/2/2 起出貨分適用），但商品頁本身是 JS 動態載入、抓不到規格內文——「管口從右後角側向穿出、離地約 560mm」與「原廠保桿要開孔」這兩點在官網一手頁面上都查不到依據，暫標未證實，上架前建議先向店家索取規格表。',
    uncertain: true },
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
    note: '側出雙管 φ75×2，後保桿完全不動；官網只寫「サイド出しデュアルマフラー」，沒有明載左右哪一側，也沒有明載尾管是鈦燒色，不應寫死。本體 S304 不鏽鋼、9.0kg，裝著時地上高 210mm，近接排氣音 88dB（原廠 81dB，全表最大聲）。JB74W 品番 32018-AS006，JB64W 是不同品番 31021-AS004，訂購時務必核對車型以免買錯。',
    uncertain: true },
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
  { id: 'suzuki_cover', key: 'spareCover', url: 'https://www.suzuki.co.jp/accessory_car/jimny_sierra-accessory.html', label: '原廠硬式備胎蓋（Jimny SIERRA 字樣）', price: 52800, cur: 'JPY', brand: 'SUZUKI', part: null,
    note: '正面／側面樹脂硬質面板、背面易拆合成皮，鈴木原廠建議售價 ¥52,800（稅込），安裝參考工時 0.2h，須先拆原廠備胎半罩。另有犀牛髮絲紋款 ¥33,880（稅込），本目錄未建模。鈴木官方用品頁不公布品番；原目錄的 9923B-77R21-003 在零件目錄查無此號，且 77R 是 JB64 車系碼（JB74 是 78R），已移除' },
  { id: 'trasharoo', key: 'spareBag', url: 'https://agileoffroad.com/products/trasharoo-spare-tire-trash-bag', label: '備胎書包（Trasharoo）', price: null, cur: 'USD', brand: 'Trasharoo', uncertain: true,
    note: '配置器「備胎書包」' },
  { id: 'maxx', photo: true, url: null, key: 'wheel', label: '旋壓 10 輻輪框 16×6.0J ±0', price: 4100, cur: 'TWD', brand: 'MAXX（台灣）', note: '消光黑，配 TOYO Open Country M/T 225/75R16（車主實車配置）' },
];


/** Which warnings apply to a configuration. Pure function so the UI and any
 *  future export share one source of truth. */
export function validate(cfg, { tyre, lift, bodyLift, wheel }) {
  const out = [];
  const totalLift = (lift?.lift ?? 0) + (bodyLift?.body ?? 0);
  // Lowering is not "insufficient lifting". A road tyre that needs no lift is
  // fine on a lowered car, so the comparison floors at stock height; a tyre
  // that genuinely needs clearance still fails, and gets told the real gap.
  if (tyre.needLift > Math.max(totalLift, 0)) {
    out.push({ level: 'error',
      msg: `${tyre.label} 需要約 ${tyre.needLift}mm 舉升，目前${totalLift < 0 ? `是降低 ${-totalLift}mm` : `只有 ${totalLift}mm`}` });
  }
  if (totalLift < 0 && tyre.dia > 700) {
    out.push({ level: 'warn',
      msg: `降低 ${-totalLift}mm 配 ${tyre.label}（外徑 ${tyre.dia}mm）：車身壓低又用大外徑胎，滿載或過坑時輪拱內襯容易磨到` });
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
  if (cfg.face && cfg.face !== 'none' && (cfg.frontBumper !== 'stock' || cfg.grille !== 'stock' || cfg.grilleLight !== 'none')) {
    out.push({ level: 'error', msg: '換臉套件已經包含水箱罩、頭燈與前保桿，前保桿、水箱護罩與車頭燈條請維持原廠' });
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

/**
 * Outer roll cages. The one thing in here that redraws the car's outline
 * instead of hanging off it -- the roof stops being a plain box and becomes a
 * box inside a frame -- which is why it earns a family of its own.
 */
export const CAGES = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'wildgoose', photo: true, url: 'https://www.rv4wildgoose.com/parts/jimny-64-74/protection_64/jm-2424.html',
    label: '外掛式防滾籠 JM-2424', price: 203500, cur: 'JPY', brand: 'RV4 Wild Goose', part: 'JM-2424',
    note: '主管 38.1×2.3t、中央橫樑 25.4×2.3t，25kg。前端鎖引擎蓋固定點——所以側 cowl 與葉子板都要切——後端鎖車頂雨槽 8 點。廠方寫明「車検対応品として、構造変更無しで使用出来ます」。注意：雙色車與有雨槽飾條的車不適用' },
];

/**
 * Wide-body over-fenders: kits that go WIDER than the Sierra's own resin
 * arches and are laid over them. `widen` is the added width per side in mm --
 * the maker's figure where one is published, otherwise the modelled
 * estimate, and the entry is then marked uncertain. The kit list
 * (docs/jb74-widebody.json) has the western brands checked too: every one
 * found fits only the old narrow JB23/JB43.
 */
export const FENDERS = [
  { id: 'none', label: '原廠爆龜', price: 0 },
  { id: 'wald_bison', url: 'https://wald.co.jp/carrange/jimnysierra_bb/', label: 'SPORTS LINE BLACK BISON 爆龜', widen: 30,
    price: 234300, cur: 'JPY', brand: 'WALD',
    note: '官網「片側約30mmワイド」。ABS 10 件組 ¥234,300、FRP 8 件組 ¥222,200，皆稅込、素地未塗裝。蓋在原廠爆龜外側；FRP 版官網明寫裝 Jimny 需要加工，ABS 版沒寫。兩版都要配 WALD 自家的前後保桿下擾流才裝得上。方正厚實的 G-Class 式樣' },
  { id: 'kuhl_blocker', url: 'https://kuhl-japan.com/ec/aeroparts/20425', label: 'BLOCKER SIERRA 寬體葉子板', widen: 30,
    price: 220000, cur: 'JPY', brand: 'KUHL RACING', uncertain: true,
    note: '¥220,000 稅込，FRP 素地，另有單件烤漆加價。蓋在原廠爆龜外側。加寬幾 mm 官網沒有公布，模型先照 WALD 的 30mm 畫；是否要切鈑金官網也沒寫' },
  { id: 'lb_gmini', url: 'https://libertywalk.co.jp/bodykit/suzuki-g-mini-type-2/', label: 'G mini 寬體葉子板', widen: 35,
    price: 154000, cur: 'JPY', brand: 'LIBERTY WALK', uncertain: true,
    note: '¥154,000 稅込（官網註明是概算價，正式以業務報價為準），FRP 素地。G mini 前保桿＋水箱罩＋寬體三件式的其中一件，JB64／JB74 車身件通用。加寬量官網未公布，模型照 35mm 估' },
  { id: 'aero_over', url: 'https://k-factory.ne.jp/art/g62-jimny3door/', label: 'G62S プラスワイドフェンダー', widen: 35,
    price: null, cur: 'JPY', brand: 'AERO OVER（K-FACTORY）', uncertain: true,
    note: 'JB74 專用的加寬版，官網寫每邊 +35mm、全車寬到 172cm，日本要辦構造變更。加寬版沒有單獨標價；標準寬度的 G62／G62S 爆龜 4 件組是 ¥120,000 稅抜' },
  { id: 'damd_delta', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta', label: 'little Δ 鼓包爆龜 4 件組', widen: 40,
    price: 140800, cur: 'JPY', brand: 'DAMD', uncertain: true,
    note: '¥140,800 稅込（¥128,000 稅抜），ABS 素地，前後左右 4 片蓋在原廠爆龜外。圓潤的拉力式鼓包，後葉子板末端的導風孔是假孔。加寬量官網未公布，模型照示範車照片估 40mm；是否要切鈑金官網沒寫' },
];

/**
 * Face kits: the whole front replaced -- grille, headlamps AND bumper -- so
 * choosing one hides all three stock parts and overrides the bumper and
 * grille pickers. The research, with the geometry read off the makers'
 * photographs, is docs/jb74-face-swap.json.
 */
export const FACES = [
  { id: 'none', label: '原廠臉', price: 0 },
  { id: 'bron55', url: 'https://shop.jetgogo.jp/items/69169821', refs: ['https://www.garage-ill.co.jp/bron55/'],
    label: 'BRON55 美式方頭換臉（雙色烤漆完成品）', price: 389400, cur: 'JPY', brand: 'GARAGE ILL',
    note: '水箱罩＋圓形 LED 頭燈組＋前保桿一整組，引擎蓋與葉子板不動。這裡畫的是官方示範車的雙色烤漆完成品 ¥389,400 稅込：水箱罩框與保桿上橫樑車身色、中央模組與下緣銀色。素地未塗裝 ¥297,000（原廠 LED 頭燈車用）／¥264,000（鹵素車用），稅込。適用 JB74W 1〜4 型；2025/11 以後的 5 型是另一個商品（附前方感知器移位套件，LED 車用 ¥330,000）；JB64 版同價但不通用。官方網店註明頭燈自 2024/8/1 起不對應日本車檢的頭燈檢查。官網未公布料號；尺寸是照官方照片估的（±10%）' },
  { id: 'damd_delta', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta/', label: 'little Δ 四圓燈臉（水箱罩＋前保桿）', price: 266200, cur: 'JPY', brand: 'DAMD',
    note: '四顆圓燈排成一列的水箱罩 ¥173,800（含圓形 LED 頭燈、圓形小燈、方形方向燈，中央 Lancia 式鍍鉻 Y 字框）加 little 5.／Δ 共用前保桿 ¥92,400（兩顆黃色 Koito 方形霧燈），素地合計 ¥266,200。外側一對約 145mm、內側一對約 105mm，官網沒寫哪一對是頭燈，也提醒要自行確認光度過不過車檢。整套 little Δ（再加爆龜、側裙、後保桿、尾翼）是 ¥539,000。尺寸是照官方照片估的' },
];

/** Roof spoilers, on the roof's rear edge above the tailgate. */
export const SPOILERS = [
  { id: 'none', label: '不裝', price: 0 },
  { id: 'damd_wing', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta/', label: 'little 5.／Δ FRP 尾翼', price: 63800, cur: 'JPY', brand: 'DAMD',
    note: '¥63,800 稅込（¥58,000 稅抜），FRP，角度可調，黑色鋼支架夾在車頂雨槽上不用鑽孔。翼展約 1230、弦長約 250mm，照官方照片估' },
  { id: 'rowen', url: 'https://www.rowen.co.jp/bodykit/details.php?id=115', label: 'Roof Spoiler Electronics TYPE3 鴨尾', price: 117700, cur: 'JPY', brand: 'ROWEN', part: '1K002R30',
    note: '¥117,700 稅込，FRP 素地（單色烤漆 +¥46,200、雙色 +¥66,000）。車頂後緣的短鴨尾，不是架高的尾翼，後斜面內建連動 LED 第三煞車燈。適用 JB74W 1〜4 型；官網寫 LED 過不了日本車檢、要拆線才能驗，安裝需鑽孔。形狀是照官方照片估的，大部分照片是舊款 1K002R20' },
];

/**
 * Side stripes. What actually makes one built JB74 look unlike another is the
 * stripe down its flank, not the bumper -- which is why five styles built out
 * of bumpers and wheels all read the same from ten metres away.
 *
 * These are cut-vinyl sets, not paint, so in Taiwan they need no 變更登記 as
 * long as the car's main colour is unchanged (道路交通安全規則第 23 條 lists
 * 顏色 among the registrable items, but no rule anywhere sets an area
 * threshold -- the widely repeated "over 1/3" comes from a 2016 television
 * interview with a wrap shop, not from any regulation).
 */
export const STRIPES = [
  { id: 'none', label: '不貼', price: 0 },
  { id: 'retro3', photo: true, label: '復古三色腰線', price: 755, cur: 'TWD', brand: '露天賣家（裁切貼）',
    note: '深棕細線＋寬鏽橘＋米色下緣，三條相連，沿門檻上方的折線跑滿側面。日本沙色 JB74 最常見的那一組。台灣露天 NT$350–755 依長度與材質；自己貼得起來，工錢另計' },
  { id: 'stencil', photo: true, label: '軍卡白色模板字', price: 629, cur: 'TWD', brand: '露天賣家（裁切貼）',
    note: '白色五角星貼在車門正中，後四分之一板一組模板體序號、前葉子板一個 4x4。用白字不用迷彩：迷彩貼在綠車上遠看會糊成一片，白字是全車對比最強的東西，一眼就認得出來。星與字都是通用樣式，不是任何國家軍方的制式徽記。台灣露天 NT$462–629' },
  { id: 'toolgear', photo: true, label: '原廠工具箱風低位黑帶', price: null, cur: 'JPY', brand: 'SUZUKI', uncertain: true,
    note: '一條約 210mm 的深黑帶壓在車門下折線與門檻之間，下緣一道銀白細邊，車門上半刻意整片留白。原廠示範色是白車，對比最強。官網未單獨標價' },
  { id: 'jaos', photo: true, url: 'https://www.jaos.co.jp/', label: 'JAOS 低位雙線', price: null, cur: 'JPY', brand: 'JAOS', uncertain: true,
    note: '2200×75mm 長條供應、由施工者照車身折線自行修邊。主帶 78mm＋6mm 露車身色＋14mm 細線，位置低到只比門檻飾板高一點。銀或黑兩色，JAOS 橢圓標以鏤空透明 PVC 挖在主帶上' },
  { id: 'damd_center', url: 'https://www.damd.co.jp/products/suzuki/jimny_sierra_littledelta/', label: '車頂中線（DAMD 示範車式樣）', price: null, cur: 'TWD', brand: '貼膜行裁切', uncertain: true,
    note: '米白 25＋深綠 35＋米白 25mm 緊貼成一條 85mm 的帶，從引擎蓋沿中線跑過車頂，避開擋風玻璃與尾門。DAMD 寫明這只貼在示範車上、套件不含，市面也沒有 Jimny 專用的縱向中線商品，要請貼膜行照這個式樣裁' },
  { id: 'toy4', photo: true, label: '四色橘帶（Toy Factory 式樣）', price: null, cur: 'JPY', brand: 'Toy Factory', uncertain: true,
    note: '淺橘細線＋鮭橘漸層帶＋實色橘＋寬近黑，四條橫跨門把，整組往車尾抬 2.3 度。原版前端四條會一起轉 90 度繞過前葉子板立面，轉角是同心圓角；這裡只畫車側那一段' },
];

/**
 * Styles: a starting point, not a package.
 *
 * 230 parts across eleven families is a wall to anyone opening this for the
 * first time, so the configurator asks for a STYLE before it asks for
 * anything else. Picking one applies the whole set below at once -- the same
 * mechanism the demo car already used, just visible and with five of them --
 * and every single item stays changeable afterwards. Nothing here is a
 * package you can buy in one box; the Japanese makers' complete kits are
 * real products and live in the parts lists instead.
 *
 * `set` holds only what differs from stock, so a style reads as a list of
 * decisions rather than a dump of state.
 */
export const STYLES = [
  // Each style is pushed apart on the axes that change the SILHOUETTE -- ride
  // height, what is on the roof, how wide the arches are, how big the wheels
  // are -- and only then on the stripe. Five cars that differ by bumper alone
  // all read the same from ten metres away.
  { id: 'jp_retro', label: '日系復古', sw: ['#d8c9a4', '#b4703a', '#1d2224'],
    desc: '米色車身配深棕、鏽橘、米白的三色腰線，黑鋼輪包白字全地形胎，KLC 不鏽鋼雙管前後保桿。車高只到 1.8 米出頭，是街上開的樣子。',
    set: { color: 'ZVG', lift: 'td60', wheel: 'mrk_retro', tyre: 't215r16', tread: 'toyo_at3', owl: true,
      rimColor: 0x1b1d1f, stripe: 'retro3', grille: 'hbar_suzuki', frontBumper: 'tube_heritage',
      rearBumper: 'klc_heritage_rear', mirrors: 'damd', sideStep: 'jst', ladder: 'jst',
      exhaust: 'hks_legal', sideSkirt: true } },

  { id: 'au_offroad', label: '澳洲越野', sw: ['#3f4a3c', '#1d2224', '#8a6b45'],
    desc: '最高最寬的一台：2 吋懸吊＋2 吋車身舉升、31 吋胎配爆龜、絞盤前桿與呼吸管，車頂載架上一排探照燈與 270 度車邊帳。',
    set: { color: 'ZVL', lift: 'combo100', wheel: 'wildboar', tyre: 't31', tread: 'bfg_km3',
      rimColor: 0x2a2d30, frontBumper: 'wmd_winch', snorkel: 'safari', roofRack: 'arb',
      awning: 'arb_touring_25', awningSide: 'left', sideStep: 'ironman', ladder: 'tube',
      lightBar: 'ipf', roofLights: 'kc_pro6', windowGuards: true, guardCan: 'right',
      shovel: true, extinguisher: 'ladder', flares: true } },

  { id: 'city', label: '都會輕改', sw: ['#d8d8d4', '#2e4a63', '#1d2224'],
    desc: '最乾淨的一台：只動輪框、胎和 20mm 舉升，加一道側裙與一條低腰銀線。車頂空的，機械車位進得去，驗車不用解釋。',
    set: { color: 'ZVR', lift: 'apio20', wheel: 'dean_cross', tyre: 't215r16', tread: 'toyo_at3',
      rimColor: 0x1d2224, stripe: 'jaos', sideSkirt: true } },

  { id: 'military', label: '軍風', sw: ['#4a513a', '#e7e4da', '#2a2c26'],
    desc: '原廠軍綠配白色軍卡模板字——車門一顆大白星、後板一組序號。方管前後桿、鋼輪、平台車頂架，側窗鐵窗上掛油桶、斧頭與鏟子。',
    set: { color: 'ZZC', lift: 'td40', wheel: 'wildboar_sr', tyre: 't225r16', tread: 'bfg_km3',
      rimColor: 0x3c4138, stripe: 'stencil', frontBumper: 'taniguchi_square',
      rearBumper: 'taniguchi_rear_pipe', roofRack: 'platform', windowGuards: true,
      guardCan: 'right', guardAxe: 'right', guardBoard: 'left', shovel: true,
      extinguisher: 'left', spareBag: true } },

  { id: 'exo_cage', label: '外掛籠硬派', sw: ['#d8c9a4', '#1d2224', '#6b6f62'],
    desc: '車頂被一圈黑鋼管整個包住，A 柱前面還跨一道橫樑過擋風玻璃。跟澳洲越野一樣兇，但那台車頂載滿東西、這台只有籠子——遠看剪影完全不同。',
    set: { color: 'ZVG', lift: 'sg50bl', wheel: 'yaochi_h598', tyre: 't31', tread: 'cp_stt',
      rimColor: 0x24262a, cage: 'wildgoose', frontBumper: 'wmd_winch',
      rearBumper: 'taniguchi_rear_pipe', sideStep: 'taniguchi_bar', windowGuards: true,
      guardCan: 'right', shovel: true, flares: true } },

  { id: 'street_low', label: '都會寬體低趴', sw: ['#1d2224', '#b8bcc0', '#2e3236'],
    desc: '唯一往下走的一台：降低彈簧配 RAYS 18 吋鍛造框與 55 系列公路胎，WALD 爆龜每邊再寬 30mm，輪拱被輪框而不是被胎填滿，車頂完全空的。亮黑車身才撐得起這個對比。',
    set: { color: 'ZJ3', lift: 'klc_turtles', wheel: 'street18', tyre: 't225r55', tread: 'toyo_ht2', fender: 'wald_bison',
      rimColor: 0x17191c, stripe: 'jaos', grille: 'outclass_g', frontBumper: 'jaos_cowl',
      rearBumper: 'jaos_rear_cowl', exhaust: 'kakimoto_kr_lr', sideSkirt: true } },

  { id: 'camp', label: '露營', sw: ['#2f3a33', '#c0a878', '#1d2224'],
    desc: '雙色車頂配整套上下車的東西：車頂架、車邊帳、側踏與尾梯，四條橘色拉花橫過門把。胎走安靜的全地形，長途不吵。',
    set: { color: 'ZVG', twoTone: true, lift: 'td60', wheel: 'wildboar_d',
      tyre: 't225r16', tread: 'toyo_at3', rimColor: 0x8a8d90, stripe: 'toy4',
      roofRack: 'pioneer', awning: 'yakima_270s', awningSide: 'left', sideStep: 'jst',
      ladder: 'jst', spareCover: true, extinguisher: 'ladder', flares: true } },
];

