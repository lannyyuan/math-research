// Automatic checks + screenshots for the picture book:  node webapp/qa.mjs [--shots=out/book_qa] [--all]
//   1. in a real browser, turn through every page, join the text that is actually displayed and compare it with the story word for word
//   2. check: console errors, horizontal overflow, which pages need scrolling in the text panel, pictures loaded
//   3. screenshots on desktop / tablet portrait / phone portrait / phone landscape
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const pwPath = ['/opt/node-tools/node_modules/playwright', '/opt/node22/node-tools/node_modules/playwright', 'playwright'].find((p) => { try { require.resolve(p); return true; } catch { return false; } });
const {chromium} = require(pwPath);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.resolve(root, (process.argv.find((a) => a.startsWith('--shots=')) ?? '--shots=out/book_qa').split('=')[1]);
fs.mkdirSync(outDir, {recursive: true});
const file = 'file://' + path.join(root, 'dist/lighthouse-light-book.html');
const norm = (t) => t.replace(/[\s“”"‘’']/g, '').toLowerCase();

const browser = await chromium.launch({executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox']});
const problems = [];
const errors = [];
const mk = async (w, h, name, opts = {}) => {
  const ctx = await browser.newContext({viewport: {width: w, height: h}, deviceScaleFactor: opts.dpr ?? 1, hasTouch: !!opts.touch, colorScheme: opts.scheme ?? 'dark', reducedMotion: 'reduce'});
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`[${name}] ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`[${name}] console: ${m.text()}`); });
  await page.goto(file);
  await page.waitForFunction(() => window.__book);
  await page.evaluate(() => document.fonts.ready);
  return page;
};

// —— 1. 全文逐页核对（桌面）
const pg = await mk(1440, 900, 'desktop');
const N = await pg.evaluate(() => window.__book.N);
let got = '';
const scrolly = [];
for (let i = 1; i <= N; i++) {
  await pg.evaluate((i) => window.__book.go(i), i);
  const info = await pg.evaluate(() => {
    const t = document.querySelector('.text'), inner = t.querySelector('.inner');
    return {text: inner.innerText, sh: t.scrollHeight, ch: t.clientHeight, ov: document.documentElement.scrollWidth > innerWidth};
  });
  const imgOk = await pg.evaluate(async () => { await Promise.all([...document.images].filter((im) => im.getAttribute('src')).map((im) => im.decode().catch(() => null))); return [...document.images].filter((im) => im.getAttribute('src')).every((im) => im.naturalWidth > 0); });
  got += info.text;
  if (info.sh > info.ch + 2) scrolly.push(`${i}(${info.sh - info.ch}px)`);
  if (info.ov) problems.push(`page ${i}: horizontal overflow`);
  if (!imgOk) problems.push(`page ${i}: a picture did not load`);
}
// chapter titles are shown on the page ("Chapter 3" + "The City"); in the story they are heading lines, so add them to the expected text
const expect = (() => {
  let s = '';
  const lines = fs.readFileSync(path.join(root, 'story/source.md'), 'utf8').split('\n');
  for (const l of lines) {
    if (/^---\s*$/.test(l)) break;
    if (l.startsWith('## ')) { const m = /^## (Chapter \d+|Epilogue):\s*(.+)$/.exec(l); s += m[1] + m[2]; }
    else if (l.trim() && !l.startsWith('#')) s += l;
  }
  return norm(s);
})();
const g = norm(got);
if (g !== expect) {
  let k = 0; while (k < Math.min(g.length, expect.length) && g[k] === expect[k]) k++;
  problems.push(`page text differs from the story at character ${k}: page="${g.slice(k - 8, k + 16)}" story="${expect.slice(k - 8, k + 16)}"`);
}
console.log(`page-by-page text check: ${g.length} characters on the pages / ${expect.length} in the story (with chapter titles, without quotes and spaces) ${g === expect ? '✓ identical' : '✗ DIFFERENT'}`);
console.log(`pages that need scrolling in the text panel (desktop 1440×900): ${scrolly.length ? scrolly.join(' ') : 'none'}`);

const data = await pg.evaluate(() => window.__book.data);
const pageOfCue = (no) => data.pages.find((p) => p.cues.includes(no)).i;
const firstOf = (nm) => data.pages.find((p) => data.sections[p.sec].no === nm).i;
const SAMPLE = [1, firstOf('Chapter 3'), firstOf('Chapter 9'), pageOfCue(12), pageOfCue(24), firstOf('Chapter 11'), firstOf('Chapter 13'), firstOf('Chapter 14'), pageOfCue(36), pageOfCue(43), firstOf('Chapter 18'), firstOf('Epilogue'), pageOfCue(46), N];
// —— 1b. 逐页缩略截图（人工看版式用）
if (process.argv.includes('--all')) {
  const small = await mk(1280, 720, 'all');
  fs.mkdirSync(path.join(outDir, 'all'), {recursive: true});
  for (let i = 0; i <= N + 1; i++) {
    await small.evaluate((i) => window.__book.go(i), i);
    await small.waitForTimeout(60);
    await small.screenshot({path: path.join(outDir, 'all', `p${String(i).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 62});
  }
  await small.close();
}
// —— 2. 截图
const shot = async (page, name) => { await page.waitForTimeout(150); await page.screenshot({path: path.join(outDir, name + '.png')}); };
await pg.evaluate(() => window.__book.go(0)); await shot(pg, 'd_cover');
for (const i of SAMPLE) { await pg.evaluate((i) => window.__book.go(i), i); await shot(pg, `d_p${String(i).padStart(2, '0')}`); }
await pg.evaluate((n) => window.__book.go(n + 1), N); await shot(pg, 'd_end');
await pg.evaluate((i) => window.__book.go(i), pageOfCue(24)); await pg.click('button[aria-label=Contents]'); await shot(pg, 'd_toc'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=Storyboard]'); await shot(pg, 'd_storyboard'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=Settings]'); await shot(pg, 'd_settings');
await pg.keyboard.press('Escape');
await pg.evaluate((i) => window.__book.go(i), pageOfCue(24)); await pg.click('mark.film'); await shot(pg, 'd_film');
await pg.keyboard.press('Escape');
await pg.evaluate(() => window.__book.startShow(24)); await shot(pg, 'd_show');
await pg.keyboard.press('Escape');
// 纸色主题
await pg.click('button[aria-label=Settings]'); await pg.click('text=Paper'); await pg.keyboard.press('Escape');
await pg.evaluate((i) => window.__book.go(i), pageOfCue(24)); await shot(pg, 'd_paper_cue17');
await pg.evaluate(() => window.__book.go(0)); await shot(pg, 'd_paper_cover');

for (const [w, h, name, opts] of [[820, 1180, 'tablet', {touch: true, dpr: 1}], [390, 844, 'phone', {touch: true, dpr: 2}], [844, 390, 'phoneL', {touch: true, dpr: 2}], [1920, 1080, 'fhd', {}]]) {
  const p = await mk(w, h, name, opts);
  await p.evaluate(() => window.__book.go(0)); await shot(p, `${name}_cover`);
  for (const i of [1, firstOf('Chapter 9'), pageOfCue(24), pageOfCue(43)]) {
    await p.evaluate((i) => window.__book.go(i), i);
    const ov = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    if (ov) problems.push(`[${name}] page ${i}: horizontal overflow`);
    await shot(p, `${name}_p${String(i).padStart(2, '0')}`);
  }
  await p.click('button[aria-label=Contents]'); await shot(p, `${name}_toc`);
  await p.close();
}
await browser.close();
console.log(errors.length ? 'console errors:\n' + errors.join('\n') : 'no console errors ✓');
console.log(problems.length ? 'problems:\n' + problems.join('\n') : 'no layout problems found ✓');
console.log('screenshots in', outDir);
process.exit(problems.length || errors.length ? 1 : 0);
