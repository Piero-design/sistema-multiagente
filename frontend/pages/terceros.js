// G5 · Terceros y DPA (Agente 7). Page of its own: it brings back the functions of the agent's original page
// (audit with a file, organization context, expedientes with download, profile, renewals, chat) through the
// platform API. Human decisions (DPO/Legal approval, profile validation) stay in «Revisión humana».
import { api, authed, session } from '../services/api.js';
import { h, badge, fmtTime, alertBox, spinner } from '../components/ui.js';
import { AGENTS } from '../services/agents-config.js';
import { table } from './dashboard.js';

const KEY = 'terceros';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// Same persisted execution as api.run, polled faster at first: reads answer in ~0.2 s, audits take minutes.
const run = async (action, input, onTick) => {
  const { execution_id } = await api.execute(KEY, action, input);
  let e;
  for (let i = 0; ; i++) {
    e = await api.execution(execution_id);
    onTick?.(e);
    if (e.status === 'succeeded' || e.status === 'failed') break;
    await sleep(i < 10 ? 400 : 2500);
  }
  if (e.status === 'failed') throw new Error(e.error || 'falló');
  return { out: (e.result || {}).output, e };
};

// ---- downloads (generated in the browser from the agent's own expediente) ----
function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = h('a', { href: url, download: name });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
const dlJSON = (name, obj) => download(name, JSON.stringify(obj, null, 2), 'application/json');
const dlMD = (name, md) => download(name, md || '', 'text/markdown;charset=utf-8');
const csvCell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
function dlCSV(name, rows, cols) {
  const lines = [cols.map(([, t]) => csvCell(t)).join(',')].concat(rows.map((r) => cols.map(([k]) => csvCell(r[k])).join(',')));
  download(name, '﻿' + lines.join('\r\n'), 'text/csv;charset=utf-8');
}
// ---- deletion: a human decision (signed-in DPO, from «Revisión humana»); the backend records who deleted what ----
async function eliminar(tipo, id, onDone, nombre) {
  const que = tipo === 'expediente' ? `el expediente ${id} (informe, JSON, copia del contrato y su chat)`
    : tipo === 'documento' ? `el documento «${nombre}» de «${id}» (el perfil ya generado no cambia hasta que lo vuelvas a generar)`
    : `el perfil de «${id}» (los documentos y la configuración se conservan)`;
  if (!session.token) { alert('Para eliminar, inicia sesión como DPO en «Revisión humana» y vuelve a esta página.'); return; }
  if (!confirm(`¿Eliminar ${que}?

Se borran los archivos del agente y no se puede deshacer. Descárgalo antes si lo necesitas.`)) return;
  try { const r = await authed('/api/human/terceros/eliminar', nombre ? { tipo, id, nombre } : { tipo, id }); alert(`Eliminado: ${(r.eliminados || []).length} archivo(s).`); onDone?.(); }
  catch (err) { alert(`No se pudo eliminar: ${err.message}`); }
}
const deleteButton = (tipo, id, onDone, label = 'Eliminar', nombre) =>
  h('button', { class: 'ghost', style: 'color:var(--bad)', title: 'Requiere sesión de DPO', onclick: () => eliminar(tipo, id, onDone, nombre) }, label);

const downloadButtons = (id, det) => h('span', { class: 'row' },
  h('button', { class: 'ghost', onclick: () => dlMD(`${id}.md`, det.informe) }, 'Descargar informe (.md)'),
  h('button', { class: 'ghost', onclick: () => dlJSON(`${id}.json`, det.resultado) }, 'Descargar expediente (.json)'));

const readFile = (file) => new Promise((ok, ko) => {
  const r = new FileReader();
  r.onload = () => ok(String(r.result).split(',')[1] || '');
  r.onerror = () => ko(r.error);
  r.readAsDataURL(file);
});

// Minimal Markdown → DOM for the agent's reports (headings, tables, lists, quotes, bold, italics, code, inline HTML
// such as the radar <svg> stays as text). Built with text nodes only: nothing from the report is parsed as HTML.
function inline(text) {
  const out = []; const re = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const t = m[0];
    out.push(t.startsWith('**') ? h('strong', {}, t.slice(2, -2)) : t.startsWith('`') ? h('code', {}, t.slice(1, -1)) : h('em', {}, t.slice(1, -1)));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
function markdown(md) {
  const box = h('div', { class: 'mdr' }); const lines = String(md || '').replace(/\r/g, '').split('\n');
  for (let i = 0; i < lines.length;) {
    const l = lines[i];
    if (/^\s*<svg[\s>]/i.test(l)) {
      const svg = []; while (i < lines.length) { svg.push(lines[i]); if (/<\/svg>/i.test(lines[i++])) break; }
      box.append(svgImagen(svg.join('\n'), 'Radar de cumplimiento por sección del Anexo A'));
      continue;
    }
    if (/^\s*\|.*\|\s*$/.test(l)) {
      const rows = []; while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) rows.push(lines[i++]);
      const cells = (r) => r.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const body = rows.filter((r) => !/^\s*\|[\s:|-]+\|\s*$/.test(r));
      box.append(h('table', {}, h('thead', {}, h('tr', {}, cells(body[0]).map((c) => h('th', {}, inline(c))))),
        h('tbody', {}, body.slice(1).map((r) => h('tr', {}, cells(r).map((c) => h('td', {}, inline(c))))))));
      continue;
    }
    const hd = l.match(/^(#{1,4})\s+(.*)/);
    if (hd) box.append(h(`h${Math.min(hd[1].length + 1, 5)}`, {}, inline(hd[2])));
    else if (/^\s*[-*]\s+/.test(l)) {
      const ul = h('ul'); while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) ul.append(h('li', {}, inline(lines[i++].replace(/^\s*[-*]\s+/, ''))));
      box.append(ul); continue;
    } else if (/^\s*\d+\.\s+/.test(l)) {
      const ol = h('ol'); while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) ol.append(h('li', {}, inline(lines[i++].replace(/^\s*\d+\.\s+/, ''))));
      box.append(ol); continue;
    } else if (/^>\s?/.test(l)) box.append(h('blockquote', {}, inline(l.replace(/^>\s?/, ''))));
    else if (/^\s*```/.test(l)) {
      const code = []; i++; while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
      box.append(h('pre', {}, code.join('\n')));
    } else if (/^\s*---+\s*$/.test(l)) box.append(h('hr'));
    else if (l.trim()) box.append(h('p', {}, inline(l)));
    i++;
  }
  return box;
}

const card = (...k) => h('div', { class: 'card', style: 'margin-top:14px' }, ...k);
const field = (label, el) => h('div', {}, h('label', {}, label), el);
const busy = (box, t) => box.replaceChildren(card(spinner(t)));
const fail = (box, err) => box.replaceChildren(alertBox('bad', String(err.message || err)));

// ---- expediente view (summary + report + downloads) ----
// ---- traffic light of the 26 controls, as in the agent's original page (web/index.html) ----
const SEM = {
  'Cumple': { c: 'cumple', col: '#2e9d62' }, 'Parcial': { c: 'parcial', col: '#d49a1f' }, 'No cumple': { c: 'nocumple', col: '#d0453a' },
  'Sin evidencia': { c: 'sinevidencia', col: '#8a94a6' }, 'No aplica': { c: 'noaplica', col: '#8a94a6' },
};
const SECCION_DE = {
  'Condiciones de recolección y tratamiento': 'A.2.2', 'Obligaciones con los titulares': 'A.2.3',
  'Privacidad desde el diseño y por defecto': 'A.2.4', 'Compartición, transferencia y comunicación': 'A.2.5',
  'Consideraciones de seguridad': 'A.3',
};
const estadoBadge = (e) => h('span', { class: `sem-badge ${(SEM[e] || {}).c || ''}` }, e || '—');
const bandaColor = (b) => (/alto/i.test(b || '') ? SEM['No cumple'].col : /medio/i.test(b || '') ? SEM.Parcial.col : SEM.Cumple.col);

// An SVG (the agent's radar) shown as an image: drawn by the browser, never executed.
const svgImagen = (svg, alt) => h('img', { class: 'radar-img', alt, src: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg) });

function huella(r) {
  const s = r.resumen || {};
  return h('div', {},
    h('div', { class: 'huella' }, (r.controles || []).map((c) => h('div', {
      class: `casilla ${(SEM[c.estado] || {}).c || ''}${c.ambito === 'Propio Agente 7' ? ' propio' : ''}`,
      title: `${c.control} · ${c.titulo || ''}\n${c.estado} · severidad ${c.severidad || '—'}\n${c.observacion || ''}`,
    }, String(c.control || '').replace(/^A\./, '')))),
    h('div', { class: 'leyenda' },
      h('span', {}, h('i', { style: `background:${SEM.Cumple.col}` }), `Cumple ${s.cumple ?? 0}`),
      h('span', {}, h('i', { style: `background:${SEM.Parcial.col}` }), `Parcial ${s.parcial ?? 0}`),
      h('span', {}, h('i', { style: `background:${SEM['No cumple'].col}` }), `No cumple ${s.no_cumple ?? 0}`),
      h('span', {}, h('i', { style: 'border:1.5px dashed #8a94a6' }), `Sin evidencia ${s.sin_evidencia ?? 0}`),
      h('span', {}, h('i', { style: 'background:#8a94a6;opacity:.45' }), `No aplica ${s.no_aplica ?? 0}`),
      h('span', {}, '● ámbito propio del Agente 7')));
}

/* Radar of the base score per Annex A section. Same drawing as radarSVG in the agent (n8n/lib/prompts.js and
   web/index.html); only the colors change so it reads on the light and dark themes of the platform. */
function radarSVG(porDimension, controles) {
  const ejes = Object.entries(porDimension || {}); const n = ejes.length;
  if (n < 3) return '';
  const col = { tinta: '#8f99ab', suave: '#8f99ab', red: '#8f99ab55', area: '#6c8cff', ref: '#2e9d62' };
  const W = 560, H = 400, cx = W / 2, cy = 205, R = 120;
  const ang = (i) => (-90 + (360 / n) * i) * Math.PI / 180;
  const pt = (i, v) => [cx + R * (v / 100) * Math.cos(ang(i)), cy + R * (v / 100) * Math.sin(ang(i))];
  const f = (x) => x.toFixed(1);
  const anillo = (v) => ejes.map((_, i) => pt(i, v).map(f).join(',')).join(' ');
  const escX = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const partir = (t, max) => { const ls = []; let a = ''; for (const w of t.split(' ')) { if (a && (a + ' ' + w).length > max) { ls.push(a); a = w; } else a = a ? a + ' ' + w : w; } if (a) ls.push(a); return ls; };
  const nCtl = (k) => { const sec = SECCION_DE[k]; return sec && Array.isArray(controles) ? controles.filter((c) => String(c.control).startsWith(sec + '.') && c.estado !== 'No aplica').length : null; };
  const o = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="system-ui,-apple-system,Segoe UI,sans-serif">`];
  for (const v of [20, 40, 60, 100]) o.push(`<polygon points="${anillo(v)}" fill="none" stroke="${col.red}" stroke-width="1"/>`);
  o.push(`<polygon points="${anillo(80)}" fill="none" stroke="${col.ref}" stroke-width="1.5" stroke-dasharray="5 4"/>`);
  ejes.forEach((_, i) => { const [x, y] = pt(i, 100); o.push(`<line x1="${cx}" y1="${cy}" x2="${f(x)}" y2="${f(y)}" stroke="${col.red}" stroke-width="1"/>`); });
  for (const v of [20, 40, 60, 80, 100]) o.push(`<text x="${cx + 4}" y="${f(cy - R * v / 100 - 2)}" font-size="9" fill="${v === 80 ? col.ref : col.suave}">${v}</text>`);
  o.push(`<polygon points="${ejes.map(([, v], i) => pt(i, v ?? 0).map(f).join(',')).join(' ')}" fill="${col.area}" fill-opacity="0.22" stroke="${col.area}" stroke-width="2" stroke-linejoin="round"/>`);
  ejes.forEach(([, v], i) => { const [x, y] = pt(i, v ?? 0); o.push(`<circle cx="${f(x)}" cy="${f(y)}" r="3.5" fill="${v === null ? '#fff' : col.area}" stroke="${col.area}" stroke-width="1.5"/>`); });
  ejes.forEach(([k, v], i) => {
    const a = ang(i), c = Math.cos(a), sn = Math.sin(a), x = cx + (R + 18) * c, y = cy + (R + 18) * sn;
    const anc = Math.abs(c) < 0.2 ? 'middle' : c > 0 ? 'start' : 'end', nc = nCtl(k);
    const ls = [`${SECCION_DE[k] ? SECCION_DE[k] + ' · ' : ''}${v === null ? '—' : v}${nc === null ? '' : ` (${nc} ctrl.)`}`, ...partir(k, 24)];
    const y0 = sn < -0.5 ? y - ls.length * 13 + 9 : sn > 0.5 ? y + 9 : y - (ls.length * 13) / 2 + 9;
    o.push(`<text x="${f(x)}" y="${f(y0)}" font-size="11" fill="${col.tinta}" text-anchor="${anc}">${ls.map((l, j) => `<tspan x="${f(x)}" dy="${j ? 13 : 0}"${j ? '' : ' font-weight="700"'}>${escX(l)}</tspan>`).join('')}</text>`);
  });
  o.push(`<text x="12" y="${H - 10}" font-size="10" fill="${col.suave}">Puntaje base por sección, 0-100, sin penalización por alertas. Línea discontinua: 80 (riesgo bajo).</text></svg>`);
  return o.join('');
}

function desglose(r) {
  const p = r.puntaje_proveedor || {}, dims = Object.entries(p.por_dimension || {});
  if (!dims.length) return null;
  return h('div', { class: 'desglose' },
    h('div', { class: 'dims' }, dims.map(([k, v]) => h('div', { class: 'dim' },
      h('span', {}, SECCION_DE[k] ? h('strong', {}, SECCION_DE[k] + ' ') : null, k),
      h('div', { class: 'barra' }, h('span', { style: `width:${v ?? 0}%;background:${v === null ? '#8a94a6' : v >= 80 ? SEM.Cumple.col : v >= 50 ? SEM.Parcial.col : SEM['No cumple'].col}` })),
      h('span', { class: 'num' }, v ?? '—'))),
      h('p', { class: 'small mute' }, 'Puntaje base por sección del Anexo A de ISO/IEC 27701:2025, sin la penalización por alertas.')),
    svgImagen(radarSVG(p.por_dimension, r.controles), 'Radar de cumplimiento por sección del Anexo A'));
}

// ---- chat about an expediente or an organization (pims/chat): same component in the expediente and in «Chat» ----
function chatBox({ ambito, id, organizacion, nombre }) {
  const log = h('div', { class: 'chat-log' });
  const q = h('textarea', { placeholder: ambito === 'expediente'
    ? `Pregunta sobre ${nombre || 'este expediente'}: p. ej. ¿qué cláusulas habría que pedirle para subir el puntaje?`
    : `Pregunta sobre ${nombre || 'la organización'}: p. ej. ¿qué terceros sin DPA tratan datos sensibles?`, style: 'min-height:80px' });
  const vacio = () => h('p', { class: 'mute small' }, 'Todavía no hay preguntas. El chat solo consulta: no modifica el expediente, el puntaje ni el perfil.');
  const burbuja = (m) => h('div', { class: `chat-msg ${m.rol === 'usuario' ? 'yo' : 'ia'}` },
    h('div', { class: 'small mute' }, `${m.rol === 'usuario' ? `Pregunta${m.usuario ? ' · ' + m.usuario : ''}` : 'Respuesta'} · ${fmtTime(m.fecha)}${m.modelo ? ' · ' + m.modelo : ''}`),
    m.rol === 'usuario' ? h('div', {}, m.texto) : markdown(m.texto));
  async function cargar() {
    try {
      const { out: c } = await run('conversacion', { ambito, id });
      const ms = c.mensajes || [];
      log.replaceChildren(...(ms.length ? ms.map(burbuja) : [vacio()]));
      log.scrollTop = log.scrollHeight;
    } catch (err) { fail(log, err); }
  }
  const send = h('button', { onclick: async () => {
    const pregunta = q.value.trim();
    if (!pregunta) return;
    send.disabled = true;
    if (log.querySelector('p.mute')) log.replaceChildren();
    log.append(burbuja({ rol: 'usuario', texto: pregunta, fecha: new Date().toISOString() }));
    const wait = h('div', { class: 'chat-msg ia' }, spinner('El modelo está respondiendo…'));
    log.append(wait); log.scrollTop = log.scrollHeight;
    try {
      const { out: st } = await run('chat', { ambito, id, organizacion, pregunta, usuario: 'plataforma' });
      if (st.estado !== 'terminado') throw new Error(st.mensaje || 'sin respuesta');
      q.value = ''; await cargar();
    } catch (err) { wait.replaceChildren(alertBox('bad', err.message)); }
    send.disabled = false;
  } }, 'Preguntar');
  q.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey)) send.click(); });
  cargar();
  return h('div', {}, log, q, h('div', { class: 'row', style: 'margin-top:10px' }, send, h('span', { class: 'small mute' }, 'Ctrl+Enter para enviar')));
}

function expedienteView(det, onDeleted) {
  const r = det.resultado || {}, reg = r._registro || {}, p = r.puntaje_proveedor || {}, c = reg.contexto || {};
  const res = r.resumen || {};
  const fuente = { perfil: 'perfil de la organización', bd: 'base de datos del PIMS', ambos: 'perfil + base de datos' }[c.fuente] || 'perfil de la organización';
  return h('div', {},
    h('div', { class: 'row', style: 'justify-content:space-between' },
      h('h2', {}, `${(r.tercero || {}).nombre || reg.id_registro} · ${reg.id_registro || ''}`),
      h('span', { class: 'row' }, downloadButtons(reg.id_registro || 'expediente', det),
        reg.id_registro ? deleteButton('expediente', reg.id_registro, onDeleted) : null)),
    h('div', { class: 'kpis', style: 'margin:10px 0' },
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Puntaje'), h('div', { class: 'kpi', style: `color:${bandaColor(p.banda)}` }, p.valor ?? '—', h('span', { style: 'font-size:14px;font-weight:500' }, '/100')),
        h('div', { class: 'small' }, `${p.banda || ''}${p.base !== undefined ? ` · base ${p.base} − ${p.penalizacion}` : ''}`)),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Dictamen'), h('div', { style: 'font-weight:700' }, r.dictamen || '—')),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Aprobación'), h('div', { style: 'font-weight:700' }, (r.aprobacion || {}).estado || '—')),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Controles'),
        h('div', { class: 'small' }, `${res.cumple ?? 0} cumple · ${res.parcial ?? 0} parcial · ${res.no_cumple ?? 0} no cumple · ${res.sin_evidencia ?? 0} sin evidencia`))),
    h('p', { class: 'small mute' }, `Modelo ${reg.modelo || '—'} · correcciones del JSON: ${reg.reintentos ?? 0} · contexto: ${fuente}` +
      (c.bd ? ` (esquema ${c.bd.esquema}, ${Object.values(c.bd.filas || {}).reduce((a, b) => a + b, 0)} filas)` : '')),
    c.aviso ? alertBox('warn', c.aviso) : null,
    h('h3', { style: 'margin:14px 0 8px;font-size:15px' }, 'Huella del contrato'), huella(r), desglose(r),
    pestanasExpediente(det));
}

// Inner tabs of an expediente, as in the agent's original page: Informe · Alertas · Historial · Preguntar · Matriz · JSON.
function pestanasExpediente(det) {
  const r = det.resultado || {}, reg = r._registro || {}, alertas = r.alertas || [];
  const hist = (r.aprobacion || {}).historial || [];
  const org = (r.organizacion || {}).id || reg.organizacion || '';
  let chat = null;                                   // built once: keeps the conversation while switching tabs
  const P = [
    ['informe', 'Informe', () => (det.informe ? markdown(det.informe) : h('p', { class: 'mute' }, '(sin informe)'))],
    ['alertas', `Alertas (${alertas.length})`, () => (alertas.length ? h('div', {}, alertas.map((a) => h('div', { class: `alerta-g5 ${a.prioridad === 'Alta' ? 'alta' : 'media'}` },
      h('strong', {}, `${a.prioridad} · ${a.tipo}`), ` — ${a.descripcion}`,
      a.controles_relacionados ? h('span', { class: 'small mute' }, ` (${a.controles_relacionados.join(', ')})`) : null)))
      : h('p', { class: 'mute' }, 'Sin alertas.'))],
    ['historial', `Historial (${hist.length})`, () => (hist.length ? table(['Fecha', 'Quién', 'Decisión', 'Comentario'], hist.map((x) => [
      fmtTime(x.fecha), h('span', {}, x.cargo || x.rol || '', h('div', { class: 'small mute' }, x.usuario || '')),
      h('span', {}, x.decision === 'aprobar' ? 'Aprobó' : 'Rechazó', h('div', { class: 'small mute' }, `${x.estado_anterior || ''} → ${x.estado_nuevo || ''}`)),
      x.comentario || '—']))
      : h('p', { class: 'mute' }, 'Nadie ha decidido todavía. El primer paso es del DPO (en «Revisión humana»).'))],
    ['preguntar', 'Preguntar', () => (chat ||= chatBox({ ambito: 'expediente', id: reg.id_registro, organizacion: org, nombre: (r.tercero || {}).nombre }))],
    ['matriz', `Matriz (${(r.controles || []).length})`, () => table(['Control', 'Estado', 'Severidad', 'Evidencia / observación'], (r.controles || []).map((x) => [
      h('span', {}, h('strong', {}, x.control), h('br'), h('span', { class: 'small mute' }, x.titulo || '')), estadoBadge(x.estado), x.severidad || '',
      h('span', { class: 'small' }, String(x.evidencia || '').slice(0, 220), x.observacion ? h('div', { class: 'mute' }, x.observacion) : null)]))],
    ['json', 'Registro JSON', () => h('pre', {}, JSON.stringify(r, null, 2))],
  ];
  let actual = 'informe';
  const barra = h('div', { class: 'tabs exp-tabs' }), cuerpo = h('div', { class: 'exp-cuerpo' });
  const dibujar = () => {
    barra.replaceChildren(...P.map(([k, t]) => h('button', { class: k === actual ? 'on' : '', 'data-p': k, onclick: () => { actual = k; dibujar(); } }, t)));
    cuerpo.replaceChildren(P.find(([k]) => k === actual)[2]());
  };
  dibujar();
  return h('div', { style: 'margin-top:16px' }, barra, cuerpo);
}

// ---------------------------------------------------------------- tabs
async function tabAuditar(box, orgs) {
  const f = h('form', {},
    field('Organización', h('select', { name: 'organizacion' }, orgs.map((o) => h('option', { value: o.id, selected: o.id === 'unsa' }, `${o.nombre} (${o.id})`)))),
    field('Proveedor (opcional)', h('input', { name: 'proveedor', placeholder: 'Nombre del tercero' })),
    field('Contexto de la organización', h('select', { name: 'contexto' },
      h('option', { value: 'perfil' }, 'Perfil de la organización (como el agente original)'),
      h('option', { value: 'bd' }, 'Base de datos del PIMS (Gestitel, solo lectura)'),
      h('option', { value: 'ambos' }, 'Perfil + base de datos'))),
    field('Fecha de referencia (opcional)', h('input', { name: 'fecha_ref', type: 'date' })),
    field('Contrato: archivo .pdf, .md o .txt (opcional)', h('input', { name: 'archivo', type: 'file', accept: '.pdf,.md,.txt' })),
    field('…o pega el texto del contrato', h('textarea', { name: 'contrato_texto', style: 'min-height:200px' },
      AGENTS.terceros.actions[0].fields.find((x) => x.name === 'contrato_texto').demo)),
    h('button', { type: 'submit', style: 'margin-top:14px' }, 'Auditar contrato'));
  const out = h('div');
  f.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const btn = f.querySelector('button'); btn.disabled = true;
    const v = Object.fromEntries(['organizacion', 'proveedor', 'contexto', 'fecha_ref', 'contrato_texto'].map((k) => [k, f.elements[k].value]));
    const input = { organizacion: v.organizacion, contexto: v.contexto };
    if (v.proveedor.trim()) input.proveedor = v.proveedor.trim();
    if (v.fecha_ref) input.fecha_ref = v.fecha_ref;
    const t0 = Date.now();
    try {
      const file = f.elements.archivo.files[0];
      if (file) input.archivo = { nombre: file.name, base64: await readFile(file) };
      else input.contrato_texto = v.contrato_texto;
      busy(out, 'Auditando…');
      const { out: st, e } = await run('auditar', input, (s) => busy(out, `Estado: ${s.status} · ${Math.round((Date.now() - t0) / 1000)} s (con un modelo real, entre 30 s y unos minutos)`));
      if (st.estado !== 'terminado') {
        out.replaceChildren(alertBox('bad', `La auditoría terminó con error: ${st.mensaje}`),
          st.nota_plataforma ? alertBox('sim', st.nota_plataforma) : null,
          (st.errores || []).length ? card(h('h2', {}, 'Errores'), h('pre', {}, st.errores.join('\n'))) : null);
      } else {
        out.replaceChildren(e.simulated ? alertBox('sim', 'Modo simulado (LLM_MODE=mock)') : null,
          (st.advertencias || []).map((a) => alertBox('warn', a)), card(expedienteView(st.expediente || {}, () => out.replaceChildren(alertBox('info', 'Expediente eliminado.')))));
      }
    } catch (err) { fail(out, err); }
    btn.disabled = false;
  });
  box.replaceChildren(card(h('h2', {}, 'Auditar contrato de encargo (DPA)'),
    h('p', { class: 'small mute' }, 'El modelo califica cada control; el puntaje y el dictamen los calcula el código. El expediente queda «Pendiente DPO»: la aprobación es humana (Revisión humana). Los archivos .docx: guárdalos como PDF o pega su texto.'), f), out);
}

async function tabExpedientes(box, orgs) {
  const sel = h('select', {}, h('option', { value: '' }, 'Todas las organizaciones'), orgs.map((o) => h('option', { value: o.id }, o.nombre)));
  const list = h('div'), view = h('div');
  const cols = [['id_registro', 'Expediente'], ['organizacion', 'Organización'], ['proveedor', 'Proveedor'], ['fecha', 'Fecha'], ['puntaje', 'Puntaje'],
    ['banda', 'Banda'], ['dictamen', 'Dictamen'], ['estado', 'Estado'], ['riesgo_pii', 'Riesgo PII'], ['modelo', 'Modelo']];
  async function load() {
    busy(list, 'Cargando expedientes…');
    try {
      const { out } = await run('registro', sel.value ? { organizacion: sel.value } : {});
      const regs = out.registros || [];
      const detalle = async (id) => (await run('detalle', { id })).out;
      list.replaceChildren(card(
        h('div', { class: 'row', style: 'justify-content:space-between' }, h('h2', {}, `${regs.length} expediente(s)`),
          h('span', { class: 'row' },
            h('button', { class: 'ghost', onclick: () => dlCSV(`expedientes_${sel.value || 'todas'}.csv`, regs, cols) }, 'Descargar listado (.csv)'),
            h('button', { class: 'ghost', onclick: async (ev) => {
              ev.target.disabled = true; ev.target.textContent = 'Reuniendo…';
              try {
                const todos = [];
                for (const r of regs) todos.push(await detalle(r.id_registro));
                dlJSON(`expedientes_${sel.value || 'todas'}.json`, todos.map((d) => ({ expediente: d.resultado, informe_markdown: d.informe })));
              } catch (err) { list.prepend(alertBox('bad', err.message)); }
              ev.target.disabled = false; ev.target.textContent = 'Descargar todos (.json)';
            } }, 'Descargar todos (.json)'))),
        regs.length ? table(['Expediente', 'Proveedor', 'Puntaje', 'Dictamen', 'Estado', ''], regs.map((r) => [
          h('span', {}, r.id_registro, h('br'), h('span', { class: 'small mute' }, `${r.organizacion} · ${r.fecha || ''}`)),
          r.proveedor || '—', `${r.puntaje ?? '—'} · ${r.banda || ''}`, r.dictamen || '', r.estado || '',
          h('span', { class: 'row' },
            h('button', { class: 'ghost', onclick: async () => { busy(view, 'Abriendo…'); try { view.replaceChildren(card(expedienteView(await detalle(r.id_registro), () => { view.replaceChildren(); load(); }))); view.scrollIntoView(); } catch (err) { fail(view, err); } } }, 'Ver'),
            h('button', { class: 'ghost', onclick: async () => { try { const d = await detalle(r.id_registro); dlMD(`${r.id_registro}.md`, d.informe); } catch (err) { fail(view, err); } } }, '.md'),
            h('button', { class: 'ghost', onclick: async () => { try { const d = await detalle(r.id_registro); dlJSON(`${r.id_registro}.json`, d.resultado); } catch (err) { fail(view, err); } } }, '.json'),
            deleteButton('expediente', r.id_registro, () => { view.replaceChildren(); load(); }))]))
          : h('p', { class: 'mute' }, 'Sin expedientes.')));
    } catch (err) { fail(list, err); }
  }
  sel.addEventListener('change', load);
  box.replaceChildren(card(h('div', { class: 'row' }, h('strong', {}, 'Organización'), h('span', { style: 'min-width:280px' }, sel)),
    h('p', { class: 'small mute' }, 'Los expedientes se guardan como archivos del agente (datos/registro/*.json y *.md); la descarga es una copia exacta.')), list, view);
  load();
}

async function tabOrganizacion(box, orgs, reload) {
  const sel = h('select', {}, orgs.map((o) => h('option', { value: o.id, selected: o.id === 'unsa' }, `${o.nombre} (${o.id})`)));
  const det = h('div');
  async function load() {
    const id = sel.value, o = orgs.find((x) => x.id === id) || {};
    busy(det, 'Cargando…');
    try {
      const [{ out: perfil }, { out: docs }] = await Promise.all([run('perfil', { organizacion: id }).catch(() => ({ out: {} })), run('documentos', { organizacion: id })]);
      const val = perfil.validacion || {};
      const sinDpa = o.terceros_sin_dpa_evaluado || [];
      const up = h('input', { type: 'file', accept: '.pdf,.md,.txt' }), upOut = h('span', { class: 'small' });
      det.replaceChildren(
        card(h('h2', {}, 'Perfil de la organización'),
          perfil.texto ? h('div', {},
            h('p', { class: 'small' }, `Estado: `, h('strong', {}, val.estado || '—'), ` · formato ${val.valido ? 'válido' : 'con errores'} · ${val.documentos ?? '?'} documento(s) de base`),
            !String(val.estado || '').startsWith('Validado') ? alertBox('warn', 'El perfil está en borrador: lo valida el DPO en «Revisión humana».') : null,
            h('span', { class: 'row' }, h('button', { class: 'ghost', onclick: () => dlMD(`perfil_${id}.md`, perfil.texto) }, 'Descargar perfil (.md)'),
              deleteButton('perfil', id, load, 'Eliminar perfil')),
            h('details', {}, h('summary', {}, 'Ver perfil'), markdown(perfil.texto)))
            : h('p', { class: 'mute' }, 'Esta organización todavía no tiene perfil.'),
          h('div', { class: 'row', style: 'margin-top:10px' },
            h('button', { onclick: async (ev) => {
              ev.target.disabled = true; const t0 = Date.now();
              const msg = h('span', { class: 'small' }); ev.target.after(msg);
              try {
                const { out: st } = await run('perfilar', { organizacion: id }, (s) => { msg.textContent = ` ${s.status} · ${Math.round((Date.now() - t0) / 1000)} s`; });
                msg.textContent = st.estado === 'terminado' ? ' ✔ Perfil generado (Borrador)' : ` ✖ ${st.mensaje}`;
                if (st.estado === 'terminado') load();
              } catch (err) { msg.textContent = ' ✖ ' + err.message; }
              ev.target.disabled = false;
            } }, 'Generar perfil desde los documentos')),
          h('p', { class: 'small mute' }, 'El perfilador (Agente 1 en el código del grupo) resume los documentos institucionales. Puede tardar varios minutos.')),
        card(h('h2', {}, `Documentos institucionales (${(docs.documentos || []).length})`),
          (docs.documentos || []).length ? table(['Documento', 'Tamaño', ''], docs.documentos.map((d) => [d.nombre, d.tam, deleteButton('documento', id, load, 'Eliminar', d.nombre)])) : h('p', { class: 'mute' }, 'Sin documentos.'),
          h('div', { class: 'row', style: 'margin-top:10px' }, h('span', { style: 'max-width:340px' }, up),
            h('button', { class: 'ghost', onclick: async () => {
              const file = up.files[0]; if (!file) return;
              upOut.textContent = 'Subiendo…';
              try {
                const input = { organizacion: id, nombre: file.name };
                if (/\.pdf$/i.test(file.name)) input.base64 = await readFile(file); else input.texto = await file.text();
                await run('subir_documento', input); upOut.textContent = '✔ Guardado'; load();
              } catch (err) { upOut.textContent = '✖ ' + err.message; }
            } }, 'Subir documento'), upOut)),
        card(h('h2', {}, `Terceros sin DPA evaluado (${sinDpa.length})`),
          sinDpa.length ? table(['Tercero / servicio', 'Tipo', 'Proceso', 'Datos'], sinDpa.map((t) => {
            // the agent lists names; the profile has the detail of each third party
            const n = typeof t === 'string' ? t : (t['tercero / servicio'] || t.nombre || '');
            const d = (perfil.terceros || []).find((x) => x['tercero / servicio'] === n) || (typeof t === 'object' ? t : {});
            return [n, d.tipo || '', d.proceso || '', d['datos que trataría'] || ''];
          }))
            : h('p', { class: 'mute' }, 'Ninguno (o la organización no tiene perfil).')));
    } catch (err) { fail(det, err); }
  }
  sel.addEventListener('change', load);
  // new organization
  const nf = h('form', {}, h('div', { class: 'grid g2' },
    field('Id (minúsculas, números y _)', h('input', { name: 'id', placeholder: 'mi_organizacion' })),
    field('Nombre', h('input', { name: 'nombre' })),
    field('Jurisdicción', h('input', { name: 'jurisdiccion', value: 'peru' })),
    field('Cargo del DPO', h('input', { name: 'cargo_dpo', value: 'Oficial de Datos Personales' })),
    field('Cargo de Legal', h('input', { name: 'cargo_legal', value: 'Asesoría Legal' }))),
  h('button', { type: 'submit', style: 'margin-top:12px' }, 'Crear organización'));
  const nOut = h('div');
  nf.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const v = Object.fromEntries(['id', 'nombre', 'jurisdiccion', 'cargo_dpo', 'cargo_legal'].map((k) => [k, nf.elements[k].value.trim()]));
    try { await run('crear_organizacion', v); nOut.replaceChildren(alertBox('info', `Organización «${v.id}» creada.`)); reload(); } catch (err) { fail(nOut, err); }
  });
  box.replaceChildren(card(h('div', { class: 'row' }, h('strong', {}, 'Organización'), h('span', { style: 'min-width:280px' }, sel))), det,
    card(h('details', {}, h('summary', {}, 'Nueva organización'), nf, nOut)));
  load();
}

async function tabRenovaciones(box) {
  busy(box, 'Calculando alertas…');
  try {
    const { out } = await run('renovaciones', {});
    const regs = out.registros_con_alertas || [];
    const rows = regs.flatMap((r) => (r.alertas || []).map((a) => ({ ...a, id_registro: r.id_registro, proveedor: r.proveedor, organizacion: r.organizacion, fin_vigencia: r.fin_vigencia })));
    box.replaceChildren(card(h('div', { class: 'row', style: 'justify-content:space-between' },
      h('h2', {}, `Renovaciones y vencimientos al ${out.fecha_referencia}`),
      rows.length ? h('button', { class: 'ghost', onclick: () => dlCSV(`renovaciones_${out.fecha_referencia}.csv`, rows,
        [['id_registro', 'Expediente'], ['organizacion', 'Organización'], ['proveedor', 'Proveedor'], ['fin_vigencia', 'Fin de vigencia'], ['prioridad', 'Prioridad'], ['tipo', 'Tipo'], ['descripcion', 'Descripción']]) }, 'Descargar (.csv)') : null),
    rows.length ? table(['Proveedor', 'Fin de vigencia', 'Prioridad', 'Alerta'], rows.map((a) => [h('span', {}, a.proveedor, h('br'), h('span', { class: 'small mute' }, a.id_registro)), a.fin_vigencia || '—', a.prioridad, a.descripcion]))
      : h('p', { class: 'mute' }, 'No hay contratos por vencer ni renovar.')));
  } catch (err) { fail(box, err); }
}

async function tabChat(box, orgs) {
  const { out } = await run('registro', {}).catch(() => ({ out: { registros: [] } }));
  const regs = out.registros || [];
  const ambito = h('select', {}, h('option', { value: 'organizacion' }, 'Una organización'), h('option', { value: 'expediente' }, 'Un expediente'));
  const objetivo = h('select');
  const zona = h('div');
  const fill = () => objetivo.replaceChildren(...(ambito.value === 'expediente'
    ? regs.map((r) => h('option', { value: r.id_registro, 'data-org': r.organizacion, 'data-nombre': r.proveedor || r.id_registro }, `${r.proveedor || r.id_registro} · ${r.id_registro}`))
    : orgs.map((o) => h('option', { value: o.id, 'data-org': o.id, 'data-nombre': o.nombre }, o.nombre))));
  const montar = () => {
    const o = objetivo.selectedOptions[0];
    zona.replaceChildren(o ? chatBox({ ambito: ambito.value, id: o.value, organizacion: o.dataset.org, nombre: o.dataset.nombre })
      : h('p', { class: 'mute' }, 'No hay nada que elegir todavía.'));
  };
  ambito.addEventListener('change', () => { fill(); montar(); });
  objetivo.addEventListener('change', montar);
  fill();
  box.replaceChildren(card(h('h2', {}, 'Chat sobre una organización o un expediente'),
    h('p', { class: 'small mute' }, 'Para un expediente también puedes abrirlo en «Expedientes» y usar su pestaña «Preguntar».'),
    h('div', { class: 'grid g2' }, field('Ámbito', ambito), field('Organización o expediente', objetivo)),
    h('div', { style: 'margin-top:12px' }, zona)));
  montar();
}

async function tabHistorial(box, agentId) {
  const rows = await api.executions(agentId);
  box.replaceChildren(card(h('h2', {}, 'Historial de ejecuciones'), rows.length ? table(['Hora', 'Acción', 'Estado', 'Modo', 'Error'],
    rows.map((r) => [fmtTime(r.created_at), r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || ''])) : h('span', { class: 'mute' }, 'Sin ejecuciones todavía.')));
}

// ---------------------------------------------------------------- page
const ESTILO = `.mdr{margin:8px 0;line-height:1.55}.mdr h2,.mdr h3{font-size:16px;margin:18px 0 6px}.mdr h4,.mdr h5{font-size:14px;margin:14px 0 4px}
.mdr p{margin:6px 0}.mdr ul,.mdr ol{margin:6px 0 6px 20px;padding:0}.mdr table{margin:8px 0;font-size:13px}
.mdr blockquote{margin:8px 0;padding:6px 12px;border-left:3px solid var(--brand);color:var(--mute)}.mdr code{font:12px ui-monospace,Consolas,monospace}
.huella{display:grid;grid-template-columns:repeat(auto-fill,minmax(62px,1fr));gap:3px}
.casilla{border-radius:4px;padding:6px 4px 5px;font:12px ui-monospace,Consolas,monospace;text-align:center;color:#fff;border:2px solid transparent;position:relative;cursor:default}
.casilla.cumple{background:#2e9d62}.casilla.parcial{background:#d49a1f}.casilla.nocumple{background:#d0453a}
.casilla.sinevidencia{background:transparent;color:var(--mute);border:2px dashed #8a94a6}.casilla.noaplica{background:#8a94a640;color:var(--mute)}
.casilla.propio::after{content:"";position:absolute;top:3px;right:3px;width:5px;height:5px;border-radius:50%;background:currentColor;opacity:.85}
.leyenda{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;color:var(--mute);margin:8px 0 4px}
.leyenda i{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:5px}
.desglose{display:grid;grid-template-columns:minmax(0,420px) minmax(0,1fr);gap:18px;align-items:center;margin:14px 0}
.dims{display:grid;gap:8px;align-content:start}.dim{display:grid;grid-template-columns:1fr 120px 44px;gap:10px;align-items:center;font-size:13px}
.barra{height:8px;background:#8a94a633;border-radius:4px;overflow:hidden}.barra span{display:block;height:100%}.num{text-align:right;font-variant-numeric:tabular-nums}
.radar-img{display:block;width:100%;max-width:560px;height:auto;margin:6px auto}
.mdr .radar-img{background:#fff;border-radius:8px;padding:8px}
.sem-badge{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;font-weight:700;white-space:nowrap;color:#fff}
.sem-badge.cumple{background:#2e9d62}.sem-badge.parcial{background:#d49a1f}.sem-badge.nocumple{background:#d0453a}
.sem-badge.sinevidencia{background:transparent;color:var(--mute);border:1.5px dashed #8a94a6}.sem-badge.noaplica{background:#8a94a640;color:var(--mute)}
.alerta-g5{padding:8px 12px;border-radius:8px;margin:6px 0;font-size:14px;border-left:4px solid}
.alerta-g5.alta{background:var(--bad-bg);border-color:#d0453a}.alerta-g5.media{background:var(--warn-bg);border-color:#d49a1f}
.exp-tabs{margin:6px 0 10px;border-bottom:1px solid var(--line);padding-bottom:8px}.exp-tabs button{padding:6px 12px;font-size:14px}
.chat-log{max-height:460px;overflow:auto;margin-bottom:10px;display:grid;gap:8px}
.chat-msg{padding:8px 12px;border-radius:10px;border:1px solid var(--line)}.chat-msg.yo{background:var(--bg);margin-left:15%}
.chat-msg.ia{border-left:3px solid var(--brand);margin-right:5%}.chat-msg .mdr{margin:4px 0}
@media (max-width:900px){.desglose{grid-template-columns:1fr}}`;

export async function tercerosPage(root) {
  if (!document.getElementById('estilo-g5')) document.head.append(h('style', { id: 'estilo-g5' }, ESTILO));
  const cfg = AGENTS.terceros;
  const detail = await api.agents().then((l) => l.find((a) => a.group === cfg.group));
  root.append(h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, `G${cfg.group} · ${cfg.title} (Agente 7)`), badge(detail.status)),
    h('p', { class: 'sub' }, 'Audita contratos de encargo de tratamiento (DPA) contra ISO/IEC 27701:2025 y la Ley 29733. El modelo califica los 26 controles; el puntaje y el dictamen los calcula el código. Las aprobaciones DPO → Legal y la validación del perfil se hacen en «Revisión humana».'));
  if (detail.reason) root.append(alertBox(detail.status === 'caido' ? 'bad' : 'warn', detail.reason));

  // The tabs show at once; the organizations load in the background (the tabs that need them wait for them).
  let orgs = [];
  const loadOrgs = async () => { try { orgs = (await run('organizaciones', {})).out.organizaciones || []; } catch { orgs = [{ id: 'unsa', nombre: 'UNSA' }]; } };
  let orgsP = loadOrgs();
  const conOrgs = (fn) => async (b) => { busy(b, 'Cargando organizaciones…'); await orgsP; return fn(b); };

  const TABS = [['Auditar', conOrgs((b) => tabAuditar(b, orgs))], ['Expedientes', conOrgs((b) => tabExpedientes(b, orgs))],
    ['Organización y perfil', conOrgs((b) => tabOrganizacion(b, orgs, async () => { orgsP = loadOrgs(); await orgsP; }))],
    ['Renovaciones', (b) => tabRenovaciones(b)], ['Chat', conOrgs((b) => tabChat(b, orgs))], ['Historial', (b) => tabHistorial(b, detail.id)]];
  const pedida = new URLSearchParams(location.search).get('tab');          // e.g. /agentes/terceros?tab=Expedientes
  let current = (TABS.find(([t]) => t === pedida) || TABS[0])[0];
  const tabs = h('div', { class: 'tabs' }), box = h('div');
  const draw = () => {
    tabs.replaceChildren(...TABS.map(([t]) => h('button', { class: t === current ? 'on' : '', onclick: () => { current = t; draw(); } }, t)));
    TABS.find(([t]) => t === current)[1](box).catch((err) => fail(box, err));
  };
  root.append(tabs, box,
    h('p', { class: 'small mute', style: 'margin-top:18px' }, 'La interfaz original del grupo sigue disponible en esta máquina con «docker compose --profile standalone up -d standalone-g5»: http://localhost:5678/webhook/pims/app'));
  draw();
}
