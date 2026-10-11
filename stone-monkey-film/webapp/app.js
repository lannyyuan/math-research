/* 《小石猴点灯》绘本网页：封面 → 一页一图一段文 → 全书完；目录、分镜总览、放映、设置、朗读、看影片。
   全部内联在一个 HTML 里（#book-data = 页与文字，window.__IMG = WebP 图），没有任何外部依赖。 */
(() => {
  'use strict';
  const BOOK = JSON.parse(document.getElementById('book-data').textContent);
  const IMG = window.__IMG;
  const N = BOOK.pages.length;
  const END = N + 1; // 0 封面，1..N 正文页，N+1 全书完
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

  const h = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
    return e;
  };
  const ic = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    grid: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3.5" y="4.5" width="7" height="6" rx="1.5"/><rect x="13.5" y="4.5" width="7" height="6" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="6" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="6" rx="1.5"/></svg>',
    gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 3v2.6M12 18.4V21M3 12h2.6M18.4 12H21M5.6 5.6l1.9 1.9M16.5 16.5l1.9 1.9M18.4 5.6l-1.9 1.9M7.5 16.5l-1.9 1.9"/></svg>',
    film: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="14" rx="2.5"/><path d="M10 9.2v5.6l4.6-2.8z" fill="currentColor"/></svg>',
    lamp: '<svg viewBox="0 0 32 32" width="26" height="26"><circle cx="16" cy="16" r="13" fill="#cfc29a" opacity=".20"/><circle cx="16" cy="16" r="7" fill="#cfc29a" opacity=".42"/><circle cx="16" cy="16" r="3.4" fill="#f4eedd"/></svg>',
    spk: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5v5h3.6L12 18.5v-13L7.6 9.5z" fill="currentColor" stroke-width="1.4"/><path d="M15.4 9a4.2 4.2 0 0 1 0 6M18 6.6a7.8 7.8 0 0 1 0 10.8"/></svg>',
  };

  /* ── 状态与保存的设置 ── */
  const store = {
    get() { try { return JSON.parse(localStorage.getItem('xiaoshihou.v1') || '{}'); } catch (e) { return {}; } },
    set(o) { try { localStorage.setItem('xiaoshihou.v1', JSON.stringify({...store.get(), ...o})); } catch (e) { /* 隐私模式等：读不到也能读书 */ } },
  };
  const saved = store.get();
  const prefersLight = matchMedia('(prefers-color-scheme: light)').matches;
  const state = {
    pos: 0,
    fs: typeof saved.fs === 'number' ? saved.fs : 1,
    theme: saved.theme || (prefersLight ? 'paper' : 'night'),
    tags: saved.tags !== false,
    py: saved.py !== false,            // 点字看拼音、听发音
    pyAuto: saved.pyAuto === true,     // 悬停即发声（默认关：悬停只显示拼音，点击才发声）
  };
  const secOf = (i) => BOOK.pages[i - 1].sec;
  const secPages = BOOK.sections.map(() => []);
  BOOK.pages.forEach((p) => secPages[p.sec].push(p.i));
  const secLabel = (s) => `${BOOK.sections[s].no} · ${BOOK.sections[s].name}`;

  /* ── 图：内联的是 data URI；用到时转成 blob 网址（缩略图很多时更省），转不了就直接用 data URI ── */
  const urlCache = {};
  function imgSrc(key) {
    if (urlCache[key]) return urlCache[key];
    const d = IMG[key];
    if (!d) return '';
    try {
      const mime = d.slice(5, d.indexOf(';'));
      const bin = atob(d.slice(d.indexOf(',') + 1));
      const u8 = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      return (urlCache[key] = URL.createObjectURL(new Blob([u8], {type: mime})));
    } catch (e) { return (urlCache[key] = d); }
  }
  const imgEl = (hero, extra = {}) => {
    const z = hero.z || 1;
    const fx = hero.fx ?? 0.5, fy = hero.fy ?? 0.55;
    const el = h('img', {src: imgSrc(hero.img), alt: extra.noalt ? '' : (hero.alt || ''), draggable: 'false', decoding: 'async', loading: extra.lazy ? 'lazy' : null});
    if (z > 1) {
      const tx = clamp(0.5 - z * fx, 1 - z, 0), ty = clamp(0.5 - z * fy, 1 - z, 0);
      el.style.transformOrigin = '0 0';
      el.style.transform = `translate(${tx * 100}%,${ty * 100}%) scale(${z})`;
    }
    return el;
  };

  /* 翻页前先把前后几页的图解码好，翻过去时不会闪一下空白 */
  const warmed = [];
  function warm(pos) {
    for (const d of [1, 2, -1]) {
      const p = BOOK.pages[pos + d - 1];
      if (!p) continue;
      const im = new Image();
      im.decoding = 'async';
      im.src = imgSrc(p.hero.img);
      im.decode().catch(() => {});
      warmed.push(im);
      if (warmed.length > 8) warmed.shift();
    }
  }

  /* ── 骨架 ── */
  const app = $('#app');
  const brand = h('button', {class: 'brand', 'aria-label': '回到封面', onclick: () => go(0)}, h('span', {html: ic.lamp}), h('span', {class: 't'}, BOOK.title));
  const chapname = h('span', {class: 'chapname'});
  const topBtn = (icon, label, fn, extra = {}) => h('button', {class: 'ibtn', 'aria-label': label, onclick: fn, ...extra}, h('span', {html: icon}), h('span', {class: 't'}, label));
  const btnToc = topBtn(ic.menu, '目录', () => openDrawer(true));
  const btnSb = topBtn(ic.grid, '分镜', () => openSb(true));
  const btnFilm = topBtn(ic.film, '看影片', () => openFilm());
  const btnSet = topBtn(ic.gear, '设置', () => togglePop(), {'aria-pressed': 'false'});
  const bar = h('header', {class: 'bar'}, brand, chapname, btnToc, btnSb, btnFilm, btnSet);
  const stage = h('main', {class: 'stage', id: 'stage'});
  const prevBtn = h('button', {class: 'rbtn', 'aria-label': '上一页', html: ic.prev, onclick: () => step(-1)});
  const nextBtn = h('button', {class: 'rbtn', 'aria-label': '下一页', html: ic.next, onclick: () => step(1)});
  const labL = h('span'), labR = h('span');
  const slider = h('input', {type: 'range', min: 0, max: END, step: 1, value: 0, 'aria-label': '跳到某一页'});
  const ticks = h('div', {class: 'ticks'});
  BOOK.sections.forEach((s, i) => ticks.append(h('i', {style: `left:${(secPages[i][0] / END) * 100}%`})));
  const nav = h('footer', {class: 'nav'}, prevBtn, h('div', {class: 'prog'}, h('div', {class: 'lab'}, labL, labR), h('div', {class: 'sl'}, slider, ticks)), nextBtn);
  app.append(bar, stage, nav);

  /* ── 页 ── */
  const pageView = (p) => {
    const pic = h('figure', {class: 'pic'}, h('div', {class: 'frame'}, imgEl(p.hero), h('i', {class: 'seal', 'aria-hidden': 'true'}, '灯')), h('figcaption', {}, h('span', {class: 'cap'}, p.hero.cap || '')));
    const inner = h('div', {class: 'inner'});
    if (p.startsSec) {
      const s = BOOK.sections[p.sec];
      inner.append(h('div', {class: 'chap'}, h('span', {class: 'no'}, hanSpans(s.no, s.pyNo)), h('h2', {}, hanSpans(s.name, s.pyName)), h('i', {class: 'rule'})));
    }
    for (const q of p.paras) inner.append(h('p', {class: q.cont ? 'cont' : ''}, q.tag ? h('span', {class: 'tag'}, q.tag) : null, hanSpans(q.text, q.py)));
    const size = p.size || '';
    const text = h('article', {class: `text ${size}`, tabindex: '-1', 'aria-label': `第 ${p.i} 页的文字`}, inner);
    text.addEventListener('scroll', () => fadeCue(text), {passive: true});
    return h('section', {class: 'spread', 'aria-label': `第 ${p.i} 页`}, pic, text);
  };

  const coverView = () => {
    const resume = saved.page && saved.page > 1 && saved.page <= N ? saved.page : 0;
    const lines = (BOOK.tagline.match(/[^。，]+[。，]?/g) || [BOOK.tagline]);
    const src = imgSrc(BOOK.cover.img);
    return h('section', {class: 'cover', 'aria-label': '封面'},
      h('img', {class: 'bg', src, alt: '', 'aria-hidden': 'true'}),
      h('div', {class: 'art'}, h('img', {src, alt: BOOK.cover.alt})),
      h('div', {class: 'in'},
        h('p', {class: 'sub'}, lines.map((l) => h('span', {class: 'ln'}, l))),
        h('div', {class: 'row'},
          h('button', {class: 'btn primary', onclick: () => go(1)}, '开始阅读'),
          resume ? h('button', {class: 'btn', onclick: () => go(resume)}, `继续（第 ${resume} 页）`) : null,
          h('button', {class: 'btn', onclick: () => openDrawer(true)}, '目录'),
          h('button', {class: 'btn', onclick: () => openSb(true)}, '分镜')),
        h('p', {class: 'meta'}, `共 ${N} 页`, h('span', {class: 'kb'}, '  ·  用 ← → 翻页'))));
  };
  const endView = () => h('section', {class: 'endpage', 'aria-label': '全书完'},
    h('img', {class: 'bg', src: imgSrc(BOOK.end.img), alt: '', 'aria-hidden': 'true'}),
    h('div', {class: 'in'},
      h('h2', {}, '全书完'),
      h('div', {class: 'row'},
        h('button', {class: 'btn primary', onclick: () => go(1)}, '再读一遍'),
        h('button', {class: 'btn', onclick: () => go(0)}, '回到封面'),
        h('button', {class: 'btn', onclick: () => openSb(true)}, '分镜')),
      h('p', {class: 'credit'}, '正文是《小石猴点灯》加长版原文，一字未改（引号只是排版）。插图与动画：水墨水彩风格。字体：霞鹜文楷（LXGW WenKai，SIL OFL 1.1）。'),
      h('p', {class: 'credit'}, `把影片（${[].concat(BOOK.filmFile).join(' 或 ')}）放在本网页旁边，点右上角“看影片”就能播放。`)));

  /* ── 文字放不下时，底部渐隐，提示还能往下滑 ── */
  const fadeCue = (t) => t.classList.toggle('more', t.scrollHeight - t.clientHeight - t.scrollTop > 8);
  const fadeAll = () => { const t = stage.querySelector('.text'); if (t) fadeCue(t); };
  window.addEventListener('resize', fadeAll);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fadeAll);

  /* ── 翻页 ── */
  let lastPos = -1, lastHero = '';
  const heroKey = (p) => `${p.hero.img}|${p.hero.fx ?? ''}|${p.hero.fy ?? ''}|${p.hero.z ?? 1}`;
  function render(dir) {
    const pos = state.pos;
    const calm = dir && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    const cur = stage.firstElementChild;
    if (pos >= 1 && pos <= N && cur && cur.classList.contains('spread') && heroKey(BOOK.pages[pos - 1]) === lastHero) {
      // 相邻几页共用一幅图：图不动，只换文字（像“同一幅图，故事往下接着讲”）
      const nv = pageView(BOOK.pages[pos - 1]);
      const nt = nv.querySelector('.text');
      if (calm) nt.classList.add(dir > 0 ? 't-next' : 't-prev');
      cur.replaceChild(nt, cur.querySelector('.text'));
      cur.setAttribute('aria-label', nv.getAttribute('aria-label'));
      cur.classList.remove('in-next', 'in-prev');
    } else {
      const el = pos === 0 ? coverView() : pos === END ? endView() : pageView(BOOK.pages[pos - 1]);
      if (calm) el.classList.add(dir > 0 ? 'in-next' : 'in-prev');
      stage.replaceChildren(el);
    }
    lastHero = pos >= 1 && pos <= N ? heroKey(BOOK.pages[pos - 1]) : '';
    requestAnimationFrame(fadeAll);
    if (pos >= 0 && pos <= N) warm(pos);
    app.dataset.pos = pos === 0 ? 'cover' : pos === END ? 'end' : 'page';
    prevBtn.disabled = pos === 0;
    nextBtn.disabled = pos === END;
    slider.value = pos;
    slider.style.setProperty('--p', `${(pos / END) * 100}%`);
    const sec = pos >= 1 && pos <= N ? secOf(pos) : null;
    const name = pos === 0 ? '封面' : pos === END ? '全书完' : secLabel(sec);
    chapname.textContent = pos === 0 ? '' : name;
    labL.textContent = name;
    labR.textContent = pos >= 1 && pos <= N ? `${pos} / ${N}` : '';
    document.title = pos === 0 || pos === END ? `${BOOK.title} · 绘本` : `${secLabel(sec)} · ${BOOK.title}`;
    stopSpeech();
    pyHide(); pyAudio.stop(); pyPreload();
    syncToc();
    if (pos >= 1 && pos <= N) store.set({page: pos});
    try { history.replaceState(null, '', pos === 0 ? '#cover' : pos === END ? '#end' : `#p${pos}`); } catch (e) { /* file:// 下有的浏览器不让改 */ }
    lastPos = pos;
  }
  function go(pos, dir) {
    pos = clamp(Math.round(pos), 0, END);
    if (pos === state.pos && lastPos !== -1) return;
    const d = dir ?? Math.sign(pos - state.pos);
    state.pos = pos;
    closeAll();
    render(d);
  }
  const step = (d) => go(state.pos + d, d);

  /* ── 目录 ── */
  const scrim = h('div', {class: 'scrim', onclick: () => closeAll()});
  const tocList = h('nav', {class: 'toc', 'aria-label': '目录'});
  const drawer = h('aside', {class: 'drawer', 'aria-label': '目录', role: 'dialog', 'aria-modal': 'true'},
    h('header', {}, h('h2', {}, '目录'), h('button', {class: 'x', 'aria-label': '关闭', onclick: () => closeAll()}, '×')), tocList);
  const tocBtns = [];
  const addToc = (label, name, pg, pos) => {
    const b = h('button', {onclick: () => go(pos), 'data-pos': pos}, h('span', {class: 'no'}, label), h('span', {}, name), h('span', {class: 'pg'}, pg));
    tocBtns.push([b, pos]);
    tocList.append(b);
  };
  addToc('封面', '小石猴点灯', '', 0);
  tocList.append(h('div', {class: 'sp'}));
  BOOK.sections.forEach((s, i) => {
    const ps = secPages[i];
    addToc(s.no, s.name, ps.length > 1 ? `${ps[0]}–${ps[ps.length - 1]} 页` : `${ps[0]} 页`, ps[0]);
  });
  tocList.append(h('div', {class: 'sp'}));
  addToc('', '全书完', '', END);
  function syncToc() {
    let cur = null;
    for (const [b, pos] of tocBtns) {
      let on = false;
      if (pos === 0) on = state.pos === 0;
      else if (pos === END) on = state.pos === END;
      else on = state.pos >= 1 && state.pos <= N && secOf(state.pos) === secOf(pos);
      if (on) { b.setAttribute('aria-current', 'true'); cur = b; } else b.removeAttribute('aria-current');
    }
    return cur;
  }
  function openDrawer(on) {
    closeAll(true);
    drawer.classList.toggle('on', on); scrim.classList.toggle('on', on);
    if (on) { const c = syncToc(); if (c) c.scrollIntoView({block: 'center'}); $('.x', drawer).focus(); }
  }

  /* ── 分镜总览（每页一张缩略图，按章分组）+ 放映 ── */
  const sbBody = h('div', {class: 'body sb'});
  const sbModal = h('div', {class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': '分镜总览'},
    h('header', {}, h('h2', {}, '分镜总览'),
      h('button', {class: 'btn', style: 'padding:.4em 1.1em;font-size:.98rem;background:var(--btn-hi);color:var(--ink);border-color:var(--accent)', onclick: () => startShow(0)}, '▶ 放映'),
      h('button', {class: 'x', 'aria-label': '关闭', onclick: () => closeAll()}, '×')), sbBody);
  let sbBuilt = false;
  const snippet = (p) => { const t = p.paras.map((q) => q.text).join('').replace(/[“”‘’]/g, ''); return t.length > 30 ? t.slice(0, 30) + '…' : t; };
  function buildSb() {
    if (sbBuilt) return; sbBuilt = true;
    sbBody.append(h('p', {class: 'hint'}, `全书 ${N} 页的画面，按章排列。点一张，翻到那一页；右上角“放映”可以全屏一张张看图。`));
    BOOK.sections.forEach((s, si) => {
      const grid = h('div', {class: 'grid'});
      secPages[si].forEach((pi) => {
        const p = BOOK.pages[pi - 1];
        grid.append(h('button', {class: 'card', 'data-page': pi, onclick: () => go(pi)},
          h('div', {class: 'thumb'}, imgEl(p.hero, {lazy: true, noalt: true})), h('div', {class: 't'}, snippet(p)), h('div', {class: 'm'}, h('span', {}, `第 ${pi} 页`), h('span', {}, p.startsSec ? '章首' : ''))));
      });
      sbBody.append(h('h3', {}, h('span', {}, s.no), s.name), grid);
    });
  }
  function openSb(on) {
    closeAll(true);
    if (on) buildSb();
    sbModal.classList.toggle('on', on); scrim.classList.toggle('on', on);
    if (on) {
      $$('.card', sbBody).forEach((c) => c.removeAttribute('aria-current'));
      const cur = state.pos >= 1 && state.pos <= N ? $(`.card[data-page="${state.pos}"]`, sbBody) : null;
      if (cur) { cur.setAttribute('aria-current', 'true'); cur.scrollIntoView({block: 'center'}); }
      $('.x', sbModal).focus();
    }
  }

  // 放映：相邻页共用的图只放一次；每张图配本章名 + 图下小字
  const showSeq = [];
  BOOK.pages.forEach((p) => {
    const last = showSeq[showSeq.length - 1];
    if (!last || last.key !== p.hero.img) showSeq.push({key: p.hero.img, text: p.hero.cap || '', scene: secLabel(p.sec), page: p.i});
  });
  let showI = 0, showTimer = null;
  const showImg = h('img', {alt: ''}), showSub = h('div', {class: 'sub'}), showInfo = h('span');
  const showPlay = h('button', {class: 'btn', style: 'padding:.35em 1em;font-size:.95rem', onclick: () => toggleAuto()}, '自动播放');
  const showEl = h('div', {class: 'show', role: 'dialog', 'aria-modal': 'true', 'aria-label': '放映模式'},
    showImg, showSub,
    h('div', {class: 'top'}, showInfo, h('div', {class: 'row'}, showPlay, h('button', {class: 'btn', style: 'padding:.35em 1em;font-size:.95rem', onclick: () => { const p = showSeq[showI].page; closeAll(); go(p); }}, '读这一页'), h('button', {class: 'x', 'aria-label': '退出放映', onclick: () => closeAll()}, '×'))),
    h('button', {class: 'arrow l', 'aria-label': '上一张', onclick: () => showGo(showI - 1), html: ic.prev}),
    h('button', {class: 'arrow r', 'aria-label': '下一张', onclick: () => showGo(showI + 1), html: ic.next}));
  function showGo(i) {
    showI = clamp(i, 0, showSeq.length - 1);
    const s = showSeq[showI];
    showImg.src = imgSrc(s.key);
    showSub.textContent = s.text;
    showSub.hidden = !s.text;
    showInfo.textContent = `${showI + 1} / ${showSeq.length}　${s.scene}`;
  }
  function toggleAuto(force) {
    const on = force ?? !showTimer;
    clearInterval(showTimer); showTimer = null;
    if (on) showTimer = setInterval(() => { if (showI >= showSeq.length - 1) toggleAuto(false); else showGo(showI + 1); }, 5200);
    showPlay.textContent = showTimer ? '暂停' : '自动播放';
  }
  function startShow(i) {
    closeAll(true);
    showEl.classList.add('on'); showGo(i);
    if (showEl.requestFullscreen && !document.fullscreenElement) showEl.requestFullscreen().then(() => { showFs = true; }).catch(() => {});
  }
  let showFs = false;
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && showFs) { showFs = false; if (showEl.classList.contains('on')) closeAll(); } });

  /* ── 看影片：影片放在本网页旁边就能播，没有就给出友好提示 ── */
  const vidBox = h('div', {class: 'vid'});
  const vidModal = h('div', {class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': '看影片', style: 'max-width:1100px;margin:auto'},
    h('header', {}, h('h2', {}, '看影片'), h('button', {class: 'x', 'aria-label': '关闭', onclick: () => closeAll()}, '×')), vidBox);
  function openFilm() {
    closeAll(true);
    vidBox.replaceChildren();
    const files = [].concat(BOOK.filmFile);
    const v = h('video', {controls: true, playsinline: true, preload: 'metadata'});
    files.forEach((f, i) => {
      const src = h('source', {src: f, type: 'video/mp4'});
      if (i === files.length - 1) src.addEventListener('error', () => vidBox.replaceChildren(h('div', {class: 'msg'}, `没有找到影片文件（${files.join(' 或 ')}）。请把影片放在与本网页相同的文件夹里，再用 Chrome、Safari 或 Edge 打开本页；不看影片也不影响读书。`)), {once: true});
      v.append(src);
    });
    vidBox.append(v);
    vidModal.classList.add('on'); scrim.classList.add('on');
    $('.x', vidModal).focus();
  }

  /* ── 设置 ── */
  const FS = [[0.88, '小'], [1, '中'], [1.2, '大'], [1.45, '特大']];
  const seg = (items, cur, onpick) => {
    const box = h('div', {class: 'seg'});
    items.forEach(([v, t]) => box.append(h('button', {'aria-pressed': String(cur === v), onclick: () => { onpick(v); [...box.children].forEach((b, i) => b.setAttribute('aria-pressed', String(items[i][0] === v))); }}, t)));
    return box;
  };
  const speakBtn = h('button', {class: 'ibtn', onclick: () => toggleSpeech()}, '朗读本页');
  const fsBtn = h('button', {class: 'ibtn', onclick: () => { if (document.fullscreenElement) document.exitFullscreen(); else root.requestFullscreen && root.requestFullscreen().catch(() => {}); }}, '全屏');
  const pop = h('div', {class: 'pop', role: 'dialog', 'aria-label': '设置'},
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '字号'), seg(FS, state.fs, (v) => applyPrefs({fs: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '背景'), seg([['night', '夜色'], ['paper', '纸色']], state.theme, (v) => applyPrefs({theme: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '小标签', h('small', {}, '段落前的小字（春游、工坊……）')), seg([[true, '开'], [false, '关']], state.tags, (v) => applyPrefs({tags: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '点字看拼音、听发音', h('small', {}, '鼠标放在字上看拼音，点一下听真人发音（触屏：轻点）')), seg([[true, '开'], [false, '关']], state.py, (v) => applyPrefs({py: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '悬停即发声', h('small', {}, '不用点击，鼠标停在字上就念（要先点一下页面）')), seg([[true, '开'], [false, '关']], state.pyAuto, (v) => applyPrefs({pyAuto: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '发音致谢', h('small', {html: '真人录音：<a href="https://github.com/hugolpz/audio-cmn" target="_blank" rel="noopener">Chen Wang 王琛（audio-cmn）</a>，<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener">CC-BY-SA 3.0</a>；已裁剪静音并转码，轻声为模拟。仅供识字参考，不是教材认证录音。'}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '更多'), h('div', {class: 'row', style: 'gap:6px;flex-wrap:wrap;justify-content:flex-end'}, speakBtn, fsBtn)));
  function applyPrefs(o) {
    Object.assign(state, o);
    root.style.setProperty('--fs', state.fs);
    root.dataset.theme = state.theme;
    root.dataset.tags = state.tags ? 'on' : 'off';
    root.dataset.py = state.py ? 'on' : 'off';
    if (!state.py) { pyHide(); pyAudio.stop(); }
    store.set({fs: state.fs, theme: state.theme, tags: state.tags, py: state.py, pyAuto: state.pyAuto});
    requestAnimationFrame(fadeAll);
  }
  function togglePop(force) {
    const on = force ?? !pop.classList.contains('on');
    pop.classList.toggle('on', on);
    btnSet.setAttribute('aria-pressed', String(on));
  }

  /* ── 朗读本页（浏览器自带的 speechSynthesis，zh-CN；没有中文声音时提示，不报错） ── */
  const canSpeak = 'speechSynthesis' in window;
  if (!canSpeak) speakBtn.hidden = true;
  function pageText() {
    if (state.pos < 1 || state.pos > N) return BOOK.title;
    const p = BOOK.pages[state.pos - 1];
    const head = p.startsSec ? `${BOOK.sections[p.sec].no}，${BOOK.sections[p.sec].name}。\n` : '';
    return head + p.paras.map((q) => q.text).join('\n').replace(/[“”‘’]/g, '').replace(/[…—]+/g, '，');
  }
  function stopSpeech() { if (canSpeak) { speechSynthesis.cancel(); speakBtn.textContent = '朗读本页'; } }
  function toggleSpeech() {
    if (!canSpeak) return;
    if (speechSynthesis.speaking) { stopSpeech(); return; }
    const u = new SpeechSynthesisUtterance(pageText());
    u.lang = 'zh-CN'; u.rate = 0.9;
    const vs = speechSynthesis.getVoices();
    const v = vs.find((x) => /^zh/i.test(x.lang));
    if (v) u.voice = v; else if (vs.length) { toast('这台设备没有中文朗读声音'); return; }
    u.onend = u.onerror = () => { speakBtn.textContent = '朗读本页'; };
    speakBtn.textContent = '停止朗读';
    pyAudio.stop();
    speechSynthesis.speak(u);
    togglePop(false);
  }

  /*@@include app_pinyin.js@@*/

  /* ── 关掉所有弹层 ── */
  function closeAll(keepScrim) {
    drawer.classList.remove('on'); sbModal.classList.remove('on'); vidModal.classList.remove('on');
    if (showEl.classList.contains('on')) { showEl.classList.remove('on'); toggleAuto(false); if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); }
    const v = $('video', vidModal); if (v) v.pause();
    if (!keepScrim) scrim.classList.remove('on');
    togglePop(false);
  }
  const anyOpen = () => drawer.classList.contains('on') || sbModal.classList.contains('on') || vidModal.classList.contains('on') || showEl.classList.contains('on') || pop.classList.contains('on');
  const toastEl = h('div', {class: 'toast', role: 'status'});
  let toastT;
  function toast(msg) { toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 2600); }
  document.body.append(scrim, drawer, sbModal, vidModal, showEl, pop, toastEl, pyb);

  /* ── 键盘 / 手势 ── */
  document.addEventListener('keydown', (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === 'Escape') { if (anyOpen()) { closeAll(); e.preventDefault(); } return; }
    if (showEl.classList.contains('on')) {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { showGo(showI + 1); e.preventDefault(); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { showGo(showI - 1); e.preventDefault(); }
      return;
    }
    if (anyOpen() && !pop.classList.contains('on')) return;
    if (e.target === slider || e.target.tagName === 'INPUT' || e.target.tagName === 'VIDEO') return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || (e.key === ' ' && e.target.tagName !== 'BUTTON')) { step(1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { step(-1); e.preventDefault(); }
    else if (e.key === 'Home') { go(0); e.preventDefault(); }
    else if (e.key === 'End') { go(END); e.preventDefault(); }
    else if (e.key === 't' || e.key === 'T') openDrawer(true);
    else if (e.key === 's' || e.key === 'S') openSb(true);
  });
  let sx = 0, sy = 0, st = 0;
  stage.addEventListener('pointerdown', (e) => { if (e.pointerType === 'mouse') return; sx = e.clientX; sy = e.clientY; st = Date.now(); });
  stage.addEventListener('pointerup', (e) => {
    if (e.pointerType === 'mouse' || !st) return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (Date.now() - st < 700 && Math.abs(dx) > 70 && Math.abs(dx) > 1.6 * Math.abs(dy)) step(dx < 0 ? 1 : -1);
    st = 0;
  });
  let raf = 0;
  slider.addEventListener('input', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => go(+slider.value)); });
  window.addEventListener('hashchange', () => { const m = /^#p(\d+)$/.exec(location.hash); const pos = m ? +m[1] : location.hash === '#end' ? END : location.hash === '#cover' ? 0 : null; if (pos != null && pos !== state.pos) go(pos); });
  document.addEventListener('click', (e) => { if (pop.classList.contains('on') && !pop.contains(e.target) && !btnSet.contains(e.target)) togglePop(false); });

  /* ── 开始 ── */
  applyPrefs({});
  const m = /^#p(\d+)$/.exec(location.hash);
  state.pos = m ? clamp(+m[1], 1, N) : location.hash === '#end' ? END : 0;
  render(0);
  window.__book = {go, state, N, END, openSb, openDrawer, openFilm, startShow, data: BOOK};
})();
