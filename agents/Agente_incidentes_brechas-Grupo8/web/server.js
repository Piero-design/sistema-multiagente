// Servidor local sin dependencias nativas: sirve la interfaz y lanza el agente.
// Proveedores soportados: Claude Code CLI, Google Gemini API, Groq API.
// Uso: node web/server.js   (abre http://localhost:3000)
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const conectores = require('./autonomia/conectores');
const { crearMotor, depositar } = require('./autonomia/buzon');
const { rutaSegura, escribirJson } = require('./autonomia/almacen');

const ROOT = path.resolve(__dirname, '..');
const SALIDAS = path.join(ROOT, 'salidas');
const DIST = path.join(__dirname, 'client', 'dist');
const PUBLIC = DIST;
const HOST = process.env.HOST || '127.0.0.1';
const DATA = process.env.IB_DATA || path.join(ROOT, '.ib-data');
const AUTH_FILE = path.join(DATA, 'auth.json');
const PORT = process.env.PORT || 3100;
const CLAUDE_BIN = process.env.CLAUDE_BIN || (process.platform === 'win32' ? 'claude.cmd' : 'claude');
const jobs = new Map();

const json = (res, code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); };
const safeId = s => /^[\w.-]+$/.test(s || '') && !String(s).includes('..');
const read = p => fs.readFileSync(p, 'utf8');
const ls = d => (fs.existsSync(d) ? fs.readdirSync(d, { withFileTypes: true }) : []);

function nowStamp() {
  const d = new Date(), p = n => String(n).padStart(2, '0');
  const off = -d.getTimezoneOffset(), sg = off >= 0 ? '+' : '-';
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())} (${sg}${p(Math.floor(Math.abs(off) / 60))}${p(Math.abs(off) % 60)})`;
}

const accionesFile = id => path.join(SALIDAS, id, 'acciones-propuestas.json');
function leerAcciones(id) { try { const l = JSON.parse(read(accionesFile(id))); return Array.isArray(l) ? l : []; } catch { return []; } }

function expedienteInfo(id) {
  const dir = path.join(SALIDAS, id);
  const files = ls(dir).filter(f => f.isFile() && f.name.endsWith('.md')).map(f => f.name).sort();
  let limite = null, clasif = null, sev = null;
  const inf = path.join(dir, '00-informe.md');
  if (fs.existsSync(inf)) {
    const lines = read(inf).split('\n');
    const l = lines.find(x => /hora l[ií]mite/i.test(x));
    const m = l && l.match(/(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})/);
    if (m) limite = `${m[1]}T${m[2]}:00`;
    const cell = re => { const x = lines.find(y => re.test(y)); return x ? (x.split('|')[2] || '').replace(/\*/g, '').trim() : null; };
    clasif = cell(/^\|\s*Clasificaci[oó]n/i);
    sev = cell(/^\|\s*Severidad/i);
  }
  const acciones = leerAcciones(id);
  return { id, files, limite, clasif, sev, accionesPendientes: acciones.filter(a => a.estado === 'pendiente').length, mtime: fs.existsSync(dir) ? fs.statSync(dir).mtimeMs : 0 };
}

// ---- startJobClaude: lanza el agente usando Claude Code CLI ----
function buildPrompt({ rel, contexto, ahora, extra }) {
  return [
    `Fecha y hora actual: ${ahora || nowStamp()}.`,
    'Usa el agente agente-incidentes-brechas para gestionar este reporte de incidente:',
    rel + ' (archivo temporal de entrada: NO uses su nombre como ID)',
    contexto ? `contexto: ${contexto}` : '',
    'Léelo primero. Calcula el tiempo restante hasta la hora límite de 48 h con la fecha actual. Sigue tu flujo (ciclo ISO/IEC 27035), guarda todo en salidas/<ID>/ con ID = INC-<AAAAMMDD de la fecha del incidente>-<slug corto>, y termina mostrando clasificación, severidad, hora límite y tiempo restante, decisiones humanas pendientes y rutas generadas.',
    extra || '',
  ].filter(Boolean).join('\n');
}

// Configuración MCP para que Claude Code use los mismos conectores que Gemini y Groq.
function mcpConfigFile() {
  const f = path.join(DATA, 'mcp-conectores.json');
  escribirJson(f, { mcpServers: { conectores: { command: process.execPath, args: [path.join(__dirname, 'autonomia', 'mcp.js')], env: { IB_DATA: DATA, ...(process.env.CONECTORES_FILE ? { CONECTORES_FILE: process.env.CONECTORES_FILE } : {}) } } } });
  return f;
}

function startJobClaude({ reporte, contexto, ahora, extra }) {
  const id = 'job' + Date.now();
  fs.mkdirSync(path.join(SALIDAS, '_entradas'), { recursive: true });
  const rel = `salidas/_entradas/${id}.md`;
  fs.writeFileSync(path.join(ROOT, rel), reporte);
  const prompt = buildPrompt({ rel, contexto, ahora, extra });
  const job = { id, status: 'running', start: Date.now(), eventos: [], incidente: null, resultado: null, error: null };
  jobs.set(id, job);
  // El prompt va por stdin para no depender del quoting del shell en Windows.
  const args = ['-p', '--agent', 'agente-incidentes-brechas', '--output-format', 'stream-json', '--verbose', '--permission-mode', 'acceptEdits',
    '--mcp-config', mcpConfigFile(), '--strict-mcp-config', '--allowedTools', conectores.HERRAMIENTAS.map(h => 'mcp__conectores__' + h.name).join(',')];
  const child = spawn(CLAUDE_BIN, args, { cwd: ROOT, shell: process.platform === 'win32', env: claudeEnv() });
  child.stdin.end(prompt);
  let buf = '', errBuf = '';
  child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
  const note = t => job.eventos.push({ t: Date.now() - job.start, texto: t });
  child.stdout.on('data', d => {
    buf += d;
    let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
      if (!line) continue;
      try {
        const ev = JSON.parse(line);
        if (ev.type === 'assistant') for (const b of ev.message?.content || []) {
          if (b.type !== 'tool_use') continue;
          const f = b.input?.file_path || b.input?.pattern || b.input?.skill || '';
          const short = String(f).replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
          const verbo = { Read: 'Leyendo', Write: 'Escribiendo', Grep: 'Buscando', Glob: 'Listando', Skill: 'Skill' }[b.name] || b.name;
          const mcp = /^mcp__conectores__(\w+)$/.exec(b.name);
          note(mcp ? `${VERBOS_CONECTOR[mcp[1]] || mcp[1]} ${resumenConector(b.input)}` : `${verbo} ${short}`);
          const m = short.match(/^salidas\/(INC-[\w.-]+)\//);
          if (m) job.incidente = m[1];
        }
        if (ev.type === 'result') { job.resultado = ev.result; if (ev.is_error) job.error = ev.result; }
      } catch { /* línea parcial */ }
    }
  });
  child.stderr.on('data', d => { errBuf += d; });
  child.on('error', e => { job.status = 'error'; job.error = `No se pudo ejecutar "${CLAUDE_BIN}": ${e.message}`; job.fin = Date.now(); });
  child.on('close', code => {
    if (job.status === 'error') return;
    job.status = code === 0 && !job.error ? 'done' : 'error';
    if (job.status === 'error' && !job.error) job.error = errBuf.slice(-800) || `salió con código ${code}`;
    if (job.error) job.error = traduceError(job.error);
    job.fin = Date.now();
  });
  job.kill = () => { try { child.kill(); } catch { /* ya terminó */ } };
  return job;
}


// ---- Multi-provider LLM: Gemini y Groq ----

// Carga el system prompt del agente + skills desde el filesystem.
function buildSystemPrompt() {
  const strip = md => String(md || '').replace(/^---[\s\S]*?---\r?\n/, '');
  const agentFile = path.join(ROOT, '.claude/agents/agente-incidentes-brechas.md');
  let sys = fs.existsSync(agentFile) ? strip(read(agentFile)) : '';
  const skillsDir = path.join(ROOT, '.claude/skills');
  for (const d of ls(skillsDir).filter(x => x.isDirectory())) {
    const sf = path.join(skillsDir, d.name, 'SKILL.md');
    if (fs.existsSync(sf)) sys += `\n\n---\n## Skill: ${d.name}\n${strip(read(sf))}`;
  }
  return sys;
}

// Implementación de Glob sin dependencias externas.
function llmGlobSync(pattern) {
  const results = [];
  const reStr = String(pattern || '')
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*\*/g, '\x00')
    .replace(/\*/g, '[^/]*')
    .replace(/\x00/g, '.*')
    .replace(/\?/g, '[^/]');
  let re;
  try { re = new RegExp(`^${reStr}$`); } catch { return results; }
  function walk(dir, rel) {
    if (results.length >= 300) return;
    try {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        if (e.name === '.env' || (!rel && ['node_modules', '.git', '.ib-data', 'config', '.claude'].includes(e.name))) continue;
        const r = rel ? `${rel}/${e.name}` : e.name;
        if (e.isDirectory()) walk(path.join(dir, e.name), r);
        else if (re.test(r)) results.push(r);
      }
    } catch {}
  }
  walk(ROOT, '');
  return results;
}

// Implementación de Grep sin dependencias externas.
function llmGrepFiles(pattern, searchPath) {
  const results = [];
  let re;
  try { re = new RegExp(pattern, 'im'); } catch { re = new RegExp(String(pattern || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'im'); }
  function walk(dir) {
    if (results.length >= 100) return;
    try {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        if (results.length >= 100) return;
        if (e.name === '.env' || (dir === ROOT && ['node_modules', '.git', '.ib-data', 'config', '.claude'].includes(e.name))) continue;
        const p = path.join(dir, e.name);
        if (e.isDirectory()) walk(p);
        else if (e.isFile()) {
          try {
            const lines = fs.readFileSync(p, 'utf8').split('\n');
            lines.forEach((l, i) => {
              if (results.length < 100 && re.test(l))
                results.push(`${path.relative(ROOT, p).replace(/\\/g, '/')}:${i + 1}: ${l.slice(0, 200)}`);
            });
          } catch {}
        }
      }
    } catch {}
  }
  const sp = searchPath ? rutaSegura(searchPath) : ROOT;
  if (sp && fs.existsSync(sp)) walk(sp);
  return results;
}

// Ejecuta una tool (Read/Write/Glob/Grep) en el filesystem local.
async function executeTool(name, input) {
  if (conectores.esHerramienta(name)) return conectores.ejecutar(name, input);
  try {
    if (name === 'Read') {
      const p = rutaSegura(input.file_path);
      if (!p) return { error: 'Acceso denegado: ruta fuera del proyecto o reservada' };
      if (!fs.existsSync(p)) return { error: `No existe: ${input.file_path}` };
      if (fs.statSync(p).isDirectory()) return { error: `Es un directorio: ${input.file_path}` };
      return { content: read(p).slice(0, 500000) };
    }
    if (name === 'Write') {
      const p = path.resolve(ROOT, String(input.file_path || ''));
      const salidas = path.join(ROOT, 'salidas');
      if (!p.startsWith(salidas + path.sep)) return { error: 'Solo puede escribir dentro de salidas/' };
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, String(input.content || ''));
      return { ok: true, bytes: String(input.content || '').length };
    }
    if (name === 'Glob') {
      const files = llmGlobSync(String(input.pattern || ''));
      return { files, count: files.length };
    }
    if (name === 'Grep') {
      const matches = llmGrepFiles(String(input.pattern || ''), input.path ? String(input.path) : '');
      return { matches, count: matches.length };
    }
    return { error: `Herramienta desconocida: ${name}` };
  } catch (e) { return { error: String(e.message || e) }; }
}

const VERBOS_CONECTOR = { BuscarConocimiento: 'Consultando conocimiento:', ListarSistemas: 'Revisando sistemas disponibles', ConsultarSistema: 'Consultando sistema', BuscarQuejas: 'Buscando quejas relacionadas:', ProponerAccion: 'Proponiendo acción:' };
const resumenConector = i => [i?.sistema, i?.consulta || i?.patron || i?.ruta || i?.accion || i?.filtro].filter(Boolean).join(' · ').slice(0, 90);

// Emite un evento de progreso y detecta el ID del incidente.
function makeNoteHandler(job) {
  return (name, args) => {
    const f = String(args?.file_path || args?.pattern || args?.path || '');
    const short = f.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
    if (conectores.esHerramienta(name)) { job.eventos.push({ t: Date.now() - job.start, texto: `${VERBOS_CONECTOR[name]} ${resumenConector(args)}` }); return; }
    const verbo = { Read: 'Leyendo', Write: 'Escribiendo', Grep: 'Buscando', Glob: 'Listando' }[name] || name;
    job.eventos.push({ t: Date.now() - job.start, texto: `${verbo} ${short}` });
    if (name === 'Write') {
      const m = (args?.file_path || '').match(/salidas\/(INC-[\w.-]+)\//);
      if (m) job.incidente = m[1];
    }
  };
}

// Definición de tools para Gemini (formato Google GenAI).
const TOOLS_GEMINI = [{
  functionDeclarations: [
    { name: 'Read', description: 'Lee un archivo del proyecto por su ruta relativa.', parameters: { type: 'OBJECT', properties: { file_path: { type: 'STRING', description: 'Ruta relativa desde la raíz del proyecto' } }, required: ['file_path'] } },
    { name: 'Write', description: 'Escribe contenido en un archivo. Solo puede escribir dentro de salidas/.', parameters: { type: 'OBJECT', properties: { file_path: { type: 'STRING', description: 'Ruta relativa, debe empezar con salidas/' }, content: { type: 'STRING', description: 'Contenido completo del archivo a escribir' } }, required: ['file_path', 'content'] } },
    { name: 'Glob', description: 'Lista archivos que coincidan con un patrón glob, ej: salidas/**/*.md', parameters: { type: 'OBJECT', properties: { pattern: { type: 'STRING', description: 'Patrón glob' } }, required: ['pattern'] } },
    { name: 'Grep', description: 'Busca líneas que contengan un patrón en los archivos del proyecto.', parameters: { type: 'OBJECT', properties: { pattern: { type: 'STRING', description: 'Texto o regex a buscar' }, path: { type: 'STRING', description: 'Subcarpeta donde buscar (opcional)' } }, required: ['pattern'] } },
    ...conectores.paraGemini(),
  ]
}];

// Definición de tools para Groq/OpenAI (formato OpenAI).
const TOOLS_GROQ = [
  { type: 'function', function: { name: 'Read', description: 'Lee un archivo del proyecto por su ruta relativa.', parameters: { type: 'object', properties: { file_path: { type: 'string', description: 'Ruta relativa desde la raíz del proyecto' } }, required: ['file_path'] } } },
  { type: 'function', function: { name: 'Write', description: 'Escribe contenido en un archivo. Solo puede escribir dentro de salidas/.', parameters: { type: 'object', properties: { file_path: { type: 'string', description: 'Ruta relativa, debe empezar con salidas/' }, content: { type: 'string', description: 'Contenido completo del archivo' } }, required: ['file_path', 'content'] } } },
  { type: 'function', function: { name: 'Glob', description: 'Lista archivos que coincidan con un patrón glob.', parameters: { type: 'object', properties: { pattern: { type: 'string', description: 'Patrón glob, ej: salidas/**/*.md' } }, required: ['pattern'] } } },
  { type: 'function', function: { name: 'Grep', description: 'Busca líneas que contengan un patrón en los archivos del proyecto.', parameters: { type: 'object', properties: { pattern: { type: 'string', description: 'Texto o regex a buscar' }, path: { type: 'string', description: 'Subcarpeta donde buscar (opcional)' } }, required: ['pattern'] } } },
  ...conectores.paraOpenAI(),
];

const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-flash-lite-latest';

async function callGemini(ai, params) {
  try {
    return await ai.models.generateContent(params);
  } catch (e) {
    const msg = String(e.message || '');
    if ((msg.includes('503') || msg.includes('high demand') || msg.includes('404')) && params.model !== 'gemini-flash-lite-latest') {
      return await ai.models.generateContent({ ...params, model: 'gemini-flash-lite-latest' });
    }
    throw e;
  }
}

// Agent loop para Google Gemini.
async function runGeminiLoop({ job, apiKey, systemPrompt, userPrompt, abortCtrl }) {
  const { GoogleGenAI } = await import('@google/genai');
  const ai = new GoogleGenAI({ apiKey });
  const noteHandler = makeNoteHandler(job);
  const contents = [{ role: 'user', parts: [{ text: userPrompt }] }];
  let turns = 0;

  while (turns++ < 40) {
    if (job.cancelled) return;
    const response = await callGemini(ai, {
      model: GEMINI_MODEL,
      contents,
      config: { systemInstruction: systemPrompt, tools: TOOLS_GEMINI }
    });
    if (job.cancelled) return;

    const candidate = response.candidates?.[0];
    if (!candidate?.content?.parts) throw new Error('Gemini no devolvió respuesta válida.');

    // Añadir respuesta del modelo al historial
    contents.push({ role: 'model', parts: candidate.content.parts });

    // Separar partes: text vs function calls
    const fcs = candidate.content.parts.filter(p => p.functionCall);
    const textParts = candidate.content.parts.filter(p => p.text).map(p => p.text).join('');

    if (!fcs.length) {
      // Respuesta final (no hay más tool calls)
      job.resultado = textParts;
      break;
    }

    // Ejecutar tools y acumular respuestas
    const toolParts = [];
    for (const part of fcs) {
      if (job.cancelled) return;
      const fc = part.functionCall;
      const args = fc.args || {};
      noteHandler(fc.name, args);
      const result = await executeTool(fc.name, args);
      toolParts.push({ functionResponse: { name: fc.name, response: result } });
    }
    contents.push({ role: 'user', parts: toolParts });
  }
  if (!job.cancelled && turns >= 40) job.resultado = (job.resultado || '') + '\n(Máximo de turnos alcanzado)';
}

const GROQ_MODEL = process.env.GROQ_MODEL || 'openai/gpt-oss-120b';

// Agent loop para Groq (formato OpenAI-compatible).
async function runGroqLoop({ job, apiKey, systemPrompt, userPrompt, abortCtrl }) {
  const Groq = (await import('groq-sdk')).default;
  const groq = new Groq({ apiKey });
  const noteHandler = makeNoteHandler(job);
  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt }
  ];
  let turns = 0;

  while (turns++ < 40) {
    if (job.cancelled) return;
    const completion = await groq.chat.completions.create({
      model: GROQ_MODEL,
      messages,
      tools: TOOLS_GROQ,
      tool_choice: 'auto',
      max_tokens: 4096,
    }, { signal: abortCtrl?.signal });
    if (job.cancelled) return;

    const msg = completion.choices?.[0]?.message;
    if (!msg) throw new Error('Groq no devolvió respuesta válida.');
    messages.push(msg);

    if (!msg.tool_calls?.length) {
      job.resultado = msg.content || '';
      break;
    }

    for (const tc of msg.tool_calls) {
      if (job.cancelled) return;
      let args = {};
      try { args = JSON.parse(tc.function.arguments || '{}'); } catch {}
      noteHandler(tc.function.name, args);
      const result = await executeTool(tc.function.name, args);
      messages.push({ role: 'tool', tool_call_id: tc.id, content: JSON.stringify(result) });
    }
  }
  if (!job.cancelled && turns >= 40) job.resultado = (job.resultado || '') + '\n(Máximo de turnos alcanzado)';
}

// Lanza un job usando Gemini o Groq (sin CLI de Claude).
function startJobLLM({ reporte, contexto, ahora, extra }) {
  const prov = proveedorActivo();
  const id = 'job' + Date.now();
  fs.mkdirSync(path.join(SALIDAS, '_entradas'), { recursive: true });
  const rel = `salidas/_entradas/${id}.md`;
  fs.writeFileSync(path.join(ROOT, rel), reporte);

  const prompt = buildPrompt({ rel, contexto, ahora, extra });

  const abortCtrl = new AbortController();
  const job = { id, status: 'running', start: Date.now(), eventos: [], incidente: null, resultado: null, error: null, cancelled: false };
  jobs.set(id, job);
  const provLabel = prov === 'gemini' ? `Google Gemini (${GEMINI_MODEL})` : `Groq (${GROQ_MODEL})`;
  job.eventos.push({ t: 0, texto: `Iniciando análisis con ${provLabel}…` });

  const apiKey = prov === 'gemini' ? getApiKey('gemini_api_key') : getApiKey('groq_api_key');
  if (!apiKey) {
    job.status = 'error';
    job.error = `No hay API key de ${prov === 'gemini' ? 'Gemini' : 'Groq'} configurada. Ve a Ajustes > Conexión.`;
    job.fin = Date.now();
    return job;
  }

  const systemPrompt = buildSystemPrompt();
  const loopFn = prov === 'gemini' ? runGeminiLoop : runGroqLoop;
  loopFn({ job, apiKey, systemPrompt, userPrompt: prompt, abortCtrl })
    .then(() => { if (!job.cancelled) { job.status = 'done'; job.fin = Date.now(); } })
    .catch(e => {
      if (!job.cancelled) {
        job.status = 'error';
        job.error = traduceError(String(e.message || e));
        job.fin = Date.now();
      }
    });

  job.kill = () => {
    job.cancelled = true;
    try { abortCtrl.abort(); } catch {}
    job.status = 'error';
    job.error = 'Análisis cancelado por el usuario.';
    job.fin = Date.now();
  };
  return job;
}

// Dispatch: elige Claude o LLM según el proveedor activo.
function startJob(opts) {
  const p = proveedorActivo();
  return (p === 'gemini' || p === 'groq') ? startJobLLM(opts) : startJobClaude(opts);
}


// Motor autónomo: sondea los buzones configurados y lanza el agente con cada queja relevante.
const motor = crearMotor({ lanzar: startJob, jobs });

// ---- Contextos de organización: demo/ (incluidos) y contextos/ (subidos desde la interfaz)
const CTX_DIRS = { demo: path.join(ROOT, 'demo'), contextos: path.join(ROOT, 'contextos') };
const CTX_RE = /^(demo|contextos)\/[a-z0-9][a-z0-9-]{0,59}$/;
const MAX_ARCHIVO = 1.5e6, MAX_ARCHIVOS = 60;
const slug = n => String(n || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
const ctxPath = c => { if (!CTX_RE.test(c || '')) return null; const [t, n] = c.split('/'); return path.join(CTX_DIRS[t], n); };
function walk(dir, base = dir, out = []) {
  for (const f of ls(dir)) {
    const p = path.join(dir, f.name);
    if (f.isDirectory()) walk(p, base, out);
    else if (out.length < 300) out.push({ ruta: path.relative(base, p).replace(/\\/g, '/'), bytes: fs.statSync(p).size });
  }
  return out;
}
function listarContextos() {
  const out = [];
  for (const [tipo, dir] of Object.entries(CTX_DIRS))
    for (const d of ls(dir).filter(x => x.isDirectory() && /^[a-z0-9][a-z0-9-]*$/.test(x.name)))
      out.push({ ruta: `${tipo}/${d.name}`, nombre: d.name, propio: tipo === 'contextos', archivos: walk(path.join(dir, d.name)).sort((a, b) => a.ruta.localeCompare(b.ruta)) });
  return out;
}
function limpiaRuta(r) {
  const seg = String(r || '').replace(/\\/g, '/').split('/').filter(Boolean);
  if (!seg.length || seg.length > 4) return null;
  const ok = seg.map(x => x.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^\w.-]+/g, '_'));
  if (ok.some(x => x.startsWith('.') || x.includes('..'))) return null;
  return ok.join('/');
}
function guardaContexto(nombre, archivos) {
  const s = slug(nombre);
  if (!s) throw new Error('Escriba un nombre para la organización.');
  if (!Array.isArray(archivos) || !archivos.length) throw new Error('No hay archivos para guardar.');
  if (archivos.length > MAX_ARCHIVOS) throw new Error(`Máximo ${MAX_ARCHIVOS} archivos por carga.`);
  const base = path.join(CTX_DIRS.contextos, s), guardados = [], omitidos = [];
  for (const a of archivos) {
    const r = limpiaRuta(a.ruta), t = a.texto;
    if (!r || typeof t !== 'string') { omitidos.push(`${a.ruta}: nombre inválido`); continue; }
    if (t.includes('\u0000')) { omitidos.push(`${a.ruta}: no es un archivo de texto`); continue; }
    if (t.length > MAX_ARCHIVO) { omitidos.push(`${a.ruta}: supera 1,5 MB`); continue; }
    const dest = path.join(base, r);
    if (!dest.startsWith(base + path.sep)) { omitidos.push(`${a.ruta}: ruta inválida`); continue; }
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, t);
    guardados.push(r);
  }
  return { ruta: `contextos/${s}`, guardados, omitidos };
}

// ---- Credenciales: variables de entorno, archivo guardado desde la interfaz o sesión local de Claude Code
const TIPOS = {
  api_key: 'ANTHROPIC_API_KEY',
  oauth_token: 'CLAUDE_CODE_OAUTH_TOKEN',
  gemini_api_key: 'GEMINI_API_KEY',
  groq_api_key: 'GROQ_API_KEY',
};
const mask = v => (v ? v.slice(0, 8) + '…' + v.slice(-4) : '');
function authGuardada() { try { return JSON.parse(read(AUTH_FILE)); } catch { return null; } }

// Devuelve el proveedor activo basado en la credencial guardada o variables de entorno.
function proveedorActivo() {
  const g = authGuardada();
  if (g && g.tipo === 'gemini_api_key' && g.valor) return 'gemini';
  if (g && g.tipo === 'groq_api_key' && g.valor) return 'groq';
  if (process.env.GEMINI_API_KEY) return 'gemini';
  if (process.env.GROQ_API_KEY) return 'groq';
  return 'claude';
}

// Obtiene la API key del proveedor especificado (guardada o desde env).
function getApiKey(tipo) {
  const g = authGuardada();
  if (g && g.tipo === tipo && g.valor) return g.valor;
  return process.env[TIPOS[tipo]] || null;
}

function authEnv() {
  const a = authGuardada();
  return a && TIPOS[a.tipo] && a.valor ? { [TIPOS[a.tipo]]: a.valor } : {};
}
function claudeEnv() {
  const e = { ...process.env, ...authEnv() };
  for (const k of Object.values(TIPOS)) if (!e[k]) delete e[k];   // variables vacías (docker compose) no cuentan
  return e;
}
function corre(args, { timeout = 20000, stdin } = {}) {
  return new Promise(resolve => {
    let out = '', err = '', fin = false;
    const fn = r => { if (!fin) { fin = true; clearTimeout(t); resolve(r); } };
    let c;
    try { c = spawn(CLAUDE_BIN, args, { cwd: ROOT, shell: process.platform === 'win32', env: claudeEnv() }); }
    catch (e) { return resolve({ code: -1, out: '', err: e.message }); }
    const t = setTimeout(() => { try { c.kill(); } catch {} fn({ code: -2, out, err: err || 'sin respuesta' }); }, timeout);
    c.stdout.setEncoding('utf8'); c.stderr.setEncoding('utf8');
    c.stdout.on('data', d => { out += d; }); c.stderr.on('data', d => { err += d; });
    c.on('error', e => fn({ code: -1, out, err: e.message }));
    c.on('close', code => fn({ code, out, err }));
    if (stdin) c.stdin.end(stdin); else c.stdin.end();
  });
}
let estadoCache = null;
async function estado(fresh) {
  if (!fresh && estadoCache && Date.now() - estadoCache.t < 30000) return estadoCache.v;
  const g = authGuardada();
  const prov = proveedorActivo();
  const v = {
    proveedor: prov,
    claude: { ok: false, version: '', detalle: '' },
    sesion: { logueado: false, metodo: '', email: '' },
    credencial: g && TIPOS[g.tipo] ? { fuente: 'interfaz', tipo: g.tipo, valor: mask(g.valor) }
      : process.env.ANTHROPIC_API_KEY ? { fuente: 'entorno', tipo: 'api_key', valor: mask(process.env.ANTHROPIC_API_KEY) }
      : process.env.CLAUDE_CODE_OAUTH_TOKEN ? { fuente: 'entorno', tipo: 'oauth_token', valor: mask(process.env.CLAUDE_CODE_OAUTH_TOKEN) }
      : process.env.GEMINI_API_KEY ? { fuente: 'entorno', tipo: 'gemini_api_key', valor: mask(process.env.GEMINI_API_KEY) }
      : process.env.GROQ_API_KEY ? { fuente: 'entorno', tipo: 'groq_api_key', valor: mask(process.env.GROQ_API_KEY) }
      : { fuente: 'ninguna', tipo: '', valor: '' },
    agente: fs.existsSync(path.join(ROOT, '.claude/agents/agente-incidentes-brechas.md')),
    skills: ls(path.join(ROOT, '.claude/skills')).filter(d => d.isDirectory()).length,
    docker: fs.existsSync('/.dockerenv'),
  };
  // Solo comprobamos Claude Code si el proveedor es Claude
  if (prov === 'claude') {
    const ver = await corre(['--version'], { timeout: 10000 });
    v.claude.ok = ver.code === 0 && /Claude Code/i.test(ver.out);
    v.claude.version = ver.out.trim().slice(0, 40);
    v.claude.detalle = v.claude.ok ? '' : (ver.err || ver.out || `código ${ver.code}`).trim().slice(0, 160);
    if (v.claude.ok) {
      const st = await corre(['auth', 'status'], { timeout: 10000 });
      try { const j = JSON.parse(st.out); v.sesion = { logueado: !!j.loggedIn, metodo: j.authMethod || '', email: j.email || '' }; } catch { /* sin json */ }
    }
  } else {
    // Con Gemini o Groq no necesitamos Claude Code
    v.claude.ok = false;
    v.claude.detalle = `Proveedor activo: ${prov} (Claude Code no requerido)`;
  }
  estadoCache = { t: Date.now(), v };
  return v;
}

async function probarConexion() {
  const prov = proveedorActivo();
  const t0 = Date.now();

  if (prov === 'gemini') {
    const apiKey = getApiKey('gemini_api_key');
    if (!apiKey) return { ok: false, ms: 0, mensaje: 'No hay API key de Gemini. Configúrala en Ajustes > Conexión.' };
    try {
      const { GoogleGenAI } = await import('@google/genai');
      const ai = new GoogleGenAI({ apiKey });
      const r = await callGemini(ai, {
        model: GEMINI_MODEL,
        contents: [{ role: 'user', parts: [{ text: 'Responde solo con la palabra: ok' }] }]
      });
      const text = (r.candidates?.[0]?.content?.parts?.find(p => p.text)?.text || '').trim();
      const ok = /ok/i.test(text);
      return { ok, ms: Date.now() - t0, mensaje: ok ? `Conexión con Gemini (${GEMINI_MODEL}) correcta.` : `Respuesta inesperada: ${text.slice(0, 100)}` };
    } catch (e) { return { ok: false, ms: Date.now() - t0, mensaje: traduceError(e.message) }; }
  }

  if (prov === 'groq') {
    const apiKey = getApiKey('groq_api_key');
    if (!apiKey) return { ok: false, ms: 0, mensaje: 'No hay API key de Groq. Configúrala en Ajustes > Conexión.' };
    try {
      const Groq = (await import('groq-sdk')).default;
      const groq = new Groq({ apiKey });
      const r = await groq.chat.completions.create({
        model: GROQ_MODEL,
        messages: [{ role: 'user', content: 'Responde solo con la palabra: ok' }],
        max_tokens: 200,
      });
      const text = (r.choices?.[0]?.message?.content || '').trim();
      const ok = /ok/i.test(text);
      return { ok, ms: Date.now() - t0, mensaje: ok ? `Conexión con Groq (${GROQ_MODEL}) correcta.` : `Respuesta inesperada: ${text.slice(0, 100)}` };
    } catch (e) { return { ok: false, ms: Date.now() - t0, mensaje: traduceError(e.message) }; }
  }

  // Claude (comportamiento original)
  const r = await corre(['-p', 'Responde solo con la palabra: ok', '--output-format', 'json', '--max-turns', '1'], { timeout: 60000 });
  let j = null; try { j = JSON.parse(r.out); } catch { /* texto plano */ }
  const ok = r.code === 0 && j && !j.is_error;
  return { ok, ms: Date.now() - t0, mensaje: ok ? 'Conexión correcta.' : traduceError((j && j.result) || r.err || r.out || `código ${r.code}`) };
}

function traduceError(t) {
  const x = String(t || '');
  if (/not logged in|please run \/login|invalid api key|authentication|unauthorized|401|oauth token|credit balance/i.test(x))
    return 'Claude Code no tiene credenciales válidas. Configure su API key o su token de suscripción en la sección Conexión. Detalle: ' + x.slice(0, 200);
  if (/quota|rate.?limit|429|resource.?exhausted|too many requests/i.test(x))
    return 'Límite de uso de la API alcanzado (cuota o rate limit). Espere unos minutos e intente de nuevo. Detalle: ' + x.slice(0, 200);
  if (/api.?key.*(invalid|not.?valid)|invalid.?api.?key/i.test(x))
    return 'API key inválida. Verifique la clave en Ajustes > Conexión. Detalle: ' + x.slice(0, 200);
  return x.slice(0, 400);
}

function cuerpo(req, max, fn, res) {
  let body = '';
  req.on('data', d => { body += d; if (body.length > max) req.destroy(); });
  req.on('end', () => {
    let d;
    try { d = JSON.parse(body || '{}'); } catch { return json(res, 400, { error: 'JSON inválido' }); }
    try { fn(d); } catch (e) { json(res, 400, { error: String(e.message || e) }); }
  });
}

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json', '.ico': 'image/x-icon', '.png': 'image/png' };

http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const p = url.pathname;
  try {
    let m;

    if (req.method === 'GET' && p === '/api/archivos-demo') {
      const base = path.join(ROOT, 'archivos-demo');
      const lista = d => ls(path.join(base, d)).filter(f => f.isFile()).map(f => ({ nombre: f.name, bytes: fs.statSync(path.join(base, d, f.name)).size })).sort((a, b) => a.nombre.localeCompare(b.nombre));
      return json(res, 200, { reportes: lista('reportes'), contexto: lista('contexto-nuevo') });
    }
    if (req.method === 'GET' && (m = p.match(/^\/api\/archivos-demo\/(reportes|contexto-nuevo)\/([\w.-]+)$/))) {
      const f = path.join(ROOT, 'archivos-demo', m[1], m[2]);
      if (!safeId(m[2]) || !fs.existsSync(f)) return json(res, 404, { error: 'no existe' });
      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8', 'Content-Disposition': `attachment; filename="${m[2]}"` });
      return res.end(fs.readFileSync(f));
    }
    if (req.method === 'GET' && p === '/api/config') {
      const EJ = { unsa: 'examples/unsa' };
      const ejemplos = Object.entries(EJ).flatMap(([grupo, d]) => ls(path.join(ROOT, d)).filter(f => f.name.endsWith('.md'))
        .map(f => ({ grupo, nombre: f.name, titulo: read(path.join(ROOT, d, f.name)).split('\n')[0].replace(/^#\s*/, '') })));
      const contextos = listarContextos();
      const expedientes = ls(SALIDAS).filter(f => f.isDirectory() && f.name.startsWith('INC-')).map(f => expedienteInfo(f.name)).sort((a, b) => b.mtime - a.mtime);
      return json(res, 200, { ejemplos, contextos, expedientes, ahora: nowStamp() });
    }
    if (req.method === 'GET' && p === '/api/ejemplo') {
      const n = url.searchParams.get('f'), g = url.searchParams.get('g') === 'unsa' ? 'unsa' : 'entradas';
      if (!safeId(n)) return json(res, 400, { error: 'nombre inválido' });
      return json(res, 200, { texto: read(path.join(ROOT, 'examples', g, n)) });
    }
    if (req.method === 'POST' && p === '/api/analizar') {
      let body = '';
      req.on('data', d => { body += d; if (body.length > 2e6) req.destroy(); });
      req.on('end', () => {
        let data;
        try { data = JSON.parse(body || '{}'); } catch { return json(res, 400, { error: 'JSON inválido' }); }
        const { reporte, contexto, ahora } = data;
        if (!reporte || reporte.trim().length < 20) return json(res, 400, { error: 'El reporte es muy corto.' });
        if (contexto && !(CTX_RE.test(contexto) && fs.existsSync(ctxPath(contexto)))) return json(res, 400, { error: 'Contexto inválido o inexistente.' });
        json(res, 202, { job: startJob({ reporte, contexto, ahora }).id });
      });
      return;
    }

    if (req.method === 'GET' && p === '/api/autonomia') return json(res, 200, motor.resumen());
    if (req.method === 'POST' && p === '/api/autonomia') {
      return cuerpo(req, 1e4, d => { motor.activar(!!d.activo); json(res, 200, motor.resumen()); }, res);
    }
    if (req.method === 'POST' && p === '/api/autonomia/sondear') return motor.tick().then(() => json(res, 200, motor.resumen()));
    if (req.method === 'POST' && p === '/api/buzon/depositar') {
      return cuerpo(req, 2e5, d => json(res, 200, { archivo: depositar(String(d.buzon || ''), d) }), res);
    }
    if (req.method === 'POST' && (m = p.match(/^\/api\/buzon\/webhook\/([\w-]+)$/))) {
      const tok = process.env.BUZON_WEBHOOK_TOKEN;
      if (!tok) return json(res, 403, { error: 'Webhook deshabilitado: defina BUZON_WEBHOOK_TOKEN.' });
      if (req.headers['x-webhook-token'] !== tok) return json(res, 401, { error: 'Token inválido.' });
      return cuerpo(req, 2e5, d => { depositar(m[1], d); json(res, 202, { ok: true }); motor.tick(); }, res);
    }
    if (req.method === 'POST' && (m = p.match(/^\/api\/buzon\/(Q[0-9a-f]{12})\/analizar$/))) {
      try { return json(res, 202, { job: motor.analizar(m[1]).id }); } catch (e) { return json(res, 400, { error: e.message }); }
    }
    if (req.method === 'GET' && (m = p.match(/^\/api\/acciones\/([\w.-]+)$/))) {
      if (!safeId(m[1])) return json(res, 400, { error: 'id inválido' });
      return json(res, 200, { acciones: leerAcciones(m[1]) });
    }
    if (req.method === 'POST' && (m = p.match(/^\/api\/acciones\/([\w.-]+)\/(A\d+)$/))) {
      if (!safeId(m[1])) return json(res, 400, { error: 'id inválido' });
      return cuerpo(req, 1e4, d => {
        if (!['aprobada', 'rechazada'].includes(d.decision)) return json(res, 400, { error: 'Decisión inválida.' });
        const lista = leerAcciones(m[1]), a = lista.find(x => x.id === m[2]);
        if (!a) return json(res, 404, { error: 'Acción inexistente.' });
        a.estado = d.decision; a.decidida = nowStamp(); a.nota = String(d.nota || '').slice(0, 300);
        escribirJson(accionesFile(m[1]), lista);
        json(res, 200, { acciones: lista });
      }, res);
    }
    if (req.method === 'GET' && p === '/api/estado') return estado(url.searchParams.get('fresh') === '1').then(v => json(res, 200, v));
    if (req.method === 'POST' && p === '/api/auth/probar') return probarConexion().then(v => json(res, 200, v));
    if (req.method === 'POST' && p === '/api/auth') {
      let body = '';
      req.on('data', d => { body += d; if (body.length > 1e4) req.destroy(); });
      req.on('end', () => {
        try {
          const { tipo, valor } = JSON.parse(body || '{}');
          const v = String(valor || '').trim();
          if (!TIPOS[tipo]) return json(res, 400, { error: 'Tipo de credencial inválido.' });
          if (v.length < 10) return json(res, 400, { error: 'La credencial es demasiado corta.' });
          // Validación específica por tipo
          if ((tipo === 'api_key' || tipo === 'oauth_token') && !/^sk-ant-/.test(v))
            return json(res, 400, { error: 'La credencial de Anthropic debe empezar con sk-ant-.' });
          if (tipo === 'groq_api_key' && !/^gsk_/.test(v))
            return json(res, 400, { error: 'La API key de Groq debe empezar con gsk_.' });
          fs.mkdirSync(DATA, { recursive: true, mode: 0o700 });
          fs.writeFileSync(AUTH_FILE, JSON.stringify({ tipo, valor: v }), { mode: 0o600 });
          estadoCache = null;
          json(res, 200, { ok: true, valor: mask(v) });
        } catch (e) { json(res, 400, { error: String(e.message || e) }); }
      });
      return;
    }
    if (req.method === 'DELETE' && p === '/api/auth') { try { fs.rmSync(AUTH_FILE, { force: true }); } catch {} estadoCache = null; return json(res, 200, { ok: true }); }
    if (req.method === 'GET' && p === '/api/contexto-archivo') {
      const base = ctxPath(url.searchParams.get('c')), r = limpiaRuta(url.searchParams.get('f'));
      const f = base && r && path.join(base, r);
      if (!f || !f.startsWith(base + path.sep) || !fs.existsSync(f)) return json(res, 404, { error: 'no existe' });
      return json(res, 200, { texto: read(f).slice(0, 400000) });
    }
    if (req.method === 'POST' && p === '/api/contexto') {
      let body = '';
      req.on('data', d => { body += d; if (body.length > 12e6) req.destroy(); });
      req.on('end', () => {
        try { const { nombre, archivos } = JSON.parse(body || '{}'); json(res, 200, guardaContexto(nombre, archivos)); }
        catch (e) { json(res, 400, { error: String(e.message || e) }); }
      });
      return;
    }
    if (req.method === 'DELETE' && p === '/api/contexto') {
      const c = url.searchParams.get('c'), base = ctxPath(c);
      if (!base || !c.startsWith('contextos/')) return json(res, 400, { error: 'Solo se pueden borrar contextos subidos.' });
      const r = url.searchParams.get('f');
      if (r) { const rr = limpiaRuta(r), f = rr && path.join(base, rr); if (f && f.startsWith(base + path.sep) && fs.existsSync(f)) fs.rmSync(f); }
      else fs.rmSync(base, { recursive: true, force: true });
      return json(res, 200, { ok: true });
    }
    if (req.method === 'GET' && (m = p.match(/^\/api\/job\/(job\d+)$/))) {
      const j = jobs.get(m[1]);
      if (!j) return json(res, 404, { error: 'no existe' });
      return json(res, 200, { status: j.status, segundos: Math.round(((j.fin || Date.now()) - j.start) / 1000), eventos: j.eventos.slice(-300), incidente: j.incidente, resultado: j.resultado, error: j.error });
    }
    if (req.method === 'DELETE' && (m = p.match(/^\/api\/job\/(job\d+)$/))) {
      const j = jobs.get(m[1]);
      if (j) {
        if (j.kill) j.kill();
        j.status = 'error';
        j.error = 'Análisis cancelado por el usuario.';
        j.fin = Date.now();
      }
      return json(res, 200, { ok: true });
    }
    if (req.method === 'GET' && (m = p.match(/^\/api\/expediente\/([\w.-]+)$/))) {
      if (!safeId(m[1])) return json(res, 400, { error: 'id inválido' });
      const info = expedienteInfo(m[1]);
      const docs = Object.fromEntries(info.files.map(f => [f, read(path.join(SALIDAS, m[1], f))]));
      return json(res, 200, { ...info, docs, acciones: leerAcciones(m[1]) });
    }
    let f = path.join(PUBLIC, p === '/' ? 'index.html' : p);
    if (!(f.startsWith(PUBLIC) && fs.existsSync(f) && fs.statSync(f).isFile()) && req.method === 'GET' && !p.startsWith('/api/') && !p.startsWith('/assets/')) f = path.join(PUBLIC, 'index.html');
    if (f.startsWith(PUBLIC) && fs.existsSync(f) && fs.statSync(f).isFile()) {
      const cache = /\/assets\//.test(f.replace(/\\/g, '/')) ? 'public, max-age=31536000, immutable' : 'no-cache';
      res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream', 'Cache-Control': cache });
      return res.end(fs.readFileSync(f));
    }
    if (!fs.existsSync(path.join(DIST, 'index.html'))) { res.writeHead(503, { 'Content-Type': 'text/plain; charset=utf-8' }); return res.end('Falta compilar la interfaz. Ejecute: npm run build'); }
    json(res, 404, { error: 'no encontrado' });
  } catch (e) { json(res, 500, { error: String(e.message || e) }); }
}).listen(PORT, HOST, () => { console.log(`Agente de incidentes y brechas → http://localhost:${PORT}`); motor.iniciar(); });
