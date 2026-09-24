// Prices in this catalogue come from whatever currency the maker quotes, which
// makes a Japanese spring impossible to compare with an Australian one at a
// glance. Everything the pages show is therefore converted to NT$ first, with
// the original kept as a subscript so the source is still traceable.
//
// These are deliberately rough shop-counter rates, not a live feed: a rate that
// silently drifts is worse than one that is openly approximate. Revisit when
// any of them moves more than about 10%.
export const FX_DATE = '2026-09';
export const RATES = { TWD: 1, JPY: 0.21, AUD: 21, GBP: 41, USD: 32, EUR: 35, NZD: 19 };
export const SYMBOL = { TWD: 'NT$', JPY: '¥', AUD: 'A$', GBP: '£', USD: 'US$', EUR: '€', NZD: 'NZ$' };

// Japanese list prices include tax; the street price for most bolt-on parts is
// well under list, so the converted figure is an upper bound, not a quote.
export const FX_NOTE = `匯率概估（${FX_DATE}）：¥1≈NT$0.21、A$1≈NT$21、£1≈NT$41。日本標價為含稅定價，實際成交多半更低。`;

/** NT$ value of a price, rounded to the nearest hundred. Null when unpriced. */
export function toTWD(price, cur = 'TWD') {
  if (price == null) return null;
  const r = RATES[cur];
  if (r == null) return null;
  return Math.round(price * r / 100) * 100;
}

/** "NT$8,100" — the headline figure. */
export const twd = (n) => 'NT$' + n.toLocaleString('en-US');

/** "¥38,500" — the original, for the small print. */
export const native = (price, cur) =>
  price == null ? '' : (SYMBOL[cur] ?? '') + price.toLocaleString('en-US');

/**
 * One label for a catalogue row: the price the shop actually quotes first,
 * the rough NT$ equivalent second ("¥97,900", "~NT$20,600") -- a Japanese
 * part is bought in yen, and a converted headline hid that.
 * `stock` items priced 0 read as 原廠, unpriced ones as 洽詢.
 */
export function priceLabel(item) {
  if (item.price === 0) return { main: '原廠', sub: '' };
  const n = toTWD(item.price, item.cur);
  if (n == null) return { main: '洽詢', sub: '' };
  return item.cur === 'TWD' || !item.cur ? { main: twd(n), sub: '' } : { main: native(item.price, item.cur), sub: '~' + twd(n) };
}
