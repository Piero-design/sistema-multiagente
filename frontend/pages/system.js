import { api } from '../services/api.js';
import { h, badge, fmtTime, alertBox } from '../components/ui.js';
import { table } from './dashboard.js';

export async function actividad(root) {
  root.append(h('h1', {}, 'Actividad'), h('p', { class: 'sub' }, 'Ejecuciones y eventos reales registrados por el orquestador en PostgreSQL.'));
  const [ex, act, sys] = await Promise.all([api.executions(), api.activity(), api.system()]);
  const l = sys.llm;
  root.append(h('div', { class: 'card' }, h('h2', {}, 'Gateway LLM'),
    h('p', { class: 'small' }, `Llamadas: ${l.requests} · errores: ${l.errors} · latencia media: ${l.avg_latency_ms} ms · tokens entrada/salida: ${l.prompt_tokens}/${l.completion_tokens}`)),
    h('h2', { style: 'margin-top:20px' }, 'Ejecuciones recientes'),
    h('div', { class: 'card' }, ex.length ? table(['Hora', 'Agente', 'Acción', 'Estado', 'Modo', 'Error'],
      ex.map((r) => [fmtTime(r.created_at), r.agent_id, r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || ''])) : h('span', { class: 'mute' }, 'Sin ejecuciones.')),
    h('h2', { style: 'margin-top:20px' }, 'Eventos'),
    h('div', { class: 'card' }, act.events.length ? table(['Hora', 'Agente', 'Evento', 'Detalle'],
      act.events.map((e) => [fmtTime(e.created_at), e.agent_id, e.kind, e.message || ''])) : h('span', { class: 'mute' }, 'Sin eventos.')));
}

export async function configuracion(root) {
  root.append(h('h1', {}, 'Configuración'), h('p', { class: 'sub' }, 'Solo lectura. La configuración se cambia en el archivo .env y reiniciando los servicios.'));
  const [sys, agents] = await Promise.all([api.system(), api.agents()]);
  const l = sys.llm;
  if (l.data_leaves_machine) root.append(alertBox('warn', 'Los datos salen de esta máquina: el modo es "nube" y cada consulta a un agente se envía al proveedor del modelo.'));
  if (l.simulated) root.append(alertBox('sim', 'Modo simulado: ninguna respuesta proviene de un modelo real.'));
  const out = h('div', { class: 'small', style: 'margin-top:10px' });
  root.append(h('div', { class: 'grid g2' },
    h('div', { class: 'card' }, h('h2', {}, 'Gateway LLM'), table(['Parámetro', 'Valor'], [
      ['Modo (LLM_MODE)', l.mode], ['Modelo', l.model || '—'], ['Modelo de embeddings', l.embed_model || '—'],
      ['Datos salen de la máquina', l.data_leaves_machine ? 'Sí' : 'No'], ['Simulado', l.simulated ? 'Sí' : 'No']]),
      h('button', { style: 'margin-top:12px', onclick: async (ev) => { ev.target.disabled = true; out.textContent = 'Probando…';
        try { const r = await api.probe(); out.textContent = `Respuesta real en ${r.latency_ms} ms (${r.model}).`; } catch (e) { out.textContent = 'Falló: ' + e.message; } ev.target.disabled = false; } }, 'Probar conexión con el modelo'), out),
    h('div', { class: 'card' }, h('h2', {}, 'Base de datos'), table(['Parámetro', 'Valor'], [
      ['PostgreSQL', sys.database.ok ? 'Conectado' : 'Sin conexión'], ['Base', sys.database.db || '—'], ['Tablas en esquema demo', sys.database.demo_tables ?? '—']]))),
    h('h2', { style: 'margin-top:20px' }, 'Clave de Gemini por equipo'),
    h('div', { class: 'card' },
      h('p', { class: 'small mute' }, 'Cada equipo usa su propia clave a través del gateway, para no saturar la cuota de otro. Aquí solo se ve si existe y cuánto usó; las claves nunca se muestran.'),
      l.shared_fallback ? alertBox('warn', 'Modo desarrollo: los equipos sin clave propia usan la clave compartida (LLM_ALLOW_SHARED_FALLBACK=true). Desactívalo cuando cada equipo tenga la suya.') : null,
      l.teams ? table(['Equipo', 'Clave propia', 'Modelo', 'Llamadas', 'Errores', 'Tokens (ent./sal.)', 'Última'],
        Object.entries(l.teams).map(([k, t]) => [k.toUpperCase(), t.own_key ? (t.key_source === 'web' ? 'Sí (puesta desde la web)' : 'Sí (archivo .env)') : (t.usable ? 'No (usa la compartida)' : 'No: falta'), t.model || '—',
          t.requests, t.errors, `${t.prompt_tokens}/${t.completion_tokens}`, t.last_call_at || '—'])) : h('span', { class: 'mute' }, 'Sin datos.')),
    h('h2', { style: 'margin-top:20px' }, 'Configurar la clave de mi equipo'),
    teamKeyForm(l),
    h('h2', { style: 'margin-top:20px' }, 'Agentes'),
    h('div', { class: 'card' }, table(['Grupo', 'Agente', 'Estado', 'Motivo'], agents.map((a) => [`G${a.group}`, a.name, badge(a.status), a.reason || '']))));
}

function teamKeyForm(l) {
  const msg = h('div', { style: 'margin-top:10px' });
  const teams = Object.keys(l.teams || {});
  const form = h('form', { class: 'card' },
    h('p', { class: 'small mute' }, 'Cada equipo pega aquí su propia clave de Gemini (se obtiene en Google AI Studio). Necesitas el código de tu equipo, que entrega el administrador. La clave se prueba contra Google antes de guardarse, no se vuelve a mostrar y solo la usa tu agente.'),
    h('div', { class: 'grid g2' },
      h('div', {}, h('label', {}, 'Equipo'), h('select', { name: 'team' }, teams.map((t) => h('option', { value: t }, t.toUpperCase())))),
      h('div', {}, h('label', {}, 'Código del equipo'), h('input', { name: 'code', type: 'password', autocomplete: 'off' }))),
    h('label', {}, 'Clave de Gemini'), h('input', { name: 'key', type: 'password', autocomplete: 'off', placeholder: 'AIza…' }),
    h('div', { class: 'row', style: 'margin-top:14px' },
      h('button', { type: 'submit' }, 'Guardar clave'),
      h('button', { type: 'button', class: 'ghost', onclick: () => send('DELETE') }, 'Quitar la clave guardada en la web')),
    msg);
  async function send(method) {
    const f = form.elements;
    msg.replaceChildren(spinner(method === 'DELETE' ? 'Quitando…' : 'Probando la clave con Google…'));
    try {
      const r = await fetch(`/api/teams/${f.team.value}/key`, { method, headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ code: f.code.value, key: method === 'DELETE' ? '' : f.key.value }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'No se pudo guardar');
      f.key.value = '';
      msg.replaceChildren(alertBox('info', method === 'DELETE' ? 'Clave quitada.' : `Clave de ${f.team.value.toUpperCase()} guardada y verificada. Recarga la página para ver el estado.`));
    } catch (e) { msg.replaceChildren(alertBox('bad', e.message)); }
  }
  form.addEventListener('submit', (ev) => { ev.preventDefault(); send('PUT'); });
  return form;
}
