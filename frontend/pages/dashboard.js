import { api } from '../services/api.js';
import { h, badge, fmtTime, alertBox } from '../components/ui.js';
import { AGENTS } from '../services/agents-config.js';

export async function dashboard(root) {
  root.append(h('h1', {}, 'Panel general'), h('p', { class: 'sub' }, 'Estado real de los ocho agentes, del gateway LLM y de PostgreSQL.'));
  const [agents, sys, act] = await Promise.all([api.agents(), api.system(), api.activity()]);
  const llm = sys.llm, db = sys.database;

  if (llm.mode === 'mock') root.append(alertBox('sim', 'Modo SIMULADO: las respuestas no provienen de un modelo real.'));
  if (llm.data_leaves_machine) root.append(alertBox('warn', 'Modo nube: los textos enviados a los agentes salen de esta máquina hacia el proveedor del modelo.'));

  root.append(h('div', { class: 'kpis' },
    kpi('Modo LLM', llm.ok ? llm.mode : 'sin conexión'), kpi('Modelo', llm.model || '—'),
    kpi('Última latencia', llm.last_latency_ms != null ? llm.last_latency_ms + ' ms' : '—'),
    kpi('PostgreSQL', db.ok ? `OK · ${db.demo_tables} tablas demo` : 'caído'),
    kpi('Llamadas LLM', `${llm.requests ?? 0} (${llm.errors ?? 0} errores)`)));

  root.append(h('h2', { style: 'margin-top:24px' }, 'Agentes'));
  const grid = h('div', { class: 'grid g4' });
  for (const a of agents) {
    const cfg = Object.values(AGENTS).find((c) => c.group === a.group);
    grid.append(h('a', { class: 'card link', href: a.route, 'data-link': '' },
      h('div', { class: 'row', style: 'justify-content:space-between' }, h('strong', {}, `G${a.group} · ${a.name}`), badge(a.status)),
      h('p', { class: 'small mute' }, a.responsibility),
      a.reason ? h('p', { class: 'small', style: 'color:var(--warn)' }, a.reason) : null,
      h('p', { class: 'small mute' }, a.status === 'fuera_de_alcance' ? 'Sin acciones disponibles' : `${a.capabilities} acción(es) disponible(s)`)));
    void cfg;
  }
  root.append(grid);

  const failed = act.by_agent.filter((r) => r.status === 'failed');
  const total = act.by_agent.reduce((s, r) => s + Number(r.n), 0);
  root.append(h('h2', { style: 'margin-top:24px' }, 'Estadísticas y actividad reciente'),
    h('div', { class: 'grid g2' },
      h('div', { class: 'card' }, h('div', { class: 'kpis' }, kpi('Ejecuciones', total),
        kpi('Con error', failed.reduce((s, r) => s + Number(r.n), 0)))),
      h('div', { class: 'card' }, act.events.length ? table(['Hora', 'Agente', 'Evento'],
        act.events.slice(0, 8).map((e) => [fmtTime(e.created_at), e.agent_id, `${e.kind}${e.message ? ' · ' + e.message : ''}`]))
        : h('span', { class: 'mute' }, 'Aún no hay actividad.'))));
}
const kpi = (t, v) => h('div', { class: 'card' }, h('div', { class: 'small mute' }, t), h('div', { class: 'kpi', style: 'font-size:20px' }, String(v)));
export const table = (head, rows) => h('table', {},
  h('thead', {}, h('tr', {}, head.map((x) => h('th', {}, x)))),
  h('tbody', {}, rows.map((r) => h('tr', {}, r.map((c) => h('td', {}, c ?? ''))))));
