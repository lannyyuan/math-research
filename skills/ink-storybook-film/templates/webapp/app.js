/* 《雪地里的那盏灯》绘本网页：封面 → 66 页（一页一张插图 + 一段原文）→ 结尾；目录、分镜总览、放映、设置、朗读。
   所有数据都内联在同一个 HTML 里（#book-data 是页面与文字，window.__IMG 是 WebP 插图）。没有任何外部依赖。 */
(() => {
  'use strict';
  const BOOK = JSON.parse(document.getElementById('book-data').textContent);
  const IMG = window.__IMG;
  const N = BOOK.pages.length;
  const END = N + 1; // 0 封面，1..N 正文，N+1 结尾
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
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
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>',
    lamp: '<svg viewBox="0 0 32 32" width="26" height="26"><circle cx="16" cy="15" r="13" fill="#ffcb62" opacity=".22"/><circle cx="16" cy="15" r="7" fill="#ffcb62" opacity=".45"/><circle cx="16" cy="15" r="3.6" fill="#fff0b8"/><path d="M16 4v-2M16 28v2M5 15H3M29 15h-2" stroke="#ffe6a0" stroke-width="1.4" stroke-linecap="round" opacity=".7"/></svg>',
  };

  /* ── 状态与存档 ── */
  const store = {
    get() { try { return JSON.parse(localStorage.getItem('snowlamp.v1') || '{}'); } catch (e) { return {}; } },
    set(o) { try { localStorage.setItem('snowlamp.v1', JSON.stringify({...store.get(), ...o})); } catch (e) { /* 隐私模式等：不存也能读 */ } },
  };
  const saved = store.get();
  const prefersLight = matchMedia('(prefers-color-scheme: light)').matches;
  const state = {
    pos: 0,
    fs: typeof saved.fs === 'number' ? saved.fs : 1,
    theme: saved.theme || (prefersLight ? 'paper' : 'night'),
    marks: saved.marks !== false,
  };
  const cueByNo = Object.fromEntries(BOOK.cues.map((c) => [c.no, c]));
  const sceneName = Object.fromEntries(BOOK.scenes.map((s) => [s.id, s.name]));
  const secOf = (i) => BOOK.pages[i - 1].sec;
  const secPages = BOOK.sections.map(() => []);
  BOOK.pages.forEach((p) => secPages[p.sec].push(p.i));
  const secLabel = (s) => `${BOOK.sections[s].no} ${BOOK.sections[s].name}`;
  const secTitle = (s) => `${BOOK.sections[s].no}　${BOOK.sections[s].name}`;
  const secCueCount = (s) => secPages[s].reduce((a, i) => a + BOOK.pages[i - 1].cues.length, 0);

  /* ── 骨架 ── */
  const app = $('#app');
  const brand = h('button', {class: 'brand', 'aria-label': '回到封面', onclick: () => go(0)}, h('span', {html: ic.lamp}), h('span', {class: 't'}, BOOK.title));
  const chapname = h('span', {class: 'chapname'});
  const btnToc = h('button', {class: 'ibtn', 'aria-label': '目录', onclick: () => openDrawer(true)}, h('span', {html: ic.menu}), h('span', {class: 't'}, '目录'));
  const btnSb = h('button', {class: 'ibtn', 'aria-label': '分镜总览', onclick: () => openSb(true)}, h('span', {html: ic.grid}), h('span', {class: 't'}, '分镜'));
  const btnSet = h('button', {class: 'ibtn', 'aria-label': '设置', 'aria-pressed': 'false', onclick: () => togglePop()}, h('span', {html: ic.gear}), h('span', {class: 't'}, '设置'));
  const bar = h('header', {class: 'bar'}, brand, chapname, btnToc, btnSb, btnSet);
  const stage = h('main', {class: 'stage', id: 'stage'});
  const prevBtn = h('button', {class: 'rbtn', 'aria-label': '上一页', html: ic.prev, onclick: () => step(-1)});
  const nextBtn = h('button', {class: 'rbtn', 'aria-label': '下一页', html: ic.next, onclick: () => step(1)});
  const labL = h('span'), labR = h('span');
  const slider = h('input', {type: 'range', min: 0, max: END, step: 1, value: 0, 'aria-label': '翻到第几页'});
  const ticks = h('div', {class: 'ticks'});
  BOOK.sections.forEach((s, i) => {
    const first = secPages[i][0];
    ticks.append(h('i', {class: secCueCount(i) ? 'film' : '', style: `left:${(first / END) * 100}%`}));
  });
  const nav = h('footer', {class: 'nav'}, prevBtn, h('div', {class: 'prog'}, h('div', {class: 'lab'}, labL, labR), h('div', {class: 'sl'}, slider, ticks)), nextBtn);
  app.append(bar, stage, nav);

  /* ── 页面 ── */
  const imgEl = (hero) => {
    const z = hero.z || 1;
    const fx = hero.fx ?? 0.5, fy = hero.fy ?? 0.55;
    const el = h('img', {src: IMG[hero.img], alt: hero.alt || '', draggable: 'false', decoding: 'async'});
    if (z > 1) {
      const tx = clamp(0.5 - z * fx, 1 - z, 0), ty = clamp(0.5 - z * fy, 1 - z, 0);
      el.style.transformOrigin = '0 0';
      el.style.transform = `translate(${tx * 100}%,${ty * 100}%) scale(${z})`;
    }
    return el;
  };
  const filmBtn = (no, label = '看影片里的这一幕') => h('button', {class: 'filmbtn', onclick: () => openFilm(no), 'aria-label': `${label}（分镜 ${no}）`}, h('span', {html: ic.play}), label);

  const pageView = (p) => {
    const cue = p.cues.length ? cueByNo[p.cues[0]] : null;
    const pic = h('figure', {class: 'pic'}, h('div', {class: 'frame'}, imgEl(p.hero)), h('figcaption', {}, h('span', {class: 'cap'}, p.hero.cap || ''), cue ? filmBtn(cue.no) : null));
    const inner = h('div', {class: 'inner'});
    if (p.startsSec) {
      const s = BOOK.sections[p.sec];
      inner.append(h('div', {class: 'chap'}, h('span', {class: 'no'}, s.no), h('h2', {}, s.name), h('i', {class: 'rule'})));
    }
    for (const q of p.paras) {
      if (q.k === 'p') {
        inner.append(h('p', {class: q.cont ? 'cont' : ''}, q.segs.map(([t, no]) => (no ? h('mark', {class: 'film', 'data-cue': no, title: '影片里的字幕：点一下，看这一幕', onclick: () => state.marks && openFilm(no)}, t) : t))));
      } else {
        inner.append(h('div', {class: q.k === 'poem' ? 'poem' : 'qlist'}, q.lines.map((l) => h('div', {}, l))));
      }
    }
    const size = p.han < 45 ? 'xs' : p.han < 110 ? 's' : '';
    const text = h('article', {class: `text ${size}`, tabindex: '-1', 'aria-label': `第 ${p.i} 页的文字`}, inner);
    text.addEventListener('scroll', () => fadeCue(text), {passive: true});
    return h('section', {class: 'spread', 'aria-label': `第 ${p.i} 页`}, pic, text);
  };

  const coverView = () => {
    const resume = saved.page && saved.page > 1 && saved.page <= N ? saved.page : 0;
    return h('section', {class: 'cover', 'aria-label': '封面'},
      h('img', {class: 'bg', src: IMG[BOOK.cover.img], alt: BOOK.cover.alt, style: 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover'}),
      h('div', {class: 'in'},
        h('h1', {}, BOOK.title),
        h('p', {class: 'sub'}, h('span', {class: 'glow'}), '一本读给 6~8 岁孩子的识字绘本'),
        h('div', {class: 'row'},
          h('button', {class: 'btn primary', onclick: () => go(1)}, '开始阅读'),
          resume ? h('button', {class: 'btn', onclick: () => go(resume)}, `接着读（第 ${resume} 页）`) : null,
          h('button', {class: 'btn', onclick: () => openDrawer(true)}, '目录'),
          h('button', {class: 'btn', onclick: () => openSb(true)}, '分镜总览')),
        h('p', {class: 'meta'}, `全文 ${N} 页　·　影片画面 ${BOOK.cues.length} 个　·　字体：霞鹜文楷（开源）`, h('span', {class: 'kb'}, '　·　← → 翻页'))));
  };
  const endView = () => h('section', {class: 'endpage', 'aria-label': '结尾'},
    h('img', {class: 'bg', src: IMG[BOOK.end.img], alt: BOOK.end.alt, style: 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:blur(4px) saturate(.9)'}),
    h('div', {class: 'in'},
      h('h2', {}, '完'),
      h('div', {class: 'row'},
        h('button', {class: 'btn primary', onclick: () => go(1)}, '再读一遍'),
        h('button', {class: 'btn', onclick: () => go(0)}, '回到封面'),
        h('button', {class: 'btn', onclick: () => openSb(true)}, '分镜总览')),
      h('p', {class: 'credit'}, '全文取自故事原文，一字未改（引号只做排版）。插图与动画：自制的水彩手绘风（Remotion）。字体：霞鹜文楷（SIL OFL 1.1）。配乐：自制。'),
      h('p', {class: 'credit'}, '把影片 snow-lamp.mp4 放在这个网页文件旁边，每页的“看影片里的这一幕”就能直接播放。')));

  /* ── 文字区放不下时，底部渐隐提示“还可以往下滑” ── */
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
    let el;
    const cur = stage.firstElementChild;
    if (pos >= 1 && pos <= N && cur && cur.classList.contains('spread') && heroKey(BOOK.pages[pos - 1]) === lastHero) {
      // 相邻两页共用一张插图：画面不动，只翻文字
      const nv = pageView(BOOK.pages[pos - 1]);
      const nt = nv.querySelector('.text');
      if (calm) nt.classList.add(dir > 0 ? 't-next' : 't-prev');
      cur.replaceChild(nt, cur.querySelector('.text'));
      cur.setAttribute('aria-label', nv.getAttribute('aria-label'));
      cur.classList.remove('in-next', 'in-prev');
    } else {
      if (pos === 0) el = coverView();
      else if (pos === END) el = endView();
      else el = pageView(BOOK.pages[pos - 1]);
      if (calm) el.classList.add(dir > 0 ? 'in-next' : 'in-prev');
      stage.replaceChildren(el);
    }
    lastHero = pos >= 1 && pos <= N ? heroKey(BOOK.pages[pos - 1]) : '';
    requestAnimationFrame(fadeAll);
    prevBtn.disabled = pos === 0;
    nextBtn.disabled = pos === END;
    slider.value = pos;
    slider.style.setProperty('--p', `${(pos / END) * 100}%`);
    const sec = pos >= 1 && pos <= N ? secOf(pos) : null;
    const name = pos === 0 ? '封面' : pos === END ? '结尾' : secLabel(sec);
    chapname.textContent = pos === 0 ? '' : name;
    labL.textContent = name;
    labR.textContent = pos >= 1 && pos <= N ? `${pos} / ${N}` : '';
    document.title = pos === 0 || pos === END ? BOOK.title : `${secTitle(sec)} · ${BOOK.title}`;
    stopSpeech();
    syncToc();
    if (pos >= 1 && pos <= N) store.set({page: pos});
    try { history.replaceState(null, '', pos === 0 ? '#cover' : pos === END ? '#end' : `#p${pos}`); } catch (e) { /* file:// 下个别浏览器不允许 */ }
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
  const addToc = (label, name, pg, pos, extra) => {
    const b = h('button', {onclick: () => go(pos), 'data-pos': pos}, h('span', {class: 'no'}, label), h('span', {}, name, extra ? h('span', {class: 'fm'}, extra) : null), h('span', {class: 'pg'}, pg));
    tocBtns.push([b, pos]);
    tocList.append(b);
  };
  addToc('封面', BOOK.title, '', 0);
  tocList.append(h('div', {class: 'sp'}));
  BOOK.sections.forEach((s, i) => {
    const ps = secPages[i];
    const n = secCueCount(i);
    addToc(s.no, s.name, ps.length > 1 ? `${ps[0]}–${ps[ps.length - 1]} 页` : `${ps[0]} 页`, ps[0], n ? `影片 ${n} 幕` : '');
  });
  tocList.append(h('div', {class: 'sp'}));
  addToc('结尾', '完', '', END);
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

  /* ── 分镜总览 + 放映 ── */
  const sbBody = h('div', {class: 'body sb'});
  const sbModal = h('div', {class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': '分镜总览'},
    h('header', {}, h('h2', {}, '分镜总览'), h('button', {class: 'btn', style: 'padding:.45em 1.1em;font-size:.95rem;background:var(--accent-soft);color:var(--ink);border-color:var(--accent)', onclick: () => startShow(0)}, '▶ 放映'), h('button', {class: 'x', 'aria-label': '关闭', onclick: () => closeAll()}, '×')), sbBody);
  let sbBuilt = false;
  function buildSb() {
    if (sbBuilt) return; sbBuilt = true;
    sbBody.append(h('p', {class: 'hint'}, `这就是影片里所有带字幕的画面（共 ${BOOK.cues.length + 1} 张，按影片顺序）。点一张，翻到绘本里对应的那一页。`));
    const card = (key, text, meta, page) => h('button', {class: 'card', onclick: () => go(page)}, h('img', {src: IMG[key], alt: '', loading: 'lazy'}), h('div', {class: 't'}, text.replace(/\n/g, '')), h('div', {class: 'm'}, h('span', {}, meta), h('span', {}, page ? `第 ${page} 页` : '封面')));
    BOOK.scenes.forEach((sc, si) => {
      const grid = h('div', {class: 'grid'});
      if (sc.id === 's0-title') grid.append(card('cue/00', BOOK.title, `片头　${BOOK.titleCard.sec ? '0:0' + BOOK.titleCard.sec : '0:02'}`, 0));
      sc.cues.forEach((no) => { const c = cueByNo[no]; grid.append(card(`cue/${String(no).padStart(2, '0')}`, c.text, `分镜 ${no}　${c.tc}`, c.page)); });
      sbBody.append(h('h3', {}, h('span', {}, si === 0 ? '片头' : `场景 ${si}`), sc.id === 's0-title' ? '' : sc.name), grid);
    });
  }
  function openSb(on) {
    closeAll(true);
    if (on) buildSb();
    sbModal.classList.toggle('on', on); scrim.classList.toggle('on', on);
    if (on) $('.x', sbModal).focus();
  }
  const showSeq = [{key: 'cue/00', text: BOOK.title, scene: '片头', tc: '0:02', page: 0}].concat(BOOK.cues.map((c) => ({key: `cue/${String(c.no).padStart(2, '0')}`, text: c.text, scene: sceneName[c.scene], tc: c.tc, page: c.page, no: c.no})));
  let showI = 0, showTimer = null;
  const showImg = h('img', {alt: ''}), showSub = h('div', {class: 'sub'}), showInfo = h('span');
  const showPlay = h('button', {class: 'btn', style: 'padding:.35em 1em;font-size:.9rem', onclick: () => toggleAuto()}, '自动播放');
  const showEl = h('div', {class: 'show', role: 'dialog', 'aria-modal': 'true', 'aria-label': '分镜放映'},
    showImg, showSub,
    h('div', {class: 'top'}, showInfo, h('div', {class: 'row'}, showPlay, h('button', {class: 'btn', style: 'padding:.35em 1em;font-size:.9rem', onclick: () => { const p = showSeq[showI].page; closeAll(); go(p); }}, '到绘本里读这一页'), h('button', {class: 'x', 'aria-label': '退出放映', onclick: () => closeAll()}, '×'))),
    h('button', {class: 'arrow l', 'aria-label': '上一张', onclick: () => showGo(showI - 1), html: ic.prev}),
    h('button', {class: 'arrow r', 'aria-label': '下一张', onclick: () => showGo(showI + 1), html: ic.next}));
  function showGo(i) {
    showI = clamp(i, 0, showSeq.length - 1);
    const s = showSeq[showI];
    showImg.src = IMG[s.key];
    showSub.textContent = s.text;
    showInfo.textContent = `${showI + 1} / ${showSeq.length}　${s.scene}　${s.tc}`;
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

  /* ── 看影片里的这一幕 ── */
  const vidBox = h('div', {class: 'vid'});
  const vidTitle = h('h2', {}, '影片里的这一幕');
  const vidModal = h('div', {class: 'modal', role: 'dialog', 'aria-modal': 'true', 'aria-label': '看影片里的这一幕', style: 'max-width:1100px;margin:auto'},
    h('header', {}, vidTitle, h('button', {class: 'x', 'aria-label': '关闭', onclick: () => closeAll()}, '×')), vidBox);
  function openFilm(no) {
    const c = cueByNo[no]; if (!c) return;
    closeAll(true);
    vidTitle.textContent = `分镜 ${no}　${c.text.replace(/\n/g, '')}`;
    vidBox.replaceChildren();
    const v = h('video', {controls: true, playsinline: true, preload: 'metadata', src: `${BOOK.filmFile}#t=${Math.max(0, c.sec - 1)}`});
    v.addEventListener('error', () => vidBox.replaceChildren(h('div', {class: 'msg'}, `没能播放影片 ${BOOK.filmFile}。请确认它和这个网页放在同一个文件夹里，并用 Chrome / Safari / Edge 打开（本幕在影片 ${c.tc} 处）。`)), {once: true});
    vidBox.append(v);
    vidModal.classList.add('on'); scrim.classList.add('on');
    $('.x', vidModal).focus();
  }

  /* ── 设置 ── */
  const FS = [[0.86, '小'], [1, '中'], [1.2, '大'], [1.45, '特大']];
  const seg = (items, cur, onpick) => {
    const box = h('div', {class: 'seg'});
    items.forEach(([v, t]) => box.append(h('button', {'aria-pressed': String(cur === v), onclick: () => { onpick(v); [...box.children].forEach((b, i) => b.setAttribute('aria-pressed', String(items[i][0] === v))); }}, t)));
    return box;
  };
  const speakBtn = h('button', {class: 'ibtn', onclick: () => toggleSpeech()}, '朗读本页');
  const fsBtn = h('button', {class: 'ibtn', onclick: () => { if (document.fullscreenElement) document.exitFullscreen(); else root.requestFullscreen && root.requestFullscreen().catch(() => {}); }}, '全屏');
  const pop = h('div', {class: 'pop', role: 'dialog', 'aria-label': '设置'},
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '字号'), seg(FS, state.fs, (v) => applyPrefs({fs: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '背景'), seg([['night', '雪夜'], ['paper', '纸色']], state.theme, (v) => applyPrefs({theme: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '影片字幕标记', h('small', {}, '文字里发金色底的句子，影片里也有')), seg([[true, '开'], [false, '关']], state.marks, (v) => applyPrefs({marks: v}))),
    h('div', {class: 'r'}, h('div', {class: 'lab'}, '其他'), h('div', {class: 'row', style: 'gap:6px'}, speakBtn, fsBtn)));
  function applyPrefs(o) {
    Object.assign(state, o);
    root.style.setProperty('--fs', state.fs);
    root.dataset.theme = state.theme;
    root.dataset.marks = state.marks ? 'on' : 'off';
    store.set({fs: state.fs, theme: state.theme, marks: state.marks});
    snow.recolor();
  }
  function togglePop(force) {
    const on = force ?? !pop.classList.contains('on');
    pop.classList.toggle('on', on);
    btnSet.setAttribute('aria-pressed', String(on));
  }

  /* ── 朗读（浏览器自带的朗读功能，没有中文声音就提示） ── */
  const canSpeak = 'speechSynthesis' in window;
  if (!canSpeak) speakBtn.hidden = true;
  function pageText() {
    if (state.pos < 1 || state.pos > N) return BOOK.title;
    return BOOK.pages[state.pos - 1].paras.map((q) => (q.k === 'p' ? q.segs.map((s) => s[0]).join('') : q.lines.join('，'))).join('\n').replace(/[“”‘’]/g, '').replace(/…+/g, '，');
  }
  function stopSpeech() { if (canSpeak) { speechSynthesis.cancel(); speakBtn.textContent = '朗读本页'; } }
  function toggleSpeech() {
    if (!canSpeak) return;
    if (speechSynthesis.speaking) { stopSpeech(); return; }
    const u = new SpeechSynthesisUtterance(pageText());
    u.lang = 'zh-CN'; u.rate = 0.82;
    const v = speechSynthesis.getVoices().find((x) => /^zh/i.test(x.lang));
    if (v) u.voice = v; else if (speechSynthesis.getVoices().length) { toast('这台设备没有中文朗读的声音'); return; }
    u.onend = u.onerror = () => { speakBtn.textContent = '朗读本页'; };
    speakBtn.textContent = '停止朗读';
    speechSynthesis.speak(u);
    togglePop(false);
  }

  /* ── 弹层统一关闭 ── */
  function closeAll(keepScrim) {
    drawer.classList.remove('on'); sbModal.classList.remove('on'); vidModal.classList.remove('on');
    if (showEl.classList.contains('on')) { showEl.classList.remove('on'); toggleAuto(false); if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); }
    const v = $('video', vidModal); if (v) { v.pause(); }
    if (!keepScrim) scrim.classList.remove('on');
    togglePop(false);
  }
  const anyOpen = () => drawer.classList.contains('on') || sbModal.classList.contains('on') || vidModal.classList.contains('on') || showEl.classList.contains('on') || pop.classList.contains('on');
  const toastEl = h('div', {class: 'toast', role: 'status'});
  let toastT;
  function toast(msg) { toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 2600); }
  document.body.append(scrim, drawer, sbModal, vidModal, showEl, pop, toastEl);

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
    if (e.target === slider || (e.target.tagName === 'INPUT') || (e.target.tagName === 'VIDEO')) return;
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

  /* ── 飘雪（背景）：全程在下雪，和影片一样；尊重“减少动态效果”设置 ── */
  const snow = (() => {
    const cv = $('#snow'), ctx = cv.getContext('2d');
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let W = 0, Hh = 0, dpr = 1, flakes = [], rgb = '236,242,255', last = 0;
    const mk = () => ({x: Math.random(), y: Math.random(), r: 0.8 + Math.random() * 2.6, v: 0.018 + Math.random() * 0.04, ph: Math.random() * 6.28, a: 0.25 + Math.random() * 0.5});
    function resize() { dpr = Math.min(2, window.devicePixelRatio || 1); W = cv.width = Math.round(innerWidth * dpr); Hh = cv.height = Math.round(innerHeight * dpr); }
    function recolor() { rgb = getComputedStyle(root).getPropertyValue('--snow').trim() || rgb; }
    function frame(t) {
      requestAnimationFrame(frame);
      if (document.hidden) return;
      const dt = Math.min(0.05, (t - last) / 1000 || 0.016); last = t;
      ctx.clearRect(0, 0, W, Hh);
      for (const f of flakes) {
        f.y += f.v * dt * 4; f.x += Math.sin(t / 1800 + f.ph) * 0.00018 + 0.00004;
        if (f.y > 1.02) { f.y = -0.02; f.x = Math.random(); }
        if (f.x > 1.02) f.x = -0.02;
        ctx.fillStyle = `rgba(${rgb},${f.a})`;
        ctx.beginPath(); ctx.arc(f.x * W, f.y * Hh, f.r * dpr, 0, 6.2832); ctx.fill();
      }
    }
    resize(); recolor();
    if (!reduce) {
      flakes = Array.from({length: 64}, mk);
      requestAnimationFrame(frame);
    }
    window.addEventListener('resize', resize);
    return {recolor};
  })();

  /* ── 开始 ── */
  applyPrefs({});
  const m = /^#p(\d+)$/.exec(location.hash);
  const start = m ? clamp(+m[1], 1, N) : location.hash === '#end' ? END : 0;
  state.pos = start;
  render(0);
  window.__book = {go, state, N, END, openSb, openDrawer, openFilm, startShow, data: BOOK};
})();
