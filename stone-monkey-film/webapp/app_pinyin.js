  /* ── 点字看拼音、听发音 ──
     汉字被包成 <span class="hz" data-p="zhang3">。鼠标悬停显示拼音气泡，点击（触屏：轻点）用真人录音念出来。
     读音在构建期标好（webapp/pinyin.py，规则表 pinyin_overrides.json）；录音是“音节+声调”粒度，同音共用一条（window.__PYA）。 */
  const PYA = window.__PYA || {};
  const PY_V = {a: 'āáǎà', e: 'ēéěè', i: 'īíǐì', o: 'ōóǒò', u: 'ūúǔù', v: 'ǖǘǚǜ'};
  function pyMark(id) {                       // zhang3 → zhǎng；de5（轻声）→ de；nv3 → nǚ
    const m = /^([a-z]+)([1-5])$/.exec(id);
    if (!m) return id;
    let s = m[1];
    const t = +m[2];
    if (t < 5) {
      let i = s.indexOf('a');
      if (i < 0) i = s.indexOf('e');
      if (i < 0) i = s.includes('ou') ? s.indexOf('o') : Math.max(...[...s].map((c, k) => ('aeiouv'.includes(c) ? k : -1)));
      s = s.slice(0, i) + PY_V[s[i]][t - 1] + s.slice(i + 1);
    }
    return s.replace(/v/g, 'ü');
  }
  function hanSpans(text, pyStr) {            // 汉字 → <span class="hz">；其余原样（textContent 不变）
    if (!pyStr) return [text];
    const py = pyStr.split(' ');
    const out = [];
    let run = '', k = 0;
    for (const ch of text) {
      const c = ch.charCodeAt(0);
      if (c >= 0x4e00 && c <= 0x9fff) { if (run) { out.push(run); run = ''; } out.push(h('span', {class: 'hz', 'data-p': py[k++]}, ch)); } else run += ch;
    }
    if (run) out.push(run);
    return out;
  }
  /* 播放：解码用 OfflineAudioContext（不受“必须先点一下”限制，可以提前解码），播放用 AudioContext（第一次点击时才创建）。
     单条录音很小，解码结果放 LRU；内联的 data URI 在 file:// 下也能用（不需要 fetch）。 */
  const pyAudio = (() => {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    const dec = OAC ? new OAC(1, 1, 22050) : null;
    const bufs = new Map(), jobs = new Map();
    let ctx = null, cur = null, token = 0;
    const toBuf = (uri) => { const b = atob(uri.slice(uri.indexOf(',') + 1)); const a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a.buffer; };
    function load(id) {
      if (bufs.has(id)) { const b = bufs.get(id); bufs.delete(id); bufs.set(id, b); return Promise.resolve(b); }
      if (jobs.has(id)) return jobs.get(id);
      if (!PYA[id] || !dec) return Promise.resolve(null);
      const job = new Promise((res, rej) => dec.decodeAudioData(toBuf(PYA[id]), res, rej))
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
      const C = window.AudioContext || window.webkitAudioContext;
      if (!C || !PYA[id]) return 'none';
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
      window.__pyPlays = (window.__pyPlays || 0) + 1;       // 自检用：真的开始播放了几次
      return 'played';
    }
    return {play, stop, load};
  })();
  let pyPreT = 0;
  function pyPreload() {                      // 翻页后在空闲时把本页用到的录音先解码，点的时候就是即时的
    clearTimeout(pyPreT);
    pyPreT = setTimeout(() => {
      if (!state.py || state.pos < 1 || state.pos > N) return;
      const ids = new Set();
      for (const q of BOOK.pages[state.pos - 1].paras) if (q.py) q.py.split(' ').forEach((x) => ids.add(x));
      [...ids].forEach((id) => pyAudio.load(id));
    }, 250);
  }
  function sayChar(ch, done) {                // 没有录音（如 ju4）：用系统自带的中文语音念单字；没有就不出声
    if (!canSpeak) return false;
    const vs = speechSynthesis.getVoices();
    const v = vs.find((x) => /^zh/i.test(x.lang));
    if (!v && vs.length) return false;
    stopSpeech();
    const u = new SpeechSynthesisUtterance(ch);
    u.lang = 'zh-CN'; u.rate = 0.85;
    if (v) u.voice = v;
    u.onend = u.onerror = done;
    speechSynthesis.speak(u);
    return true;
  }
  const pyb = h('div', {class: 'pyb', 'aria-hidden': 'true'}, h('b', {class: 'py'}), h('small', {class: 'qs', hidden: true}, '轻声'), h('i', {class: 'spk', html: ic.spk}));
  let pyEl = null, sayEl = null, showT = 0, hideT = 0;
  function pyShow(el) {
    clearTimeout(hideT);
    if (pyEl && pyEl !== el) pyEl.classList.remove('on');
    pyEl = el; el.classList.add('on');
    const id = el.dataset.p;
    $('.py', pyb).textContent = pyMark(id);
    $('.qs', pyb).hidden = !id.endsWith('5');
    pyb.classList.toggle('mute', !PYA[id] && !canSpeak);
    pyb.classList.add('on');
    const r = el.getBoundingClientRect(), bw = pyb.offsetWidth, bh = pyb.offsetHeight;
    const below = r.top < bh + 16;
    const cx = clamp(r.left + r.width / 2, bw / 2 + 8, innerWidth - bw / 2 - 8);
    pyb.style.left = `${cx}px`;
    pyb.style.top = `${below ? r.bottom + 8 : r.top - 8}px`;
    pyb.style.setProperty('--ax', `${r.left + r.width / 2 - cx}px`);
    pyb.classList.toggle('below', below);
  }
  function pyHide() {
    clearTimeout(showT); clearTimeout(hideT);
    hideT = setTimeout(() => { pyb.classList.remove('on'); if (pyEl) pyEl.classList.remove('on'); pyEl = null; }, 90);
  }
  function pyEnd(el) { if (sayEl === el) { el.classList.remove('say'); pyb.classList.remove('say'); sayEl = null; } }
  async function pySay(el) {
    const id = el.dataset.p;
    if (sayEl && sayEl !== el) sayEl.classList.remove('say');
    sayEl = el; el.classList.add('say'); pyb.classList.add('say');
    let r = 'none';
    if (PYA[id]) { stopSpeech(); r = await pyAudio.play(id, () => pyEnd(el)); }
    if (r === 'none') { if (!sayChar(el.textContent, () => pyEnd(el))) pyEnd(el); }
  }
  const hzOf = (e) => (state.py && e.target.closest ? e.target.closest('.hz') : null);
  stage.addEventListener('pointerover', (e) => {
    if (e.pointerType !== 'mouse') return;
    const z = hzOf(e);
    if (!z) return;
    clearTimeout(showT);
    showT = setTimeout(() => { pyShow(z); if (state.pyAuto && navigator.userActivation && navigator.userActivation.hasBeenActive) pySay(z); }, pyb.classList.contains('on') ? 0 : 150);
  });
  stage.addEventListener('pointerout', (e) => { if (e.pointerType === 'mouse' && hzOf(e)) pyHide(); });
  stage.addEventListener('click', (e) => { const z = hzOf(e); if (z) { pyShow(z); pySay(z); } });
  document.addEventListener('click', (e) => { if (!(e.target.closest && e.target.closest('.hz'))) pyHide(); });
  stage.addEventListener('scroll', () => pyHide(), {capture: true, passive: true});

