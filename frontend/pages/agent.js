import { api } from '../services/api.js';
import { h, badge, fmtTime, alertBox, spinner } from '../components/ui.js';
import { AGENTS } from '../services/agents-config.js';
import { table } from './dashboard.js';

function field(f) {
  let input;
  if (f.type === 'textarea') input = h('textarea', { name: f.name }, f.demo ?? '');
  else if (f.type === 'select') input = h('select', { name: f.name }, f.options.map((o) => h('option', { value: o, selected: o === f.demo }, o)));
  else if (f.type === 'multi') input = h('select', { name: f.name, multiple: true, size: f.options.length },
    f.options.map((o) => h('option', { value: o, selected: (f.demo || []).includes(o) }, o)));
  else input = h('input', { name: f.name, type: f.type === 'date' ? 'date' : 'text', value: f.demo ?? '' });
  return h('div', {}, h('label', {}, f.label), input);
}
const values = (form, fields) => Object.fromEntries(fields.map((f) => {
  const el = form.elements[f.name];
  return [f.name, f.type === 'multi' ? [...el.selectedOptions].map((o) => o.value) : el.value];
}));

// Show the readable part of a result when the agent provides one; always keep the raw JSON available.
function pickText(o) {
  if (!o || typeof o !== 'object') return null;
  for (const k of ['dictamen_markdown', 'text', 'resultado', 'respuesta', 'output']) {
    if (typeof o[k] === 'string') return o[k];
    if (o[k] && typeof o[k] === 'object') { const r = pickText(o[k]); if (r) return r; }
  }
  return null;
}

export async function agentPage(root, key) {
  const cfg = AGENTS[key];
  const detail = await api.agents().then((l) => l.find((a) => a.group === cfg.group));
  root.append(h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, `G${cfg.group} · ${cfg.title}`), badge(detail.status)),
    h('p', { class: 'sub' }, cfg.about));
  if (detail.reason) root.append(alertBox(detail.status === 'caido' ? 'bad' : 'warn', detail.reason));
  root.append(alertBox('info', 'Los valores precargados son datos de demostración (organización simulada UNSA). Puedes editarlos.'));

  let current = cfg.actions[0];
  const tabs = h('div', { class: 'tabs' });
  const formBox = h('div', { class: 'card' });
  const out = h('div', { style: 'margin-top:14px' });

  const draw = () => {
    tabs.replaceChildren(...cfg.actions.map((a) => h('button', { class: a === current ? 'on' : '', onclick: () => { current = a; draw(); } }, a.label)));
    const form = h('form', {}, current.fields.map(field));
    const btn = h('button', { type: 'submit', style: 'margin-top:14px' }, 'Ejecutar');
    form.append(btn);
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault(); btn.disabled = true;
      const t0 = Date.now();
      out.replaceChildren(h('div', { class: 'card' }, spinner(current.long ? 'En ejecución (puede tardar varios minutos)…' : 'Ejecutando…')));
      try {
        const e = await api.run(key, current.id, current.build(values(form, current.fields)), (s) =>
          out.replaceChildren(h('div', { class: 'card' }, spinner(`Estado: ${s.status} · ${Math.round((Date.now() - t0) / 1000)} s`))));
        showResult(e);
      } catch (err) { out.replaceChildren(alertBox('bad', String(err.message))); }
      btn.disabled = false; history();
    });
    formBox.replaceChildren(h('h2', {}, current.label), current.fields.length ? '' : h('p', { class: 'mute small' }, 'Esta acción no requiere datos.'), form);
  };

  const docsView = (o) => h('div', {}, h('p', { class: 'small mute' }, `Expediente ${o.id} · ${o.files?.length || 0} documentos${o.limite ? ' · hora límite ' + o.limite : ''}`),
    ...Object.entries(o.docs || {}).map(([name, body]) => h('details', { open: /informe|ficha/i.test(name) }, h('summary', {}, name), h('div', { class: 'md', style: 'margin:8px 0' }, body))),
    (o.acciones || []).length ? h('p', { class: 'small mute' }, `${o.acciones.length} acción(es) propuesta(s). Las decisiones se toman en «Revisión humana».`) : null);

  function showResult(e) {
    if (e.status === 'failed') return out.replaceChildren(alertBox('bad', `Falló: ${e.error}`));
    const r = e.result || {}, o = r.output ?? r, text = pickText(o);
    if (o && o.docs) return out.replaceChildren(h('div', { class: 'card' }, docsView(o)));
    const incId = o && typeof o.incidente === 'string' && o.incidente !== 'None' ? o.incidente : null;
    out.replaceChildren(h('div', { class: 'card' },
      h('div', { class: 'row small mute' }, `Duración ${Math.round(e.seconds || 0)} s · modo LLM: ${e.llm_mode}`, e.simulated ? h('span', { class: 'badge b-sim' }, 'simulado') : null),
      incId ? h('button', { style: 'margin:8px 0', onclick: async (ev) => { ev.target.disabled = true; try { const x = await api.run(key, 'expediente', { id: incId }); out.replaceChildren(h('div', { class: 'card' }, docsView((x.result || {}).output || {}))); } catch (err) { out.append(alertBox('bad', err.message)); } } }, `Ver el expediente completo (${incId})`) : null,
      text ? h('div', { class: 'md', style: 'margin:10px 0' }, text) : null,
      h('details', { open: !text }, h('summary', {}, 'Resultado completo (JSON)'), h('pre', {}, JSON.stringify(o, null, 2)))));
  }

  const histBox = h('div', { class: 'card', style: 'margin-top:14px' });
  async function history() {
    const rows = await api.executions(detail.id);
    histBox.replaceChildren(h('h2', {}, 'Historial de ejecuciones'), rows.length ? table(['Hora', 'Acción', 'Estado', 'Modo', 'Error'],
      rows.map((r) => [fmtTime(r.created_at), r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || ''])) : h('span', { class: 'mute' }, 'Sin ejecuciones todavía.'));
  }
  draw(); history();
  root.append(tabs, formBox, out, histBox);
}
