async function j(url, opt) {
  const r = await fetch(url, opt);
  if (!r.ok) throw new Error(`${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.json();
}

export const api = {
  agents: () => j('/api/agents'),
  system: () => j('/api/system'),
  activity: () => j('/api/activity?limit=60'),
  executions: (agent) => j('/api/executions?limit=30' + (agent ? `&agent_id=${agent}` : '')),
  execution: (id) => j(`/api/executions/${id}`),
  probe: () => j('/api/system/llm/probe', { method: 'POST' }),
  execute: (agent, action, input) => j(`/api/agents/${agent}/execute`, {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action, input }) }),
  // Real polling of the persisted execution; no simulated progress.
  async run(agent, action, input, onTick) {
    const { execution_id } = await this.execute(agent, action, input);
    for (;;) {
      const e = await this.execution(execution_id);
      onTick?.(e);
      if (e.status === 'succeeded' || e.status === 'failed') return e;
      await new Promise((r) => setTimeout(r, 2500));
    }
  },
};

// ---- signed-in human (decisions that agents leave to a person) ----
const KEY = 'pims_token';
export const session = {
  get token() { try { return sessionStorage.getItem(KEY); } catch { return null; } },
  set token(v) { try { v ? sessionStorage.setItem(KEY, v) : sessionStorage.removeItem(KEY); } catch { /* ignore */ } },
  user: null,
};
export async function authed(url, body) {
  const r = await fetch(url, { method: body ? 'POST' : 'GET', headers: { 'content-type': 'application/json', Authorization: 'Bearer ' + session.token }, body: body ? JSON.stringify(body) : undefined });
  const text = await r.text();
  let data; try { data = JSON.parse(text); } catch { data = { detail: text }; }
  if (r.status === 401) { session.token = null; session.user = null; }
  if (!r.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data));
  return data;
}
export async function login(user, password) {
  const r = await fetch('/api/auth/login', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ user, password }) });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || 'No se pudo iniciar sesión');
  session.token = d.token; session.user = { user: d.user, role: d.role };
  return session.user;
}
export async function whoami() {
  if (!session.token) return null;
  try { session.user = await authed('/api/auth/me'); return session.user; } catch { return null; }
}
