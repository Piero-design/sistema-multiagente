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
