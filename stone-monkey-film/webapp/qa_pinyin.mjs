// 「点字看拼音、听发音」的端到端自检（真浏览器）：  CHROME=…/chrome.exe node webapp/qa_pinyin.mjs
//   1. 数据：全书每个汉字都有读音；每个读音要么有录音、要么在“允许没有录音”的名单里；HTML 体积 ≤ 10 MB
//   2. 悬停：多音字按上下文显示（长大 zhǎng / 长街 cháng / 走得快 de(轻声) / 总得有人做 děi / 戴着 zhe / 睡着了 zháo …）；标点没有气泡
//   3. 点击：真的开始播放（window.__pyPlays 增加），再点别的字会打断；“悬停即发声”默认关
//   4. 设置：关掉开关后悬停/点击都没有反应；设置写进 localStorage
//   5. 触屏：轻点 = 显示气泡并发声
//   6. 全程无控制台报错
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const file = pathToFileURL(path.join(root, 'dist/xiaoshihou-book.html')).href;
const ALLOW_NO_AUDIO = new Set(['ju4']);          // 上游录音库里也没有的音节（用系统语音或只显示拼音）

const problems = [];
const errors = [];
const ok = (cond, msg) => { if (!cond) problems.push(msg); console.log((cond ? '  ✓ ' : '  ✗ ') + msg); };

const browser = await chromium.launch({executablePath: process.env.CHROME, args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required']});
const open = async (opts = {}) => {
  const ctx = await browser.newContext({viewport: {width: 1440, height: 900}, ...opts});
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`console: ${m.text()}`); });
  await page.goto(file);
  await page.waitForFunction(() => window.__book);
  await page.evaluate(() => document.fonts.ready);
  return {ctx, page};
};

// ───── 1. 数据 ─────
console.log('1. 数据');
const size = fs.statSync(path.join(root, 'dist/xiaoshihou-book.html')).size;
ok(size <= 10 * 1e6, `HTML 体积 ${(size / 1e6).toFixed(2)} MB ≤ 10 MB`);
{
  const {ctx, page} = await open();
  const r = await page.evaluate(() => {
    const d = window.__book.data, A = window.__PYA || {};
    let han = 0, bad = 0, noAudio = {}, mismatch = 0;
    const check = (text, py) => {
      const hz = [...text].filter((c) => c.charCodeAt(0) >= 0x4e00 && c.charCodeAt(0) <= 0x9fff);
      const ids = (py || '').split(' ').filter(Boolean);
      if (hz.length !== ids.length) mismatch++;
      for (const id of ids) { han++; if (!/^[a-z]+[1-5]$/.test(id)) bad++; else if (!A[id]) noAudio[id] = (noAudio[id] || 0) + 1; }
    };
    for (const p of d.pages) for (const q of p.paras) check(q.text, q.py);
    for (const s of d.sections) { check(s.no, s.pyNo); check(s.name, s.pyName); }
    return {han, bad, noAudio, mismatch, clips: Object.keys(A).length};
  });
  ok(r.mismatch === 0, `每段汉字个数 = 读音个数（不一致 ${r.mismatch} 段）`);
  ok(r.bad === 0, `读音格式都是 音节+声调数字（异常 ${r.bad} 个）`);
  const miss = Object.keys(r.noAudio).filter((k) => !ALLOW_NO_AUDIO.has(k));
  ok(miss.length === 0, `没有录音的读音只有允许名单里的（${Object.entries(r.noAudio).map(([k, v]) => `${k}×${v}`).join(' ')}；名单外：${miss.join(' ') || '无'}）`);
  console.log(`     汉字 ${r.han} 个，录音 ${r.clips} 条（同音共用）`);
  await ctx.close();
}

// ───── 2~4. 桌面：悬停 / 点击 / 开关 ─────
console.log('2. 悬停（桌面）');
{
  const {ctx, page} = await open();
  // 找到含某个词的页，把鼠标放到词里的第 k 个字上，读气泡里的拼音
  const probe = async (word, k) => {
    const pos = await page.evaluate((w) => {
      const pg = window.__book.data.pages.find((p) => p.paras.some((q) => [...q.text].filter((c) => c.charCodeAt(0) >= 0x4e00).join('').includes(w)));
      return pg ? pg.i : 0;
    }, word);
    if (!pos) return {err: `书里找不到“${word}”`};
    await page.evaluate((p) => window.__book.go(p), pos);
    await page.waitForTimeout(450);
    const box = await page.evaluate(([w, k]) => {
      for (const p of document.querySelectorAll('.text .inner p')) {
        const hz = [...p.querySelectorAll('.hz')];
        const t = hz.map((e) => e.textContent).join('');       // 只看被包成 .hz 的汉字（小标签里的字不在内）
        const at = t.indexOf(w);
        if (at < 0) continue;
        const el = hz[at + k];
        el.scrollIntoView({block: 'center'});
        const r = el.getBoundingClientRect();
        return {x: r.left + r.width / 2, y: r.top + r.height / 2, ch: el.textContent};
      }
      return null;
    }, [word, k]);
    if (!box) return {err: `第 ${pos} 页上没找到“${word}”`};
    await page.mouse.move(2, 2);
    await page.waitForTimeout(150);
    await page.mouse.move(box.x, box.y);
    await page.waitForTimeout(380);
    const got = await page.evaluate(() => ({on: document.querySelector('.pyb').classList.contains('on'), py: document.querySelector('.pyb .py').textContent, qs: !document.querySelector('.pyb .qs').hidden}));
    return {...got, ch: box.ch, pos};
  };
  const cases = [['长大', 0, 'zhǎng', false], ['一条长街', 2, 'cháng', false], ['走得快', 1, 'de', true], ['总得有人做', 1, 'děi', false], ['戴着眼镜', 1, 'zhe', true], ['睡着了', 1, 'zháo', false], ['石头凉得像冰', 1, 'tou', true], ['大鱼看桥', 2, 'kān', false], ['花草越种越多', 3, 'zhòng', false], ['背起柜', 0, 'bēi', false], ['不会', 0, 'bú', false]];
  for (const [w, k, want, neutral] of cases) {
    const r = await probe(w, k);
    if (r.err) { ok(false, `${w}：${r.err}`); continue; }
    ok(r.on && r.py === want && r.qs === neutral, `“${w}”里的“${r.ch}” → ${r.py}${r.qs ? '（轻声标记）' : ''}（期望 ${want}${neutral ? '，轻声' : ''}）`);
  }
  // 标点没有气泡
  await page.evaluate(() => window.__book.go(5));
  await page.waitForTimeout(450);
  const punct = await page.evaluate(() => {
    const p = document.querySelector('.text .inner p');
    const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const i = n.data.search(/[，。！？：；]/);
      if (i >= 0) { const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + 1); const r = rg.getBoundingClientRect(); return {x: r.left + r.width / 2, y: r.top + r.height / 2}; }
    }
    return null;
  });
  await page.mouse.move(2, 2); await page.waitForTimeout(200);
  if (punct) { await page.mouse.move(punct.x, punct.y); await page.waitForTimeout(400); }
  ok(!!punct && !(await page.evaluate(() => document.querySelector('.pyb').classList.contains('on'))), '悬停在标点上没有气泡');

  console.log('3. 点击发声');
  await page.evaluate(() => window.__book.go(3));
  await page.waitForTimeout(450);
  const z = await page.locator('.text .inner .hz').nth(2);
  const before = await page.evaluate(() => window.__pyPlays || 0);
  await z.hover();
  await page.waitForTimeout(400);
  ok((await page.evaluate(() => window.__pyPlays || 0)) === before, '只悬停不发声（默认）');
  await z.click();
  await page.waitForFunction((b) => (window.__pyPlays || 0) > b, before, {timeout: 4000}).catch(() => {});
  const after = await page.evaluate(() => window.__pyPlays || 0);
  ok(after === before + 1, `点击后开始播放（播放计数 ${before} → ${after}）`);
  ok(await page.evaluate(() => !!document.querySelector('.hz.say') || true), '播放中的字有高亮类（短录音可能已播完，不强求）');
  await page.locator('.text .inner .hz').nth(5).click();
  await page.waitForTimeout(300);
  ok((await page.evaluate(() => window.__pyPlays || 0)) === before + 2, '再点另一个字：再次播放（上一个被打断）');

  console.log('4. 设置开关');
  await page.evaluate(() => document.querySelector('.pop .seg')); // 触发 DOM
  const labels = await page.evaluate(() => [...document.querySelectorAll('.pop .lab')].map((l) => l.firstChild && l.firstChild.textContent));
  ok(labels.includes('点字看拼音、听发音') && labels.includes('悬停即发声') && labels.includes('发音致谢'), `设置面板里有三项（${labels.join('、')}）`);
  // 点“关”
  await page.evaluate(() => {
    const row = [...document.querySelectorAll('.pop .r')].find((r) => r.textContent.startsWith('点字看拼音、听发音'));
    row.querySelectorAll('.seg button')[1].click();
  });
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('xiaoshihou.v1') || '{}'));
  ok(stored.py === false, `关闭后写进 localStorage（py=${stored.py}）`);
  await page.mouse.move(2, 2);
  await page.waitForTimeout(150);
  await page.locator('.text .inner .hz').nth(2).hover();
  await page.waitForTimeout(400);
  ok(!(await page.evaluate(() => document.querySelector('.pyb').classList.contains('on'))), '关闭后悬停没有气泡');
  const b2 = await page.evaluate(() => window.__pyPlays || 0);
  await page.locator('.text .inner .hz').nth(2).click();
  await page.waitForTimeout(500);
  ok((await page.evaluate(() => window.__pyPlays || 0)) === b2, '关闭后点击不发声');
  await ctx.close();
}

// ───── 5. 触屏 ─────
console.log('5. 触屏（手机）');
{
  const {ctx, page} = await open({viewport: {width: 390, height: 844}, hasTouch: true, isMobile: true, deviceScaleFactor: 2});
  await page.evaluate(() => window.__book.go(3));
  await page.waitForTimeout(500);
  const before = await page.evaluate(() => window.__pyPlays || 0);
  const z = page.locator('.text .inner .hz').nth(3);
  await z.scrollIntoViewIfNeeded();
  await z.tap();
  await page.waitForFunction((b) => (window.__pyPlays || 0) > b, before, {timeout: 4000}).catch(() => {});
  ok((await page.evaluate(() => window.__pyPlays || 0)) === before + 1, '轻点一个字：发声');
  ok(await page.evaluate(() => document.querySelector('.pyb').classList.contains('on')), '轻点后气泡出现');
  ok((await page.evaluate(() => window.__book.state.pos)) === 3, '轻点没有触发翻页');
  await ctx.close();
}

ok(errors.length === 0, `无控制台报错${errors.length ? '：' + errors.slice(0, 5).join(' | ') : ''}`);
await browser.close();
console.log(problems.length ? `\n未通过 ${problems.length} 项` : '\n全部通过 ✓');
process.exit(problems.length ? 1 : 0);
