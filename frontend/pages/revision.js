import { authed, login, session, whoami } from '../services/api.js';
import { h, alertBox, spinner } from '../components/ui.js';

export function loginForm(root, onDone) {
  const err = h('div');
  const f = h('form', { class: 'card', style: 'max-width:420px' },
    h('h2', {}, 'Iniciar sesión'),
    h('p', { class: 'small mute' }, 'Las decisiones que los agentes dejan a una persona solo se registran con una sesión y un rol. Cuentas de demostración por defecto: dpo / demo-dpo y legal / demo-legal (cámbialas en el archivo .env).'),
    h('label', {}, 'Usuario'), h('input', { name: 'u', autocomplete: 'username' }),
    h('label', {}, 'Contraseña'), h('input', { name: 'p', type: 'password', autocomplete: 'current-password' }),
    h('button', { type: 'submit', style: 'margin-top:14px' }, 'Entrar'), err);
  f.addEventListener('submit', async (ev) => {
    ev.preventDefault(); err.replaceChildren(spinner('Verificando…'));
    try { await login(f.elements.u.value, f.elements.p.value); onDone(); } catch (e) { err.replaceChildren(alertBox('bad', e.message)); }
  });
  root.append(f);
}

const row = (...c) => h('div', { class: 'row', style: 'justify-content:space-between;border-bottom:1px solid var(--line);padding:10px 0' }, ...c);

function actionBox(label, run, fields = []) {
  const out = h('span', { class: 'small' });
  const inputs = fields.map((x) => h('input', { placeholder: x.ph, name: x.name, style: 'max-width:200px' }));
  const btn = h('button', { class: 'ghost', onclick: async (ev) => {
    ev.target.disabled = true; out.textContent = '…';
    try { const r = await run(Object.fromEntries(inputs.map((i) => [i.name, i.value]))); out.textContent = '✔ ' + (r?.status || r?.estado || 'registrado'); }
    catch (e) { out.textContent = '✖ ' + e.message.slice(0, 160); out.style.color = 'var(--bad)'; }
    ev.target.disabled = false; } }, label);
  return h('span', { class: 'row' }, ...inputs, btn, out);
}

export async function revision(root, rerender) {
  root.append(h('h1', {}, 'Revisión humana'),
    h('p', { class: 'sub' }, 'Aquí una persona toma las decisiones que los agentes dejan abiertas a propósito: ningún modelo puede aprobar, rechazar ni verificar identidad. Cada decisión queda registrada con quién la tomó.'));
  const me = await whoami();
  if (!me) return loginForm(root, rerender);
  root.append(h('div', { class: 'row', style: 'margin-bottom:14px' }, h('span', { class: 'badge b-operativo' }, `${me.user} · ${me.role}`),
    h('button', { class: 'ghost', onclick: () => { session.token = null; session.user = null; rerender(); } }, 'Cerrar sesión')));
  const box = h('div', {}, spinner('Cargando pendientes…'));
  root.append(box);
  let d;
  try { d = await authed('/api/human/pendientes'); } catch (e) { return box.replaceChildren(alertBox('bad', e.message)); }
  box.replaceChildren();

  // G5: DPO first, then Legal (the agent enforces the order)
  box.append(h('div', { class: 'card' }, h('h2', {}, 'G5 · Contratos con proveedores (aprobación DPO → Legal)'),
    d.terceros.length ? d.terceros.map((x) => row(h('span', {}, h('strong', {}, x.proveedor || x.id_registro), h('br'),
      h('span', { class: 'small mute' }, `${x.id_registro}${x.organizacion ? ' · ' + x.organizacion : ''} · puntaje ${x.puntaje} · ${x.banda} · ${x.estado}`)),
      h('span', { class: 'row' },
        actionBox('Aprobar', (v) => authed('/api/human/terceros/aprobar', { id_registro: x.id_registro, decision: 'aprobar', comentario: v.c }), [{ name: 'c', ph: 'Comentario' }]),
        actionBox('Rechazar', (v) => authed('/api/human/terceros/aprobar', { id_registro: x.id_registro, decision: 'rechazar', comentario: v.c }), [{ name: 'c', ph: 'Motivo' }]))))
      : h('p', { class: 'mute' }, 'No hay expedientes pendientes.'),
    h('p', { class: 'small mute' }, 'Un expediente sigue «Pendiente DPO» hasta que decida el DPO; después le toca a Legal. Fuera de turno, el agente rechaza la decisión (409).'),
    h('h2', { style: 'margin-top:14px' }, 'G5 · Perfiles de organización por validar (DPO)'),
    (d.terceros_perfiles || []).length ? d.terceros_perfiles.map((p) => row(h('span', {}, h('strong', {}, p.nombre || p.organizacion), h('br'),
      h('span', { class: 'small mute' }, `${p.organizacion} · ${p.estado || 'sin estado'}${p.valido === false ? ' · con errores de formato' : ''}`)),
      actionBox('Validar perfil', () => authed('/api/human/terceros/perfil/validar', { organizacion: p.organizacion }))))
      : h('p', { class: 'mute' }, 'No hay perfiles en borrador.'),
    h('p', { class: 'small mute' }, 'El agente genera el perfil a partir de los documentos institucionales y lo deja en Borrador; mientras no lo valide el DPO, cada auditoría lo advierte.')));

  // G3: identity then decision (DPO)
  box.append(h('div', { class: 'card', style: 'margin-top:14px' }, h('h2', {}, 'G3 · Solicitudes de derechos (verificar identidad y decidir)'),
    d.dsar.length ? d.dsar.map((x) => row(h('span', {}, h('strong', {}, x.case_id), h('br'), h('span', { class: 'small mute' }, x.status)),
      h('span', { class: 'row' },
        actionBox('Verificar identidad', (v) => authed('/api/human/dsar/verificar', { case_id: x.case_id, method: v.m || 'DNI presencial', reference: v.r || '' }), [{ name: 'm', ph: 'Método (DNI presencial)' }]),
        actionBox('Aprobar', (v) => authed('/api/human/dsar/decidir', { case_id: x.case_id, decision: 'APPROVED', note: v.n || 'Aprobado' }), [{ name: 'n', ph: 'Justificación' }]),
        actionBox('Rechazar', (v) => authed('/api/human/dsar/decidir', { case_id: x.case_id, decision: 'REJECTED', note: v.n || 'Rechazado' }), [{ name: 'n', ph: 'Justificación' }]))))
      : h('p', { class: 'mute' }, 'No hay solicitudes pendientes.'),
    h('p', { class: 'small mute' }, 'Sin identidad verificada el agente no busca registros ni permite decidir. Al aprobar se generan los handoffs hacia otros agentes (ver «Flujos entre agentes» en el Panel).')));

  // G8: proposed actions
  box.append(h('div', { class: 'card', style: 'margin-top:14px' }, h('h2', {}, 'G8 · Acciones propuestas por el agente de incidentes'),
    d.incidentes.length ? d.incidentes.map((inc) => h('div', {}, h('strong', {}, inc.expediente),
      ...inc.acciones.map((a) => row(h('span', { class: 'small' }, `${a.id}: ${a.descripcion || a.accion || a.titulo || JSON.stringify(a).slice(0, 140)}`),
        h('span', { class: 'row' },
          actionBox('Aprobar', () => authed('/api/human/incidentes/decidir', { expediente: inc.expediente, accion: a.id, decision: 'aprobada' })),
          actionBox('Rechazar', () => authed('/api/human/incidentes/decidir', { expediente: inc.expediente, accion: a.id, decision: 'rechazada' })))))))
      : h('p', { class: 'mute' }, 'No hay acciones propuestas pendientes (analiza un incidente en G8 primero).'),
    h('p', { class: 'small mute' }, 'Aprobar solo registra la decisión: el agente no ejecuta contención ni envía notificaciones.')));
}
