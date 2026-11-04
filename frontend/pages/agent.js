import { AUDIT_CASES } from '../services/audit-cases.js';
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
  for (const k of ['informe_markdown', 'dictamen_markdown', 'text', 'resultado', 'respuesta', 'output']) {
    if (typeof o[k] === 'string') return o[k];
    if (o[k] && typeof o[k] === 'object') { const r = pickText(o[k]); if (r) return r; }
  }
  return null;
}

export async function agentPage(root, key) {
  const cfg = AGENTS[key];
  if (key === 'auditoria') root.classList.add('audit-page');
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
    tabs.replaceChildren(...cfg.actions.map((a) => h('button', { class: a === current ? 'on' : '', onclick: () => { current = a; draw(); history(); } }, a.label)));
    const form = h('form', {}, current.fields.map(field));
    if (key === 'auditoria' && current.id === 'auditar') {
      const select = h('select', {}, h('option', { value: '' }, 'Selecciona un caso de demostración'),
        ...Object.entries(AUDIT_CASES).map(([id, c]) => h('option', { value: id }, c.titulo)));
      select.addEventListener('change', () => {
        const c = AUDIT_CASES[select.value];
        if (c) { form.elements.nombre_archivo.value = c.archivo; form.elements.contenido.value = c.contenido; }
      });
      const file = h('input', { type: 'file', accept: '.txt,.md,.json,.csv' });
      file.addEventListener('change', async () => {
        const f = file.files[0]; if (!f) return;
        if (f.size > 1024 * 1024) { out.replaceChildren(alertBox('warn', 'Elige un archivo de texto de hasta 1 MB.')); return; }
        form.elements.nombre_archivo.value = f.name;
        form.elements.contenido.value = await f.text();
      });
      form.prepend(h('div', {}, h('label', {}, 'Casos originales de G4 (datos ficticios)'), select,
        h('label', {}, 'O cargar texto (.txt, .md, .json o .csv; máximo 1 MB)'), file));
    }
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
        wrapAuditTables();
      } catch (err) { out.replaceChildren(alertBox('bad', String(err.message))); }
      btn.disabled = false; history();
    });
    formBox.replaceChildren(h('h2', {}, current.label), current.fields.length ? '' : h('p', { class: 'mute small' }, 'Esta acción no requiere datos.'), form);
  };

  function showResult(e) {
    if (e.status === 'failed') return out.replaceChildren(alertBox('bad', `Falló: ${e.error}`));
    const r = e.result || {}, o = r.output ?? r, text = pickText(o);
    out.replaceChildren(h('div', { class: 'card' },
      key === 'auditoria' ? alertBox('info', 'Propuesta pendiente de validación humana. No constituye certificación ni aprobación registrada.') : null,
      o.motor_contingencia ? alertBox('warn', 'Resultado de contingencia mediante plantillas; no proviene de un modelo de IA.') : null,
      o.modo === 'M1' ? h('div', {}, h('h2', {}, 'Checklist inicial de evidencias'),
        h('p', {}, `${o.total} ítems · rol: ${o.rol} · alcance: ${o.alcance}`), alertBox('info', o.nota),
        table(['Código interno', 'Tema', 'Requisito', 'Evidencia esperada', 'Responsable', 'Base legal del catálogo'], o.items.map(x => [x.codigo_interno, x.tema, x.requisito, x.evidencia_esperada, x.responsable, x.base_legal]))) : null,
      o.modo === 'M3' ? h('div', {}, h('h2', {}, 'Matriz consolidada de evaluación de evidencias'),
        h('p', {}, `${o.total_evaluaciones} evaluaciones. No es la SoA de G7. Sin porcentaje de cumplimiento inferido.`),
        table(['Evidencia vinculada', 'Ejecución', 'SHA-256 del texto', 'Resultado propuesto', 'Revisión'], o.filas.map(x => [x.evidencia + (x.simulado ? ' (simulada)' : '') + (x.motor_contingencia ? ' (contingencia sin LLM)' : ''), x.ejecucion_id, x.sha256, x.severidad_propuesta, x.estado_revision])),
        h('button', { type: 'button', onclick: () => {
          const url = URL.createObjectURL(new Blob([o.informe_markdown], { type: 'text/markdown;charset=utf-8' }));
          const a = h('a', { href: url, download: 'informe-auditoria-M3.md' }); a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
        } }, 'Descargar informe Markdown')) : null,
      h('div', { class: 'row small mute' }, `Duración ${Math.round(e.seconds || 0)} s · modo LLM: ${e.llm_mode}`, e.simulated ? h('span', { class: 'badge b-sim' }, 'simulado') : null),
      text ? h('div', { class: 'md', style: 'margin:10px 0' }, text) : null,
      h('details', { open: !text }, h('summary', {}, 'Resultado completo (JSON)'), h('pre', {}, JSON.stringify(o, null, 2)))));
  }

  function wrapAuditTables() {
    if (key !== 'auditoria') return;
    root.querySelectorAll('table').forEach(t => {
      if (t.parentElement.classList.contains('audit-table-scroll')) return;
      const wrap = h('div', { class: 'audit-table-scroll' }); t.replaceWith(wrap); wrap.append(t);
    });
  }

  const histBox = h('div', { class: 'card', style: 'margin-top:14px' });
  async function history() {
    const rows = await api.executions(detail.id);
    if (key === 'auditoria' && current.id === 'consolidar') {
      const form = formBox.querySelector('form');
      form.querySelector('[data-m2-selection]')?.remove();
      const choices = h('div', { 'data-m2-selection': true }, h('h3', {}, 'Selecciona evaluaciones M2 del historial'));
      for (const e of rows.filter(x => x.action === 'auditar' && x.status === 'succeeded')) {
        const check = h('input', { type: 'checkbox', value: e.id, style: 'width:auto;flex-shrink:0' });
        check.addEventListener('change', () => { form.elements.execution_ids.value = [...choices.querySelectorAll('input:checked')].map(x => x.value).join('\n'); });
        choices.append(h('label', { style: 'display:flex;align-items:center;gap:8px;overflow-wrap:anywhere' }, check, ` ${fmtTime(e.created_at)} · ${e.id}${e.simulated ? ' · simulado' : ''}`));
      }
      if (!choices.querySelector('input')) choices.append(h('p', {}, 'Primero ejecuta M2. Aquí se mostrarán las evaluaciones finalizadas.'));
      form.prepend(choices);
    }
    histBox.replaceChildren(h('h2', {}, 'Historial de ejecuciones'), rows.length ? table(['Hora', 'Acción', 'Estado', 'Modo', 'Error'],
      rows.map((r) => [fmtTime(r.created_at), r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || ''])) : h('span', { class: 'mute' }, 'Sin ejecuciones todavía.'));
    wrapAuditTables();
  }
  draw(); history();
  root.append(tabs, formBox, out, histBox);
}

export function inventarioPage(root) {
  root.append(h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, 'G6 · Inventario de datos'), badge('fuera_de_alcance')),
    h('p', { class: 'sub' }, 'Responsabilidad: activos de datos, clasificación y registro de tratamientos.'),
    alertBox('info', 'Fuera del alcance de esta entrega.'),
    h('div', { class: 'card' }, h('h2', {}, 'Qué entregó el grupo'),
      h('p', {}, 'Una herramienta en un solo archivo HTML ("PII Privacy Assistant") que se ejecuta en el navegador con reglas de coincidencia por alias. No es un modelo de IA, no tiene backend ni conexión a la base compartida.'),
      h('p', { class: 'mute small' }, 'Por eso no hay formulario ni datos aquí: no se inventa un inventario. Su integración (adaptador sin LLM y, opcionalmente, escritura en core_asset, core_process y core_personaldataoperation) queda para una siguiente ronda.')));
}
