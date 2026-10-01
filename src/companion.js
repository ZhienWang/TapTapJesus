(async () => {
  const api = window.companion;
  const stage = document.getElementById('stage');
  const panel = document.getElementById('panel');
  const menuBtn = document.getElementById('menuBtn');
  const $ = (id) => document.getElementById(id);

  // ---------- Avatar ----------
  // Each avatar SVG describes itself with data-* attributes on its root: the crop to show,
  // and where/how to paint the main counter on the thing it slaps.

  let svg;
  let counter;
  let lastStats = null;
  let lastProgress = null;

  // Swapped in place (no page reload) so the window's click-through state survives a switch.
  async function loadAvatar() {
    stage.innerHTML = await api.getSvg();
    svg = stage.querySelector('svg');
    const meta = svg.dataset;
    svg.removeAttribute('width');
    svg.removeAttribute('height');
    svg.setAttribute('viewBox', meta.crop || '96 120 320 380');
    document.title = meta.name || 'Tap Tap Jesus';

    counter = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    counter.id = 'counter';
    counter.setAttribute('x', meta.counterX || '256');
    counter.setAttribute('y', meta.counterY || '417');
    counter.setAttribute('text-anchor', 'middle');
    if (meta.counterFill) counter.style.fill = meta.counterFill;
    if (meta.counterStroke) counter.style.stroke = meta.counterStroke;
    svg.appendChild(counter);
    if (lastStats) renderStats(lastStats);
    if (lastProgress) renderProgress(lastProgress);
  }

  await loadAvatar();
  api.onAvatarChanged(loadAvatar);

  const MIN_DOWN_MS = 70; // keep very quick taps visible for a few frames
  const downAt = { left: 0, right: 0 };
  const liftTimer = {};

  function setHand(side, down) {
    clearTimeout(liftTimer[side]);
    if (down) {
      downAt[side] = performance.now();
      svg.classList.add('tap-' + side);
    } else {
      const wait = MIN_DOWN_MS - (performance.now() - downAt[side]);
      liftTimer[side] = setTimeout(() => svg.classList.remove('tap-' + side), Math.max(0, wait));
    }
  }

  api.onHands((hands) => {
    setHand('left', hands.left);
    setHand('right', hands.right);
  });

  // ---------- Stats ----------

  const fmt = (n) => Math.floor(n).toLocaleString();

  function formatMiles(inches) {
    const miles = inches / 63360;
    return (miles < 1 ? miles.toFixed(3) : miles.toFixed(2)) + ' mi';
  }

  function paintCounter(n) {
    counter.textContent = fmt(n);
    // Squeeze very large numbers so they stay on the board.
    counter.removeAttribute('textLength');
    if (counter.getComputedTextLength() > 250) {
      counter.setAttribute('textLength', '250');
      counter.setAttribute('lengthAdjust', 'spacingAndGlyphs');
    }
  }

  function renderStats(s) {
    lastStats = s;
    const total = s.keystrokes + s.leftClicks + s.rightClicks;
    $('statKeys').textContent = fmt(s.keystrokes);
    $('statLeft').textContent = fmt(s.leftClicks);
    $('statRight').textContent = fmt(s.rightClicks);
    $('statMiles').textContent = formatMiles(s.mouseInches);
    $('statTotal').textContent = fmt(total);
    $('since').textContent = 'since ' + new Date(s.since).toLocaleDateString();
  }

  renderStats(await api.getStats());
  api.onStats(renderStats);

  // ---------- Levels & unlocks ----------
  // Each character has its own counter (painted on what they slap); 10,000 taps unlocks the next one.

  const roster = $('roster');
  let rosterKey = '';

  function renderProgress(p) {
    lastProgress = p;
    paintCounter(p.activeTaps);
    $('lvNum').textContent = 'Level ' + p.level;
    $('lvMax').textContent = p.maxLevel;
    const active = p.roster.find((c) => c.id === p.active);
    $('lvActive').textContent = `${active.label} · ${fmt(active.taps)}`;

    // Rebuild the cards only when lock state or the active character changes.
    const key = p.active + '|' + p.roster.map((c) => +c.unlocked).join('');
    if (key !== rosterKey) {
      rosterKey = key;
      roster.replaceChildren(...p.roster.map((c, i) => {
        const li = document.createElement('li');
        const b = document.createElement('button');
        b.type = 'button';
        b.className = (c.unlocked ? '' : 'locked') + (c.id === p.active ? ' active' : '');
        b.title = c.unlocked ? `${c.label}\n${fmt(c.taps)} taps` : 'Locked. Keep tapping to unlock!';
        const img = document.createElement('img');
        img.src = `../assets/avatars/${c.id}.png`;
        img.alt = c.unlocked ? c.label : 'Locked character';
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = c.unlocked ? `Lv ${i + 1}` : `🔒 Lv ${i + 1}`;
        b.append(img, tag);
        if (c.unlocked) b.addEventListener('click', () => api.setAvatar(c.id));
        li.appendChild(b);
        return li;
      }));
    }

    const next = $('nextUnlock');
    if (!p.next) {
      next.innerHTML = '<b>Every character unlocked!</b> You are a legend.';
      return;
    }
    const pct = (p.next.have / p.next.taps) * 100;
    const playingIt = p.active === p.next.after;
    next.innerHTML = '';
    const line = document.createElement('div');
    const b = document.createElement('b');
    b.textContent = `${fmt(p.next.have)} / ${fmt(p.next.taps)}`;
    line.append('Next: ', b, ` as ${p.next.afterLabel}`);
    if (!playingIt) line.append(' (switch to them)');
    const track = document.createElement('div');
    track.className = 'bar-track';
    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    fill.style.width = pct + '%';
    track.appendChild(fill);
    next.append(line, track);
  }

  renderProgress(await api.getProgress());
  api.onProgress(renderProgress);

  const toast = $('toast');
  let toastTimer;
  api.onUnlocked(({ label, level }) => {
    toast.replaceChildren(`🎉 ${label} unlocked!`);
    const small = document.createElement('small');
    small.textContent = `Level ${level} · switch in ☰ → Unlocks`;
    toast.appendChild(small);
    toast.classList.add('show');
    stage.classList.add('celebrate');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.classList.remove('show'); stage.classList.remove('celebrate'); }, 5000);
  });

  // ---------- Top apps ----------

  function fmtDuration(sec) {
    sec = Math.floor(sec);
    if (sec < 60) return sec + 's';
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`;
  }

  function renderApps({ top, totalSeconds, trackedCount }) {
    const list = $('appList');
    list.replaceChildren();
    if (!top.length) {
      const li = document.createElement('li');
      li.className = 'empty';
      li.textContent = 'No app time yet. Keep using your PC!';
      list.appendChild(li);
    }
    const max = top.length ? top[0].seconds : 1;
    top.forEach((a, i) => {
      const li = document.createElement('li');
      li.title = `${a.name} (${a.exe})\n${fmtDuration(a.seconds)} used · ${a.taps.toLocaleString()} taps`;
      const bar = document.createElement('span');
      bar.className = 'bar';
      bar.style.width = Math.max(4, (a.seconds / max) * 100) + '%';
      const rank = document.createElement('span');
      rank.className = 'rank';
      rank.textContent = i + 1;
      const name = document.createElement('span');
      name.className = 'name';
      name.textContent = a.name;
      const time = document.createElement('span');
      time.className = 'time';
      time.textContent = fmtDuration(a.seconds);
      li.append(bar, rank, name, time);
      list.appendChild(li);
    });
    $('appsTotalTime').textContent = fmtDuration(totalSeconds);
    $('appsCount').textContent = trackedCount ? `(${trackedCount} app${trackedCount === 1 ? '' : 's'})` : '';
  }

  renderApps(await api.getApps());
  api.onApps(renderApps);
  $('btnChooseApps').addEventListener('click', () => api.openTracker());

  // ---------- Details panel ----------

  panel.querySelectorAll('[data-tab]').forEach((tab) => tab.addEventListener('click', () => {
    panel.querySelectorAll('[data-tab]').forEach((t) => t.classList.toggle('active', t === tab));
    panel.querySelectorAll('[data-tab-panel]').forEach((p) => p.classList.toggle('active', p.dataset.tabPanel === tab.dataset.tab));
  }));

  menuBtn.addEventListener('click', () => {
    const open = panel.classList.toggle('open');
    menuBtn.classList.toggle('open', open);
  });

  const btnReset = $('btnReset');
  let resetArmed = null;
  btnReset.addEventListener('click', () => {
    if (resetArmed) {
      clearTimeout(resetArmed);
      resetArmed = null;
      btnReset.textContent = 'Reset';
      api.resetStats();
      return;
    }
    btnReset.textContent = 'Sure?';
    resetArmed = setTimeout(() => { resetArmed = null; btnReset.textContent = 'Reset'; }, 3000);
  });
  $('btnHide').addEventListener('click', () => {
    panel.classList.remove('open');
    menuBtn.classList.remove('open');
    api.hide();
  });
  $('btnQuit').addEventListener('click', () => api.quit());
  $('btnDonate').addEventListener('click', () => api.donate());

  // ---------- Dragging & context menu ----------

  stage.addEventListener('pointerdown', (e) => {
    if (e.button === 0) api.dragStart();
  });
  window.addEventListener('pointerup', () => api.dragEnd());
  // Ctrl + scroll over him to resize.
  stage.addEventListener('wheel', (e) => {
    if (!e.ctrlKey) return;
    e.preventDefault();
    api.scaleBy(e.deltaY < 0 ? 1.1 : 1 / 1.1);
  }, { passive: false });
  stage.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    api.contextMenu();
  });

  // ---------- Click-through ----------
  // The window ignores the mouse (clicks fall through to the desktop) except over the baby,
  // the menu button and the open panel. Mouse moves are still forwarded so we can tell.

  let ignoring = true;
  api.setIgnoreMouse(true); // start in sync with the window, whatever state it was left in
  function isSolid(el) {
    if (!el || el === document.documentElement || el === document.body || el === stage || el === svg) return false;
    if (panel.contains(el)) return panel.classList.contains('open');
    return true;
  }
  document.addEventListener('mousemove', (e) => {
    const ignore = !isSolid(document.elementFromPoint(e.clientX, e.clientY));
    if (ignore !== ignoring) {
      ignoring = ignore;
      api.setIgnoreMouse(ignore);
    }
  });
  document.addEventListener('mouseleave', () => {
    if (!ignoring) {
      ignoring = true;
      api.setIgnoreMouse(true);
    }
  });
})();
