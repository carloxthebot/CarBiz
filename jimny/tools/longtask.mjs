// Every main-thread block (>50 ms) from navigation to the boot screen going
// away. Assembling the car is synchronous work, so this is what decides
// whether the wait screen looks alive or frozen.
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/longtask.mjs [url]
import { chromium } from 'playwright-core';
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
await page.addInitScript(() => {
  window.__lt = [];
  new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__lt.push([Math.round(e.startTime), Math.round(e.duration)]); })
    .observe({ entryTypes: ['longtask'] });
});
await page.goto(process.argv[2] || 'http://127.0.0.1:8899/app.html');
await page.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none', null, { timeout: 180000 });
const r = await page.evaluate(() => ({ lt: window.__lt, now: Math.round(performance.now()) }));
let tot = 0;
for (const [s, d] of r.lt) { tot += d; console.log(`t=${String(s).padStart(6)}ms  block ${String(d).padStart(5)}ms`); }
console.log(`\nboot done at ${r.now}ms; ${r.lt.length} long tasks, ${tot}ms blocked`);
await browser.close();
