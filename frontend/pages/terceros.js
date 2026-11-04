// G5 · Terceros y DPA (Agente 7). Page of its own: it brings back the functions of the agent's original page
// (audit with a file, organization context, expedientes with download, profile, renewals, chat) through the
// platform API. Human decisions (DPO/Legal approval, profile validation) stay in «Revisión humana».
import { api } from '../services/api.js';
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
function expedienteView(det) {
  const r = det.resultado || {}, reg = r._registro || {}, p = r.puntaje_proveedor || {}, c = reg.contexto || {};
  const res = r.resumen || {};
  const fuente = { perfil: 'perfil de la organización', bd: 'base de datos del PIMS', ambos: 'perfil + base de datos' }[c.fuente] || 'perfil de la organización';
  return h('div', {},
    h('div', { class: 'row', style: 'justify-content:space-between' },
      h('h2', {}, `${(r.tercero || {}).nombre || reg.id_registro} · ${reg.id_registro || ''}`), downloadButtons(reg.id_registro || 'expediente', det)),
    h('div', { class: 'kpis', style: 'margin:10px 0' },
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Puntaje'), h('div', { class: 'kpi' }, p.valor ?? '—'), h('div', { class: 'small' }, p.banda || '')),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Dictamen'), h('div', { style: 'font-weight:700' }, r.dictamen || '—')),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Aprobación'), h('div', { style: 'font-weight:700' }, (r.aprobacion || {}).estado || '—')),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Controles'),
        h('div', { class: 'small' }, `${res.cumple ?? 0} cumple · ${res.parcial ?? 0} parcial · ${res.no_cumple ?? 0} no cumple · ${res.sin_evidencia ?? 0} sin evidencia`))),
    h('p', { class: 'small mute' }, `Modelo ${reg.modelo || '—'} · correcciones del JSON: ${reg.reintentos ?? 0} · contexto: ${fuente}` +
      (c.bd ? ` (esquema ${c.bd.esquema}, ${Object.values(c.bd.filas || {}).reduce((a, b) => a + b, 0)} filas)` : '')),
    c.aviso ? alertBox('warn', c.aviso) : null,
    h('details', { open: true }, h('summary', {}, 'Informe'), det.informe ? markdown(det.informe) : h('p', { class: 'mute' }, '(sin informe)')),
    h('details', {}, h('summary', {}, 'Matriz de los 26 controles'),
      table(['Control', 'Estado', 'Severidad', 'Evidencia'], (r.controles || []).map((x) => [x.id, x.estado, x.severidad || '', String(x.evidencia || x.hallazgo || '').slice(0, 220)]))),
    h('details', {}, h('summary', {}, 'Expediente completo (JSON)'), h('pre', {}, JSON.stringify(r, null, 2))));
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
          (st.advertencias || []).map((a) => alertBox('warn', a)), card(expedienteView(st.expediente || {})));
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
            h('button', { class: 'ghost', onclick: async () => { busy(view, 'Abriendo…'); try { view.replaceChildren(card(expedienteView(await detalle(r.id_registro)))); view.scrollIntoView(); } catch (err) { fail(view, err); } } }, 'Ver'),
            h('button', { class: 'ghost', onclick: async () => { try { const d = await detalle(r.id_registro); dlMD(`${r.id_registro}.md`, d.informe); } catch (err) { fail(view, err); } } }, '.md'),
            h('button', { class: 'ghost', onclick: async () => { try { const d = await detalle(r.id_registro); dlJSON(`${r.id_registro}.json`, d.resultado); } catch (err) { fail(view, err); } } }, '.json'))]))
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
            h('span', { class: 'row' }, h('button', { class: 'ghost', onclick: () => dlMD(`perfil_${id}.md`, perfil.texto) }, 'Descargar perfil (.md)')),
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
          (docs.documentos || []).length ? table(['Documento', 'Tamaño'], docs.documentos.map((d) => [d.nombre, d.tam])) : h('p', { class: 'mute' }, 'Sin documentos.'),
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
  const ambito = h('select', {}, h('option', { value: 'expediente' }, 'Un expediente'), h('option', { value: 'organizacion' }, 'Una organización'));
  const objetivo = h('select');
  const fill = () => objetivo.replaceChildren(...(ambito.value === 'expediente'
    ? regs.map((r) => h('option', { value: r.id_registro, 'data-org': r.organizacion }, `${r.proveedor || r.id_registro} · ${r.id_registro}`))
    : orgs.map((o) => h('option', { value: o.id, 'data-org': o.id }, o.nombre))));
  const log = h('div'), q = h('textarea', { placeholder: '¿Qué controles críticos incumple este proveedor y qué cláusulas habría que pedirle?', style: 'min-height:80px' });
  async function history() {
    if (!objetivo.value) return log.replaceChildren();
    try {
      const { out: c } = await run('conversacion', { ambito: ambito.value, id: objetivo.value });
      log.replaceChildren(...(c.mensajes || []).map((m) => h('div', { class: 'card', style: `margin:8px 0;${m.rol === 'usuario' ? '' : 'border-left:3px solid var(--brand)'}` },
        h('div', { class: 'small mute' }, `${m.rol === 'usuario' ? 'Pregunta' : 'Respuesta'} · ${fmtTime(m.fecha)}${m.modelo ? ' · ' + m.modelo : ''}`), markdown(m.texto))));
    } catch (err) { fail(log, err); }
  }
  ambito.addEventListener('change', () => { fill(); history(); });
  objetivo.addEventListener('change', history);
  const send = h('button', { onclick: async () => {
    if (!q.value.trim() || !objetivo.value) return;
    send.disabled = true;
    const org = objetivo.selectedOptions[0]?.dataset.org || '';
    const wait = h('div', { class: 'card' }, spinner('El modelo está respondiendo…')); log.append(wait);
    try {
      const { out: st } = await run('chat', { ambito: ambito.value, id: objetivo.value, organizacion: org, pregunta: q.value.trim(), usuario: 'plataforma' });
      if (st.estado !== 'terminado') throw new Error(st.mensaje || 'sin respuesta');
      q.value = ''; await history();
    } catch (err) { wait.replaceChildren(alertBox('bad', err.message)); }
    send.disabled = false;
  } }, 'Preguntar');
  fill();
  box.replaceChildren(card(h('h2', {}, 'Chat sobre un expediente o una organización'),
    h('p', { class: 'small mute' }, 'El chat solo consulta: no modifica expedientes, puntajes ni perfiles.'),
    h('div', { class: 'grid g2' }, field('Ámbito', ambito), field('Expediente u organización', objetivo)), field('Pregunta', q),
    h('div', { style: 'margin-top:12px' }, send)), card(h('h2', {}, 'Conversación'), log));
  history();
}

async function tabHistorial(box, agentId) {
  const rows = await api.executions(agentId);
  box.replaceChildren(card(h('h2', {}, 'Historial de ejecuciones'), rows.length ? table(['Hora', 'Acción', 'Estado', 'Modo', 'Error'],
    rows.map((r) => [fmtTime(r.created_at), r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || ''])) : h('span', { class: 'mute' }, 'Sin ejecuciones todavía.')));
}

// ---------------------------------------------------------------- page
const ESTILO = `.mdr{margin:8px 0;line-height:1.55}.mdr h2,.mdr h3{font-size:16px;margin:18px 0 6px}.mdr h4,.mdr h5{font-size:14px;margin:14px 0 4px}
.mdr p{margin:6px 0}.mdr ul,.mdr ol{margin:6px 0 6px 20px;padding:0}.mdr table{margin:8px 0;font-size:13px}
.mdr blockquote{margin:8px 0;padding:6px 12px;border-left:3px solid var(--brand);color:var(--mute)}.mdr code{font:12px ui-monospace,Consolas,monospace}`;

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
