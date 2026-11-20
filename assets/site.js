/* definitelyBenny: everything here is drawn from projects.json.
   Home renders the questions, the secret question, the coming-soon teasers and the apps on the bench.
   A tool page (body[data-tool]) renders that question's detail sheets.
   Shared toys: the chaos dial, the theme button, five taps on the logo, the "?" key. */
(() => {
  const root = document.documentElement;
  const body = document.body;
  const BASE = body.dataset.root || './';
  const TOOL = body.dataset.tool || null;
  const $ = s => document.querySelector(s);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }
  };
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const url = href => /^(https?:|#|\/)/.test(href) ? href : BASE + href;
  const arrow = '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M4 9h10M10 5l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const ext = href => /^https?:/.test(href) ? ' target="_blank" rel="noopener"' : '';

  /* ---------- shared toys ---------- */

  function burst(x, y) {
    if (reduce) return;
    const n = 3 + (+root.dataset.chaos || 0) * 2;
    for (let i = 0; i < n; i++) {
      const s = document.createElement('span');
      s.className = 'pop';
      s.textContent = ['?', '!', '?!', '+1'][i % 4];
      s.style.left = (x - 8) + 'px';
      s.style.top = (y - 14) + 'px';
      s.style.setProperty('--px', (Math.random() * 120 - 60) + 'px');
      s.style.setProperty('--pr', (Math.random() * 60 - 30) + 'deg');
      s.style.animationDelay = (i * 40) + 'ms';
      body.appendChild(s);
      setTimeout(() => s.remove(), 1400);
    }
  }

  // Chaos dial: a visitor toy. Unhinged (3) unless they picked something else.
  function setChaos(c, wobble) {
    root.dataset.chaos = c;
    document.querySelectorAll('#dial button').forEach(b => b.setAttribute('aria-pressed', +b.dataset.c === c));
    store.set('dbd-chaos', c);
    if (wobble && c === 3 && !reduce) {
      document.querySelectorAll('.q:not(.soon), .sheet').forEach((q, i) => setTimeout(() => {
        q.classList.remove('wobble'); void q.offsetWidth; q.classList.add('wobble');
      }, i * 90));
    }
  }
  $('#dial')?.addEventListener('click', e => {
    const b = e.target.closest('button');
    if (b) setChaos(+b.dataset.c, true);
  });
  setChaos(+root.dataset.chaos, false);

  // Theme: follows the system unless the visitor picks light or dark.
  const modes = ['system', 'light', 'dark'];
  const themeBtn = $('#theme');
  let mode = modes.includes(store.get('dbd-theme')) ? store.get('dbd-theme') : 'system';
  function applyTheme() {
    mode === 'system' ? root.removeAttribute('data-theme') : root.setAttribute('data-theme', mode);
    if (themeBtn) themeBtn.textContent = 'Theme: ' + mode;
    store.set('dbd-theme', mode === 'system' ? null : mode);
  }
  themeBtn?.addEventListener('click', () => { mode = modes[(modes.indexOf(mode) + 1) % 3]; applyTheme(); });
  applyTheme();

  // Five quick taps on the logo cycle the chaos level. One tap just goes home.
  let taps = 0, tapT;
  $('#brand')?.addEventListener('click', e => {
    e.preventDefault();
    const href = e.currentTarget.getAttribute('href');
    taps++;
    clearTimeout(tapT);
    if (taps === 5) {
      taps = 0;
      setChaos(((+root.dataset.chaos) + 1) % 4, true);
      burst(e.clientX, e.clientY + 20);
      return;
    }
    tapT = setTimeout(() => {
      if (taps < 5) {
        if (TOOL) location.href = href;
        else { history.replaceState(null, '', location.pathname); scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); }
      }
      taps = 0;
    }, 350);
  });

  console.log('%cYou opened the console. You’re my kind of person.', 'font:700 16px Caveat, cursive; color:#3D7643');
  console.log('Everything on this page comes from projects.json. The source: https://github.com/definitelybenny/definitelybenny.github.io');

  /* ---------- load the data ---------- */

  if (TOOL || $('#qs')) fetch(BASE + 'projects.json', { cache: 'no-cache' })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => (TOOL ? renderTool(data) : renderHome(data)))
    .catch(err => {
      console.error('Could not load projects.json', err);
      const el = $('#qs') || $('#page');
      if (el) el.insertAdjacentHTML('beforebegin', '<p class="noscript">The notebook didn’t load. Try a refresh?</p>');
    });

  /* ---------- home ---------- */

  const SCRIB = [
    '<span class="scribble s2" style="right:-4px;top:16px;transform:rotate(12deg)">!!</span>',
    '<span class="scribble s3 txt" style="left:16px;bottom:14px;transform:rotate(-8deg)">trust me</span>',
    '<span class="scribble s3" style="right:20px;bottom:16px"><svg width="54" height="40" viewBox="0 0 54 40"><path d="M4 30c14-24 30-26 44-8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><path d="M42 14l7 8-10 2" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg></span>',
    '<span class="scribble s2" style="left:12px;top:18px;transform:rotate(-14deg)">?!</span>'
  ];

  function linkButtons(t) {
    const links = (t.links || []).map(l =>
      `<a class="btn${l.primary ? ' go' : ''}" href="${esc(url(l.href))}"${ext(l.href)}>${esc(l.label)}${l.primary ? ' ' + arrow : ''}</a>`);
    if (t.page) links.push(`<a class="btn" href="${esc(url(t.page))}">Read the full page</a>`);
    return links.join('');
  }

  function renderHome(data) {
    const qs = $('#qs');
    if (!qs) return; // pages without a question list (like the 404) only want the toys
    const tools = data.questions || [];
    const byId = Object.fromEntries(tools.map(t => [t.id, t]));
    const opened = new Set();
    const count = $('#count');
    const updateCount = () => { count.textContent = `${tools.length} answered · ${opened.size} opened`; };
    qs.innerHTML = '';

    tools.forEach((t, i) => {
      const n = byId[t.next] || tools[(i + 1) % tools.length];
      const li = document.createElement('li');
      li.className = 'q';
      li.id = 'q-' + t.id;
      li.style.setProperty('--tilt', t.tilt || '0deg');
      li.innerHTML = `${SCRIB[i % 4]}${SCRIB[(i + 1) % 4]}<button class="qh" type="button" aria-expanded="false" aria-controls="a-${esc(t.id)}">
        <span class="qg">${esc(t.game)}</span><span class="qt">${esc(t.question)}</span><span class="note">${esc(t.note)}</span>
        <span class="pillbtn"><span class="lbl">Show me how</span>${arrow}</span></button>
        <div class="ans" id="a-${esc(t.id)}"><div><div class="tiles">
          <div class="tile"><span class="k">the answer</span><h3>${esc(t.name)}</h3><p>${esc(t.what)}</p>
            <div class="use"><span class="k">reach for it when</span><ul>${(t.useWhen || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
            <div class="row">${linkButtons(t)}</div></div>
          <div class="tile"><span class="k">then ask</span><div class="asks">${(t.thenAsk || []).map(x => `<div class="ask">${esc(x)}</div>`).join('')}</div></div>
          ${n && n !== t ? `<div class="tile wide nextq"><span><b>next question</b>${esc(n.question)}</span><button class="btn" type="button" data-next="${esc(n.id)}">Ask it ${arrow}</button></div>` : ''}
        </div></div></div>`;
      qs.appendChild(li);
    });

    const sd = data.secret;
    if (sd) {
      const sec = document.createElement('li');
      sec.className = 'q secret';
      sec.id = 'q-secret';
      sec.style.setProperty('--tilt', '1.8deg');
      sec.innerHTML = `<button class="qh" type="button" aria-expanded="false" aria-controls="a-secret"><span class="qg">${esc(sd.game)}</span><span class="qt">${esc(sd.question)}</span><span class="note">${esc(sd.note)}</span><span class="pillbtn"><span class="lbl">Show me how</span>${arrow}</span></button>
        <div class="ans" id="a-secret"><div><div class="tiles"><div class="tile wide"><span class="k">the answer</span><h3>${esc(sd.title)}</h3><p>${esc(sd.body)}</p></div>
        <div class="tile wide"><span class="k">then ask</span><div class="asks">${(sd.thenAsk || []).map(x => `<div class="ask">${esc(x)}</div>`).join('')}</div></div></div></div></div>`;
      qs.appendChild(sec);
    }

    (data.soon || []).forEach(s => {
      const li = document.createElement('li');
      li.className = 'q soon';
      li.innerHTML = `<div class="qh"><span class="qg">Coming soon</span><span class="qt" aria-hidden="true">${esc(s.question)}</span><span class="note">${esc(s.note || 'WIP, don’t look yet')}</span></div>`;
      qs.appendChild(li);
    });

    const bench = $('#bench');
    if (bench) {
      bench.innerHTML = (data.bench || []).map(a => `<div class="app" style="--t:${esc(a.tilt || '0deg')}">
        <div class="icon">?</div><span class="badge">${esc(a.badge || 'Coming soon')}</span><b>${esc(a.name)}</b><p>${esc(a.blurb)}</p>
        <div class="bar" aria-hidden="true"><i style="--w:${Math.max(0, Math.min(100, +a.progress || 0))}%"></i></div>
        ${a.scrawl ? `<span class="scrawl">${esc(a.scrawl)}</span>` : ''}</div>`).join('');
    }
    updateCount();

    function setOpen(li, on) {
      li.classList.toggle('open', on);
      const b = li.querySelector('button.qh');
      if (!b) return;
      b.setAttribute('aria-expanded', on);
      b.querySelector('.lbl').textContent = on ? 'Got it, close' : 'Show me how';
    }
    function openQ(id, scroll) {
      const li = $('#q-' + id);
      if (!li) return;
      document.querySelectorAll('.q.open').forEach(o => { if (o !== li) setOpen(o, false); });
      setOpen(li, true);
      if (id !== 'secret') {
        opened.add(id);
        updateCount();
        const s = $('#q-secret');
        if (s && opened.size === tools.length && !s.classList.contains('show')) {
          s.classList.add('show');
          const r = s.getBoundingClientRect();
          burst(r.left + 80, r.top + 30);
        }
      }
      if (scroll) setTimeout(() => li.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }), reduce ? 0 : 140);
    }
    function randomQ() {
      const pool = tools.filter(t => !opened.has(t.id));
      const list = pool.length ? pool : tools;
      if (list.length) openQ(list[Math.floor(Math.random() * list.length)].id, true);
    }

    let suppress = false;
    qs.addEventListener('click', e => {
      if (suppress) { suppress = false; return; }
      const nx = e.target.closest('[data-next]');
      if (nx) { openQ(nx.dataset.next, true); return; }
      const b = e.target.closest('button.qh');
      if (!b) return;
      const li = b.parentElement;
      if (li.classList.contains('open')) setOpen(li, false);
      else { openQ(li.id.slice(2), false); if (+root.dataset.chaos >= 2) burst(e.clientX, e.clientY); }
    });
    $('#mark')?.addEventListener('click', e => { burst(e.clientX, e.clientY); randomQ(); });
    addEventListener('keydown', e => {
      if (e.key === '?' && !e.target.closest('input,textarea,[contenteditable]')) randomQ();
    });

    // Drag cards around on a computer; on a phone the page just scrolls.
    let drag = null;
    qs.addEventListener('pointerdown', e => {
      if (e.pointerType === 'touch' || innerWidth < 640) return;
      const li = e.target.closest('.q');
      if (!li || li.classList.contains('soon') || li.classList.contains('open') || e.target.closest('a,[data-next]')) return;
      const cs = getComputedStyle(li);
      drag = { li, x: e.clientX, y: e.clientY, dx: parseFloat(cs.getPropertyValue('--dx')) || 0, dy: parseFloat(cs.getPropertyValue('--dy')) || 0, moved: false };
    });
    addEventListener('pointermove', e => {
      if (!drag) return;
      const mx = e.clientX - drag.x, my = e.clientY - drag.y;
      if (!drag.moved && Math.hypot(mx, my) < 6) return;
      drag.moved = true;
      drag.li.classList.add('dragging');
      drag.li.style.setProperty('--dx', (drag.dx + mx) + 'px');
      drag.li.style.setProperty('--dy', (drag.dy + my) + 'px');
    });
    addEventListener('pointerup', () => {
      if (!drag) return;
      if (drag.moved) suppress = true;
      drag.li.classList.remove('dragging');
      drag = null;
      setTimeout(() => { suppress = false; }, 0);
    });

    // Deep links: #pokopia opens that question, #random opens one at random, #apps scrolls to the bench.
    function route() {
      const h = decodeURIComponent(location.hash.slice(1));
      if (!h) return false;
      if (h === 'random') { randomQ(); return true; }
      if (h === 'apps') { setTimeout(() => $('#apps')?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }), 30); return true; }
      if (byId[h]) { openQ(h, true); return true; }
      return false;
    }
    addEventListener('hashchange', route);
    if (!route() && tools[0]) openQ(tools[0].id, false);
  }

  /* ---------- tool page ---------- */

  function highlight(code) {
    return code.split('\n').map(line => {
      const i = line.indexOf('//');
      const head = i >= 0 ? line.slice(0, i) : line;
      const tail = i >= 0 ? line.slice(i) : '';
      const kw = esc(head).replace(/\b(const|let|new|for|if|else|return|function)\b/g, '<span class="h">$1</span>');
      return kw + (tail ? `<span class="c">${esc(tail)}</span>` : '');
    }).join('\n');
  }

  const VENN = `<svg class="venn" viewBox="0 0 420 340" role="img" aria-label="Three overlapping circles, one per roommate. The middle where all three overlap is labeled everyone loves this.">
    <g fill="var(--moss)" fill-opacity=".14" stroke="var(--moss)" stroke-width="3"><circle cx="150" cy="135" r="100"/><circle cx="270" cy="135" r="100"/><circle cx="210" cy="225" r="100"/></g>
    <text x="70" y="70">roommate 1</text><text x="282" y="70">roommate 2</text><text x="160" y="332">roommate 3</text>
    <path d="M210 168l-6 22 22-8" fill="none" stroke="var(--pen)" stroke-width="3" stroke-linecap="round"/><circle cx="210" cy="168" r="10" fill="var(--pen)"/>
    <text class="lbl2" x="232" y="168">everyone</text><text class="lbl2" x="232" y="190">loves this</text></svg>`;

  function figure(f) {
    if (!f) return '';
    if (f.type === 'venn') return VENN;
    if (f.type === 'image') return `<figure class="shot"><img src="${esc(url(f.src))}" alt="${esc(f.alt)}" loading="lazy" decoding="async">${f.caption ? `<figcaption>${esc(f.caption)}</figcaption>` : ''}</figure>`;
    if (f.type === 'beforeafter') return `<figure class="shot"><div class="ba" style="--cut:50%">
      <img src="${esc(url(f.before.src))}" alt="${esc(f.before.alt)}" loading="lazy" decoding="async">
      <img class="after" src="${esc(url(f.after.src))}" alt="${esc(f.after.alt)}" loading="lazy" decoding="async">
      <span class="lbl l">${esc(f.before.label)}</span><span class="lbl r">${esc(f.after.label)}</span><span class="knob"></span>
      <input type="range" min="0" max="100" value="50" aria-label="Compare ${esc(f.before.label)} and ${esc(f.after.label)}"></div></figure>`;
    return '';
  }

  function renderTool(data) {
    const tools = data.questions || [];
    const t = tools.find(x => x.id === TOOL);
    const page = $('#page');
    if (!t || !t.detail) { page.innerHTML = '<p class="noscript">This page wandered off. <a href="' + BASE + '">Back to all questions</a></p>'; return; }
    const d = t.detail;
    const n = tools.find(x => x.id === t.next);
    const tilts = ['-.5deg', '.6deg', '-.4deg', '.5deg', '-.3deg'];
    const sheet = (i, inner, extra = '') => `<article class="sheet"${extra} style="--t:${tilts[i % tilts.length]}">${inner}</article>`;
    const primary = (t.links || []).filter(l => l.primary);
    const rest = (t.links || []).filter(l => !l.primary);

    let html = `<div class="hero t-hero">
      <span class="status"><i></i>${esc(d.status)}</span>
      <h1 class="qt">${esc(t.question)}</h1>
      <p class="lede">${esc(d.lede)}</p>
      <div class="row" style="justify-content:center">${primary.map(l => `<a class="btn go" href="${esc(url(l.href))}"${ext(l.href)}>${esc(l.label)} ${arrow}</a>`).join('')}
        ${d.works ? '<a class="btn" href="#works">Skip to the nerdy part</a>' : ''}</div>
    </div><div class="page">`;

    let i = 0;
    if (d.what) {
      html += sheet(i++, `<span class="k">what it is</span><div class="two"><div><h2>${esc(d.what.title)}</h2>${(d.what.body || []).map(p => `<p>${esc(p)}</p>`).join('')}${d.what.callout ? `<p class="callout">${esc(d.what.callout)}</p>` : ''}</div>${figure(d.what.figure)}</div>`);
    }
    if (d.how) {
      html += sheet(i++, `<span class="k">how to use it</span><h2>${esc(d.how.title)}</h2>
        <ol class="steps">${(d.how.steps || []).map(s => `<li><div><b>${esc(s.title)}</b><span>${esc(s.body)}</span></div></li>`).join('')}</ol>
        <div class="tiles" style="padding:22px 0 0">
          <div class="tile"><span class="k">reach for it when</span><ul>${(t.useWhen || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
          ${d.how.headsUp ? `<div class="tile"><span class="k">heads up</span><p>${esc(d.how.headsUp)}</p></div>` : ''}
        </div>`);
    }
    if (d.works) {
      html += sheet(i++, `<span class="k">how it works</span><h2>${esc(d.works.title)}</h2>${(d.works.body || []).map(p => `<p>${esc(p)}</p>`).join('')}
        ${d.works.code ? `<pre><code>${highlight(d.works.code)}</code></pre>` : ''}${d.works.callout ? `<p class="callout">${esc(d.works.callout)}</p>` : ''}
        ${rest.length ? `<div class="row">${rest.map(l => `<a class="btn" href="${esc(url(l.href))}"${ext(l.href)}>${esc(l.label)}</a>`).join('')}</div>` : ''}`, ' id="works"');
    }
    if (d.ideas) {
      const it = ['-1deg', '.8deg', '-.6deg'];
      html += sheet(i++, `<span class="k">build on it</span><h2>${esc(d.ideas.title)}</h2>
        <div class="ideas">${(d.ideas.items || []).map((x, k) => `<div class="idea" style="--t:${it[k % 3]}"><em>${esc(x.tag)}</em><b>${esc(x.title)}</b><span>${esc(x.body)}</span></div>`).join('')}</div>`);
    }
    if (n && n !== t) {
      html += `<article class="sheet nextq" style="--t:-.3deg"><span><b>next question</b>${esc(n.question)}</span>
        <a class="btn" href="${esc(BASE + '#' + n.id)}">Ask it ${arrow}</a></article>`;
    }
    html += '</div>';
    page.innerHTML = html;

    // before/after slider
    page.querySelectorAll('.ba').forEach(ba => {
      const r = ba.querySelector('input');
      r.addEventListener('input', () => ba.style.setProperty('--cut', r.value + '%'));
    });
    // "?" on a tool page sends you home to a random question
    addEventListener('keydown', e => { if (e.key === '?' && !e.target.closest('input,textarea')) location.href = BASE + '#random'; });
  }
})();
