export async function api(path, opt) {
  const r = await fetch(path, opt);
  let j = {};
  try { j = await r.json(); } catch { /* sin cuerpo */ }
  if (!r.ok) throw new Error(j.error || `Error ${r.status}`);
  return j;
}
export const post = (p, body) => api(p, { method: 'POST', body: JSON.stringify(body ?? {}) });
export const del = p => api(p, { method: 'DELETE' });

export const store = {
  get(k, d = '') { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* sin almacenamiento */ } },
};
