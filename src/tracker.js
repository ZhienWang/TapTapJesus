(() => {
  const api = window.companion;
  const list = document.getElementById('list');
  const search = document.getElementById('search');
  const autoTrack = document.getElementById('autoTrack');
  const summary = document.getElementById('summary');
  let apps = [];

  function fmtDuration(sec) {
    sec = Math.floor(sec);
    if (sec < 60) return sec ? sec + 's' : '—';
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`;
  }

  function render() {
    const q = search.value.trim().toLowerCase();
    const shown = apps
      .filter((a) => !q || a.name.toLowerCase().includes(q) || a.exe.toLowerCase().includes(q))
      .sort((a, b) => b.seconds - a.seconds || a.name.localeCompare(b.name));
    list.replaceChildren();
    if (!shown.length) {
      const li = document.createElement('li');
      li.className = 'empty';
      li.textContent = q ? 'No apps match your search.' : 'No apps seen yet.';
      list.appendChild(li);
    }
    for (const a of shown) {
      const li = document.createElement('li');
      li.classList.toggle('off', !a.tracked);
      const label = document.createElement('label');
      const box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = a.tracked;
      box.addEventListener('change', () => {
        a.tracked = box.checked;
        li.classList.toggle('off', !a.tracked);
        api.setAppTracked(a.exe, a.tracked);
        renderSummary();
      });
      const name = document.createElement('span');
      name.className = 'name';
      const b = document.createElement('b');
      b.textContent = a.name;
      const small = document.createElement('small');
      small.textContent = a.exe;
      if (a.running) {
        const run = document.createElement('span');
        run.className = 'running';
        run.textContent = '● running';
        small.append(' ', run);
      }
      name.append(b, small);
      const time = document.createElement('span');
      time.className = 'time';
      time.textContent = fmtDuration(a.seconds);
      label.append(box, name, time);
      li.appendChild(label);
      list.appendChild(li);
    }
    renderSummary();
  }

  function renderSummary() {
    const tracked = apps.filter((a) => a.tracked);
    const total = tracked.reduce((s, a) => s + a.seconds, 0);
    summary.textContent = `Tracking ${tracked.length} of ${apps.length} apps · ${fmtDuration(total)} total time used`;
  }

  async function refresh() {
    const data = await api.getTrackerList();
    apps = data.apps;
    autoTrack.checked = data.autoTrackNew;
    render();
  }

  autoTrack.addEventListener('change', () => api.setAutoTrack(autoTrack.checked));
  search.addEventListener('input', render);
  document.getElementById('all').addEventListener('click', () => {
    api.setAllTracked(true);
    apps.forEach((a) => { a.tracked = true; });
    render();
  });
  document.getElementById('none').addEventListener('click', () => {
    api.setAllTracked(false);
    apps.forEach((a) => { a.tracked = false; });
    render();
  });

  refresh();
  // Pick up newly opened apps and updated times, unless you're in the middle of clicking around.
  setInterval(() => { if (!document.querySelector('label:active')) refresh(); }, 5000);
})();
