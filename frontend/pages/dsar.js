// G3 · Gestión DSAR: the rest of the agent's own panel, for a signed-in DPO only.
// Every call goes to /api/human/dsar/gestion/* (backend → G3 bridge), or to the same identity/decision endpoints
// /revision uses; the backend sets the reviewer to the signed-in person. Nothing here runs a right.
import { api, authed, session, whoami } from '../services/api.js';
import { h, alertBox, badge, spinner } from '../components/ui.js';
import { AGENTS } from '../services/agents-config.js';
import { agentPage } from './agent.js';
import { table } from './dashboard.js';
import { loginForm } from './revision.js';

const RIGHTS = ['information', 'access', 'portability', 'rectification', 'erasure', 'objection'];

async function g3(path, method = 'GET', body) {
  const r = await fetch('/api/human/dsar/gestion/' + path, {
    method, headers: { 'content-type': 'application/json', Authorization: 'Bearer ' + session.token },
    body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await r.text();
  let data; try { data = JSON.parse(text); } catch { data = { detail: text }; }
  if (r.status === 401) { session.token = null; session.user = null; }
  if (!r.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data));
  return data;
}

const card = (title, ...kids) => h('div', { class: 'card', style: 'margin-top:14px' }, h('h2', {}, title), ...kids);
const json = (o, open = false) => h('details', { open }, h('summary', {}, 'Detalle (JSON)'), h('pre', {}, JSON.stringify(o, null, 2)));
const input = (name, ph, value = '') => h('input', { name, placeholder: ph, value, style: 'max-width:260px' });
const select = (name, options, multiple = false, chosen = []) => h('select', { name, multiple, size: multiple ? options.length : undefined },
  options.map((o) => h('option', { value: o, selected: chosen.includes(o) }, o)));
const picked = (el) => [...el.selectedOptions].map((o) => o.value);

// A button that runs an action and shows its outcome next to it.
function act(label, run, after) {
  const out = h('span', { class: 'small' });
  const btn = h('button', { class: 'ghost', type: 'button', onclick: async () => {
    btn.disabled = true; out.style.color = ''; out.replaceChildren(spinner(''));
    try { const r = await run(); out.textContent = '✔ ' + (r?.status || 'hecho'); after?.(r); }
    catch (e) { out.textContent = '✖ ' + e.message.slice(0, 220); out.style.color = 'var(--bad)'; }
    btn.disabled = false; } }, label);
  return h('span', { class: 'row' }, btn, out);
}

function download(name, data) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  const a = h('a', { href: url, download: name });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ---------------------------------------------------------------- expediente
async function expediente(box, caseId) {
  const list = await g3('casos');
  const pick = select('case', list.map((c) => c.case_id), false, [caseId]);
  const view = h('div');
  const load = async () => {
    if (!pick.value) return view.replaceChildren(h('p', { class: 'mute' }, 'Todavía no hay expedientes. Crea uno en G3 · DSAR o confirma un correo.'));
    view.replaceChildren(spinner('Cargando expediente…'));
    try { showCase(view, await g3('casos/' + pick.value), load); } catch (e) { view.replaceChildren(alertBox('bad', e.message)); }
  };
  pick.addEventListener('change', load);
  box.replaceChildren(h('div', { class: 'row' }, h('label', {}, 'Expediente'), pick), view);
  await load();
}

function showCase(view, p, reload) {
  const id = p.case_id;
  const deadlines = Object.entries(p.deadlines || {});
  const records = p.discovered_records || [];
  view.replaceChildren(
    card(`${id} · ${p.status}`,
      h('p', { class: 'small mute' }, `Derechos: ${(p.request_types || []).join(', ')} · perfil ${p.policy?.policy_id} · recibido ${p.received_at} · identidad ${p.identity_verification?.status}`),
      (p.hitl?.reasons || []).length ? h('div', {}, h('strong', {}, 'Motivos de revisión humana'), h('ul', {}, p.hitl.reasons.map((r) => h('li', { class: 'small' }, r)))) : null,
      decisionBox(p, reload)),
    card('Plazos por derecho', table(['Derecho', 'Días', 'Vence', 'Tope legal', 'Base legal', 'Prórroga'],
      deadlines.map(([right, d]) => [right, `${d.days} ${d.day_type === 'business' ? 'hábiles' : 'naturales'}`, d.deadline_at,
        d.legal_deadline_at || '—', d.legal_basis || '', d.extension ? `+${d.extension.days} · ${d.extension.decided_by || ''}` : '—']))),
    card('Línea de tiempo', table(['#', 'Estado', 'Descripción'], (p.audit_trail || []).map((e) => [e.sequence, e.state, e.description]))),
    card('Registros encontrados', records.length ? table(['Registro', 'Sistema', 'Categoría', 'Campos entregables', 'Retirados (terceros/confidenciales)', 'Restricciones'],
      records.map((r) => [r.record_id, r.source_system, r.category + (r.sensitive ? ' (sensible)' : ''), Object.keys(r.data || {}).join(', '),
        (r.redacted_fields || []).join(', ') || '—', (r.restrictions || []).join(', ') || '—']))
      : h('p', { class: 'mute' }, p.status === 'IDENTITY_PENDING' ? 'Sin registros: la identidad no está verificada (no se busca nada).' : 'Sin registros.'),
      p.coverage ? h('p', { class: 'small' }, `Sistemas esperados: ${(p.coverage.expected_systems || []).join(', ')} · faltantes: ${(p.coverage.missing_systems || []).join(', ') || 'ninguno'}`) : null),
    card('Acciones propuestas (no ejecutadas)', table(['Derecho', 'Acción', 'Ejecutada'],
      (p.proposed_actions || []).map((a) => [a.type, a.description, a.executed ? 'sí' : 'no']))),
    card('Controles y cláusulas ISO/IEC 27701 aplicados', table(['Control', 'Título', 'Motivo'],
      (p.controls || []).map((c) => [c.control, c.title, c.reason]))),
    extensionCard(id, deadlines.map(([r]) => r), reload),
    draftCard(p),
    json(p));
}

// Same endpoints as /revision: the agent itself refuses deciding before the identity is verified.
const DECIDED = ['APPROVED', 'REJECTED', 'CANCELLED'];
function decisionBox(p, reload) {
  const id = p.case_id;
  if (DECIDED.includes(p.status)) {
    const d = p.human_decision || {};
    return h('p', { class: 'small' }, h('strong', {}, `Decisión humana: ${p.status}`), ` · ${d.reviewer || ''} · ${d.note || ''}`);
  }
  const method = input('method', 'Método (DNI presencial)');
  const ref = input('reference', 'Referencia (opcional)');
  const note = input('note', 'Justificación de la decisión');
  const decide = (decision) => () => authed('/api/human/dsar/decidir', { case_id: id, decision, note: note.value || (decision === 'APPROVED' ? 'Aprobado' : 'Rechazado') });
  return h('div', { style: 'margin-top:10px' },
    p.status === 'IDENTITY_PENDING'
      ? h('div', { class: 'row' }, method, ref, act('Verificar identidad', () => authed('/api/human/dsar/verificar',
        { case_id: id, method: method.value || 'DNI presencial', reference: ref.value }), reload))
      : h('div', { class: 'row' }, note, act('Aprobar', decide('APPROVED'), reload), act('Rechazar', decide('REJECTED'), reload)),
    h('p', { class: 'small mute' }, 'Aprobar genera los handoffs hacia otros agentes (G4 Evidencia, G5 Terceros, G6 Inventario). También puedes decidir en Revisión humana.'));
}

function extensionCard(id, rights, reload) {
  const right = select('right', rights);
  const days = input('days', 'Días (opcional)');
  const reason = input('reason', 'Motivo de la prórroga');
  const note = input('note', 'Nota al reanudar');
  const preview = h('div', { class: 'small' });
  return card('Prórroga (art. 71) y reanudación',
    h('div', { class: 'row' }, right, days,
      act('Ver opciones', async () => { const o = await g3(`casos/${id}/prorroga?derecho=${right.value}` + (days.value ? `&dias=${Number(days.value)}` : ''));
        preview.replaceChildren(json(o, true)); return { status: o.allowed ? 'permitida' : 'no permitida' }; })),
    h('div', { class: 'row' }, reason,
      act('Aplicar prórroga', () => g3(`casos/${id}/prorroga`, 'POST', { right: right.value, reason: reason.value, days: days.value ? Number(days.value) : null }), reload)),
    h('div', { class: 'row' }, note, act('Reanudar trámite suspendido', () => g3(`casos/${id}/reanudar`, 'POST', { note: note.value }), reload)),
    preview,
    h('p', { class: 'small mute' }, 'El motor calcula los límites; aplicarla es una decisión humana que queda registrada con tu usuario.'));
}

function draftCard(p) {
  const id = p.case_id;
  const mode = select('mode', ['guided', 'gateway']);
  const text = h('textarea', { rows: 14, placeholder: 'Genera el borrador o escríbelo aquí.' });
  const warn = h('div');
  const to = input('to', 'Correo del titular (si no llegó por correo)');
  const kind = select('kind', ['respuesta', 'identidad', 'subsanacion']);
  const missing = input('missing', 'Qué falta (solo subsanación)');
  return card('Borrador de respuesta y exportación',
    h('div', { class: 'row' }, h('label', {}, 'Modo'), mode,
      act('Redactar con el asistente', async () => { const d = await g3(`casos/${id}/borrador`, 'POST', { mode: mode.value, letter: true });
        text.value = d.draft; warn.replaceChildren(...(d.warnings || []).map((w) => alertBox('warn', w))); return { status: 'borrador listo' }; })),
    h('p', { class: 'small mute' }, '«guided» redacta con plantillas, sin modelo. «gateway» usa el modelo de la plataforma (puede ser la nube): solo recibe hechos minimizados.'),
    text, warn,
    h('div', { class: 'row', style: 'margin-top:10px' },
      act('Exportar expediente', async () => { const r = await g3(`casos/${id}/exportar`, 'POST', { draft: text.value });
        download(`${id}.json`, { package: r.package, draft: r.draft, files: r.files }); return { status: 'exportado' }; })),
    h('div', { class: 'row', style: 'margin-top:10px' }, kind, to, missing,
      act('Preparar correo en la bandeja de salida', () => g3('salida', 'POST', { case_id: id, kind: kind.value, to_address: to.value || null, missing: missing.value || null }))));
}

// ---------------------------------------------------------------- correos entrantes
async function correos(box) {
  const [summary, items] = await Promise.all([g3('correos/resumen'), g3('correos')]);
  const reload = () => correos(box);
  box.replaceChildren(
    card('Buzón de entrada', h('p', { class: 'small' }, Object.entries(summary).map(([k, v]) => `${k}: ${v}`).join(' · ')),
      h('div', { class: 'row' },
        act('Cargar 5 correos de demostración', () => g3('correos/demo', 'POST', { count: 5 }), reload),
        act('Revisar buzón y analizar', () => g3('correos/sincronizar', 'POST', { limit: 50 }), reload)),
      h('p', { class: 'small mute' }, 'Un correo nunca verifica la identidad. Sin un modelo local, cada correo queda en «triaje» para que una persona lo revise.')),
    card('Correos', items.length ? table(['#', 'Remitente', 'Asunto', 'Estado', 'Motivo', 'Caso'],
      items.map((m) => [m.id, m.sender, m.subject, m.status, m.reason || '', m.case_id || '—'])) : h('p', { class: 'mute' }, 'Sin correos.')),
    ...items.filter((m) => m.status === 'triaje').map((m) => triage(m, reload)));
}

function triage(m, reload) {
  const rights = select('rights', RIGHTS, true, ['access']);
  const email = input('email', 'Correo del titular', m.sender);
  const reason = input('reason', 'Motivo del descarte');
  const body = h('div');
  return card(`Triaje · correo #${m.id}: ${m.subject}`,
    h('div', { class: 'row' }, act('Ver correo', async () => { const full = await g3(`correos/${m.id}`);
      body.replaceChildren(h('pre', {}, full.body), json(full.proposal)); return { status: 'abierto' }; })), body,
    h('div', { class: 'row' }, rights, email,
      act('Confirmar y registrar caso', () => g3(`correos/${m.id}/confirmar`, 'POST', { request_types: picked(rights), subject_email: email.value }), reload)),
    h('div', { class: 'row' }, reason, act('Descartar', () => g3(`correos/${m.id}/descartar`, 'POST', { reason: reason.value }), reload)));
}

// ---------------------------------------------------------------- bandeja de salida
async function salida(box) {
  const items = await g3('salida');
  const reload = () => salida(box);
  box.replaceChildren(alertBox('info', 'El envío real está desactivado por defecto (DSAR_MAIL_SEND_ENABLED) y solo va a destinatarios de la lista blanca. Enviar es una decisión humana.'),
    ...(items.length ? items.map((o) => {
      const subject = input('subject', 'Asunto', o.subject);
      const text = h('textarea', { rows: 8 }, o.body);
      const reason = input('reason', 'Motivo del descarte');
      const open = o.status === 'borrador';
      return card(`#${o.id} · ${o.case_id} · ${o.kind} → ${o.to_address} · ${o.status}`,
        open ? h('div', {}, subject, text,
          h('div', { class: 'row', style: 'margin-top:10px' },
            act('Guardar cambios', () => g3(`salida/${o.id}`, 'PUT', { subject: subject.value, body: text.value }), reload),
            act('Enviar', () => g3(`salida/${o.id}/enviar`, 'POST', {}), reload), reason,
            act('Descartar', () => g3(`salida/${o.id}/descartar`, 'POST', { reason: reason.value }), reload)))
          : h('pre', {}, o.body));
    }) : [h('p', { class: 'mute' }, 'La bandeja de salida está vacía. Prepara un correo desde un expediente.')]));
}

// ---------------------------------------------------------------- indicadores, política y auditoría
// ---- charts: plain HTML/CSS bars (no libraries, nothing loaded from outside); colors follow the platform theme
const LABELS = {
  IDENTITY_PENDING: 'Identidad pendiente', APPROVAL_REQUIRED: 'Requiere aprobación', REVIEW: 'En revisión', ON_HOLD: 'Suspendido',
  APPROVED: 'Aprobado', REJECTED: 'Rechazado', CANCELLED: 'Cancelado', TRIAGED: 'Clasificado',
  information: 'Información', access: 'Acceso', portability: 'Portabilidad', rectification: 'Rectificación', erasure: 'Supresión', objection: 'Oposición',
  API: 'Formulario / API', MCP: 'Plataforma (MCP)', EMAIL: 'Correo', correo: 'Lectura de correos', chat: 'Asistente',
  recibido: 'Recibido', en_analisis: 'En análisis', registrado: 'Registrado', triaje: 'En triaje (revisión humana)',
  descartado: 'Descartado', asociado: 'Asociado a un caso',
};
const STATE_COLOR = { APPROVED: 'var(--ok)', REJECTED: 'var(--bad)', CANCELLED: 'var(--off)', IDENTITY_PENDING: 'var(--warn)', ON_HOLD: 'var(--warn)' };
const label = (k) => LABELS[k] || k;
const pct = (v) => (v == null ? '—' : `${Math.round(v)} %`);
const num = (v, unit = '') => (v == null ? '—' : `${Math.round(v * 10) / 10}${unit}`);

function tile(title, value, note, color) {
  return h('div', { class: 'card' }, h('div', { class: 'small mute' }, title),
    h('div', { class: 'kpi', style: color ? `color:${color}` : '' }, value), note ? h('div', { class: 'small mute' }, note) : null);
}

// Horizontal bars, one row per item: label, bar proportional to the largest value, and the number.
function bars(items, colorOf = () => 'var(--brand)') {
  if (!items.length || !items.some((x) => x.count)) return h('p', { class: 'mute small' }, 'Sin datos todavía.');
  const max = Math.max(...items.map((x) => x.count));
  return h('div', { role: 'list', style: 'display:grid;gap:8px' }, items.map((x) => h('div', { role: 'listitem', style: 'display:grid;grid-template-columns:minmax(110px,38%) 1fr auto;gap:10px;align-items:center' },
    h('span', { class: 'small', style: 'overflow-wrap:anywhere' }, label(x.key)),
    h('span', { style: 'background:var(--off-bg);border-radius:6px;height:14px;overflow:hidden' },
      h('span', { style: `display:block;height:100%;width:${max ? (x.count / max) * 100 : 0}%;background:${colorOf(x.key)};border-radius:6px` })),
    h('strong', { class: 'small', style: 'min-width:2ch;text-align:right' }, x.count))));
}

// Weekly columns (the last 8 weeks the agent reports).
function columns(items) {
  if (!items.some((x) => x.count)) return h('p', { class: 'mute small' }, 'Sin casos en las últimas semanas.');
  const max = Math.max(...items.map((x) => x.count));
  return h('div', { style: 'display:flex;gap:8px;align-items:flex-end;height:170px;padding-top:6px' }, items.map((x) =>
    h('div', { title: `${x.key}: ${x.count}`, style: 'flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;height:100%;justify-content:flex-end' },
      h('strong', { class: 'small' }, x.count),
      h('span', { style: `width:100%;max-width:42px;height:${(x.count / max) * 120}px;min-height:2px;background:var(--brand);border-radius:6px 6px 0 0` }),
      h('span', { class: 'small mute', style: 'font-size:11px' }, x.key.split('-')[1] || x.key))));
}

// One bar split in parts (open cases by deadline status), with a legend.
function stacked(parts) {
  const total = parts.reduce((s, p) => s + p.value, 0);
  if (!total) return h('p', { class: 'mute small' }, 'No hay expedientes abiertos.');
  return h('div', {},
    h('div', { style: 'display:flex;height:22px;border-radius:6px;overflow:hidden;background:var(--off-bg)' },
      parts.filter((p) => p.value).map((p) => h('span', { title: `${p.label}: ${p.value}`, style: `width:${(p.value / total) * 100}%;background:${p.color}` }))),
    h('div', { class: 'row small', style: 'margin-top:8px' }, parts.map((p) =>
      h('span', { class: 'row', style: 'gap:6px' }, h('i', { style: `width:10px;height:10px;border-radius:3px;background:${p.color};display:inline-block` }), `${p.label}: ${p.value}`))));
}

async function indicadores(box) {
  const i = await g3('indicadores');
  const d = i.deadlines || {}, hitl = i.hitl || {}, mail = i.mail || {}, out = i.outbox || {}, llm = i.llm || {};
  box.replaceChildren(
    h('p', { class: 'small mute' }, `Datos al ${i.as_of}. Los calcula el motor del agente (cláusula 9.1, seguimiento y medición); no hay estimaciones del modelo.`),
    h('div', { class: 'kpis' },
      tile('Expedientes', i.cases_total, `${d.open ?? 0} abiertos · ${d.decided ?? 0} decididos`),
      tile('Plazos vencidos', d.overdue ?? 0, 'expedientes abiertos', d.overdue ? 'var(--bad)' : 'var(--ok)'),
      tile('Por vencer', d.due_soon ?? 0, 'en los próximos días', d.due_soon ? 'var(--warn)' : null),
      tile('Decididos en plazo', pct(d.within_pct), `${d.decided_within ?? 0} de ${d.decided ?? 0}`),
      tile('Requieren revisión humana', pct(hitl.required_pct), `${hitl.required ?? 0} de ${hitl.verified ?? 0} con identidad verificada`),
      tile('Identidad pendiente', i.identity?.pending ?? 0, i.identity?.avg_age_days != null ? `antigüedad media ${num(i.identity.avg_age_days, ' días')}` : null)),
    card('Plazos de los expedientes abiertos', stacked([
      { label: 'A tiempo', value: d.on_time || 0, color: 'var(--ok)' },
      { label: 'Por vencer', value: d.due_soon || 0, color: 'var(--warn)' },
      { label: 'Vencidos', value: d.overdue || 0, color: 'var(--bad)' }]),
    h('p', { class: 'small mute', style: 'margin-top:10px' }, `Prórrogas aplicadas: ${d.extensions ?? 0} · suspensiones: ${d.suspensions ?? 0} · resolución media: ${d.avg_resolution_days == null ? '—' : d.avg_resolution_days < 1 ? 'menos de 1 día' : num(d.avg_resolution_days, ' días')}`)),
    h('div', { class: 'grid g2' },
      card('Casos por estado', bars(i.by_status || [], (k) => STATE_COLOR[k] || 'var(--brand)')),
      card('Casos por derecho', bars(i.by_right || [])),
      card('Casos por origen', bars(i.by_origin || [])),
      card('Casos por semana', columns(i.by_week || [])),
      card('Decisiones humanas', bars(hitl.decisions || [], (k) => STATE_COLOR[k] || 'var(--brand)')),
      card('Motivos de revisión humana más frecuentes', bars(hitl.top_reasons || [], () => 'var(--warn)')),
      card('Correos entrantes', bars(mail.by_status || []),
        h('p', { class: 'small mute', style: 'margin-top:10px' }, `Registrados en triaje por una persona: ${mail.triage_registered ?? 0} · automáticos: ${mail.auto_registered ?? 0}`)),
      card('Bandeja de salida', bars([{ key: 'Borradores', count: out.drafts || 0 }, { key: 'Enviados', count: out.sent || 0 }, { key: 'Descartados', count: out.discarded || 0 }])),
      card('Uso del modelo', h('div', { class: 'kpis' },
        tile('Llamadas', llm.calls ?? 0), tile('Con error', llm.errors ?? 0, null, llm.errors ? 'var(--bad)' : null), tile('Latencia media', num(llm.avg_latency_s, ' s'))),
      h('div', { style: 'margin-top:10px' }, bars(llm.by_task || [])))),
    json(i));
}

async function politica(box) {
  const p = await g3('politica');
  const text = h('textarea', { rows: 18 }, JSON.stringify(p.policy, null, 2));
  box.replaceChildren(card('Política de la organización', h('p', { class: 'small mute' }, `sha256 ${p.sha256 || '—'} · versiones anteriores: ${(p.history || []).length}`),
    text, h('div', { class: 'row', style: 'margin-top:10px' },
      act('Guardar política', () => { let policy; try { policy = JSON.parse(text.value); } catch { throw new Error('El JSON no es válido.'); }
        return g3('politica', 'PUT', { policy }); }, () => politica(box))),
    h('p', { class: 'small mute' }, 'El motor la valida: puede acortar plazos, nunca alargar uno legal. Se guarda en el contenedor del agente.')));
}

async function auditoria(box) {
  const a = await g3('auditoria');
  box.replaceChildren(card('Llamadas al modelo (solo metadatos, sin texto)', (a.llm || []).length ? table(['Hora', 'Caso', 'Tarea', 'Proveedor', 'Modelo', 'OK', 'Segundos'],
    a.llm.map((c) => [c.at, c.case_id || '—', c.task || '', c.provider, c.model, c.ok ? 'sí' : 'no', c.latency_s])) : h('p', { class: 'mute' }, 'Sin llamadas.')),
  card('Skill y modelos', json({ skill: a.skill, modelos: a.modelos }, true)));
}

const TABS = [['Expediente', expediente], ['Correos entrantes', correos], ['Bandeja de salida', salida],
  ['Indicadores', indicadores], ['Política', politica], ['Auditoría', auditoria]];

async function gestion(root, rerender) {
  root.append(h('p', { class: 'sub' }, 'Expediente completo, identidad y decisión, borrador, prórroga, exportación, correos, bandeja de salida, indicadores y política. Solo para una persona con rol DPO; ninguna acción la toma un modelo.'));
  const me = await whoami();
  if (!me) return loginForm(root, rerender);
  if (me.role !== 'DPO') return root.append(alertBox('warn', `Tu rol (${me.role}) no puede gestionar solicitudes de derechos: se requiere DPO.`));
  let current = TABS[0];
  const tabs = h('div', { class: 'tabs' });
  const box = h('div');
  const draw = async () => {
    tabs.replaceChildren(...TABS.map((t) => h('button', { class: t === current ? 'on' : '', onclick: () => { current = t; draw(); } }, t[0])));
    box.replaceChildren(spinner('Cargando…'));
    try { await current[1](box); } catch (e) { box.replaceChildren(alertBox('bad', e.message)); }
  };
  root.append(h('div', { class: 'row', style: 'margin-bottom:14px' }, h('span', { class: 'badge b-operativo' }, `${me.user} · ${me.role}`),
    h('button', { class: 'ghost', onclick: () => { session.token = null; session.user = null; rerender(); } }, 'Cerrar sesión')), tabs, box);
  await draw();
}

// G3 · DSAR: one page. «Herramientas del agente» is the platform's generic agent page (open, like the other
// agents); «Gestión (DPO)» is the agent's own panel behind a DPO session. /agentes/dsar/gestion opens the second.
const VIEWS = [['herramientas', 'Herramientas del agente'], ['gestion', 'Gestión (DPO)']];

export async function dsarPage(root, rerender) {
  const cfg = AGENTS.dsar;
  const detail = await api.agents().then((l) => l.find((a) => a.group === cfg.group)).catch(() => null);
  const view = location.pathname.endsWith('/gestion') ? 'gestion' : 'herramientas';
  const go = (v) => { history.pushState({}, '', v === 'gestion' ? '/agentes/dsar/gestion' : '/agentes/dsar'); rerender(); };
  const box = h('div');
  root.append(h('div', { class: 'row', style: 'justify-content:space-between' }, h('h1', {}, `G${cfg.group} · ${cfg.title}`), detail ? badge(detail.status) : null),
    h('p', { class: 'sub' }, cfg.about),
    h('div', { class: 'tabs', style: 'border-bottom:1px solid var(--line);padding-bottom:12px' },
      VIEWS.map(([id, label]) => h('button', { class: id === view ? 'on' : '', onclick: () => id !== view && go(id) }, label))),
    box);
  if (view === 'gestion') await gestion(box, rerender);
  else await agentPage(box, 'dsar', { header: false });
}
