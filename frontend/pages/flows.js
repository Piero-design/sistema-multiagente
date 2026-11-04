import { h, alertBox, spinner, fmtTime } from '../components/ui.js';
import { table } from './dashboard.js';

async function j(url, opt) {
  const r = await fetch(url, opt);
  if (!r.ok) throw new Error(`${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.json();
}

const FLOWS = [
  { id: 'terceros_a_controles', title: 'G5 → G7 · Terceros alimentan la SoA',
    about: 'Toma el último expediente de G5 y envía sus controles cumplidos o parciales como evidencias a G7; muestra qué controles cambian en la SoA. Solo 3 controles coinciden entre ambos catálogos (A.2.5.7, A.3.11, A.3.12).',
    fields: [{ name: 'rol', label: 'Rol de la organización', type: 'select', options: ['ambos', 'responsable', 'encargado'], value: 'ambos' }],
    params: (v) => ({ organizacion: 'unsa', rol: v.rol }) },
  { id: 'incidente_a_formacion', title: 'G8 → G1 · Incidente genera recomendaciones de formación',
    about: 'G8 analiza el incidente (1–3 min); sus lecciones aprendidas, sin datos personales, se envían a G1, que propone capacitaciones.',
    fields: [{ name: 'reporte', label: 'Reporte del incidente (datos de demostración)', type: 'textarea',
      value: 'Un funcionario envió por error una hoja de cálculo con DNI y notas de 300 estudiantes a una lista externa de correo de la universidad.' }],
    params: (v) => ({ reporte: v.reporte }) },
  { id: 'inventario_a_auditoria', title: 'G6 → G4 · Inventario como evidencia de auditoría',
    about: 'G6 prepara su inventario como documento de evidencia (sin valores de datos personales) y G4 lo evalúa. Registra antes activos en la página de G6. La severidad es una propuesta para un auditor humano.',
    fields: [{ name: 'organizacion', label: 'Organización (datos de demostración)', type: 'text', value: 'UNSA-DEMO' }],
    params: (v) => ({ organizacion: v.organizacion }) },
  { id: 'inventario_a_riesgos', title: 'G6 → G2 · Inventario alimenta la evaluación de riesgos',
    about: 'Toma del inventario de G6 el sistema con más campos de datos personales (o el que indiques) y envía a G2 solo nombres de campos, finalidad y titulares, nunca valores. G2 propone los riesgos de privacidad (ISO/IEC 27701, cláusula 6.1.2) e indica qué información falta. Registra antes activos en la página de G6; la evaluación la valida una persona.',
    fields: [{ name: 'organizacion', label: 'Organización (datos de demostración)', type: 'text', value: 'UNSA-DEMO' },
      { name: 'sistema', label: 'Sistema a evaluar (opcional; vacío = el de más datos personales)', type: 'text', value: '' }],
    params: (v) => ({ organizacion: v.organizacion, sistema: v.sistema }) },
  { id: 'dsar_handoffs', title: 'G3 → G4 / G6 · Handoffs de un caso decidido',
    about: 'Transporta los handoffs que G3 genera después de una decisión humana. El de evidencia se entrega a G4; el de terceros queda pendiente de una persona; el de inventario lo recibe G6, que verifica el hash y responde la cobertura. Una persona debe haber verificado la identidad y decidido el caso (ver CASOS_DE_PRUEBA.md, B3).',
    fields: [{ name: 'case_id', label: 'Identificador del caso (DSAR-MCP-…)', type: 'text', value: '' }],
    params: (v) => ({ case_id: v.case_id }) },
];

function render(f) {
  const r = f.result || {};
  const box = h('div', { style: 'margin-top:14px' });
  if (f.status === 'failed') return h('div', {}, box, alertBox('bad', f.error));
  if (f.flow === 'terceros_a_controles') {
    box.append(h('p', {}, `Controles de G5: ${r.controles_g5} · presentes en el catálogo de G7: ${r.controles_g5_en_catalogo_g7} · evidencias enviadas: ${r.evidencias_enviadas_a_g7}`),
      r.controles_que_cambiaron_en_soa?.length
        ? table(['Control', 'Antes', 'Después'], r.controles_que_cambiaron_en_soa.map((c) => [c.control, c.antes, c.despues]))
        : h('p', { class: 'mute' }, 'Ningún control cambió: el último expediente de G5 no cumple (ni parcialmente) los controles que G7 conoce.'));
  } else if (f.flow === 'incidente_a_formacion') {
    box.append(h('h2', {}, 'Recomendación de G1'), h('div', { class: 'md' }, r.recomendacion_g1 || ''));
  } else if (f.flow === 'inventario_a_riesgos') {
    const e = r.enviado_a_g2 || {};
    box.append(table(['Sistema evaluado', 'Campos personales enviados', 'Finalidad declarada'], [[r.sistema_evaluado, (e.campos_personales || []).join(', '), e.finalidad]]),
      h('h2', {}, 'Evaluación de G2'), h('div', { class: 'md' }, r.evaluacion_g2 || ''), h('p', { class: 'small mute' }, r.nota));
  } else if (f.flow === 'inventario_a_auditoria') {
    box.append(table(['Documento', 'Enviado por G6', 'Severidad propuesta por G4'], [[r.documento, String(r.enviado_por_g6), r.severidad_propuesta_g4]]),
      h('p', { class: 'small mute' }, r.nota));
  } else {
    box.append(table(['Destino', 'Acción', 'Entrega', 'Detalle'], (r.handoffs || []).map((x) => [x.to, x.action, x.delivery, x.severidad ? `Severidad propuesta: ${x.severidad}` : x.motivo || ''])));
  }
  return box;
}

// ---- Visual timeline: which agent is doing what, what it reads, what it produced (live while the flow runs)
const WHO = {
  formacion: ['G1', 'Formación', '#2b5cff'], riesgos: ['G2', 'Riesgos', '#7c3aed'], dsar: ['G3', 'Derechos (DSAR)', '#0e9f6e'],
  auditoria: ['G4', 'Evidencia y auditoría', '#c2680a'], terceros: ['G5', 'Terceros y DPA', '#d6246e'], inventario: ['G6', 'Inventario de datos', '#0b8aa6'],
  controles: ['G7', 'Controles y SoA', '#4f46e5'], incidentes: ['G8', 'Incidentes y brechas', '#d92d20'],
};
const who = (a) => WHO[a] || ['', a, '#6b7280'];

function secs(iso) { return iso ? Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000)) : 0; }

function avatar(agent) {
  const [g, , color] = who(agent);
  return h('span', { class: 'tl-av', style: `background:${color}` }, g || '⚙');
}

function activityList(st, running) {
  const lines = (st.actividad && st.actividad.length ? st.actividad.map((e) => e.texto) : st.actividad_final) || [];
  if (!lines.length) return running ? h('div', { class: 'tl-act mute' }, h('span', { class: 'spin' }), ' Esperando respuesta del agente…') : null;
  const shown = running ? lines.slice(-8) : lines;
  return h('div', { class: 'tl-act' }, shown.map((t) => {
    const reading = /^leyendo/i.test(t);
    return h('div', { class: 'tl-line' }, h('span', { class: 'tl-ic' }, reading ? '📖' : '•'), ' ', t);
  }), running ? h('div', { class: 'tl-line mute' }, h('span', { class: 'spin' }), ' trabajando…') : null);
}

function stepCard(st) {
  const [g, name, color] = who(st.agent);
  const running = st.status === 'running';
  const pill = running ? h('span', { class: 'badge b-run' }, h('span', { class: 'spin' }), ` En curso · ${secs(st.inicio)} s`)
    : st.status === 'failed' ? h('span', { class: 'badge b-bad' }, '✕ Falló')
      : h('span', { class: 'badge b-ok' }, `✓ Listo · ${st.segundos ?? 0} s`);
  return h('div', { class: `tl-card${running ? ' running' : ''}${st.status === 'failed' ? ' failed' : ''}`, style: `--c:${color}` },
    h('div', { class: 'tl-head' }, avatar(st.agent), h('div', { class: 'tl-who' }, h('b', {}, `${g} · ${name}`), h('div', { class: 'tl-title' }, st.titulo || st.action)), pill),
    st.lee ? h('div', { class: 'tl-row' }, h('span', { class: 'tl-k' }, 'Recibe'), ' ', st.lee) : null,
    activityList(st, running),
    st.produce ? h('div', { class: 'tl-row' }, h('span', { class: 'tl-k ok' }, 'Entrega'), ' ', st.produce) : null,
    st.error ? h('div', { class: 'tl-row bad' }, st.error) : null);
}

function connector(text) {
  return h('div', { class: 'tl-conn' }, h('span', { class: 'tl-gear' }, '⚙'), h('div', {}, h('b', {}, 'Orquestador'), h('div', { class: 'small mute' }, text)));
}

function timeline(f) {
  const steps = f.steps || [];
  const box = h('div', { class: 'tl' });
  steps.forEach((st) => { if (st.prep) box.append(connector(st.prep)); else if (st !== steps[0]) box.append(h('div', { class: 'tl-arrow' }, '↓')); box.append(stepCard(st)); });
  if (f.status === 'running') {
    (f.plan || []).slice(steps.length).forEach((p) => {
      const [g, name, color] = who(p.agent);
      box.append(h('div', { class: 'tl-arrow' }, '↓'), h('div', { class: 'tl-card pending', style: `--c:${color}` },
        h('div', { class: 'tl-head' }, avatar(p.agent), h('div', { class: 'tl-who' }, h('b', {}, `${g} · ${name}`), h('div', { class: 'tl-title' }, p.titulo)), h('span', { class: 'badge b-off' }, 'En espera'))));
    });
  }
  if (!steps.length) box.append(h('div', { class: 'tl-act mute' }, h('span', { class: 'spin' }), ' Iniciando el flujo…'));
  return box;
}

export async function flowsPanel(root) {
  root.append(h('h2', { style: 'margin-top:24px' }, 'Flujos entre agentes'),
    h('p', { class: 'small mute' }, 'Cada paso es una ejecución real de un agente a través del orquestador y queda registrado en Actividad.'));
  const grid = h('div', { class: 'grid g2' });
  const cards = new Map();
  for (const fl of FLOWS) {
    const out = h('div', { style: 'margin-top:12px' });
    const form = h('form', {}, fl.fields.map((f) => h('div', {}, h('label', {}, f.label),
      f.type === 'textarea' ? h('textarea', { name: f.name }, f.value)
        : f.type === 'select' ? h('select', { name: f.name }, f.options.map((o) => h('option', { value: o }, o)))
          : h('input', { name: f.name, value: f.value }))));
    const btn = h('button', { type: 'submit', style: 'margin-top:12px' }, 'Ejecutar flujo');
    form.append(btn);
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault(); btn.disabled = true;
      const v = Object.fromEntries(fl.fields.map((f) => [f.name, form.elements[f.name].value]));
      cards.get(fl.id).classList.add('wide');            // the timeline needs the full width
      out.replaceChildren(spinner('Iniciando el flujo…'));
      try {
        const { flow_run_id } = await j(`/api/flows/${fl.id}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ params: fl.params(v) }) });
        for (;;) {
          const f = await j(`/api/flows/${flow_run_id}`);
          if (f.status !== 'running') { out.replaceChildren(timeline(f), render(f)); break; }
          out.replaceChildren(timeline(f));
          await new Promise((r) => setTimeout(r, 2000));
        }
      } catch (e) { out.replaceChildren(alertBox('bad', e.message)); }
      btn.disabled = false;
    });
    const card = h('div', { class: 'card' }, h('h2', {}, fl.title), h('p', { class: 'small mute' }, fl.about), form, out);
    cards.set(fl.id, card);
    grid.append(card);
  }
  root.append(grid);
  try {
    const { handoffs } = await j('/api/flows');
    if (handoffs.length) root.append(h('h2', { style: 'margin-top:20px' }, 'Handoffs transportados'), h('div', { class: 'card' },
      table(['Hora', 'Caso', 'Hacia', 'Acción', 'Entrega'], handoffs.map((x) => [fmtTime(x.created_at), x.case_ref, x.to_agent, x.action, x.delivery_status]))));
  } catch { /* panel still usable */ }
}
