// Servidor MCP mínimo (stdio, JSON-RPC por líneas) que expone los conectores a Claude Code.
// Lo lanza el propio servidor web con --mcp-config; no requiere dependencias.
const readline = require('readline');
const { paraMcp, ejecutar } = require('./conectores');

const send = o => process.stdout.write(JSON.stringify({ jsonrpc: '2.0', ...o }) + '\n');

readline.createInterface({ input: process.stdin }).on('line', async linea => {
  let m;
  try { m = JSON.parse(linea); } catch { return; }
  if (m.id === undefined) return;                       // notificaciones: sin respuesta
  switch (m.method) {
    case 'initialize':
      return send({ id: m.id, result: { protocolVersion: m.params?.protocolVersion || '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'conectores', version: '1.0.0' } } });
    case 'ping':
      return send({ id: m.id, result: {} });
    case 'tools/list':
      return send({ id: m.id, result: { tools: paraMcp() } });
    case 'tools/call': {
      const r = await ejecutar(m.params?.name, m.params?.arguments);
      return send({ id: m.id, result: { content: [{ type: 'text', text: JSON.stringify(r) }], isError: !!r.error } });
    }
    default:
      return send({ id: m.id, error: { code: -32601, message: 'Método no soportado' } });
  }
});
