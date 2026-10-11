// 《小石猴点灯》绘本网页的自动检查 + 截图：  node webapp/qa.mjs [--shots=out/book_qa] [--all]
//   1. 在真浏览器里逐页翻一遍，把页面上真正显示出来的正文（加章名；不含小标签）拼起来，
//      和“独立重新抽取的原文（按 plan.py 的 ORDER 排序）”逐字比对（去掉空白、引号、·）
//   2. 检查：控制台报错、横向溢出、桌面 1440×900 下哪些页的文字区需要滚动、图是否加载、字体是否加载
//   3. 截图：桌面 1440×900 / 平板竖屏 820×1180 / 手机竖屏 390×844 / 手机横屏 844×390 / 1920×1080
//   --all 再把每一页存成 1280×720 缩略图（人工看版式用）
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const pwPath = ['/opt/node-tools/node_modules/playwright', '/opt/node22/node-tools/node_modules/playwright', 'playwright'].find((p) => { try { require.resolve(p); return true; } catch { return false; } });
const {chromium} = require(pwPath);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = path.resolve(root, (process.argv.find((a) => a.startsWith('--shots=')) ?? '--shots=out/book_qa').split('=')[1]);
fs.mkdirSync(outDir, {recursive: true});
const file = pathToFileURL(path.join(root, 'dist/xiaoshihou-book.html')).href;
const norm = (t) => t.replace(/[\s“”"‘’'「」·]/g, '');

// —— 独立重新抽取原文（不复用 build.py / plan.py 的解析代码）；章节顺序从 plan.py 顶部的 ORDER 读
const py = fs.readFileSync(path.join(root, 'webapp/plan.py'), 'utf8');
const ORDER = [...py.slice(py.indexOf('ORDER = ['), py.indexOf(']', py.indexOf('ORDER = [')) ).matchAll(/'([^']+)'/g)].map((m) => m[1]);
const expectedText = (() => {
  const chap = {}; let cur = null, skip = false;
  for (const line of fs.readFileSync(path.join(root, 'story/book_source.txt'), 'utf8').split('\n')) {
    if (!line.trim() || line[0] === '#') continue;
    let body = line;
    if (line[0] === '【') {
      const end = line.indexOf('】');
      const label = line.slice(1, end); body = line.slice(end + 1);
      if (label.startsWith('附')) { skip = true; continue; }
      skip = false;
      if (label.startsWith('封面')) continue;
      if (label.startsWith('增补') || (label.startsWith('第') && label.slice(0, 5).includes('分'))) { cur = label.split(' ')[0]; chap[cur] = label; continue; }
    } else if (skip) continue;
    chap[cur] += body;
  }
  const missing = ORDER.filter((k) => !(k in chap)), extra = Object.keys(chap).filter((k) => !ORDER.includes(k));
  if (missing.length || extra.length) throw new Error(`ORDER 与原文章节不一致：缺 ${missing} 多 ${extra}`);
  return {text: ORDER.map((k) => chap[k]).join(''), chap};
})();

const browser = await chromium.launch({executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox']});
const problems = [];
const errors = [];
let expectMissingFile = false;   // 打开“看影片”时，影片文件不在旁边是预期的（页面会给出友好提示），浏览器会在控制台记一条加载失败
const mk = async (w, h, name, opts = {}) => {
  const ctx = await browser.newContext({viewport: {width: w, height: h}, deviceScaleFactor: opts.dpr ?? 1, hasTouch: !!opts.touch, colorScheme: opts.scheme ?? 'dark', reducedMotion: 'reduce'});
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`[${name}] ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error' && !(expectMissingFile && /Failed to load resource/.test(m.text()))) errors.push(`[${name}] console: ${m.text()}`); });
  await page.goto(file);
  await page.waitForFunction(() => window.__book);
  await page.evaluate(() => document.fonts.ready);
  return page;
};

// —— 1. 全文逐页核对（桌面 1440×900）
const pg = await mk(1440, 900, 'desktop');
const N = await pg.evaluate(() => window.__book.N);
await pg.addStyleTag({content: '.tag{display:none!important}'});   // 小标签不算正文
let got = '';
const scrolly = [];
const fill = [];
for (let i = 1; i <= N; i++) {
  await pg.evaluate((i) => window.__book.go(i), i);
  const info = await pg.evaluate(() => {
    const t = document.querySelector('.text'), inner = t.querySelector('.inner');
    const cs = getComputedStyle(t);
    const pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
    return {text: inner.innerText, sh: t.scrollHeight, ch: t.clientHeight, ih: inner.getBoundingClientRect().height, avail: t.clientHeight - pad, lh: parseFloat(cs.lineHeight), ov: document.documentElement.scrollWidth > innerWidth};
  });
  const imgOk = await pg.evaluate(async () => { await Promise.all([...document.images].filter((im) => im.getAttribute('src')).map((im) => im.decode().catch(() => null))); return [...document.images].filter((im) => im.getAttribute('src')).every((im) => im.naturalWidth > 0); });
  got += info.text;
  fill.push({page: i, ih: Math.round(info.ih), avail: Math.round(info.avail), lh: Math.round(info.lh * 10) / 10, lines: Math.round(info.ih / info.lh * 10) / 10});
  if (info.sh > info.ch + 2) scrolly.push(`${i}(+${info.sh - info.ch}px)`);
  if (info.ov) problems.push(`第 ${i} 页：横向溢出`);
  if (!imgOk) problems.push(`第 ${i} 页：有图没加载出来`);
}
fs.writeFileSync(path.join(outDir, 'fill.json'), JSON.stringify(fill));
const g = norm(got), expect = norm(expectedText.text);
if (g !== expect) {
  let k = 0; while (k < Math.min(g.length, expect.length) && g[k] === expect[k]) k++;
  problems.push(`页面文字与原文在第 ${k} 个字起不一致：页面「${g.slice(Math.max(0, k - 8), k + 16)}」 原文「${expect.slice(Math.max(0, k - 8), k + 16)}」`);
}
console.log(`章节顺序（ORDER）：${ORDER.join(' → ')}`);
console.log(`逐页文字核对：页面上 ${g.length} 个字 / 原文（含章名，不含引号、空白、·）${expect.length} 个字  ${g === expect ? '✓ 逐字相同' : '✗ 不同'}`);
console.log(`桌面 1440×900 下文字区需要滚动的页：${scrolly.length ? scrolly.join(' ') : '无'}`);
const fonts = await pg.evaluate(() => [...document.fonts].map((f) => `${f.family}/${f.weight}:${f.status}`));
console.log('字体：' + fonts.join('  '));
if (!fonts.some((f) => f.startsWith('LXGWWenKaiBook/400:loaded'))) problems.push('霞鹜文楷常规字体没有加载');
const tagCount = await pg.evaluate(() => window.__book.data.pages.reduce((a, p) => a + p.paras.filter((q) => q.tag).length, 0));
console.log(`小标签：${tagCount} 个（不参与核对）`);

// —— 1a. 操作：键盘翻页、地址直达、记住读到哪一页（刷新后封面出现“继续”）、Esc 关弹层、滑块
{
  await pg.evaluate(() => window.__book.go(1));
  await pg.keyboard.press('ArrowRight');
  let pos = await pg.evaluate(() => window.__book.state.pos);
  if (pos !== 2) problems.push(`键盘 → 没有翻到下一页（现在在 ${pos}）`);
  await pg.keyboard.press('ArrowLeft');
  pos = await pg.evaluate(() => window.__book.state.pos);
  if (pos !== 1) problems.push(`键盘 ← 没有翻回上一页（现在在 ${pos}）`);
  await pg.keyboard.press('End');
  pos = await pg.evaluate(() => window.__book.state.pos);
  if (pos !== N + 1) problems.push('End 键没有到“全书完”');
  await pg.keyboard.press('Home');
  await pg.evaluate(() => window.__book.go(37));
  await pg.reload(); await pg.waitForFunction(() => window.__book); await pg.evaluate(() => document.fonts.ready);
  pos = await pg.evaluate(() => window.__book.state.pos);   // 地址里是 #p37，刷新后应在第 37 页
  if (pos !== 37) problems.push(`刷新后地址 #p37 没有回到第 37 页（现在在 ${pos}）`);
  await pg.evaluate(() => window.__book.go(0));
  const resume = await pg.evaluate(() => [...document.querySelectorAll('.cover .btn')].map((b) => b.textContent));
  if (!resume.some((t) => t.includes('继续（第 37 页）'))) problems.push(`封面没有“继续（第 37 页）”按钮：${resume.join('/')}`);
  await pg.addStyleTag({content: '.tag{display:none!important}'});
  await pg.evaluate(() => window.__book.openSb(true));
  const cards = await pg.evaluate(() => document.querySelectorAll('.sb .card').length);
  if (cards !== N) problems.push(`分镜总览里有 ${cards} 张缩略图，应为 ${N}`);
  await pg.keyboard.press('Escape');
  const open = await pg.evaluate(() => document.querySelector('.modal.on, .drawer.on, .show.on') !== null);
  if (open) problems.push('Esc 没有关掉分镜总览');
}

const data = await pg.evaluate(() => window.__book.data);
const firstOf = (key) => data.pages.find((p) => data.sections[p.sec].no === key).i;
const lastOf = (key) => data.pages.filter((p) => data.sections[p.sec].no === key).pop().i;
const SAMPLE = [1, 6, firstOf('第三分'), firstOf('第六分') + 4, firstOf('增补三') + 1, firstOf('第七分') + 5, firstOf('第八分'), firstOf('第九分') + 4, firstOf('第十二分') + 2, firstOf('第十四分') + 1, firstOf('第十九分') + 4, firstOf('第二十分') + 5, lastOf('第二十一分') - 1, N];

// —— 1b. 逐页缩略截图（人工看版式用）
if (process.argv.includes('--all')) {
  const small = await mk(1280, 720, 'all');
  fs.mkdirSync(path.join(outDir, 'all'), {recursive: true});
  for (let i = 0; i <= N + 1; i++) {
    await small.evaluate((i) => window.__book.go(i), i);
    await small.evaluate(async () => { await Promise.all([...document.images].filter((im) => im.getAttribute('src')).map((im) => im.decode().catch(() => null))); });
    await small.waitForTimeout(30);
    await small.screenshot({path: path.join(outDir, 'all', `p${String(i).padStart(3, '0')}.jpg`), type: 'jpeg', quality: 60});
  }
  await small.close();
}

// —— 2. 截图
const shot = async (page, name) => { await page.waitForTimeout(160); await page.screenshot({path: path.join(outDir, name + '.png')}); };
const pn = (i) => String(i).padStart(3, '0');
await pg.evaluate(() => window.__book.go(0)); await shot(pg, 'd_cover');
for (const i of SAMPLE) { await pg.evaluate((i) => window.__book.go(i), i); await shot(pg, `d_p${pn(i)}`); }
await pg.evaluate((n) => window.__book.go(n + 1), N); await shot(pg, 'd_end');
const mid = firstOf('第九分') + 2;
await pg.evaluate((i) => window.__book.go(i), mid); await pg.click('button[aria-label=目录]'); await shot(pg, 'd_toc'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=分镜]'); await shot(pg, 'd_storyboard'); await pg.keyboard.press('Escape');
await pg.click('button[aria-label=设置]'); await shot(pg, 'd_settings');
await pg.keyboard.press('Escape');
expectMissingFile = true;
await pg.click('button[aria-label=看影片]');
const filmMsg = await pg.waitForSelector('.vid .msg', {timeout: 4000}).then(() => true).catch(() => false);
if (!filmMsg && !fs.existsSync(path.join(root, 'dist/xiaoshihou-dian-deng.mp4')) && !fs.existsSync(path.join(root, 'dist/xiao-shi-hou-720p.mp4'))) problems.push('影片文件不在旁边时，“看影片”没有给出友好提示');
await shot(pg, 'd_film'); await pg.keyboard.press('Escape');
expectMissingFile = false;
await pg.evaluate(() => window.__book.startShow(3)); await shot(pg, 'd_show');
await pg.keyboard.press('Escape');
// 小标签关掉 / 字号 XL（看设置是否生效，且不报错）
await pg.click('button[aria-label=设置]'); await pg.click('.pop >> text=特大'); await pg.keyboard.press('Escape');
await pg.evaluate((i) => window.__book.go(i), firstOf('第十二分') + 1); await shot(pg, 'd_xl');
await pg.click('button[aria-label=设置]'); await pg.click('.pop >> text=中'); await pg.keyboard.press('Escape');
// 纸色主题
await pg.click('button[aria-label=设置]'); await pg.click('.pop >> text=纸色'); await pg.keyboard.press('Escape');
await pg.evaluate(() => window.__book.go(0)); await shot(pg, 'd_paper_cover');
for (const i of [SAMPLE[2], SAMPLE[8]]) { await pg.evaluate((i) => window.__book.go(i), i); await shot(pg, `d_paper_p${pn(i)}`); }
await pg.click('button[aria-label=目录]'); await shot(pg, 'd_paper_toc'); await pg.keyboard.press('Escape');

for (const [w, h, name, opts] of [[820, 1180, 'tablet', {touch: true, dpr: 1}], [390, 844, 'phone', {touch: true, dpr: 2}], [844, 390, 'phoneL', {touch: true, dpr: 2}], [1920, 1080, 'fhd', {}]]) {
  const p = await mk(w, h, name, opts);
  await p.evaluate(() => window.__book.go(0)); await shot(p, `${name}_cover`);
  const scr = [];
  for (let i = 1; i <= N; i++) {
    await p.evaluate((i) => window.__book.go(i), i);
    const r = await p.evaluate(() => { const t = document.querySelector('.text'); return {ov: document.documentElement.scrollWidth > innerWidth, sc: t.scrollHeight > t.clientHeight + 2, pic: document.querySelector('.frame').getBoundingClientRect().bottom <= innerHeight, cap: document.querySelector('.pic figcaption').getBoundingClientRect().bottom <= innerHeight}; });
    if (r.ov) problems.push(`[${name}] 第 ${i} 页：横向溢出`);
    if (!r.pic || !r.cap) problems.push(`[${name}] 第 ${i} 页：图或图注被挤出屏幕`);
    if (r.sc) scr.push(i);
  }
  console.log(`[${name} ${w}×${h}] 文字区需要内部滚动的页：${scr.length} / ${N}`);
  for (const i of [1, SAMPLE[2], SAMPLE[5], SAMPLE[10]]) { await p.evaluate((i) => window.__book.go(i), i); await shot(p, `${name}_p${pn(i)}`); }
  await p.evaluate(() => window.__book.go(window.__book.END)); await shot(p, `${name}_end`);
  await p.click('button[aria-label=目录]'); await shot(p, `${name}_toc`); await p.keyboard.press('Escape');
  await p.click('button[aria-label=设置]'); await shot(p, `${name}_settings`);
  await p.close();
}
await browser.close();
console.log(errors.length ? '控制台报错：\n' + errors.join('\n') : '无控制台报错 ✓');
console.log(problems.length ? '问题：\n' + problems.join('\n') : '没有发现版式问题 ✓');
console.log('截图在', outDir);
process.exit(problems.length || errors.length ? 1 : 0);
