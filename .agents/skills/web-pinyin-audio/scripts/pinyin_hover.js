/* pinyin_hover.js — 点字看拼音、听发音（无依赖，单文件）
   页面里的汉字被包成 <span class="hz" data-p="zhang3">：鼠标悬停显示拼音气泡，点击（触屏：轻点）用录音念出来。
   录音：window.__PYA = {id: dataURI}，“音节+声调”粒度，同音共用（构建期由 pinyin_clips.py 生成）。
   没有某条录音时用系统中文语音念单字；再没有就只显示拼音。默认“悬停只显示、点击才发声”；auto:true 才悬停即发声。
   API：
     PinyinHover.init({root, audio, enabled, auto, speech, toggle, storageKey}) → {enable(b), setAuto(b), hide(), stop(), preload(ids), destroy()}
     PinyinHover.mark('zhang3') → 'zhǎng'
     PinyinHover.wrap(text, 'ta1 zhang3 da4 le5') → [string | <span class="hz">]   （JS 渲染的应用用它生成汉字 span，文字内容保持不变）
   自检钩子：每次真的开始播放，window.__pyPlays 加 1。 */
(function (global) {
  'use strict';
  const TONES = {a: 'āáǎà', e: 'ēéěè', i: 'īíǐì', o: 'ōóǒò', u: 'ūúǔù', v: 'ǖǘǚǜ'};
  const isHan = (c) => c >= 0x4e00 && c <= 0x9fff;
  const clamp = (v, a, b) => Math.min(Math.max(v, a), b);
  const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5v5h3.6L12 18.5v-13L7.6 9.5z" fill="currentColor" stroke-width="1.4"/><path d="M15.4 9a4.2 4.2 0 0 1 0 6M18 6.6a7.8 7.8 0 0 1 0 10.8"/></svg>';

  function mark(id) {                         // zhang3 → zhǎng；de5（轻声）→ de；nv3 → nǚ
    const m = /^([a-z]+)([1-5])$/.exec(id);
    if (!m) return id;
    let s = m[1];
    const t = +m[2];
    if (t < 5) {
      let i = s.indexOf('a');
      if (i < 0) i = s.indexOf('e');
      if (i < 0) i = s.includes('ou') ? s.indexOf('o') : Math.max(...[...s].map((c, k) => ('aeiouv'.includes(c) ? k : -1)));
      s = s.slice(0, i) + TONES[s[i]][t - 1] + s.slice(i + 1);
    }
    return s.replace(/v/g, 'ü');
  }

  function wrap(text, pyStr) {
    if (!pyStr) return [text];
    const py = pyStr.split(' ');
    const out = [];
    let run = '', k = 0;
    for (const ch of text) {
      if (isHan(ch.codePointAt(0))) {
        if (run) { out.push(run); run = ''; }
        const s = document.createElement('span');
        s.className = 'hz'; s.dataset.p = py[k++]; s.textContent = ch;
        out.push(s);
      } else run += ch;
    }
    if (run) out.push(run);
    return out;
  }

  /* 播放：解码用 OfflineAudioContext（不受“必须先点一下”限制，可以提前解码），播放用 AudioContext（第一次点击时才创建）。
     单条录音很小，解码结果放 LRU；内联的 data URI 在 file:// 下也能用（不需要 fetch）。 */
  function makeAudio(A) {
    const OAC = global.OfflineAudioContext || global.webkitOfflineAudioContext;
    const dec = OAC ? new OAC(1, 1, 22050) : null;
    const bufs = new Map(), jobs = new Map();
    let ctx = null, cur = null, token = 0;
    const toBuf = (uri) => { const b = atob(uri.slice(uri.indexOf(',') + 1)); const a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a.buffer; };
    function load(id) {
      if (bufs.has(id)) { const b = bufs.get(id); bufs.delete(id); bufs.set(id, b); return Promise.resolve(b); }
      if (jobs.has(id)) return jobs.get(id);
      if (!A[id] || !dec) return Promise.resolve(null);
      const job = new Promise((res, rej) => dec.decodeAudioData(toBuf(A[id]), res, rej))
        .then((b) => { bufs.set(id, b); while (bufs.size > 200) bufs.delete(bufs.keys().next().value); return b; })
        .catch(() => null)
        .finally(() => jobs.delete(id));
      jobs.set(id, job);
      return job;
    }
    function stop() { token++; if (cur) { try { cur.stop(); } catch (e) { /* 已经停了 */ } cur = null; } }
    /** → 'played' | 'cancelled'（被新的点击打断）| 'none'（没有这条录音/不能播） */
    async function play(id, onend) {
      stop();
      const my = token;
      const C = global.AudioContext || global.webkitAudioContext;
      if (!C || !A[id]) return 'none';
      if (!ctx) ctx = new C();
      if (ctx.state !== 'running') { try { await ctx.resume(); } catch (e) { /* 没有用户手势 */ } }
      const b = await load(id);
      if (!b) return 'none';
      if (my !== token) return 'cancelled';
      const src = ctx.createBufferSource();
      src.buffer = b; src.connect(ctx.destination);
      cur = src;
      src.onended = () => { if (cur === src) cur = null; onend && onend(); };
      src.start();
      global.__pyPlays = (global.__pyPlays || 0) + 1;
      return 'played';
    }
    return {play, stop, load};
  }

  function init(opts) {
    opts = opts || {};
    const A = opts.audio || global.__PYA || {};
    const root = opts.root || document.body;
    const key = opts.storageKey === undefined ? 'web-pinyin-audio' : opts.storageKey;
    const st = {on: opts.enabled !== false, auto: !!opts.auto};
    if (key) { try { const s = JSON.parse(localStorage.getItem(key) || '{}'); if (typeof s.on === 'boolean') st.on = s.on; if (typeof s.auto === 'boolean') st.auto = s.auto; } catch (e) { /* 没有存储也能用 */ } }
    const speech = opts.speech !== false && 'speechSynthesis' in global && 'SpeechSynthesisUtterance' in global;
    const audio = makeAudio(A);
    const ac = new AbortController();
    const on = {signal: ac.signal};
    const doc = document.documentElement;

    const pyb = document.createElement('div');
    pyb.className = 'pyb'; pyb.setAttribute('aria-hidden', 'true');
    pyb.innerHTML = '<b class="py"></b><small class="qs" hidden>轻声</small><i class="spk">' + ICON + '</i>';
    document.body.appendChild(pyb);
    const pyEl = pyb.querySelector('.py'), qsEl = pyb.querySelector('.qs');
    let curEl = null, sayEl = null, showT = 0, hideT = 0;

    function show(el) {
      clearTimeout(hideT);
      if (curEl && curEl !== el) curEl.classList.remove('on');
      curEl = el; el.classList.add('on');
      const id = el.dataset.p;
      pyEl.textContent = mark(id);
      qsEl.hidden = !id.endsWith('5');
      pyb.classList.toggle('mute', !A[id] && !speech);
      pyb.classList.add('on');
      const r = el.getBoundingClientRect(), bw = pyb.offsetWidth, bh = pyb.offsetHeight;
      const below = r.top < bh + 16;
      const cx = clamp(r.left + r.width / 2, bw / 2 + 8, innerWidth - bw / 2 - 8);
      pyb.style.left = cx + 'px';
      pyb.style.top = (below ? r.bottom + 8 : r.top - 8) + 'px';
      pyb.style.setProperty('--ax', (r.left + r.width / 2 - cx) + 'px');
      pyb.classList.toggle('below', below);
    }
    function hide() {
      clearTimeout(showT); clearTimeout(hideT);
      hideT = setTimeout(() => { pyb.classList.remove('on'); if (curEl) curEl.classList.remove('on'); curEl = null; }, 90);
    }
    function end(el) { if (sayEl === el) { el.classList.remove('say'); pyb.classList.remove('say'); sayEl = null; } }
    function sayChar(ch, done) {                // 没有录音（如 ju4）：用系统自带的中文语音念单字；没有就不出声
      if (!speech) return false;
      const vs = speechSynthesis.getVoices();
      const v = vs.find((x) => /^zh/i.test(x.lang));
      if (!v && vs.length) return false;
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(ch);
      u.lang = 'zh-CN'; u.rate = 0.85;
      if (v) u.voice = v;
      u.onend = u.onerror = done;
      speechSynthesis.speak(u);
      return true;
    }
    async function say(el) {
      const id = el.dataset.p;
      if (sayEl && sayEl !== el) sayEl.classList.remove('say');
      sayEl = el; el.classList.add('say'); pyb.classList.add('say');
      let r = 'none';
      if (A[id]) { if (speech) speechSynthesis.cancel(); r = await audio.play(id, () => end(el)); }
      if (r === 'none' && !sayChar(el.textContent, () => end(el))) end(el);
    }
    function save() { if (key) { try { localStorage.setItem(key, JSON.stringify({on: st.on, auto: st.auto})); } catch (e) { /* 忽略 */ } } }
    function enable(b) {
      st.on = !!b; doc.dataset.pyh = st.on ? 'on' : 'off';
      if (!st.on) { hide(); audio.stop(); if (speech) speechSynthesis.cancel(); }
      if (btn) { btn.textContent = st.on ? '关闭拼音' : '开启拼音'; btn.setAttribute('aria-pressed', String(st.on)); }
      save();
    }
    function preload(ids) { (ids || []).forEach((id) => audio.load(id)); }

    const hzOf = (e) => (st.on && e.target.closest ? e.target.closest('.hz') : null);
    root.addEventListener('pointerover', (e) => {
      if (e.pointerType !== 'mouse') return;
      const z = hzOf(e);
      if (!z) return;
      clearTimeout(showT);
      showT = setTimeout(() => { show(z); if (st.auto && navigator.userActivation && navigator.userActivation.hasBeenActive) say(z); }, pyb.classList.contains('on') ? 0 : 150);
    }, on);
    root.addEventListener('pointerout', (e) => { if (e.pointerType === 'mouse' && hzOf(e)) hide(); }, on);
    root.addEventListener('click', (e) => { const z = hzOf(e); if (z) { show(z); say(z); } }, on);
    document.addEventListener('click', (e) => { if (!(e.target.closest && e.target.closest('.hz'))) hide(); }, on);
    global.addEventListener('scroll', hide, {capture: true, passive: true, signal: ac.signal});

    const btn = typeof opts.toggle === 'string' ? document.querySelector(opts.toggle) : opts.toggle || null;
    if (btn) btn.addEventListener('click', () => enable(!st.on), on);
    enable(st.on);
    return {
      enable, hide, preload, stop: () => { audio.stop(); if (speech) speechSynthesis.cancel(); },
      setAuto: (b) => { st.auto = !!b; save(); },
      destroy: () => { ac.abort(); pyb.remove(); audio.stop(); delete doc.dataset.pyh; },
    };
  }

  global.PinyinHover = {init, mark, wrap};
})(window);
