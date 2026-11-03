// Rutas, configuración y utilidades compartidas por el servidor y el servidor MCP.
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DATA = process.env.IB_DATA || path.join(ROOT, '.ib-data');
const SALIDAS = path.join(ROOT, 'salidas');
const BUZON_FILE = path.join(DATA, 'buzon.json');
const ESTADO_FILE = path.join(DATA, 'autonomia.json');

const leerJson = (f, def) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return def; } };
const escribirJson = (f, o) => {
  fs.mkdirSync(path.dirname(f), { recursive: true });
  const t = f + '.tmp';
  fs.writeFileSync(t, JSON.stringify(o, null, 2));
  fs.renameSync(t, f);
};
const ls = d => { try { return fs.readdirSync(d, { withFileTypes: true }); } catch { return []; } };

// Carpetas que ningún conector ni herramienta del agente puede leer (credenciales y configuración).
const VETADOS = new Set(['.ib-data', '.git', 'config', 'node_modules', '.claude']);
function rutaSegura(rel, base = ROOT) {
  const p = path.resolve(base, String(rel || ''));
  if (p !== base && !p.startsWith(base + path.sep)) return null;
  const partes = path.relative(ROOT, p).split(path.sep);
  if (partes[0] === '..' || path.isAbsolute(path.relative(ROOT, p))) return null;
  if (VETADOS.has(partes[0]) || partes.some(x => x === '.env' || x.startsWith('.env.'))) return null;
  return p;
}

// ---- Configuración de conectores ----
const CONFIG_CANDIDATAS = [
  process.env.CONECTORES_FILE,
  path.join(ROOT, 'config', 'conectores.json'),
  path.join(ROOT, 'config', 'conectores.ejemplo.json'),
].filter(Boolean);

const DEFECTO = { autonomia: {}, conocimiento: [], sistemas: [], buzones: [] };
function cargarConfig() {
  for (const f of CONFIG_CANDIDATAS) {
    if (!fs.existsSync(f)) continue;
    const c = leerJson(f, null);
    if (!c) return { ...DEFECTO, _archivo: f, _error: 'JSON inválido' };
    const norm = l => (Array.isArray(l) ? l.filter(x => x && /^[a-z0-9][\w-]{0,40}$/.test(x.id || '')) : []);
    return {
      autonomia: { intervalo_seg: 60, max_por_hora: 6, desde_dias: 7, ...(c.autonomia || {}) },
      conocimiento: norm(c.conocimiento), sistemas: norm(c.sistemas), buzones: norm(c.buzones),
      _archivo: path.relative(ROOT, f).replace(/\\/g, '/'),
    };
  }
  return { ...DEFECTO, autonomia: { intervalo_seg: 60, max_por_hora: 6, desde_dias: 7 }, _archivo: null };
}

const estadoAutonomia = () => leerJson(ESTADO_FILE, { activo: process.env.AUTONOMIA === '1' });
const guardarEstadoAutonomia = e => escribirJson(ESTADO_FILE, e);

function nowStamp() {
  const d = new Date(), p = n => String(n).padStart(2, '0');
  const off = -d.getTimezoneOffset(), sg = off >= 0 ? '+' : '-';
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())} (${sg}${p(Math.floor(Math.abs(off) / 60))}${p(Math.abs(off) % 60)})`;
}
const norm = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

module.exports = { ROOT, DATA, SALIDAS, BUZON_FILE, ESTADO_FILE, leerJson, escribirJson, ls, rutaSegura, cargarConfig, estadoAutonomia, guardarEstadoAutonomia, nowStamp, norm };
