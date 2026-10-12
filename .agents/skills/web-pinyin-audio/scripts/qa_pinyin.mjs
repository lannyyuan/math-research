// 「点字看拼音、听发音」的端到端自检（真浏览器）。
//   CHROME=/path/to/chrome  node qa_pinyin.mjs  page.html  [--source original.html] [--cases 长大:0:zhǎng,走得快:1:de] [--allow-missing ju4] [--no-toggle]
//   需要 playwright（先在页面所在项目里 `npm i --no-save playwright`；浏览器路径用 CHROME 指定，不设就用 playwright 自己的）。
//   检查：① 每个 .hz 都有合法读音、录音覆盖  ② --source 给了就核对“页面文字一个字没改”  ③ 悬停气泡 = 带调拼音；标点上没有气泡
//        ④ 点击真的开始播放（window.__pyPlays 加 1），只悬停不发声  ⑤ #pyh-toggle 开关  ⑥ 触屏轻点  ⑦ 无控制台报错
//   --cases 词:第几个字:期望拼音，用来验多音字（在页面某块文字里找这个词，把鼠标放到它的第 k 个字上）。
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const args = process.argv.slice(2);
const opt = (n, d = '') => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : d; };
const flag = (n) => { const i = args.indexOf(n); if (i >= 0) args.splice(i, 1); return i >= 0; };
const source = opt('--source'), cases = opt('--cases').split(',').filter(Boolean), allow = new Set(opt('--allow-missing').split(',').filter(Boolean));
const noToggle = flag('--no-toggle');
const target = args[0];
if (!target) { console.error('用法：node qa_pinyin.mjs page.html [--source original.html] [--cases 长大:0:zhǎng] [--allow-missing ju4]'); process.exit(2); }
let chromium;
try { ({chromium} = createRequire(path.join(process.cwd(), 'noop.js'))('playwright')); } catch { ({chromium} = createRequire(import.meta.url)('playwright')); }
const url = (p) => (/^https?:|^file:/.test(p) ? p : pathToFileURL(path.resolve(p)).href);

const problems = [], errors = [];
const ok = (c, m) => { if (!c) problems.push(m); console.log((c ? '  ✓ ' : '  ✗ ') + m); };
const browser = await chromium.launch({executablePath: process.env.CHROME || undefined, args: ['--no-sandbox', '--mute-audio', '--autoplay-policy=no-user-gesture-required']});  // 静音：点击会真的触发播放，别在用户机器上出声
const open = async (u, opts = {}, hover = true) => {
  const ctx = await browser.newContext({viewport: {width: 1280, height: 800}, ...opts});
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.goto(url(u));
  if (hover) await page.waitForFunction(() => window.PinyinHover, null, {timeout: 8000}).catch(() => { throw new Error(`${u}：页面里没有 window.PinyinHover（没内联 pinyin_hover.js，或脚本出错）`); });
  return {ctx, page};
};
const plays = (page) => page.evaluate(() => window.__pyPlays || 0);
const bubble = (page) => page.evaluate(() => { const b = document.querySelector('.pyb'); return {on: b.classList.contains('on'), py: b.querySelector('.py').textContent, qs: !b.querySelector('.qs').hidden}; });

console.log('1. 数据');
{
  const {ctx, page} = await open(target);
  const r = await page.evaluate(() => {
    const A = window.__PYA || {}, ids = {};
    let bad = 0;
    const hz = [...document.querySelectorAll('.hz')];
    for (const e of hz) { const p = e.dataset.p || ''; if (!/^[a-z]{1,6}[1-5]$/.test(p)) bad++; else ids[p] = (ids[p] || 0) + 1; }
    return {n: hz.length, bad, uniq: Object.keys(ids).length, noAudio: Object.keys(ids).filter((k) => !A[k]), clips: Object.keys(A).length};
  });
  ok(r.n > 0, `页面里有 ${r.n} 个 .hz 汉字`);
  ok(r.bad === 0, `读音格式都是 音节+声调数字（异常 ${r.bad} 个）`);
  const miss = r.noAudio.filter((k) => !allow.has(k));
  ok(miss.length === 0, `没有录音的读音：${r.noAudio.join(' ') || '无'}${miss.length ? `（名单外：${miss.join(' ')}）` : ''}`);
  console.log(`     ${r.uniq} 种读音，内联录音 ${r.clips} 条（同音共用）`);
  if (source) {
    const norm = (p) => p.evaluate(() => { const c = document.body.cloneNode(true); c.querySelectorAll('script,style,.pyh-note,.pyb').forEach((x) => x.remove()); return c.textContent.replace(/\s+/g, ' ').trim(); });
    const a = await norm(page), b2 = await open(source, {}, false), b = await norm(b2.page);
    ok(a === b, `页面文字与原稿逐字相同（${a.length} 字符）`);
    await b2.ctx.close();
  }
  await ctx.close();
}

console.log('2. 悬停 / 3. 点击（桌面）');
{
  const {ctx, page} = await open(target);
  const info = await page.evaluate(() => [...document.querySelectorAll('.hz')].map((e, i) => i));
  const picks = [0, Math.floor(info.length / 3), Math.floor(info.length * 2 / 3), info.length - 1];
  for (const k of picks) {
    const z = page.locator('.hz').nth(k);
    await z.scrollIntoViewIfNeeded();
    await page.mouse.move(2, 2); await page.waitForTimeout(120);
    await z.hover(); await page.waitForTimeout(350);
    const [p, ch] = await z.evaluate((e) => [e.dataset.p, e.textContent]);
    const want = await page.evaluate((id) => PinyinHover.mark(id), p);
    const b = await bubble(page);
    ok(b.on && b.py === want && b.qs === p.endsWith('5'), `“${ch}” 悬停 → ${b.py}${b.qs ? '（轻声）' : ''}（期望 ${want}）`);
  }
  for (const c of cases) {
    const [word, k, want] = c.split(':');
    const box = await page.evaluate(([w, k]) => {
      for (const blk of document.querySelectorAll('p,li,h1,h2,h3,h4,h5,h6,td,th,div,span')) {
        const hz = [...blk.querySelectorAll(':scope > .hz')];
        const at = hz.map((e) => e.textContent).join('').indexOf(w);
        if (at < 0) continue;
        const el = hz[at + +k]; el.scrollIntoView({block: 'center'});
        const r = el.getBoundingClientRect();
        return {x: r.left + r.width / 2, y: r.top + r.height / 2, ch: el.textContent};
      }
      return null;
    }, [word, k]);
    if (!box) { ok(false, `${word}：页面里没找到`); continue; }
    await page.mouse.move(2, 2); await page.waitForTimeout(120);
    await page.mouse.move(box.x, box.y); await page.waitForTimeout(350);
    const b = await bubble(page);
    ok(b.on && b.py === want, `“${word}”里的“${box.ch}” → ${b.py}（期望 ${want}）`);
  }
  await page.mouse.move(2, 2); await page.waitForTimeout(200);
  const z = page.locator('.hz').nth(picks[1]);
  const before = await plays(page);
  await z.hover(); await page.waitForTimeout(350);
  ok(await plays(page) === before, '只悬停不发声（默认）');
  await z.click();
  await page.waitForFunction((b) => (window.__pyPlays || 0) > b, before, {timeout: 4000}).catch(() => {});
  const pid = await z.evaluate((e) => e.dataset.p), hasAudio = await page.evaluate((id) => !!(window.__PYA || {})[id], pid);
  ok(hasAudio ? await plays(page) === before + 1 : true, hasAudio ? `点击后开始播放（${before} → ${await plays(page)}）` : `“${pid}”没有录音，点击走系统语音/静音（不计播放）`);
  if (!noToggle && await page.locator('#pyh-toggle').count()) {
    console.log('4. 开关');
    await page.locator('#pyh-toggle').click();
    await page.mouse.move(2, 2); await page.waitForTimeout(150);
    await z.hover(); await page.waitForTimeout(350);
    ok(!(await bubble(page)).on, '关闭后悬停没有气泡');
    const b0 = await plays(page); await z.click(); await page.waitForTimeout(400);
    ok(await plays(page) === b0, '关闭后点击不发声');
    await page.locator('#pyh-toggle').click();
    await page.mouse.move(2, 2); await page.waitForTimeout(150);
    await z.hover(); await page.waitForTimeout(350);
    ok((await bubble(page)).on, '重新开启后悬停有气泡');
  }
  await ctx.close();
}

console.log('5. 触屏');
{
  const {ctx, page} = await open(target, {viewport: {width: 390, height: 844}, hasTouch: true, isMobile: true, deviceScaleFactor: 2});
  const z = page.locator('.hz').nth(2);
  await z.scrollIntoViewIfNeeded();
  const before = await plays(page);
  await z.tap(); await page.waitForTimeout(500);
  ok((await bubble(page)).on, '轻点后气泡出现');
  const pid = await z.evaluate((e) => e.dataset.p);
  if (await page.evaluate((id) => !!(window.__PYA || {})[id], pid)) ok(await plays(page) === before + 1, '轻点 = 显示 + 发声');
  await ctx.close();
}

ok(errors.length === 0, `无控制台报错${errors.length ? '：' + errors.slice(0, 5).join(' | ') : ''}`);
await browser.close();
console.log(problems.length ? `\n未通过 ${problems.length} 项` : '\n全部通过 ✓');
process.exit(problems.length ? 1 : 0);
