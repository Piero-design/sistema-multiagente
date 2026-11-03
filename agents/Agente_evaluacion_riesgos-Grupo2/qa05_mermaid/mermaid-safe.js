// Reparación conservadora: solo se aplica después de que Mermaid rechace la sintaxis original.
// No elimina contenido y no intenta corregir diagramas de otros tipos.
export function normalizeFlowchartLabels(source) {
  const text = String(source ?? '').trim();
  if (!/^(?:flowchart|graph)\s+(?:TD|TB|BT|LR|RL)\b/i.test(text)) return text;
  return text.replace(/\b([a-zA-Z][a-zA-Z0-9_-]*)\[([^\[\]\r\n]+)\]/g, (all, node, label) => {
    const clean = label.trim();
    if (!clean || /^["'`]/.test(clean)) return all;
    return `${node}["${clean.replace(/"/g, '#quot;')}"]`;
  });
}
