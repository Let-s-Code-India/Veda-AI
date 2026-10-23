const $ = id => document.getElementById(id);
let conv = 0, agent = 'auto', agents = [], file = null, busy = false, deep = false;
let convData = {items: [], period: 2592000, period_label: '30 days', enabled: true};
let memCache = {}, rec = null, recChunks = [], platformInfo = {platform: 'unknown', is_mobile: false};
const RAW = [];
const log = $('log'), q = $('q'), fileIn = $('fileIn');
const COL = {vishwakarma:'#51308f', saraswati:'#b3263e', valmiki:'#c2476a', chanakya:'#2f4b9c', aryabhata:'#2a7fa8',
  dronacharya:'#e8830c', dhanvantari:'#2f7d4f', kubera:'#a87a00', vidura:'#6b3fa0', panini:'#8a5a2b',
  narada:'#1f7a7a', sanjaya:'#4a6a8a', chitragupta:'#5a5a7a', drishti:'#d4540f', shruti:'#2a7f6a', auto:'#2a1052'};
const PLACEHOLDER = 'Ask anything...';

/* ---------- helpers ---------- */
async function api(p, o) {
  let r;
  try { r = await fetch(p, o); } catch (e) { throw new Error('Cannot reach the server. Is it still running?'); }
  let j = {};
  try { j = await r.json(); } catch (e) {}
  if (!r.ok) throw new Error(j.error || ('Request failed (' + r.status + ')'));
  return j;
}
const post = (p, d) => api(p, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(d || {})});
const put = (p, d) => api(p, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(d || {})});
const del = p => api(p, {method: 'DELETE'});
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function ava(k, name) { return '<span class="av" style="background:' + (COL[k] || '#51308f') + '">' + esc((name || '?')[0]) + '</span>'; }
function keyOf(name) {
  const n = (name || '').replace(' (auto)', ''); const a = agents.find(x => x.name === n); return a ? a.key : 'auto';
}
function human(s) {
  if (s < 90) return Math.max(1, Math.round(s)) + ' seconds';
  if (s < 5400) return Math.round(s / 60) + ' minutes';
  if (s < 129600) return Math.round(s / 3600) + ' hours';
  return Math.round(s / 86400) + ' days';
}
function flash(b, t) { const o = b.textContent; b.textContent = t; setTimeout(() => b.textContent = o, 1200); }

/* ---------- toast ---------- */
let toastTimer;
function toast(msg, label, fn, ms) {
  ms = ms || (label ? 10000 : 3500);
  const t = $('toast');
  t.innerHTML = '<span>' + esc(msg) + '</span>' + (label ? '<button>' + esc(label) + '</button>' : '') +
    (label ? '<i class="bar" style="animation-duration:' + ms + 'ms"></i>' : '');
  if (label) t.querySelector('button').onclick = () => { hideToast(); fn(); };
  t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(hideToast, ms);
}
function hideToast() { $('toast').classList.remove('show'); }

/* ---------- theme ---------- */
function toggleTheme() {
  const t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = t; try { localStorage.setItem('theme', t); } catch (e) {}
}

/* ---------- markdown ---------- */
function inline(s) {
  return esc(s).replace(/`([^`\n]+)`/g, '<code class="il">$1</code>')
    .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
    .replace(/(https?:\/\/[^\s<)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
}
function table(rows) {
  const r = rows.filter(x => !/^[\s|:-]+$/.test(x)).map(x => x.trim().replace(/^\||\|$/g, '').split('|'));
  if (!r.length) return '';
  let h = '<div class="tw"><table><tr>' + r[0].map(c => '<th>' + inline(c.trim()) + '</th>').join('') + '</tr>';
  r.slice(1).forEach(x => h += '<tr>' + x.map(c => '<td>' + inline(c.trim()) + '</td>').join('') + '</tr>');
  return h + '</table></div>';
}
function text2html(s) {
  const out = []; let mode = '', buf = [], start = 1;
  const flush = () => {
    if (!buf.length) return;
    if (mode === 'ul') out.push('<ul>' + buf.join('') + '</ul>');
    else if (mode === 'ol') out.push('<ol start="' + start + '">' + buf.join('') + '</ol>');
    else if (mode === 'tb') out.push(table(buf));
    buf = []; mode = '';
  };
  const set = m => { if (m !== mode) { flush(); mode = m; } };
  s.split('\n').forEach(l => {
    let m;
    if (/^\s*([-*_])\1{2,}\s*$/.test(l)) { flush(); out.push('<hr>'); }
    else if (/^\s*\|.*\|\s*$/.test(l)) { set('tb'); buf.push(l); }
    else if ((m = l.match(/^\s*[-*] (.*)$/))) { set('ul'); buf.push('<li>' + inline(m[1]) + '</li>'); }
    else if ((m = l.match(/^\s*(\d+)[.)] (.*)$/))) { if (mode !== 'ol') start = parseInt(m[1], 10); set('ol'); buf.push('<li>' + inline(m[2]) + '</li>'); }
    else { flush(); if ((m = l.match(/^#{1,4} (.*)$/))) out.push('<h3>' + inline(m[1]) + '</h3>'); else if (l.trim()) out.push('<p>' + inline(l) + '</p>'); }
  });
  flush(); return out.join('');
}
function md(s) {
  return s.split('```').map((p, i) => {
    if (i % 2) { const n = p.indexOf('\n'); const c = p.slice(n >= 0 ? n + 1 : 0);
      return '<pre><button class="cp" onclick="cp(this)">Copy</button><code>' + esc(c) + '</code></pre>'; }
    return text2html(p);
  }).join('');
}
function cp(b) { navigator.clipboard.writeText(b.nextSibling.textContent); flash(b, 'Copied'); }
function copyMsg(b, i) { navigator.clipboard.writeText(RAW[i]); flash(b, 'Copied'); }

/* ---------- layout ---------- */
function toggleSide() { $('side').classList.toggle('open'); $('shade').classList.toggle('open'); }
function closeSide() { $('side').classList.remove('open'); $('shade').classList.remove('open'); }
function toggleDeep() {
  deep = !deep; const b = $('deepBtn');
  b.classList.toggle('on', deep); b.textContent = deep ? 'Deep mode on' : 'Deep mode off';
}
function chips() {
  const all = [{key: 'auto', name: 'Sarathi (Auto)'}].concat(agents);
  $('chips').innerHTML = all.map(a => '<button class="chip' + (a.key === agent ? ' on' : '') + '" onclick="pick(\'' + a.key + '\')">' +
    ava(a.key, a.name) + esc(a.name) + '</button>').join('');
  const cur = agents.find(a => a.key === agent);
  $('sub').textContent = cur ? cur.role : 'Sarathi picks the best agent for each message';
}
function pick(k) { agent = k; chips(); q.focus(); }
async function loadPlatformInfo() {
  try {
    platformInfo = await api('/api/platform');
  } catch (e) {
    platformInfo = {platform: 'unknown', is_mobile: false};
  }
}

function welcome() {
  const installHint = platformInfo.is_mobile
    ? '<p>Install this as a home-screen app from your browser menu for the smoothest mobile experience.</p>'
    : '<p>Sarathi reads each message and sends it to the right agent and model. Or pick an agent yourself.</p>';
  log.innerHTML = '<div class="welcome"><img class="logo" src="/logo.svg" alt="" onerror="this.style.display=\'none\'"><h2>Namaste</h2>' +
    installHint + '<div class="cards">' +
    agents.filter(a => !a.custom).map(a => '<button class="ac" onclick="pick(\'' + a.key + '\')">' + ava(a.key, a.name) +
      '<span><b>' + esc(a.name) + '</b><small>' + esc(a.role) + '</small></span></button>').join('') + '</div></div>';
}
function add(role, text, m) {
  const d = document.createElement('div'); d.className = 'msg ' + role;
  let meta = role === 'user' ? 'You' : '', acts = '';
  if (m && m.agent) {
    meta = ava(keyOf(m.agent), m.agent) + '<span class="badge">' + esc(m.agent) + '</span><span>' + esc(m.model || '') + '</span>';
    RAW.push(text); acts = '<div class="acts"><button onclick="copyMsg(this,' + (RAW.length - 1) + ')">Copy answer</button></div>';
  }
  d.innerHTML = '<div class="meta">' + meta + '</div><div class="bub">' + (role === 'user' ? esc(text) : md(text)) + '</div>' + acts;
  log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
}

/* ---------- chats ---------- */
async function loadConvs() {
  convData = await api('/api/convs'); renderConvs(); updatePin(); return convData.items;
}
function renderConvs() {
  const f = ($('find').value || '').toLowerCase();
  $('convs').innerHTML = convData.items.filter(x => !f || x.title.toLowerCase().includes(f)).map(x =>
    '<div class="cv' + (x.id === conv ? ' on' : '') + '" onclick="openConv(' + x.id + ')">' +
    '<span class="ct">' + (x.pinned ? '&#9733; ' : '') + esc(x.title) + '</span>' +
    (x.expires_in != null ? '<b class="dot" title="Will be deleted soon" onclick="event.stopPropagation();expiryPop(' + x.id + ')"></b>' : '') +
    '<i onclick="event.stopPropagation();delConv(' + x.id + ')">x</i></div>').join('');
}
function updatePin() {
  const c = convData.items.find(x => x.id === conv);
  $('pinBtn').classList.toggle('on', !!(c && c.pinned));
  $('title').textContent = c ? c.title : 'New chat';
}
function expiryPop(id) {
  const c = convData.items.find(x => x.id === id); if (!c || c.expires_in == null) return;
  toast('This chat will be deleted in ' + human(c.expires_in) + ' to save storage. Keep it for another ' + convData.period_label + '?',
    'Keep', async () => { try { await post('/api/convs/' + id + '/keep'); await loadConvs(); toast('Kept for another ' + convData.period_label + '.'); } catch (e) { toast(e.message); } });
}
async function togglePin() {
  const c = convData.items.find(x => x.id === conv); if (!c) return;
  try { await post('/api/convs/' + conv + '/pin', {pinned: c.pinned ? 0 : 1}); await loadConvs();
    toast(c.pinned ? 'Chat unpinned.' : 'Chat pinned. It will never be auto-deleted.'); } catch (e) { toast(e.message); }
}
function exportChat() { if (conv) location.href = '/api/convs/' + conv + '/export'; }
async function newChat() {
  try { const r = await api('/api/convs', {method: 'POST'}); await openConv(r.id); } catch (e) { toast(e.message); }
}
async function openConv(id) {
  try {
    conv = id; const m = await api('/api/convs/' + id + '/msgs');
    log.innerHTML = ''; if (!m.length) welcome();
    m.forEach(x => add(x.role, x.content, x.role === 'assistant' ? {agent: x.agent, model: x.model} : null));
    await loadConvs(); closeSide();
  } catch (e) { toast(e.message); }
}
async function delConv(id) {
  try {
    await del('/api/convs/' + id);
    const items = await loadConvs();
    if (id === conv) { items.length ? openConv(items[0].id) : newChat(); }
    toast('Chat deleted.', 'Undo', async () => {
      try { await post('/api/convs/' + id + '/restore'); await openConv(id); } catch (e) { toast(e.message); }
    });
  } catch (e) { toast(e.message); }
}

/* ---------- sending ---------- */
function clearFile() { file = null; fileIn.value = ''; $('attach').innerHTML = ''; }
fileIn.onchange = () => {
  file = fileIn.files[0] || null; if (!file) return;
  const img = file.type.startsWith('image/') ? '<img src="' + URL.createObjectURL(file) + '">' : '';
  $('attach').innerHTML = img + '<span>' + esc(file.name) + ' (tap to remove)</span>';
};
$('attach').onclick = clearFile;
function send() {
  if (busy) return;
  const text = q.value.trim(); if (!text && !file) return;
  const f = file; q.value = ''; q.style.height = 'auto'; clearFile();
  run(text, f, false);
}
async function run(text, f, isRetry) {
  busy = true;
  const wl = log.querySelector('.welcome'); if (wl) wl.remove();
  if (!isRetry) add('user', (f ? '[Attached: ' + f.name + ']\n' : '') + text);
  const w = add('assistant', '');
  w.querySelector('.bub').innerHTML = '<span class="dots"><i></i><i></i><i></i></span>';
  const fd = new FormData(); fd.append('conv', conv); fd.append('agent', agent); fd.append('text', text); fd.append('deep', deep ? '1' : '0');
  if (f) fd.append('file', f);
  try {
    const j = await api('/api/chat', {method: 'POST', body: fd});
    w.remove(); add('assistant', j.reply, {agent: j.agent, model: j.label}); await loadConvs();
  } catch (e) {
    const b = w.querySelector('.bub'); b.classList.add('err');
    b.innerHTML = '<div>' + esc(e.message) + '</div><button>Try again</button>';
    b.querySelector('button').onclick = () => { if (!busy) { w.remove(); run(text, f, true); } };
  }
  busy = false;
}
q.oninput = () => { q.style.height = 'auto'; q.style.height = Math.min(q.scrollHeight, 140) + 'px'; };
q.onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey && innerWidth > 800) { e.preventDefault(); send(); } };

/* ---------- microphone ---------- */
async function toggleMic() {
  if (rec) { rec.stop(); return; }
  if (!navigator.mediaDevices || !window.MediaRecorder) { toast('The microphone needs http://localhost or https. Typing still works.', null, null, 5000); return; }
  try {
    const st = await navigator.mediaDevices.getUserMedia({audio: true});
    const mt = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'].find(t => MediaRecorder.isTypeSupported(t)) || '';
    rec = new MediaRecorder(st, mt ? {mimeType: mt} : {}); recChunks = [];
    rec.ondataavailable = e => { if (e.data.size) recChunks.push(e.data); };
    rec.onstop = async () => {
      st.getTracks().forEach(t => t.stop()); $('micBtn').classList.remove('rec');
      const type = (rec && rec.mimeType) || 'audio/webm'; rec = null;
      const blob = new Blob(recChunks, {type});
      if (blob.size < 1500) { toast('Nothing was recorded.'); return; }
      await voiceToText(blob, type);
    };
    rec.start(); $('micBtn').classList.add('rec'); toast('Listening. Tap the mic again to stop.', null, null, 3000);
  } catch (e) { rec = null; toast('Microphone permission was denied or no microphone was found.', null, null, 5000); }
}
async function voiceToText(blob, type) {
  const ext = type.includes('mp4') ? 'mp4' : type.includes('ogg') ? 'ogg' : 'webm';
  const fd = new FormData(); fd.append('audio', blob, 'voice.' + ext);
  q.placeholder = 'Transcribing...';
  try {
    const j = await api('/api/transcribe', {method: 'POST', body: fd});
    q.value = (q.value ? q.value + ' ' : '') + j.text; q.oninput(); q.focus();
  } catch (e) { toast('Voice failed: ' + e.message, null, null, 5000); }
  q.placeholder = PLACEHOLDER;
}

/* ---------- panels ---------- */
function openPanel(w) {
  $('panel').classList.add('open'); closeSide();
  ({mem: memPanel, ag: agPanel, mod: modPanel, set: setPanel})[w]();
}
function closePanel() { $('panel').classList.remove('open'); }
function pickJson(cb) {
  const i = document.createElement('input'); i.type = 'file'; i.accept = '.json,application/json';
  i.onchange = async () => { try { cb(JSON.parse(await i.files[0].text())); } catch (e) { toast('That file is not valid JSON.'); } };
  i.click();
}

/* memory */
async function memPanel() {
  $('ptitle').textContent = 'Memory';
  try {
    const [m, s] = await Promise.all([api('/api/memory'), api('/api/convs/' + conv + '/summary')]);
    memCache = {}; m.forEach(x => memCache[x.id] = x);
    $('pbody').innerHTML =
      '<p class="mut"><b>Skill memory</b> is what every agent knows about you. It is shared by all agents and stays even when you delete chats.</p>' +
      '<div class="row"><input id="nf" placeholder="Add something to remember"><button class="send" onclick="addMem()">Add</button></div>' +
      '<div class="row"><button class="tool" onclick="location.href=\'/api/memory/export\'">Export</button>' +
      '<button class="tool" onclick="importMem()">Import</button></div>' +
      (m.length ? m.map(x => '<div class="card" id="mc' + x.id + '"><small>' + (x.src === 'user' ? 'added by you' : 'learned') + '</small>' +
        '<div id="mt' + x.id + '">' + esc(x.fact) + '</div><div><i class="lnk ok" onclick="editMem(' + x.id + ')">Edit</i>' +
        '<i class="lnk" onclick="delMem(' + x.id + ')">Delete</i></div></div>').join('') :
        '<p class="mut">Nothing yet. Agents learn as you chat, or add a fact above.</p>') +
      (m.length ? '<button class="tool" onclick="clearMem()">Clear all skill memory</button>' : '') +
      '<div class="card"><b>Chat memory</b><div class="mut">A short summary of this chat. Agents use it to continue where you left off. It is deleted with the chat.</div>' +
      '<textarea id="sm" rows="4" placeholder="No summary yet. It appears after a few messages.">' + esc(s.summary) + '</textarea>' +
      '<button class="tool" onclick="saveSummary()">Save summary</button></div>';
  } catch (e) { $('pbody').innerHTML = '<p class="mut">' + esc(e.message) + '</p>'; }
}
async function addMem() { const v = $('nf').value.trim(); if (!v) return; try { await post('/api/memory', {fact: v}); memPanel(); } catch (e) { toast(e.message); } }
function editMem(id) {
  $('mt' + id).innerHTML = '<textarea id="me' + id + '" rows="3">' + esc(memCache[id].fact) + '</textarea>' +
    '<div class="row" style="margin-top:6px"><button class="send" onclick="saveMem(' + id + ')">Save</button><button class="tool" onclick="memPanel()">Cancel</button></div>';
}
async function saveMem(id) { try { await put('/api/memory/' + id, {fact: $('me' + id).value}); memPanel(); } catch (e) { toast(e.message); } }
async function delMem(id) {
  try { await del('/api/memory/' + id); memPanel();
    toast('Memory deleted.', 'Undo', async () => { try { await post('/api/memory/' + id + '/restore'); memPanel(); } catch (e) { toast(e.message); } });
  } catch (e) { toast(e.message); }
}
async function clearMem() { if (confirm('Delete ALL skill memory? This cannot be undone.')) { await post('/api/memory/clear'); memPanel(); } }
function importMem() { pickJson(async d => { try { const r = await post('/api/memory/import', d); toast('Imported ' + r.imported + ' memories.'); memPanel(); } catch (e) { toast(e.message); } }); }
async function saveSummary() { try { await put('/api/convs/' + conv + '/summary', {summary: $('sm').value}); toast('Summary saved.'); } catch (e) { toast(e.message); } }

/* agents */
async function agPanel() {
  $('ptitle').textContent = 'Agents';
  try {
    agents = await api('/api/agents'); chips();
    $('pbody').innerHTML = '<div class="row"><button class="tool" onclick="location.href=\'/api/custom/export\'">Export my agents</button>' +
      '<button class="tool" onclick="importAg()">Import agents</button></div>' +
      agents.map(a => '<div class="card"><div>' + ava(a.key, a.name) + ' <b>' + esc(a.name) + '</b> <small>' + esc(a.level) + '</small></div>' +
        '<div class="mut">' + esc(a.role) + '</div><div class="mut">' + esc(a.model) + '</div>' +
        (a.custom ? '<div><i class="lnk" onclick="delAg(' + a.id + ')">Delete</i></div>' : '') + '</div>').join('') +
      '<div class="card"><b>Create your own agent</b><input id="agn" placeholder="Name"><input id="agr" placeholder="What it does (short)">' +
      '<textarea id="agp" rows="3" placeholder="Instructions for this agent"></textarea>' +
      '<select id="agl"><option value="sutra">sutra (fast)</option><option value="shloka">shloka (balanced)</option><option value="veda">veda (deep)</option></select>' +
      '<button class="send" onclick="addAg()">Create agent</button></div>';
  } catch (e) { $('pbody').innerHTML = '<p class="mut">' + esc(e.message) + '</p>'; }
}
async function addAg() {
  try { await post('/api/custom', {name: $('agn').value, role: $('agr').value, prompt: $('agp').value, level: $('agl').value}); agPanel(); }
  catch (e) { toast(e.message); }
}
async function delAg(i) { if (confirm('Delete this agent?')) { await del('/api/custom/' + i); if (agent === 'c' + i) agent = 'auto'; agPanel(); } }
function importAg() { pickJson(async d => { try { const r = await post('/api/custom/import', d); toast('Imported ' + r.imported + ' agents.'); agPanel(); } catch (e) { toast(e.message); } }); }

/* models */
async function modPanel() {
  $('ptitle').textContent = 'Models';
  try {
    const m = await api('/api/models');
    $('pbody').innerHTML = '<p class="mut">Model names live in the .env file. Change them there. No restart needed. Deep mode makes Veda and Shloka draft in parallel, then Veda merges the best answer.</p>' +
      m.map(x => '<div class="card"><div><b>' + esc(x.name) + '</b> <small>' + esc(x.role) + '</small></div><div class="mut">' + esc(x.model) + '</div></div>').join('');
  } catch (e) { $('pbody').innerHTML = '<p class="mut">' + esc(e.message) + '</p>'; }
}

/* settings */
async function setPanel() {
  $('ptitle').textContent = 'Settings';
  try {
    const [s, st] = await Promise.all([api('/api/settings'), api('/api/status')]);
    const ok = (v, y, n) => '<span class="' + (v ? 'good' : 'bad') + '">' + (v ? y : n) + '</span>';
    $('pbody').innerHTML =
      '<div class="card"><b>Auto-cleanup</b><div class="mut">Chats you have not touched for a while are marked with a red dot, then deleted after a short warning, together with their chat memory. Skill memory is never touched. Pinned chats are never deleted.</div>' +
      '<div class="switch"><span>Delete old chats</span><button class="pill ' + (s.cleanup_enabled ? 'on' : '') + '" onclick="setCleanup(' + (!s.cleanup_enabled) + ')">' + (s.cleanup_enabled ? 'On' : 'Off') + '</button></div>' +
      '<select id="per" onchange="setPeriod(this.value)">' + s.periods.map(p => '<option value="' + p.secs + '"' + (p.secs === s.cleanup_secs ? ' selected' : '') + '>After ' + p.label + '</option>').join('') + '</select></div>' +
      '<div class="card"><b>Backup</b><div class="mut">Download all chats, skill memory and your agents as one JSON file.</div>' +
      '<button class="tool" onclick="location.href=\'/api/export\'">Export everything</button></div>' +
      '<div class="card"><b>Status</b>' +
      '<div class="switch"><span>Groq API key</span>' + ok(st.key, 'found', 'missing (see README)') + '</div>' +
      '<div class="switch"><span>ffmpeg (odd audio/video formats)</span>' + ok(st.ffmpeg, 'found', 'not installed (optional)') + '</div>' +
      '<div class="switch"><span>PDF reading</span>' + ok(st.pdf, 'ready', 'pip install pypdf') + '</div>' +
      '<div class="switch"><span>Password protection</span>' + ok(st.password, 'on', 'off') + '</div>' +
      '<div class="mut">Version ' + esc(st.version) + ' &middot; listening on ' + esc(st.host) + '</div></div>' +
      '<button class="tool" onclick="toggleTheme()">Switch light / dark</button>';
  } catch (e) { $('pbody').innerHTML = '<p class="mut">' + esc(e.message) + '</p>'; }
}
async function setCleanup(on) { try { await post('/api/settings', {cleanup_enabled: on}); setPanel(); loadConvs(); } catch (e) { toast(e.message); } }
async function setPeriod(v) { try { await post('/api/settings', {cleanup_secs: parseInt(v, 10)}); toast('Saved.'); loadConvs(); } catch (e) { toast(e.message); } }

/* ---------- start ---------- */
(async () => {
  try {
    await loadPlatformInfo();
    const c = await api('/api/config');
    $('appName').textContent = c.name; $('appTag').textContent = c.tagline; document.title = c.name;
    if (!c.name) $('appName').style.display = 'none';
    agents = await api('/api/agents'); chips();
    const items = await loadConvs(); items.length ? openConv(items[0].id) : newChat();
  } catch (e) {
    log.innerHTML = '<div class="welcome"><h2>Cannot reach the server</h2><p>' + esc(e.message) + '</p></div>';
  }
})();
