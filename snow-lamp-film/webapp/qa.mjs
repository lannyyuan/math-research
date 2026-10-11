// 绘本网页的自动检查 + 截图：node webapp/qa.mjs [--shots=out/book_qa]
//   1. 在真浏览器里把 66 页逐页翻一遍，把页面上显示出来的字拼起来，和故事原文逐字比对
//   2. 检查：控制台报错、横向溢出、每页文字区是否需要滚动
//   3. 桌面 / 平板竖屏 / 手机竖屏 / 手机横屏 各截几张图
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const pwPath = ['/opt/node-tools/node_modules/playwright', '/opt/node22/node-tools/node_modules/playwright', 'playwright'].find((p) => { try { require.resolve(p); return true; } catch { return false; } });
const {chromium} = require(pwPath);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.resolve(root, (process.argv.find((a) => a.startsWith('--shots=')) ?? '--shots=out/book_qa').split('=')[1]);
fs.mkdirSync(outDir, {recursive: true});
const file = 'file://' + path.join(root, 'dist/snow-lamp-book.html');
const norm = (t) => t.replace(/[\s“”"‘’'「」]/g, '');
const src = fs.readFileSync(path.join(root, 'story/source.md'), 'utf8').split('\n').filter((l) => l.trim() && !l.startsWith('#')).join('');

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
  if (info.ov) problems.push(`第 ${i} 页横向溢出`);
  if (!imgOk) problems.push(`第 ${i} 页有图没加载`);
}
// 章名在页面上也显示了（“第三节”“影子和害怕”），原文里是标题行；这里把标题行也拼进“期望文本”
const heads = JSON.parse(fs.readFileSync(path.join(root, 'webapp/out/plan.json'), 'utf8')).sections;
const expect = (() => {
  let s = '';
  const lines = fs.readFileSync(path.join(root, 'story/source.md'), 'utf8').split('\n');
  for (const l of lines) {
    if (l.startsWith('## ')) { const m = /^## (第[一二三四五六七八九十]+节|开头|尾声)[　 ]+(.+)$/.exec(l); s += m[1] + m[2]; }
    else if (l.trim() && !l.startsWith('#')) s += l;
  }
  return norm(s);
})();
const g = norm(got);
if (g !== expect) {
  let k = 0; while (k < Math.min(g.length, expect.length) && g[k] === expect[k]) k++;
  problems.push(`逐页文字与原文不一致：第 ${k} 个字起 页面=「${g.slice(k - 8, k + 16)}」 原文=「${expect.slice(k - 8, k + 16)}」`);
}
console.log(`全文逐页比对：页面 ${g.length} 字 / 原文 ${expect.length} 字（含章名、不含引号空白） ${g === expect ? '✓ 一致' : '✗ 不一致'}`);
console.log(`需要在文字区里滚动的页（桌面 1440×900）：${scrolly.length ? scrolly.join(' ') : '无'}`);

const data = await pg.evaluate(() => window.__book.data);
const pageOfCue = (no) => data.pages.find((p) => p.cues.includes(no)).i;
const firstOf = (nm) => data.pages.find((p) => data.sections[p.sec].no === nm).i;
const SAMPLE = [1, firstOf('第一节'), firstOf('第四节'), pageOfCue(12), pageOfCue(17), firstOf('第七节'), firstOf('第八节'), firstOf('第九节'), firstOf('第十二节'), firstOf('第十三节'), firstOf('第十五节'), pageOfCue(25), pageOfCue(28), pageOfCue(38), N];
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
await pg.evaluate((i) => window.__book.go(i), pageOfCue(17)); await pg.click('button[aria-label=目录]'); await shot(pg, 'd_toc'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=分镜总览]'); await shot(pg, 'd_storyboard'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=设置]'); await shot(pg, 'd_settings');
await pg.keyboard.press('Escape');
await pg.evaluate((i) => window.__book.go(i), pageOfCue(17)); await pg.click('mark.film'); await shot(pg, 'd_film');
await pg.keyboard.press('Escape');
await pg.evaluate(() => window.__book.startShow(14)); await shot(pg, 'd_show');
await pg.keyboard.press('Escape');
// 纸色主题
await pg.click('button[aria-label=设置]'); await pg.click('text=纸色'); await pg.keyboard.press('Escape');
await pg.evaluate((i) => window.__book.go(i), pageOfCue(17)); await shot(pg, 'd_paper_cue17');
await pg.evaluate(() => window.__book.go(0)); await shot(pg, 'd_paper_cover');

for (const [w, h, name, opts] of [[820, 1180, 'tablet', {touch: true, dpr: 1}], [390, 844, 'phone', {touch: true, dpr: 2}], [844, 390, 'phoneL', {touch: true, dpr: 2}], [1920, 1080, 'fhd', {}]]) {
  const p = await mk(w, h, name, opts);
  await p.evaluate(() => window.__book.go(0)); await shot(p, `${name}_cover`);
  for (const i of [1, firstOf('第四节'), pageOfCue(17), pageOfCue(28)]) {
    await p.evaluate((i) => window.__book.go(i), i);
    const ov = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    if (ov) problems.push(`[${name}] 第 ${i} 页横向溢出`);
    await shot(p, `${name}_p${String(i).padStart(2, '0')}`);
  }
  await p.click('button[aria-label=目录]'); await shot(p, `${name}_toc`);
  await p.close();
}
await browser.close();
console.log(errors.length ? '控制台错误:\n' + errors.join('\n') : '控制台无报错 ✓');
console.log(problems.length ? '问题:\n' + problems.join('\n') : '没有发现版式问题 ✓');
console.log('截图在', outDir);
process.exit(problems.length || errors.length ? 1 : 0);
