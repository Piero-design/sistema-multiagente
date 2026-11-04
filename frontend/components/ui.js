export const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'class') el.className = v;
    else if (v !== false && v != null) el.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : document.createTextNode(k));
  return el;
};
export const STATUS = { operativo: 'Operativo', degradado: 'Degradado', parcial: 'Parcial', caido: 'Caído', fuera_de_alcance: 'Fuera de alcance' };
export const badge = (s) => h('span', { class: `badge b-${s}` }, STATUS[s] || s);
export const fmtTime = (t) => (t ? new Date(t).toLocaleString('es-PE') : '—');
export const alertBox = (kind, text) => h('div', { class: `alert ${kind}` }, text);
export const spinner = (txt) => h('span', {}, h('span', { class: 'spin' }), ' ', txt || 'Procesando…');
