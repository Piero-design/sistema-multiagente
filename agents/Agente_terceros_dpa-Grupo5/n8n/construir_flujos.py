#!/usr/bin/env python3
"""
construir_flujos.py — Genera los flujos de n8n del PIMS Privacy Guard (Etapa 2).

    python n8n/construir_flujos.py --raiz "C:/Users/tu_usuario/TIF/AS-agente-main"

Escribe en n8n/flujos_listos/ un .json por flujo, listos para importar en n8n, con:
  - la ruta del proyecto (RAIZ) ya insertada (con barras "/", también en Windows),
  - las librerías de n8n/lib/*.js embebidas en los nodos Code (una sola fuente de verdad).

Si no se indica --raiz se usa la carpeta del proyecto donde está este script.
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LIB = {n: (AQUI / "lib" / f"{n}.js").read_text(encoding="utf-8") for n in ("calcular", "perfil", "prompts")}
VERSION = "2.0"

IDS = {
    "leer": "PimsLeerArchivos", "guardar": "PimsGuardarArchi", "modelo": "PimsModeloIA0000",
    "claude": "PimsClaudeCode00", "carpetas": "PimsCrearCarpeta", "auditar": "PimsAuditar00000",
    "perfilar": "PimsPerfilar0000", "aprobar": "PimsAprobaciones", "renovar": "PimsRenovaciones",
    "consultas": "PimsConsultas000", "admin": "PimsAdministrar0", "pagina": "PimsPaginaWeb000",
    "chat": "PimsChat00000000", "bd": "PimsBaseDatos000",
}
# Credencial Postgres de n8n (rol agente7). La crea n8n/configurar_bd.py con este id fijo.
CREDENCIAL_BD = {"id": "PimsPostgresBD01", "name": "PIMS Postgres"}

# --------------------------------------------------------------------------- JS común
COMUN = r"""
const RAIZ = '__RAIZ__';
const R = (...p) => [RAIZ, ...p].join('/');
const idValido = (s) => /^[a-z0-9_]{2,60}$/.test(String(s || ''));
const nombreSeguro = (s) => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/[^A-Za-z0-9._-]+/g, '_').replace(/^[._]+/, '').slice(0, 100);
const hoy = () => $now.toFormat('yyyy-MM-dd');
const ahora = () => $now.toISO();
const nuevoTrabajo = () => 'T' + $now.toFormat('yyyyLLddHHmmss') + Math.random().toString(36).slice(2, 6);
const archivoTrabajo = (t, datos) => ({ json: { ruta: R('datos', 'trabajos', `${t}.json`),
  texto: JSON.stringify(Object.assign({ trabajo: t, actualizado: ahora() }, datos), null, 2) } });
const textoDe = (leidos, clave) => { const x = leidos.find((l) => l.clave === clave);
  return x && x.existe ? x.archivos[0].texto : null; };
const archivoDe = (leidos, clave) => { const x = leidos.find((l) => l.clave === clave);
  return x && x.existe ? x.archivos[0] : null; };
const todosDe = (leidos, clave) => { const x = leidos.find((l) => l.clave === clave); return x ? x.archivos : []; };
const jsonDe = (leidos, clave) => { const t = textoDe(leidos, clave); if (t === null) return null;
  try { return JSON.parse(t); } catch (e) { throw new Error(`El archivo '${clave}' no es JSON válido: ${e.message}`); } };
"""


def js(cuerpo, *libs):
    """Código de un nodo Code: librerías + utilidades comunes + cuerpo."""
    partes = [LIB[n] for n in libs] + [COMUN, cuerpo.strip()]
    return "\n".join(partes)


# --------------------------------------------------------------------------- constructor
class Flujo:
    def __init__(self, clave, nombre, descripcion, guardar_exitos=True):
        self.id = IDS[clave]
        self.nombre = nombre
        self.descripcion = descripcion
        self.nodos = []
        self.conexiones = {}
        self.guardar_exitos = guardar_exitos

    def nodo(self, nombre, tipo, version, params, pos, **extra):
        n = {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.id}/{nombre}")), "name": nombre,
             "type": tipo, "typeVersion": version, "position": list(pos), "parameters": params}
        n.update(extra)
        self.nodos.append(n)
        return nombre

    def unir(self, origen, destino, salida=0):
        lst = self.conexiones.setdefault(origen, {"main": []})["main"]
        while len(lst) <= salida:
            lst.append([])
        lst[salida].append({"node": destino, "type": "main", "index": 0})

    def cadena(self, *nombres):
        for a, b in zip(nombres, nombres[1:]):
            self.unir(a, b)

    # ---- atajos de nodos
    def code(self, nombre, pos, cuerpo, *libs, **extra):
        return self.nodo(nombre, "n8n-nodes-base.code", 2, {"mode": "runOnceForAllItems", "language": "javaScript",
                                                             "jsCode": js(cuerpo, *libs)}, pos, **extra)

    def webhook(self, nombre, pos, metodo, ruta):
        return self.nodo(nombre, "n8n-nodes-base.webhook", 2.1, {
            "httpMethod": metodo, "path": ruta, "responseMode": "responseNode",
            # Solo la página servida por n8n (origen "null" por el sandbox CSP) y el propio n8n pueden leer las respuestas.
            "options": {"allowedOrigins": "__ORIGENES__"}},
            pos, webhookId=str(uuid.uuid5(uuid.NAMESPACE_URL, f"pims/{ruta}/{metodo}")))

    def responder(self, nombre, pos, codigo="={{ $json.codigo || 200 }}", cuerpo="={{ JSON.stringify($json.respuesta) }}"):
        return self.nodo(nombre, "n8n-nodes-base.respondToWebhook", 1.5, {
            "respondWith": "json", "responseBody": cuerpo,
            "options": {"responseCode": codigo, "responseHeaders": {"entries": [
                {"name": "Cache-Control", "value": "no-store"}]}}}, pos)

    def llamar(self, nombre, pos, clave, **extra):
        return self.nodo(nombre, "n8n-nodes-base.executeWorkflow", 1.2, {
            "source": "database",
            "workflowId": {"__rl": True, "value": IDS[clave], "mode": "id"},
            "workflowInputs": {"mappingMode": "defineBelow", "value": {}, "matchingColumns": [], "schema": [],
                               "attemptToConvertTypes": False, "convertFieldsToString": True},
            "mode": "once", "options": {"waitForSubWorkflow": True}}, pos, **extra)

    def si(self, nombre, pos, expresion):
        return self.nodo(nombre, "n8n-nodes-base.if", 2.2, {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                           "conditions": [{"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.id}/{nombre}/c")),
                                           "leftValue": expresion, "rightValue": "",
                                           "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                           "combinator": "and"},
            "looseTypeValidation": True, "options": {}}, pos)

    def entrada(self, pos=(0, 0)):
        return self.nodo("Entrada", "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, pos)

    def json(self, raiz, origenes="null"):
        settings = {"executionOrder": "v1", "callerPolicy": "workflowsFromSameOwner",
                    "saveDataErrorExecution": "all", "saveManualExecutions": True,
                    "saveDataSuccessExecution": "all" if self.guardar_exitos else "none"}
        datos = {"id": self.id, "name": self.nombre, "active": False, "nodes": self.nodos,
                 "connections": self.conexiones, "settings": settings, "pinData": {},
                 "meta": {"templateCredsSetupCompleted": True, "pims_version": VERSION},
                 "tags": [], "description": self.descripcion}
        texto = json.dumps(datos, ensure_ascii=False, indent=1)
        return texto.replace("__RAIZ__", raiz.replace("\\", "\\\\")).replace("__ORIGENES__", origenes)


# =========================================================================== FLUJOS
def flujo_leer():
    f = Flujo("leer", "PIMS · Leer archivos (subflujo)",
              "Lee archivos o patrones (glob) del proyecto. Entrada: items {clave, ruta}. Salida: un item por pedido "
              "{clave, ruta, existe, archivos:[{ruta_real, nombre, extension, tam, sha256, texto, paginas}]}. "
              "Los PDF se convierten a texto con marcadores [Página N].")
    f.entrada()
    f.nodo("Leer", "n8n-nodes-base.readWriteFile", 1.1, {"operation": "read", "fileSelector": "={{ $json.ruta }}",
                                                         "options": {}}, (220, 0),
           onError="continueRegularOutput", alwaysOutputData=True)
    f.code("Bytes", (440, 0), r"""
const salida = [];
const items = $input.all();
for (let i = 0; i < items.length; i++) {
  const it = items[i];
  const b = it.binary && it.binary.data;
  if (!b) { salida.push({ json: { error: (it.json && it.json.error) || 'sin archivo' } }); continue; }
  const buf = await this.helpers.getBinaryDataBuffer(i, 'data');
  const dir = String(b.directory || '').replace(/\\/g, '/');
  const ruta_real = (dir ? dir.replace(/\/$/, '') + '/' : '') + b.fileName;
  const ext = String(b.fileExtension || b.fileName.split('.').pop() || '').toLowerCase();
  const j = { ruta_real, nombre: b.fileName, extension: ext, tam: buf.length, sha256: PIMS_CALC.sha256Hex(buf) };
  if (ext === 'pdf') { salida.push({ json: j, binary: { data: b } }); continue; }
  j.texto = new TextDecoder('utf-8').decode(buf).replace(/^\uFEFF/, '');
  salida.push({ json: j });
}
return salida;
""", "calcular")
    f.nodo("Texto PDF", "n8n-nodes-base.extractFromFile", 1.1, {"operation": "pdf", "binaryPropertyName": "data",
                                                                "options": {"joinPages": False}}, (660, 0),
           onError="continueRegularOutput", alwaysOutputData=True)
    f.code("Resultado", (880, 0), r"""
const pedidos = $('Entrada').all().map((x) => x.json);
const bytes = $('Bytes').all().map((x) => x.json);
const pdf = $input.all().map((x) => x.json);
const win = /^[A-Za-z]:\//.test(RAIZ);
const norm = (s) => { const t = String(s || '').replace(/\\/g, '/'); return win ? t.toLowerCase() : t; };
const esGlob = (s) => /[*?{]/.test(s);
function globRe(g) {
  const s = norm(g); let out = '', prof = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '*') { if (s[i + 1] === '*') { out += '.*'; i++; if (s[i + 1] === '/') i++; } else out += '[^/]*'; }
    else if (c === '?') out += '[^/]';
    else if (c === '{') { out += '(?:'; prof++; }
    else if (c === '}' && prof) { out += ')'; prof--; }
    else if (c === ',' && prof) out += '|';
    else out += c.replace(/[.+^$()|[\]\\]/g, '\\$&');
  }
  return new RegExp('^' + out + '$');
}
const archivos = bytes.map((b, i) => {
  if (b.error) return null;
  const a = Object.assign({}, b);
  const p = pdf[i] || {};
  if (a.extension === 'pdf') {
    if (Array.isArray(p.text)) {
      a.paginas = p.text.length;
      a.texto = p.text.map((t, k) => `[Página ${k + 1}]\n${t}`).join('\n\n');
    } else { a.texto = ''; a.error_texto = p.error ? String(p.error.message || p.error) : 'No se pudo extraer texto del PDF'; }
  }
  return a;
}).filter(Boolean);
return pedidos.map((ped) => {
  const re = esGlob(ped.ruta) ? globRe(ped.ruta) : null;
  const objetivo = norm(ped.ruta);
  const enc = archivos.filter((a) => (re ? re.test(norm(a.ruta_real)) : norm(a.ruta_real) === objetivo))
    .sort((x, y) => x.ruta_real.localeCompare(y.ruta_real));
  return { json: { clave: ped.clave, ruta: ped.ruta, existe: enc.length > 0, archivos: enc } };
});
""", "calcular")
    f.cadena("Entrada", "Leer", "Bytes", "Texto PDF", "Resultado")
    return f


def flujo_guardar():
    f = Flujo("guardar", "PIMS · Guardar archivos (subflujo)",
              "Escribe archivos de texto o binarios (base64) en el proyecto. Entrada: items {ruta, texto | b64}. "
              "La carpeta de destino debe existir.")
    f.entrada()
    f.code("Preparar", (220, 0), r"""
return $input.all().map((it) => {
  const j = it.json;
  const ruta = String(j.ruta || '').replace(/\\/g, '/');
  if (!ruta.startsWith(RAIZ + '/') || ruta.includes('/../')) throw new Error(`Ruta fuera del proyecto: ${ruta}`);
  const b64 = typeof j.b64 === 'string' ? j.b64 : Buffer.from(String(j.texto ?? ''), 'utf8').toString('base64');
  return { json: { ruta, b64, nombre: ruta.split('/').pop() } };
});
""")
    f.nodo("A binario", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "toBinary", "sourceProperty": "b64", "binaryPropertyName": "data",
        "options": {"encoding": "base64", "fileName": "={{ $json.nombre }}"}}, (440, 0))
    f.nodo("Escribir", "n8n-nodes-base.readWriteFile", 1.1, {
        "operation": "write", "fileName": "={{ $('Preparar').item.json.ruta }}", "dataPropertyName": "data",
        "options": {}}, (660, 0), onError="continueRegularOutput")
    f.code("Resultado", (880, 0), r"""
const prep = $('Preparar').all().map((x) => x.json.ruta);
return $input.all().map((it, i) => ({ json: { ruta: prep[i], ok: !it.json.error,
  error: it.json.error ? String(it.json.error.message || it.json.error) : null } }));
""")
    f.cadena("Entrada", "Preparar", "A binario", "Escribir", "Resultado")
    return f


def flujo_claude():
    f = Flujo("claude", "PIMS · Claude Code (opcional, requiere Execute Command)",
              "Ejecuta 'claude -p' con la suscripción del usuario. Requiere NODES_EXCLUDE=\"[]\" y que el comando "
              "'claude' esté en el PATH del proceso de n8n. El modelo no recibe herramientas.")
    f.entrada()
    f.code("Archivos", (220, 0), r"""
const salida = [];
const pref = 'cc_' + $now.toFormat('yyyyLLddHHmmss') + '_' + Math.random().toString(36).slice(2, 6);
$input.all().forEach((it, i) => {
  salida.push({ json: { ruta: R('datos', 'tmp', `${pref}_${i}_sys.txt`), texto: it.json.system || '' } });
  salida.push({ json: { ruta: R('datos', 'tmp', `${pref}_${i}_msg.txt`), texto: it.json.mensaje || '' } });
});
return salida;
""")
    f.llamar("Guardar temporales", (440, 0), "guardar")
    f.code("Comandos", (660, 0), r"""
const pedidos = $('Entrada').all().map((x) => x.json);
const rutas = $('Archivos').all().map((x) => x.json.ruta);
const guardados = $input.all().map((x) => x.json);
const fallo = guardados.find((g) => !g.ok);
if (fallo) throw new Error(`No se pudieron escribir los temporales (${fallo.ruta}): ${fallo.error}`);
return pedidos.map((p, i) => {
  const modelo = String(p.modelo || 'sonnet');
  if (!/^[A-Za-z0-9._:\-\[\]]+$/.test(modelo)) throw new Error(`Nombre de modelo no permitido: ${modelo}`);
  const bin = String(p.claude_bin || 'claude');
  if (!/^[A-Za-z0-9._:\\\/ \-]+$/.test(bin)) throw new Error(`Ruta del ejecutable no permitida: ${bin}`);
  const comando = `"${bin}" -p --model ${modelo} --output-format json --permission-mode dontAsk ` +
    `--disallowedTools "Bash,PowerShell,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task,Read,Glob,Grep,Skill" ` +
    `--append-system-prompt-file "${rutas[2 * i]}" < "${rutas[2 * i + 1]}"`;
  return { json: { comando } };
});
""")
    f.nodo("Ejecutar claude", "n8n-nodes-base.executeCommand", 1, {"executeOnce": False, "command": "={{ $json.comando }}"},
           (880, 0), onError="continueRegularOutput")
    f.code("Resultado", (1100, 0), r"""
return $input.all().map((it) => {
  const j = it.json;
  if (j.error) return { json: { error: String(j.error.message || j.error), stderr: j.stderr || '' } };
  return { json: { stdout: j.stdout || '', stderr: j.stderr || '', exitCode: j.exitCode } };
});
""")
    f.cadena("Entrada", "Archivos", "Guardar temporales", "Comandos", "Ejecutar claude", "Resultado")
    return f


def flujo_carpetas():
    f = Flujo("carpetas", "PIMS · Crear carpetas de organización (opcional, requiere Execute Command)",
              "Crea organizaciones/<id>/documentos y /contratos con n8n/scripts/crear_carpetas.js.")
    f.entrada()
    f.code("Comando", (220, 0), r"""
const id = $input.first().json.organizacion;
if (!idValido(id)) throw new Error(`Id de organización no válido: ${id}`);
return [{ json: { comando: `node "${R('n8n', 'scripts', 'crear_carpetas.js')}" "${RAIZ}" "${id}"` } }];
""")
    f.nodo("Ejecutar", "n8n-nodes-base.executeCommand", 1, {"executeOnce": True, "command": "={{ $json.comando }}"},
           (440, 0), onError="continueRegularOutput")
    f.code("Resultado", (660, 0), r"""
const j = $input.first().json;
let r = { ok: false, error: j.error ? String(j.error.message || j.error) : (j.stderr || 'sin salida') };
try { if (j.stdout) r = JSON.parse(j.stdout); } catch (e) { /* se queda el error */ }
return [{ json: r }];
""")
    f.cadena("Entrada", "Comando", "Ejecutar", "Resultado")
    return f


def flujo_bd():
    f = Flujo("bd", "PIMS · Base de datos (Postgres del PIMS Gestitel)",
              "Escribe en la base del PIMS con las funciones de bd/agente7_terceros_dpa.sql. Entrada: "
              "{operacion: guardar_auditoria, registro, informe} o {operacion: registrar_decision, id, rol, decision, "
              "usuario, cargo, comentario, fecha}. Lee datos/config_bd.json: si 'activo' es false no hace nada. "
              "Salida: {ok, omitido?, error?, resultado?}. Nunca detiene al flujo que lo llama.")
    f.entrada()
    f.code("Pedir configuración", (220, 0), r"""
return [{ json: { clave: 'cfg', ruta: R('datos', 'config_bd.json') } }];
""")
    f.llamar("Leer configuración", (440, 0), "leer")
    f.code("Preparar consulta", (660, 0), r"""
const p = $('Entrada').first().json;
let cfg;
try { cfg = jsonDe($input.all().map((x) => x.json), 'cfg'); } catch (e) { return [{ json: { ok: false, activo: false, error: e.message } }]; }
if (!cfg || !cfg.activo) return [{ json: { ok: true, activo: false, omitido: true } }];
const esq = String(cfg.esquema || 'demo');
if (!/^[a-z_][a-z0-9_]{0,62}$/.test(esq)) return [{ json: { ok: false, activo: false, error: `Esquema no válido en config_bd.json: ${esq}` } }];
const autor = Number(cfg.usuario_autor_id);
if (!Number.isInteger(autor) || autor < 1) return [{ json: { ok: false, activo: false, error: "Falta 'usuario_autor_id' en config_bd.json." } }];
// Los valores van como parámetros ($1, $2…): el contrato y los comentarios son contenido no confiable.
if (p.operacion === 'guardar_auditoria' && p.registro)
  return [{ json: { activo: true, consulta: `SELECT ${esq}.agente7_guardar_auditoria($1::jsonb, $2, ${autor}) AS id`,
    parametros: [p.registro, p.informe ?? null] } }];
if (p.operacion === 'registrar_decision')
  return [{ json: { activo: true, consulta: `SELECT ${esq}.agente7_registrar_decision($1, $2, $3, $4, $5, $6, $7::timestamptz) AS estado`,
    parametros: [p.id, p.rol, p.decision, p.usuario, p.cargo ?? null, p.comentario ?? '', p.fecha ?? null] } }];
return [{ json: { ok: true, activo: false, omitido: true } }];
""")
    f.si("¿Base activa?", (880, 0), "={{ $json.activo }}")
    f.nodo("Postgres", "n8n-nodes-base.postgres", 2.6, {
        "operation": "executeQuery", "query": "={{ $json.consulta }}",
        "options": {"queryReplacement": "={{ $json.parametros }}"}}, (1100, -100),
        credentials={"postgres": CREDENCIAL_BD}, onError="continueRegularOutput", alwaysOutputData=True)
    f.code("Resultado", (1320, -100), r"""
const j = $input.first().json;
// Con onError=continueRegularOutput el nodo devuelve { message, error }; el texto útil se reparte
// entre message, error.message y error.description (p. ej. "Connection refused" y "127.0.0.1:5432").
if (j.error) {
  const e = typeof j.error === 'object' ? j.error : { message: String(j.error) };
  const partes = [j.message, e.message, e.description].filter((x, i, a) => x && a.indexOf(x) === i);
  return [{ json: { ok: false, error: (partes.join(' — ') || JSON.stringify(e)).slice(0, 500) } }];
}
return [{ json: { ok: true, resultado: j } }];
""")
    f.code("Sin base", (1100, 100), r"""
const j = $input.first().json;
return [{ json: { ok: j.ok !== false, omitido: true, error: j.error || null } }];
""")
    f.cadena("Entrada", "Pedir configuración", "Leer configuración", "Preparar consulta", "¿Base activa?")
    f.unir("¿Base activa?", "Postgres", 0)
    f.unir("¿Base activa?", "Sin base", 1)
    f.unir("Postgres", "Resultado")
    return f


def flujo_modelo():
    f = Flujo("modelo", "PIMS · Modelo de IA (subflujo con selector)",
              "Envía cada item {system, mensaje, etiqueta} al proveedor configurado en datos/config_modelo.json: "
              "Ollama, Anthropic, compatible con OpenAI o Claude Code. Salida: {ok, texto, error, proveedor, modelo}.")
    f.entrada()
    f.code("Pedir configuración", (220, 0), r"""
return [{ json: { clave: 'config', ruta: R('datos', 'config_modelo.json') } }];
""")
    f.llamar("Leer configuración", (440, 0), "leer")
    f.code("Preparar peticiones", (660, 0), r"""
const DEF = { proveedor: 'claude_code', modelo: 'sonnet', url_ollama: 'http://127.0.0.1:11434',
  url_openai: 'https://api.openai.com/v1', url_anthropic: 'https://api.anthropic.com', api_key: '', num_ctx: 49152, temperatura: 0,
  max_tokens: 20000, timeout_s: 1800, claude_bin: 'claude', formato_correccion: 'json' };
let cfg = Object.assign({}, DEF);
const leido = $input.first().json;
if (leido.existe) { try { Object.assign(cfg, JSON.parse(leido.archivos[0].texto)); } catch (e) { /* se usan los valores por defecto */ } }
const SALIDA = { ollama: 0, anthropic: 1, openai: 2, claude_code: 3 };
// Node 17+ resuelve 'localhost' primero a ::1 (IPv6) y Ollama, en Windows, escucha solo en 127.0.0.1:
// ECONNREFUSED ::1:11434. Se usa siempre la dirección IPv4.
const ipv4 = (u) => String(u).replace(/\/+$/, '').replace(/^(https?:\/\/)localhost(?=[:\/]|$)/i, '$1127.0.0.1');
return $('Entrada').all().map((it) => {
  const { system, mensaje, etiqueta, formato } = it.json;
  const r = { proveedor: cfg.proveedor, modelo: cfg.modelo, etiqueta: etiqueta || '', inicio: Date.now(),
    timeout: Math.max(60, Number(cfg.timeout_s) || 1800) * 1000, salida: SALIDA[cfg.proveedor] ?? 4, cabeceras: {} };
  const temp = Number(cfg.temperatura) || 0;
  // Sin mensaje no hay nada que preguntar (p. ej. el paso anterior ya falló): no se llama al modelo.
  if (!mensaje) return { json: Object.assign(r, { salida: 4, error_previo: 'Petición al modelo sin mensaje (el paso anterior falló).' }) };
  if (cfg.proveedor === 'ollama') {
    r.url = ipv4(cfg.url_ollama) + '/api/chat';
    r.cuerpo = { model: cfg.modelo, stream: false, messages: [{ role: 'system', content: system }, { role: 'user', content: mensaje }],
      options: { num_ctx: Number(cfg.num_ctx) || 49152, temperature: temp,
        // Tope de salida: sin él, un modelo que entra en bucle escribe hasta llenar el contexto.
        num_predict: Number(cfg.max_tokens) || 20000 } };
    // Salida estructurada de Ollama en la corrección del JSON (formato_correccion):
    //   'json'    → JSON válido garantizado (sin comentarios); costo casi nulo. Por defecto.
    //   'esquema' → además la forma exacta (26 controles, valores permitidos); más lento con modelos locales.
    //   'ninguno' → sin restricción.
    if (formato && typeof formato === 'object') {
      const modo = cfg.formato_correccion || 'json';
      if (modo === 'esquema') r.cuerpo.format = formato;
      else if (modo === 'json') r.cuerpo.format = 'json';
    }
  } else if (cfg.proveedor === 'anthropic') {
    r.url = String(cfg.url_anthropic).replace(/\/+$/, '') + '/v1/messages';
    r.cabeceras = { 'x-api-key': cfg.api_key, 'anthropic-version': '2023-06-01' };
    r.cuerpo = { model: cfg.modelo, max_tokens: Number(cfg.max_tokens) || 20000, system,
      messages: [{ role: 'user', content: mensaje }], temperature: temp };
  } else if (cfg.proveedor === 'openai') {
    r.url = ipv4(cfg.url_openai) + '/chat/completions';
    if (cfg.api_key) r.cabeceras = { Authorization: `Bearer ${cfg.api_key}` };
    r.cuerpo = { model: cfg.modelo, temperature: temp, max_tokens: Number(cfg.max_tokens) || 20000,
      messages: [{ role: 'system', content: system }, { role: 'user', content: mensaje }] };
  } else if (cfg.proveedor === 'claude_code') {
    Object.assign(r, { system, mensaje, claude_bin: cfg.claude_bin });
  }
  return { json: r };
});
""")
    f.nodo("Proveedor", "n8n-nodes-base.switch", 3.2, {"mode": "expression", "numberOutputs": 5,
                                                        "output": "={{ $json.salida }}"}, (880, 0))
    http = lambda con_cabeceras: {
        "method": "POST", "url": "={{ $json.url }}",
        "sendHeaders": con_cabeceras, **({"specifyHeaders": "json",
                                         "jsonHeaders": "={{ JSON.stringify($json.cabeceras) }}"} if con_cabeceras else {}),
        "sendBody": True, "contentType": "json", "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.cuerpo) }}",
        "options": {"timeout": "={{ $json.timeout }}",
                    "response": {"response": {"fullResponse": True, "neverError": True, "responseFormat": "json"}}}}
    f.nodo("Ollama", "n8n-nodes-base.httpRequest", 4.2, http(False), (1100, -300), onError="continueRegularOutput")
    f.nodo("Anthropic API", "n8n-nodes-base.httpRequest", 4.2, http(True), (1100, -150), onError="continueRegularOutput")
    f.nodo("API compatible OpenAI", "n8n-nodes-base.httpRequest", 4.2, http(True), (1100, 0), onError="continueRegularOutput")
    f.llamar("Claude Code", (1100, 150), "claude", onError="continueRegularOutput")
    f.code("Normalizar", (1340, 0), r"""
const reqs = $('Preparar peticiones').all().map((x) => x.json);
const res = $input.all().map((x) => x.json);
const err = (e) => (e && typeof e === 'object') ? (e.message || JSON.stringify(e)) : String(e);
return reqs.map((r, i) => {
  const x = res[i] || {};
  let texto = null, error = null, truncado = false;
  try {
    if (r.salida === 4) error = r.error_previo || `Proveedor de modelo no válido: '${r.proveedor}'. Usa ollama, anthropic, openai o claude_code.`;
    else if (r.proveedor === 'claude_code') {
      if (x.error) error = `Claude Code no disponible: ${err(x.error)}. ¿Está habilitado Execute Command (NODES_EXCLUDE="[]") y 'claude' en el PATH?`;
      else {
        let o = null;
        try { o = JSON.parse(String(x.stdout || '').trim().split('\n').filter((l) => l.trim().startsWith('{')).pop() || '{}'); } catch (e) { o = null; }
        if (!o || o.type !== 'result') error = `Salida inesperada de claude (código ${x.exitCode}): ${String(x.stderr || x.stdout || '').slice(-800)}`;
        else if (o.is_error || o.subtype !== 'success') error = `claude terminó con '${o.subtype}': ${String(o.result || '').slice(0, 800)}`;
        else texto = o.result;
      }
    } else if (x.error) error = `Error de red con ${r.proveedor}: ${err(x.error)}`;
    else if ((x.statusCode || 0) >= 400) error = `HTTP ${x.statusCode} de ${r.proveedor}: ${JSON.stringify(x.body).slice(0, 800)}`;
    else {
      const b = x.body || {};
      if (r.proveedor === 'ollama') { texto = b.message && b.message.content; truncado = b.done_reason === 'length'; }
      else if (r.proveedor === 'anthropic') { texto = (b.content || []).filter((c) => c.type === 'text').map((c) => c.text).join(''); truncado = b.stop_reason === 'max_tokens'; }
      else { const c = (b.choices || [])[0] || {}; texto = c.message && c.message.content; truncado = c.finish_reason === 'length'; }
      if (!texto) error = `Respuesta vacía de ${r.proveedor}: ${JSON.stringify(b).slice(0, 500)}`;
    }
  } catch (e) { error = `Respuesta inesperada del modelo: ${e.message}`; }
  return { json: { ok: !error, texto: texto || null, error, truncado, proveedor: r.proveedor, modelo: r.modelo,
    etiqueta: r.etiqueta, duracion_ms: Date.now() - r.inicio } };
});
""")
    f.cadena("Entrada", "Pedir configuración", "Leer configuración", "Preparar peticiones", "Proveedor")
    for i, n in enumerate(["Ollama", "Anthropic API", "API compatible OpenAI", "Claude Code"]):
        f.unir("Proveedor", n, i)
        f.unir(n, "Normalizar")
    f.unir("Proveedor", "Normalizar", 4)
    return f


# --------------------------------------------------------------------------- Auditar
def flujo_auditar():
    f = Flujo("auditar", "PIMS · Auditar contrato (Agente 7)",
              "POST /webhook/pims/auditar {organizacion, proveedor?, contrato_texto? | archivo:{nombre, base64}, fecha_ref?}. "
              "Responde 202 {trabajo} y continúa en segundo plano: skill + organización + jurisdicción + perfil → modelo → "
              "cálculo determinista → datos/registro/<id>.json y .md. Avance en GET /webhook/pims/trabajo?id=")
    f.webhook("Webhook auditar", (0, 0), "POST", "pims/auditar")
    f.code("Validar petición", (220, 0), r"""
const b = $input.first().json.body || {};
const r = { ok: false, codigo: 400 };
const org = String(b.organizacion || '').trim();
const texto = typeof b.contrato_texto === 'string' ? b.contrato_texto : '';
const arch = b.archivo && typeof b.archivo === 'object' ? b.archivo : null;
const fecha = b.fecha_ref ? String(b.fecha_ref) : hoy();
if (!idValido(org)) r.error = "Falta 'organizacion' o no es un id válido (minúsculas, números y _).";
else if (!texto.trim() && !arch) r.error = "Envía 'contrato_texto' o 'archivo' {nombre, base64}.";
else if (texto.length > 400000) r.error = 'El contrato supera 400 000 caracteres.';
else if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) r.error = "'fecha_ref' debe tener formato AAAA-MM-DD.";
else if (arch && !/\.(pdf|md|txt)$/i.test(String(arch.nombre || ''))) r.error = 'El archivo debe ser .pdf, .md o .txt (los .docx se convierten a texto en la página).';
else if (arch && (typeof arch.base64 !== 'string' || arch.base64.length > 20000000)) r.error = "'archivo.base64' falta o supera ~15 MB.";
if (r.error) return [{ json: Object.assign(r, { respuesta: { ok: false, error: r.error } }) }];
const t = nuevoTrabajo();
return [{ json: { ok: true, codigo: 202, trabajo: t, inicio: ahora(), organizacion: org, proveedor: String(b.proveedor || '').slice(0, 200),
  contrato_texto: texto, archivo: arch ? { nombre: `${t}_${nombreSeguro(arch.nombre)}`, b64: arch.base64 } : null,
  fechaRef: fecha, respuesta: { ok: true, trabajo: t, consultar: `/webhook/pims/trabajo?id=${t}` } } }];
""")
    f.si("¿Petición válida?", (440, 0), "={{ $json.ok }}")
    f.responder("Responder error", (660, 200))
    f.code("Registrar trabajo", (660, -100), r"""
const v = $('Validar petición').first().json;
const items = [archivoTrabajo(v.trabajo, { tipo: 'auditoria', organizacion: v.organizacion, proveedor: v.proveedor,
  estado: 'en_cola', mensaje: 'Recibido', inicio: v.inicio })];
if (v.archivo) items.push({ json: { ruta: R('datos', 'tmp', v.archivo.nombre), b64: v.archivo.b64 } });
return items;
""")
    f.llamar("Guardar trabajo", (880, -100), "guardar")
    f.code("Respuesta 202", (1100, -100), r"""
const v = $('Validar petición').first().json;
const fallo = $input.all().map((x) => x.json).find((g) => !g.ok);
if (fallo) return [{ json: { codigo: 500, respuesta: { ok: false, error: `No se pudo registrar el trabajo: ${fallo.error}` } } }];
return [{ json: { codigo: 202, respuesta: v.respuesta } }];
""")
    f.responder("Responder aceptado", (1320, -100))
    f.code("Pedir archivos", (1540, -100), r"""
const v = $('Validar petición').first().json;
const p = (clave, ...r) => ({ json: { clave, ruta: R(...r) } });
const items = [
  p('skill', 'pims-dpa-auditor', 'SKILL.md'),
  p('criterios', 'pims-dpa-auditor', 'references', 'criterios_semaforo.md'),
  p('controles', 'pims-dpa-auditor', 'references', 'controles_iso27701_2025.md'),
  p('baseline', 'pims-dpa-auditor', 'assets', 'plantilla_dpa_baseline.md'),
  p('esquema', 'pims-dpa-auditor', 'assets', 'esquema_salida.json'),
  p('config', 'organizaciones', v.organizacion, 'config_organizacion.json'),
  p('perfil', 'organizaciones', v.organizacion, 'perfil_organizacion.md'),
  p('jur_params', 'pims-dpa-auditor', 'jurisdicciones', '*', 'parametros_legales.json'),
  p('jur_marco', 'pims-dpa-auditor', 'jurisdicciones', '*', 'marco_legal.md'),
];
if (v.archivo) items.push(p('contrato', 'datos', 'tmp', v.archivo.nombre));
return items;
""")
    f.llamar("Leer archivos", (1760, -100), "leer")
    f.code("Construir prompt", (1980, -100), r"""
const v = $('Validar petición').first().json;
const L = $input.all().map((x) => x.json);
const fallo = (msg) => [{ json: { ok: false, error: msg } }];
try {
  const config = jsonDe(L, 'config');
  if (!config) return fallo(`La organización '${v.organizacion}' no existe (falta organizaciones/${v.organizacion}/config_organizacion.json).`);
  config.id_organizacion = config.id_organizacion || v.organizacion;
  const jid = config.jurisdiccion || 'peru';
  const dentro = (a) => a.ruta_real.replace(/\\/g, '/').includes(`/jurisdicciones/${jid}/`);
  const pArch = todosDe(L, 'jur_params').find(dentro), mArch = todosDe(L, 'jur_marco').find(dentro);
  const params = pArch ? JSON.parse(pArch.texto) : null;
  try { PIMS_CALC.cargarJurisdiccion(config, params, []); } catch (e) { return fallo(e.message); }
  if (!mArch) return fallo(`Falta marco_legal.md en la jurisdicción '${jid}'.`);
  const esquema = jsonDe(L, 'esquema');
  const perfilA = archivoDe(L, 'perfil');
  const contratoA = archivoDe(L, 'contrato');
  let contrato = v.contrato_texto, hash = null;
  if (contratoA) {
    contrato = contratoA.texto || '';
    hash = contratoA.sha256;
    if (!contrato.replace(/\[Página \d+\]/g, '').trim()) return fallo('No se pudo extraer texto del archivo (¿PDF escaneado?). Pega el texto del contrato.');
  } else hash = PIMS_CALC.sha256Hex(contrato);
  const system = PIMS_PROMPTS.systemAuditoria({
    skillMd: textoDe(L, 'skill'),
    referencias: [
      { ruta: 'references/criterios_semaforo.md', contenido: textoDe(L, 'criterios') },
      { ruta: 'references/controles_iso27701_2025.md', contenido: textoDe(L, 'controles') },
      { ruta: 'assets/plantilla_dpa_baseline.md', contenido: textoDe(L, 'baseline') },
      { ruta: 'assets/esquema_salida.json', contenido: JSON.stringify(esquema, null, 2) },
    ],
    organizacion: { id: v.organizacion, config, perfilTexto: perfilA ? perfilA.texto : null },
    jurisdiccion: { id: jid, marcoMd: mArch.texto, params },
  });
  const mensaje = PIMS_PROMPTS.mensajeAuditoria({ contrato, proveedor: v.proveedor, fechaRef: v.fechaRef });
  return [{ json: { ok: true, system, mensaje, ctx: { config, jur: params, esquema, hash, contrato,
    perfil: perfilA ? { texto: perfilA.texto, ruta: `organizaciones/${v.organizacion}/perfil_organizacion.md`, sha256: perfilA.sha256 } : null } } }];
} catch (e) { return fallo(`Error al preparar la auditoría: ${e.message}`); }
""", "calcular", "prompts")
    f.si("¿Contexto completo?", (2200, -100), "={{ $json.ok }}")
    f.code("Estado: evaluando", (2420, -200), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'auditoria', organizacion: v.organizacion, proveedor: v.proveedor,
  estado: 'evaluando', mensaje: 'El modelo está evaluando los 26 controles', inicio: v.inicio })];
""")
    f.llamar("Guardar estado", (2640, -200), "guardar")
    f.code("Petición al modelo", (2860, -200), r"""
const c = $('Construir prompt').first().json;
return [{ json: { system: c.system, mensaje: c.mensaje, etiqueta: 'auditoria' } }];
""")
    f.llamar("Modelo", (3080, -200), "modelo")
    f.code("Procesar respuesta", (3300, -200), r"""
const r = $input.first().json;
const ctx = $('Construir prompt').first().json.ctx;
if (!r.ok) return [{ json: { ok: false, error: r.error, necesita_correccion: false } }];
const ext = PIMS_PROMPTS.extraerJSON(r.texto);
const informe = PIMS_PROMPTS.informeSinJSON(r.texto);
let errores = [];
const ajustes = ext.objeto ? PIMS_PROMPTS.normalizarRegistro(ext.objeto, ctx.esquema) : [];
if (ext.reparado) ajustes.unshift('JSON con comentarios o comas finales, reparado');
if (!ext.objeto) errores = ['No se encontró un bloque ```json válido con el registro.'];
else errores = PIMS_CALC.validarEntrada(JSON.parse(JSON.stringify(ext.objeto)), ctx.esquema)
  .concat(PIMS_PROMPTS.revisarControles(ext.objeto));
return [{ json: { ok: true, necesita_correccion: errores.length > 0, errores, informe, objeto: ext.objeto, ajustes,
  crudo: ext.crudo, modelo: r.modelo, proveedor: r.proveedor, truncado: r.truncado, reintentos: 0, texto_modelo: r.texto } }];
""", "calcular", "prompts")
    f.si("¿Corregir JSON?", (3520, -200), "={{ $json.necesita_correccion }}")
    f.code("Pedir corrección", (3740, -300), r"""
const p = $('Procesar respuesta').first().json;
const c = $('Construir prompt').first().json;
// 'formato' solo lo usa Ollama (salida estructurada); los demás proveedores lo ignoran.
return [{ json: { system: c.system, etiqueta: 'correccion_json', formato: PIMS_PROMPTS.esquemaParaModelo(c.ctx.esquema),
  mensaje: c.mensaje + '\n\n' + PIMS_PROMPTS.mensajeCorreccionJSON(p.crudo || '(no entregaste un bloque JSON: genéralo completo)', p.errores,
    PIMS_PROMPTS.seccion(p.informe, 4)) } }];
""", "prompts")
    f.llamar("Modelo (corrección)", (3960, -300), "modelo")
    f.code("Procesar corrección", (4180, -300), r"""
const r = $input.first().json;
const p = $('Procesar respuesta').first().json;
const ctx = $('Construir prompt').first().json.ctx;
if (!r.ok) return [{ json: Object.assign({}, p, { ok: false, error: `La corrección falló: ${r.error}` }) }];
const ext = PIMS_PROMPTS.extraerJSON(r.texto);
const ajustes = ext.objeto ? PIMS_PROMPTS.normalizarRegistro(ext.objeto, ctx.esquema) : p.ajustes;
if (ext.reparado) ajustes.unshift('JSON con comentarios o comas finales, reparado');
const errores = ext.objeto ? PIMS_CALC.validarEntrada(JSON.parse(JSON.stringify(ext.objeto)), ctx.esquema)
  .concat(PIMS_PROMPTS.revisarControles(ext.objeto)) : ['Sin JSON en la corrección'];
return [{ json: Object.assign({}, p, { objeto: ext.objeto || p.objeto, errores, ajustes, reintentos: 1, texto_correccion: r.texto }) }];
""", "calcular", "prompts")
    f.code("Calcular y componer", (4400, -100), r"""
const x = $input.first().json;
const v = $('Validar petición').first().json;
const ctx = $('Construir prompt').first().json.ctx;
const items = [];
const terminar = (datos) => items.push(archivoTrabajo(v.trabajo, Object.assign({ tipo: 'auditoria',
  organizacion: v.organizacion, proveedor: v.proveedor, inicio: v.inicio, fin: ahora() }, datos)));
const fallar = (msg, extra) => {
  if (x.texto_modelo) {
    const partes = [`# Auditoría fallida ${v.trabajo}`, '', `Motivo: ${msg}`, ''];
    const errs = (extra && extra.errores) || x.errores || [];
    if (errs.length) partes.push('## Errores de esquema', '', ...errs.slice(0, 40).map((e) => `- ${e}`), '');
    partes.push('## Primera respuesta del modelo', '', x.texto_modelo, '');
    if (x.texto_correccion) partes.push('## Respuesta a la corrección', '', x.texto_correccion, '');
    items.push({ json: { ruta: R('datos', 'fallidos', `${v.trabajo}.md`), texto: partes.join('\n') } });
  }
  terminar(Object.assign({ estado: 'error', mensaje: msg }, extra || {}));
  return items;
};
if (!x.ok) return fallar(x.error);
if (!x.objeto) return fallar('El modelo no entregó el JSON del registro.', { errores: x.errores });
const obj = x.objeto;
const incompletos = PIMS_PROMPTS.revisarControles(obj);
if (incompletos.length) return fallar('El modelo no evaluó los 26 controles, incluso tras una corrección.', { errores: incompletos });
obj.trazabilidad = obj.trazabilidad || {};
obj.trazabilidad.version_skill = obj.trazabilidad.version_skill || '2.0';
obj.trazabilidad.evaluador = obj.trazabilidad.evaluador || `Agente 7 — ${x.modelo} (${x.proveedor}) vía n8n`;
obj.trazabilidad.calculo = 'script';
obj.trazabilidad.version_config = obj.trazabilidad.version_config || ctx.config.version_config || 'sin versión';
const r = PIMS_CALC.ejecutar({ resultado: obj, config: ctx.config, jurisdiccion: ctx.jur, esquema: ctx.esquema,
  perfil: ctx.perfil, hashDocumento: ctx.hash, fechaRef: v.fechaRef });
if (r.codigo === 2) return fallar('El JSON del modelo no cumple el esquema incluso tras una corrección.', { errores: r.errores.slice(0, 30) });
const res = r.resultado;
const base = nombreSeguro(String(res.id_evaluacion || '').replace(/\s+/g, '')) || `DPA-${v.fechaRef.replace(/-/g, '')}`;
const id = `${base}_${$now.toFormat('HHmmss')}`;
res._registro = { id_registro: id, trabajo: v.trabajo, organizacion: v.organizacion, creado: ahora(),
  modelo: x.modelo, proveedor: x.proveedor, reintentos: x.reintentos, errores_esquema_salida: r.errores, truncado: !!x.truncado,
  ajustes_automaticos: x.ajustes || [] };
let md = PIMS_PROMPTS.componerInforme(x.informe, res, ctx.config, { modelo: x.modelo, proveedor: x.proveedor, reintentos: x.reintentos });
if (!/\|\s*A\.2\.2\.2\s*\|/.test(md)) md = PIMS_PROMPTS.insertarEnSeccion(md, 4, PIMS_PROMPTS.matrizControles(res));
items.push({ json: { ruta: R('datos', 'registro', `${id}.json`), texto: JSON.stringify(res, null, 2) } });
items.push({ json: { ruta: R('datos', 'registro', `${id}.md`), texto: md } });
// Copia del texto evaluado: la usa el chat para responder sobre el contrato.
if (ctx.contrato) items.push({ json: { ruta: R('datos', 'registro', `${id}.contrato.txt`), texto: ctx.contrato } });
const p = res.puntaje_proveedor;
terminar({ estado: 'terminado', mensaje: r.resumenTexto, id_registro: id, puntaje: p.valor, banda: p.banda,
  dictamen: res.dictamen, advertencias: r.advertencias, errores_esquema: r.errores });
return items;
""", "calcular", "prompts")
    f.code("Error de contexto", (2420, 50), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'auditoria', organizacion: v.organizacion, proveedor: v.proveedor,
  estado: 'error', mensaje: $input.first().json.error, inicio: v.inicio, fin: ahora() })];
""")
    # Base de datos del PIMS (si datos/config_bd.json la activa). Los archivos se escriben siempre:
    # son la copia de respaldo mientras dure la doble escritura.
    f.code("BD: preparar", (4620, -200), r"""
const it = $input.all().map((x) => x.json);
const reg = it.find((j) => /\/datos\/registro\/[^/]+\.json$/.test(j.ruta || ''));
if (!reg) return [{ json: { operacion: 'nada' } }];
const md = it.find((j) => j.ruta === reg.ruta.replace(/\.json$/, '.md'));
return [{ json: { operacion: 'guardar_auditoria', registro: reg.texto, informe: md ? md.texto : null } }];
""")
    f.llamar("Base de datos", (4840, -200), "bd", onError="continueRegularOutput")
    f.code("BD: anotar", (5060, -100), r"""
const items = $('Calcular y componer').all().map((x) => ({ json: Object.assign({}, x.json) }));
const b = $input.first().json || {};
const err = b.error && typeof b.error === 'object' ? (b.error.message || JSON.stringify(b.error)) : b.error;
const t = items.find((x) => /\/datos\/trabajos\/[^/]+\.json$/.test(x.json.ruta || ''));
if (t && !b.omitido) {
  const trabajo = JSON.parse(t.json.texto);
  if (b.ok === false || err) {
    trabajo.bd = 'error';
    trabajo.advertencias = (trabajo.advertencias || []).concat([`No se guardó en la base de datos: ${err || 'error desconocido'}. El registro en disco sigue siendo válido.`]);
  } else if (b.resultado) trabajo.bd = 'guardado';
  t.json.texto = JSON.stringify(trabajo, null, 2);
}
return items;
""")
    f.llamar("Guardar resultado", (5280, -100), "guardar")
    f.cadena("Webhook auditar", "Validar petición", "¿Petición válida?")
    f.unir("¿Petición válida?", "Registrar trabajo", 0)
    f.unir("¿Petición válida?", "Responder error", 1)
    f.cadena("Registrar trabajo", "Guardar trabajo", "Respuesta 202", "Responder aceptado", "Pedir archivos",
             "Leer archivos", "Construir prompt", "¿Contexto completo?")
    f.unir("¿Contexto completo?", "Estado: evaluando", 0)
    f.unir("¿Contexto completo?", "Error de contexto", 1)
    f.cadena("Estado: evaluando", "Guardar estado", "Petición al modelo", "Modelo", "Procesar respuesta", "¿Corregir JSON?")
    f.unir("¿Corregir JSON?", "Pedir corrección", 0)
    f.unir("¿Corregir JSON?", "Calcular y componer", 1)
    f.cadena("Pedir corrección", "Modelo (corrección)", "Procesar corrección", "Calcular y componer",
             "BD: preparar", "Base de datos", "BD: anotar", "Guardar resultado")
    f.unir("Error de contexto", "Guardar resultado")
    return f


# --------------------------------------------------------------------------- Perfilar
def flujo_perfilar():
    f = Flujo("perfilar", "PIMS · Perfilar organización (Agente 1)",
              "POST /webhook/pims/perfilar {organizacion}. Lee organizaciones/<id>/documentos/ (pdf, md, txt), extrae "
              "notas por partes con el modelo, redacta perfil_organizacion.md (Borrador), lo valida y lo guarda. "
              "Avance en GET /webhook/pims/trabajo?id=")
    f.webhook("Webhook perfilar", (0, 0), "POST", "pims/perfilar")
    f.code("Validar petición", (220, 0), r"""
const b = $input.first().json.body || {};
const org = String(b.organizacion || '').trim();
if (!idValido(org)) return [{ json: { ok: false, codigo: 400, respuesta: { ok: false, error: "Falta 'organizacion' o no es un id válido." } } }];
const t = nuevoTrabajo();
return [{ json: { ok: true, codigo: 202, trabajo: t, organizacion: org, inicio: ahora(),
  respuesta: { ok: true, trabajo: t, consultar: `/webhook/pims/trabajo?id=${t}` } } }];
""")
    f.si("¿Petición válida?", (440, 0), "={{ $json.ok }}")
    f.responder("Responder error", (660, 200))
    f.code("Registrar trabajo", (660, -100), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'perfil', organizacion: v.organizacion, estado: 'en_cola', mensaje: 'Recibido', inicio: v.inicio })];
""")
    f.llamar("Guardar trabajo", (880, -100), "guardar")
    f.code("Respuesta 202", (1100, -100), r"""
return [{ json: { codigo: 202, respuesta: $('Validar petición').first().json.respuesta } }];
""")
    f.responder("Responder aceptado", (1320, -100))
    f.code("Pedir archivos", (1540, -100), r"""
const v = $('Validar petición').first().json;
const p = (clave, ...r) => ({ json: { clave, ruta: R(...r) } });
return [
  p('config', 'organizaciones', v.organizacion, 'config_organizacion.json'),
  p('documentos', 'organizaciones', v.organizacion, 'documentos', '*.{pdf,md,txt,PDF,MD,TXT}'),
  p('skill', 'pims-perfilador-organizacion', 'SKILL.md'),
  p('plantilla', 'pims-perfilador-organizacion', 'assets', 'plantilla_perfil.md'),
  p('criterios', 'pims-dpa-auditor', 'references', 'criterios_semaforo.md'),
  p('perfil_actual', 'organizaciones', v.organizacion, 'perfil_organizacion.md'),
  p('modelo', 'datos', 'config_modelo.json'),
];
""")
    f.llamar("Leer archivos", (1760, -100), "leer")
    f.code("Preparar notas", (1980, -100), r"""
const v = $('Validar petición').first().json;
const L = $input.all().map((x) => x.json);
const fallo = (msg) => [{ json: { ok: false, error: msg } }];
try {
  const config = jsonDe(L, 'config');
  if (!config) return fallo(`La organización '${v.organizacion}' no existe.`);
  const docs = todosDe(L, 'documentos').filter((d) => d.texto && d.texto.replace(/\[Página \d+\]/g, '').trim());
  const sinTexto = todosDe(L, 'documentos').filter((d) => !(d.texto && d.texto.replace(/\[Página \d+\]/g, '').trim())).map((d) => d.nombre);
  if (!docs.length) return fallo(`No hay documentos con texto en organizaciones/${v.organizacion}/documentos/` + (sinTexto.length ? ` (sin texto extraíble: ${sinTexto.join(', ')})` : ''));
  const system = PIMS_PROMPTS.systemPerfilador({ skillMd: textoDe(L, 'skill'), plantilla: textoDe(L, 'plantilla'), criterios: textoDe(L, 'criterios') });
  const meta = docs.map((d, i) => ({ id: `D${i + 1}`, titulo: d.nombre.replace(/\.[^.]+$/, ''), nombre: d.nombre, sha256: d.sha256,
    paginas: d.paginas || null, tipo: 'Otro' }));
  const items = [];
  docs.forEach((d, i) => {
    const partes = PIMS_PROMPTS.trocear(d.texto, 18000);
    partes.forEach((t, k) => items.push({ json: { ok: true, system, etiqueta: `D${i + 1} ${k + 1}/${partes.length}`, doc: `D${i + 1}`,
      mensaje: PIMS_PROMPTS.mensajeNotas({ id: `D${i + 1}`, titulo: meta[i].titulo, parte: k + 1, total: partes.length, texto: t }) } }));
  });
  let modelo = {}; try { modelo = jsonDe(L, 'modelo') || {}; } catch (e) { modelo = {}; }
  items[0].json.ctx = { config, meta, sinTexto, perfilActual: textoDe(L, 'perfil_actual'), system, modelo };
  return items;
} catch (e) { return fallo(`Error al preparar el perfil: ${e.message}`); }
""", "prompts")
    f.si("¿Hay documentos?", (2200, -100), "={{ $json.ok }}")
    f.code("Estado: notas", (2420, -200), r"""
const v = $('Validar petición').first().json;
const n = $('Preparar notas').all().length;
return [archivoTrabajo(v.trabajo, { tipo: 'perfil', organizacion: v.organizacion, estado: 'extrayendo',
  mensaje: `Extrayendo notas de ${n} parte(s) de los documentos`, inicio: v.inicio })];
""")
    f.llamar("Guardar estado", (2640, -200), "guardar")
    f.code("Peticiones de notas", (2860, -200), r"""
return $('Preparar notas').all().map((x) => ({ json: { system: x.json.system, mensaje: x.json.mensaje, etiqueta: x.json.etiqueta } }));
""")
    f.llamar("Modelo (notas)", (3080, -200), "modelo")
    f.code("Preparar perfil", (3300, -200), r"""
const v = $('Validar petición').first().json;
const pedidos = $('Preparar notas').all().map((x) => x.json);
const ctx = pedidos[0].ctx;
const res = $input.all().map((x) => x.json);
const malo = res.find((r) => !r.ok);
if (malo) return [{ json: { ok: false, error: `El modelo falló al extraer notas (${malo.etiqueta}): ${malo.error}` } }];
const porDoc = {};
res.forEach((r, i) => { (porDoc[pedidos[i].doc] = porDoc[pedidos[i].doc] || []).push(`(${r.etiqueta})\n${r.texto}`); });
// Las notas de todos los documentos deben caber en el contexto del modelo (ver presupuestoNotas).
const fijos = ctx.system.length + 4000 + ctx.meta.length * 160;
const comp = PIMS_PROMPTS.compactarNotas(porDoc, PIMS_PROMPTS.presupuestoNotas(ctx.modelo, fijos));
const mensaje = PIMS_PROMPTS.mensajePerfil({ organizacion: { nombre: ctx.config.organizacion, id: v.organizacion },
  jurisdiccion: ctx.config.jurisdiccion || 'peru', fecha: hoy(), documentos: ctx.meta, notas: comp.texto });
return [{ json: { ok: true, system: ctx.system, mensaje, etiqueta: 'perfil', notas_recortadas: comp.recortadas,
  notas_caracteres: comp.original } }];
""", "prompts")
    f.llamar("Modelo (perfil)", (3520, -200), "modelo")
    f.code("Validar perfil", (3740, -200), r"""
const r = $input.first().json;
const prev = $('Preparar perfil').first().json;
if (!prev.ok) return [{ json: { ok: false, error: prev.error, necesita: false } }];
if (!r.ok) return [{ json: { ok: false, error: r.error, necesita: false } }];
const ctx = $('Preparar notas').first().json.ctx;
const v = $('Validar petición').first().json;
const norm = PIMS_PROMPTS.normalizarPerfil(PIMS_PROMPTS.limpiarMarkdown(r.texto), { meta: ctx.meta,
  organizacion: ctx.config.organizacion, id: v.organizacion, jurisdiccion: ctx.config.jurisdiccion || 'peru', fecha: hoy() });
const md = norm.md;
const val = PIMS_PERFIL.validar(md);
return [{ json: { ok: true, md, val, ajustes: norm.ajustes, necesita: !val.valido, reintentos: 0, modelo: r.modelo, proveedor: r.proveedor } }];
""", "perfil", "prompts")
    f.si("¿Corregir perfil?", (3960, -200), "={{ $json.necesita }}")
    f.code("Pedir corrección", (4180, -300), r"""
const p = $('Validar perfil').first().json;
const pp = $('Preparar perfil').first().json;
return [{ json: { system: pp.system, etiqueta: 'correccion_perfil', mensaje: PIMS_PROMPTS.mensajeCorreccionPerfil(p.md, p.val.errores) } }];
""", "prompts")
    f.llamar("Modelo (corrección)", (4400, -300), "modelo")
    f.code("Revalidar", (4620, -300), r"""
const r = $input.first().json;
const p = $('Validar perfil').first().json;
if (!r.ok) return [{ json: Object.assign({}, p, { reintentos: 1 }) }];
const ctx = $('Preparar notas').first().json.ctx;
const v = $('Validar petición').first().json;
const norm = PIMS_PROMPTS.normalizarPerfil(PIMS_PROMPTS.limpiarMarkdown(r.texto), { meta: ctx.meta,
  organizacion: ctx.config.organizacion, id: v.organizacion, jurisdiccion: ctx.config.jurisdiccion || 'peru', fecha: hoy() });
const md = norm.md;
const val = PIMS_PERFIL.validar(md);
return [{ json: Object.assign({}, p, val.errores.length <= p.val.errores.length ? { md, val, ajustes: norm.ajustes } : {}, { reintentos: 1 }) }];
""", "perfil", "prompts")
    f.code("Guardar perfil", (4840, -100), r"""
const x = $input.first().json;
const v = $('Validar petición').first().json;
const items = [];
const fin = (datos) => items.push(archivoTrabajo(v.trabajo, Object.assign({ tipo: 'perfil', organizacion: v.organizacion,
  inicio: v.inicio, fin: ahora() }, datos)));
if (!x.ok) { fin({ estado: 'error', mensaje: x.error }); return items; }
const carpeta = (n) => R('organizaciones', v.organizacion, n);
const ctx = $('Preparar notas').first().json.ctx;
const pp = $('Preparar perfil').first().json;
const resumen = { valido: x.val.valido, errores: x.val.errores, advertencias: x.val.advertencias, documentos: ctx.meta,
  sin_texto: ctx.sinTexto, generado: ahora(), modelo: x.modelo, proveedor: x.proveedor, reintentos: x.reintentos,
  ajustes_automaticos: x.ajustes || [], notas_recortadas: pp.notas_recortadas || 0 };
if (x.val.valido) {
  if (ctx.perfilActual) items.push({ json: { ruta: carpeta('perfil_organizacion.anterior.md'), texto: ctx.perfilActual } });
  items.push({ json: { ruta: carpeta('perfil_organizacion.md'), texto: x.md } });
} else {
  items.push({ json: { ruta: carpeta('perfil_organizacion.borrador_invalido.md'), texto: x.md } });
}
items.push({ json: { ruta: carpeta('validacion_perfil.json'), texto: JSON.stringify(resumen, null, 2) } });
fin({ estado: x.val.valido ? 'terminado' : 'terminado_con_errores',
  mensaje: x.val.valido ? `Perfil generado (Borrador, ${ctx.meta.length} documento(s)). Debe validarlo el DPO.`
      + ((x.ajustes || []).some((s) => s.includes('Supuesto')) ? ' Hay filas marcadas como Supuesto: revísalas.' : '')
      + (pp.notas_recortadas ? ` Se omitieron ${pp.notas_recortadas} nota(s) para que cupieran en el contexto del modelo.` : '')
    : `El perfil no pasó la validación (${x.val.errores.length} errores); se guardó como perfil_organizacion.borrador_invalido.md`,
  validacion: resumen });
return items;
""")
    f.code("Error de documentos", (2420, 50), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'perfil', organizacion: v.organizacion, estado: 'error',
  mensaje: $input.first().json.error, inicio: v.inicio, fin: ahora() })];
""")
    f.llamar("Guardar archivos", (5060, -100), "guardar")
    f.cadena("Webhook perfilar", "Validar petición", "¿Petición válida?")
    f.unir("¿Petición válida?", "Registrar trabajo", 0)
    f.unir("¿Petición válida?", "Responder error", 1)
    f.cadena("Registrar trabajo", "Guardar trabajo", "Respuesta 202", "Responder aceptado", "Pedir archivos",
             "Leer archivos", "Preparar notas", "¿Hay documentos?")
    f.unir("¿Hay documentos?", "Estado: notas", 0)
    f.unir("¿Hay documentos?", "Error de documentos", 1)
    f.cadena("Estado: notas", "Guardar estado", "Peticiones de notas", "Modelo (notas)", "Preparar perfil",
             "Modelo (perfil)", "Validar perfil", "¿Corregir perfil?")
    f.unir("¿Corregir perfil?", "Pedir corrección", 0)
    f.unir("¿Corregir perfil?", "Guardar perfil", 1)
    f.cadena("Pedir corrección", "Modelo (corrección)", "Revalidar", "Guardar perfil", "Guardar archivos")
    f.unir("Error de documentos", "Guardar archivos")
    return f


# --------------------------------------------------------------------------- Aprobaciones
def flujo_aprobar():
    f = Flujo("aprobar", "PIMS · Aprobaciones (doble puerta DPO → Legal)",
              "POST /webhook/pims/aprobar {id_registro, rol: DPO|Legal, decision: aprobar|rechazar, usuario, comentario}. "
              "POST /webhook/pims/perfil/validar {organizacion, validado_por}: el DPO valida el perfil.")
    # --- A. Aprobar o rechazar un registro
    f.webhook("Webhook aprobar", (0, 0), "POST", "pims/aprobar")
    f.code("Validar decisión", (220, 0), r"""
const b = $input.first().json.body || {};
const id = String(b.id_registro || '');
const rol = String(b.rol || ''), dec = String(b.decision || '').toLowerCase(), usuario = String(b.usuario || '').trim();
let error = null;
if (!/^[A-Za-z0-9_.-]{3,140}$/.test(id)) error = "Falta 'id_registro' válido.";
else if (!['DPO', 'Legal'].includes(rol)) error = "'rol' debe ser DPO o Legal.";
else if (!['aprobar', 'rechazar'].includes(dec)) error = "'decision' debe ser aprobar o rechazar.";
else if (!usuario) error = "Indica 'usuario' (quién decide).";
if (error) return [{ json: { ok: false, codigo: 400, respuesta: { ok: false, error } } }];
return [{ json: { ok: true, id, rol, dec, usuario: usuario.slice(0, 120), comentario: String(b.comentario || '').slice(0, 2000) } }];
""")
    f.si("¿Decisión válida?", (440, 0), "={{ $json.ok }}")
    f.responder("Responder (aprobar)", (2200, 0))
    f.code("Pedir registro", (660, -100), r"""
const v = $('Validar decisión').first().json;
return [{ json: { clave: 'json', ruta: R('datos', 'registro', `${v.id}.json`) } },
        { json: { clave: 'md', ruta: R('datos', 'registro', `${v.id}.md`) } }];
""")
    f.llamar("Leer registro", (880, -100), "leer")
    f.code("Aplicar decisión", (1100, -100), r"""
const v = $('Validar decisión').first().json;
const L = $input.all().map((x) => x.json);
const res = jsonDe(L, 'json');
if (!res) return [{ json: { ok: false, codigo: 404, respuesta: { ok: false, error: `No existe el registro ${v.id}.` } } }];
const actual = (res.aprobacion || {}).estado || 'Pendiente DPO';
const TRANS = { 'Pendiente DPO|DPO': { aprobar: 'Pendiente Legal', rechazar: 'Rechazado' },
                'Pendiente Legal|Legal': { aprobar: 'Aprobado', rechazar: 'Rechazado' } };
const t = TRANS[`${actual}|${v.rol}`];
if (!t) {
  const turno = actual === 'Pendiente DPO' ? 'DPO' : actual === 'Pendiente Legal' ? 'Legal' : 'nadie (ya está cerrado)';
  return [{ json: { ok: false, codigo: 409, respuesta: { ok: false, error: `El registro está en '${actual}'; le corresponde decidir a ${turno}.` } } }];
}
const nuevo = t[v.dec];
const cfgCargos = ((res.trazabilidad || {}).parametros_aplicados || {}).aprobadores_cargos || {};
const evento = { rol: v.rol, cargo: cfgCargos[v.rol] || v.rol, usuario: v.usuario, decision: v.dec, comentario: v.comentario,
  fecha: ahora(), estado_anterior: actual, estado_nuevo: nuevo };
res.aprobacion = Object.assign({}, res.aprobacion, { estado: nuevo });
res.aprobacion.historial = (res.aprobacion.historial || []).concat([evento]);
res.contrato.estado_dpa = nuevo;
const items = [{ json: { ruta: R('datos', 'registro', `${v.id}.json`), texto: JSON.stringify(res, null, 2) } }];
const md = textoDe(L, 'md');
if (md !== null) {
  const linea = `> **${evento.fecha.slice(0, 16).replace('T', ' ')} · ${evento.cargo} (${v.usuario})**: ${v.dec === 'aprobar' ? '✅ aprobó' : '❌ rechazó'}` +
    ` — estado: ${actual} → **${nuevo}**${v.comentario ? `. Comentario: ${v.comentario.replace(/\n/g, ' ')}` : ''}`;
  items.push({ json: { ruta: R('datos', 'registro', `${v.id}.md`), texto: PIMS_PROMPTS.insertarEnSeccion(md, 10, linea) } });
}
return items;
""", "prompts")
    f.si("¿Transición válida?", (1320, -100), "={{ $json.ok !== false }}")
    f.llamar("Guardar registro", (1540, -200), "guardar")
    f.code("BD: decisión", (1760, -300), r"""
const v = $('Validar decisión').first().json;
const res = JSON.parse($('Aplicar decisión').first().json.texto);
const ev = res.aprobacion.historial[res.aprobacion.historial.length - 1];
return [{ json: { operacion: 'registrar_decision', id: v.id, rol: ev.rol, decision: ev.decision, usuario: ev.usuario,
  cargo: ev.cargo, comentario: ev.comentario, fecha: ev.fecha } }];
""")
    f.llamar("Base de datos", (1980, -300), "bd", onError="continueRegularOutput")
    f.code("Respuesta aprobar", (2200, -200), r"""
const v = $('Validar decisión').first().json;
const res = JSON.parse($('Aplicar decisión').first().json.texto);
const fallo = $('Guardar registro').all().map((x) => x.json).find((g) => !g.ok);
if (fallo) return [{ json: { codigo: 500, respuesta: { ok: false, error: fallo.error } } }];
const b = $input.first().json || {};
const respuesta = { ok: true, id_registro: v.id, estado: res.aprobacion.estado, historial: res.aprobacion.historial };
// La decisión ya quedó en disco; si la base la rechaza (p. ej. el expediente no se migró), se avisa sin deshacerla.
const err = b.error && typeof b.error === 'object' ? (b.error.message || JSON.stringify(b.error)) : b.error;
if (!b.omitido) respuesta.bd = b.ok === false || err ? { ok: false, error: err || 'error desconocido' } : { ok: true };
return [{ json: { codigo: 200, respuesta } }];
""")
    f.cadena("Webhook aprobar", "Validar decisión", "¿Decisión válida?")
    f.unir("¿Decisión válida?", "Pedir registro", 0)
    f.unir("¿Decisión válida?", "Responder (aprobar)", 1)
    f.cadena("Pedir registro", "Leer registro", "Aplicar decisión", "¿Transición válida?")
    f.unir("¿Transición válida?", "Guardar registro", 0)
    f.unir("¿Transición válida?", "Responder (aprobar)", 1)
    f.cadena("Guardar registro", "BD: decisión", "Base de datos", "Respuesta aprobar", "Responder (aprobar)")

    # --- B. El DPO valida el perfil
    f.webhook("Webhook validar perfil", (0, 500), "POST", "pims/perfil/validar")
    f.code("Validar petición perfil", (220, 500), r"""
const b = $input.first().json.body || {};
const org = String(b.organizacion || ''), quien = String(b.validado_por || '').trim();
if (!idValido(org) || !quien) return [{ json: { ok: false, codigo: 400, respuesta: { ok: false, error: "Indica 'organizacion' y 'validado_por'." } } }];
return [{ json: { ok: true, org, quien: quien.slice(0, 120) } }];
""")
    f.si("¿Petición perfil válida?", (440, 500), "={{ $json.ok }}")
    f.responder("Responder (perfil)", (2200, 500))
    f.code("Pedir perfil", (660, 400), r"""
const v = $('Validar petición perfil').first().json;
return [{ json: { clave: 'perfil', ruta: R('organizaciones', v.org, 'perfil_organizacion.md') } }];
""")
    f.llamar("Leer perfil", (880, 400), "leer")
    f.code("Marcar validado", (1100, 400), r"""
const v = $('Validar petición perfil').first().json;
const md = textoDe($input.all().map((x) => x.json), 'perfil');
if (md === null) return [{ json: { ok: false, codigo: 404, respuesta: { ok: false, error: 'La organización no tiene perfil_organizacion.md.' } } }];
const val = PIMS_PERFIL.validar(md);
if (!val.valido) return [{ json: { ok: false, codigo: 422, respuesta: { ok: false, error: 'El perfil tiene errores de formato; corrígelo antes de validarlo.', errores: val.errores } } }];
const nuevo = PIMS_PERFIL.marcarValidado(md, v.quien, hoy());
return [{ json: { ok: true, ruta: R('organizaciones', v.org, 'perfil_organizacion.md'), texto: nuevo } }];
""", "perfil")
    f.si("¿Perfil validable?", (1320, 400), "={{ $json.ok }}")
    f.llamar("Guardar perfil", (1540, 300), "guardar")
    f.code("Respuesta perfil", (1760, 300), r"""
const g = $input.first().json;
const v = $('Validar petición perfil').first().json;
if (!g.ok) return [{ json: { codigo: 500, respuesta: { ok: false, error: g.error } } }];
return [{ json: { codigo: 200, respuesta: { ok: true, organizacion: v.org, estado: `Validado por DPO (${v.quien}, ${hoy()})` } } }];
""")
    f.cadena("Webhook validar perfil", "Validar petición perfil", "¿Petición perfil válida?")
    f.unir("¿Petición perfil válida?", "Pedir perfil", 0)
    f.unir("¿Petición perfil válida?", "Responder (perfil)", 1)
    f.cadena("Pedir perfil", "Leer perfil", "Marcar validado", "¿Perfil validable?")
    f.unir("¿Perfil validable?", "Guardar perfil", 0)
    f.unir("¿Perfil validable?", "Responder (perfil)", 1)
    f.cadena("Guardar perfil", "Respuesta perfil", "Responder (perfil)")
    return f


# --------------------------------------------------------------------------- Renovaciones
RENOV_JS = r"""
const L = $input.all().map((x) => x.json);
const ref = hoy();
const lista = [];
for (const a of todosDe(L, 'registros')) {
  let r; try { r = JSON.parse(a.texto); } catch (e) { continue; }
  const estado = (r.aprobacion || {}).estado || 'Pendiente DPO';
  if (estado === 'Rechazado') continue;
  const dias = ((r.trazabilidad || {}).parametros_aplicados || {}).dias_alerta_renovacion || 60;
  let alertas = [];
  try { alertas = PIMS_CALC.alertasRenovacion(r.contrato || {}, ref, dias); } catch (e) { alertas = [{ prioridad: 'Media', descripcion: `Fecha inválida en el registro: ${e.message}` }]; }
  if (alertas.length) lista.push({ id_registro: (r._registro || {}).id_registro || a.nombre.replace(/\.json$/, ''),
    organizacion: (r.organizacion || {}).id || (r._registro || {}).organizacion || null, proveedor: (r.tercero || {}).nombre || '',
    estado, fin_vigencia: (r.contrato || {}).fecha_vigencia_fin || null, alertas });
}
lista.sort((x, y) => (y.alertas.some((a) => a.prioridad === 'Alta') - x.alertas.some((a) => a.prioridad === 'Alta')));
return [{ json: { codigo: 200, fecha_referencia: ref, total: lista.length, altas: lista.filter((x) => x.alertas.some((a) => a.prioridad === 'Alta')).length,
  respuesta: { ok: true, fecha_referencia: ref, registros_con_alertas: lista } } }];
"""


def flujo_renovar():
    f = Flujo("renovar", "PIMS · Renovaciones y vencimientos",
              "Cada lunes 07:52 (zona de n8n) recalcula las alertas de renovación de todos los registros con la fecha "
              "del día y las guarda en datos/alertas_renovacion.json. También bajo demanda: GET /webhook/pims/renovaciones.")
    pedir = r"""return [{ json: { clave: 'registros', ruta: R('datos', 'registro', '*.json') } }];"""
    f.nodo("Cada lunes", "n8n-nodes-base.scheduleTrigger", 1.2, {"rule": {"interval": [
        {"field": "weeks", "weeksInterval": 1, "triggerAtDay": [1], "triggerAtHour": 7, "triggerAtMinute": 52}]}}, (0, 0))
    f.code("Pedir registros", (220, 0), pedir)
    f.llamar("Leer registros", (440, 0), "leer")
    f.code("Calcular alertas", (660, 0), RENOV_JS, "calcular")
    f.code("Archivo de alertas", (880, 0), r"""
const j = $input.first().json;
return [{ json: { ruta: R('datos', 'alertas_renovacion.json'), texto: JSON.stringify(j.respuesta, null, 2) } }];
""")
    f.llamar("Guardar alertas", (1100, 0), "guardar")
    f.cadena("Cada lunes", "Pedir registros", "Leer registros", "Calcular alertas", "Archivo de alertas", "Guardar alertas")
    f.webhook("Webhook renovaciones", (0, 300), "GET", "pims/renovaciones")
    f.code("Pedir registros (web)", (220, 300), pedir)
    f.llamar("Leer registros (web)", (440, 300), "leer")
    f.code("Calcular alertas (web)", (660, 300), RENOV_JS, "calcular")
    f.responder("Responder", (880, 300))
    f.cadena("Webhook renovaciones", "Pedir registros (web)", "Leer registros (web)", "Calcular alertas (web)", "Responder")
    return f


# --------------------------------------------------------------------------- Consultas (GET)
def flujo_consultas():
    f = Flujo("consultas", "PIMS · Consultas (API de lectura para la página)",
              "GET /webhook/pims/{estado, organizaciones, registro, registro/detalle, trabajo, perfil, jurisdicciones}. "
              "No guarda las ejecuciones exitosas (la página consulta el avance cada pocos segundos).",
              guardar_exitos=False)
    rutas = {
        "estado": (r"""
return [{ json: { clave: 'config', ruta: R('datos', 'config_modelo.json') } },
        { json: { clave: 'orgs', ruta: R('organizaciones', '*', 'config_organizacion.json') } }];
""", r"""
const L = $input.all().map((x) => x.json);
let cfg = {}; try { cfg = jsonDe(L, 'config') || {}; } catch (e) { cfg = { error: e.message }; }
if (cfg.api_key) cfg.api_key = '********' + String(cfg.api_key).slice(-4);
const orgs = todosDe(L, 'orgs').filter((a) => !a.ruta_real.includes('/_plantilla/')).map((a) => {
  try { const c = JSON.parse(a.texto); return { id: c.id_organizacion, nombre: c.organizacion, jurisdiccion: c.jurisdiccion }; }
  catch (e) { return { id: a.ruta_real.split('/').slice(-2)[0], error: 'config inválida' }; }
});
return [{ json: { respuesta: { ok: true, version: '2.0', hoy: hoy(), modelo: cfg, organizaciones: orgs } } }];
"""),
        "organizaciones": (r"""
return [{ json: { clave: 'orgs', ruta: R('organizaciones', '*', 'config_organizacion.json') } },
        { json: { clave: 'perfiles', ruta: R('organizaciones', '*', 'perfil_organizacion.md') } },
        { json: { clave: 'validaciones', ruta: R('organizaciones', '*', 'validacion_perfil.json') } },
        { json: { clave: 'registros', ruta: R('datos', 'registro', '*.json') } },
        { json: { clave: 'documentos', ruta: R('organizaciones', '*', 'documentos', '*.{md,txt,MD,TXT}') } }];
""", r"""
const L = $input.all().map((x) => x.json);
const carpetaDe = (a) => a.ruta_real.replace(/\\/g, '/').split('/organizaciones/')[1].split('/')[0];
const regs = todosDe(L, 'registros').map((a) => { try { return JSON.parse(a.texto); } catch (e) { return null; } }).filter(Boolean);
const normal = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/s\.?a\.?c?\.?|s\.?r\.?l\.?|[^a-z0-9 ]/g, ' ').trim().split(/\s+/)[0] || '';
const orgs = todosDe(L, 'orgs').filter((a) => !a.ruta_real.includes('/_plantilla/')).map((a) => {
  const id = carpetaDe(a);
  let c = {}; try { c = JSON.parse(a.texto); } catch (e) { c = { error: 'config inválida' }; }
  const pa = todosDe(L, 'perfiles').find((p) => carpetaDe(p) === id);
  const va = todosDe(L, 'validaciones').find((p) => carpetaDe(p) === id);
  let perfil = { existe: false };
  if (pa) {
    const v = PIMS_PERFIL.validar(pa.texto);
    perfil = { existe: true, estado: v.estado, valido: v.valido, errores: v.errores.length, terceros: PIMS_PERFIL.terceros(pa.texto) };
  }
  let ultima = null; if (va) { try { ultima = JSON.parse(va.texto); } catch (e) { ultima = null; } }
  const misRegs = regs.filter((r) => ((r.organizacion || {}).id || (r._registro || {}).organizacion) === id).map((r) => ({
    id_registro: (r._registro || {}).id_registro, proveedor: (r.tercero || {}).nombre, puntaje: (r.puntaje_proveedor || {}).valor,
    dictamen: r.dictamen, estado: (r.aprobacion || {}).estado, fecha: r.fecha }));
  const evaluados = new Set(misRegs.map((r) => normal(r.proveedor)));
  const brechas = (perfil.terceros || []).filter((t) => !evaluados.has(normal(t['tercero / servicio']))).map((t) => t['tercero / servicio']);
  return { id, nombre: c.organizacion, jurisdiccion: c.jurisdiccion, cargos: c.aprobadores_cargos || {}, config: c,
    perfil, ultima_generacion_perfil: ultima, registros: misRegs, terceros_sin_dpa_evaluado: brechas };
});
return [{ json: { respuesta: { ok: true, organizaciones: orgs } } }];
"""),
        "registro": (r"""
return [{ json: { clave: 'registros', ruta: R('datos', 'registro', '*.json') } }];
""", r"""
const q = $('Webhook registro').first().json.query || {};
const L = $input.all().map((x) => x.json);
const lista = todosDe(L, 'registros').map((a) => { try { return JSON.parse(a.texto); } catch (e) { return null; } }).filter(Boolean)
  .filter((r) => !q.organizacion || ((r.organizacion || {}).id || (r._registro || {}).organizacion) === q.organizacion)
  .filter((r) => !q.estado || (r.aprobacion || {}).estado === q.estado)
  .map((r) => ({ id_registro: (r._registro || {}).id_registro, organizacion: (r.organizacion || {}).id, proveedor: (r.tercero || {}).nombre,
    rol: (r.tercero || {}).rol, fecha: r.fecha, creado: (r._registro || {}).creado, puntaje: (r.puntaje_proveedor || {}).valor,
    banda: (r.puntaje_proveedor || {}).banda, dictamen: r.dictamen, estado: (r.aprobacion || {}).estado, riesgo_pii: r.nivel_riesgo_pii,
    resumen: r.resumen, modelo: (r._registro || {}).modelo }))
  .sort((x, y) => String(y.creado || '').localeCompare(String(x.creado || '')));
return [{ json: { respuesta: { ok: true, total: lista.length, registros: lista } } }];
"""),
        "registro/detalle": (r"""
const id = String(($('Webhook registro/detalle').first().json.query || {}).id || '');
if (!/^[A-Za-z0-9_.-]{3,140}$/.test(id)) return [{ json: { clave: 'nada', ruta: R('datos', 'registro', '__no_existe__') } }];
return [{ json: { clave: 'json', ruta: R('datos', 'registro', `${id}.json`) } }, { json: { clave: 'md', ruta: R('datos', 'registro', `${id}.md`) } }];
""", r"""
const L = $input.all().map((x) => x.json);
const res = jsonDe(L, 'json');
if (!res) return [{ json: { codigo: 404, respuesta: { ok: false, error: 'Registro no encontrado.' } } }];
return [{ json: { respuesta: { ok: true, resultado: res, informe: textoDe(L, 'md') } } }];
"""),
        "trabajo": (r"""
const id = String(($('Webhook trabajo').first().json.query || {}).id || '');
if (!/^T[0-9a-z]{10,30}$/.test(id)) return [{ json: { clave: 'nada', ruta: R('datos', 'trabajos', '__no_existe__') } }];
return [{ json: { clave: 'trabajo', ruta: R('datos', 'trabajos', `${id}.json`) } }];
""", r"""
const t = jsonDe($input.all().map((x) => x.json), 'trabajo');
if (!t) return [{ json: { codigo: 404, respuesta: { ok: false, error: 'Trabajo no encontrado.' } } }];
return [{ json: { respuesta: Object.assign({ ok: true }, t) } }];
"""),
        "perfil": (r"""
const org = String(($('Webhook perfil').first().json.query || {}).organizacion || '');
const o = idValido(org) ? org : '__no_existe__';
return [{ json: { clave: 'perfil', ruta: R('organizaciones', o, 'perfil_organizacion.md') } },
        { json: { clave: 'invalido', ruta: R('organizaciones', o, 'perfil_organizacion.borrador_invalido.md') } },
        { json: { clave: 'validacion', ruta: R('organizaciones', o, 'validacion_perfil.json') } }];
""", r"""
const L = $input.all().map((x) => x.json);
const md = textoDe(L, 'perfil');
const inval = textoDe(L, 'invalido');
let ultima = null; try { ultima = jsonDe(L, 'validacion'); } catch (e) { ultima = null; }
if (md === null && inval === null) return [{ json: { codigo: 404, respuesta: { ok: false, error: 'La organización no tiene perfil.' } } }];
return [{ json: { respuesta: { ok: true, texto: md, validacion: md !== null ? PIMS_PERFIL.validar(md) : null,
  terceros: md !== null ? PIMS_PERFIL.terceros(md) : [], borrador_invalido: inval, ultima_generacion: ultima } } }];
"""),
        "jurisdicciones": (r"""
return [{ json: { clave: 'j', ruta: R('pims-dpa-auditor', 'jurisdicciones', '*', 'parametros_legales.json') } }];
""", r"""
const L = $input.all().map((x) => x.json);
const lista = todosDe(L, 'j').map((a) => { try { const p = JSON.parse(a.texto);
  return { id: a.ruta_real.split('/').slice(-2)[0], pais: p.pais, estado: p.estado, version: p.version, ley: p.ley_aplicable_corta || p.ley_aplicable,
    usable: ['Borrador', 'En uso', 'Verificada'].includes(p.estado) }; } catch (e) { return null; } }).filter(Boolean);
return [{ json: { respuesta: { ok: true, jurisdicciones: lista } } }];
"""),
    }
    y = 0
    # Lista de documentos institucionales: lee solo los metadatos (sin extraer el texto de los PDF).
    f.webhook("Webhook documentos", (0, -260), "GET", "pims/documentos")
    f.code("Ruta documentos", (220, -260), r"""
const org = String(($('Webhook documentos').first().json.query || {}).organizacion || '');
return [{ json: { ruta: R('organizaciones', idValido(org) ? org : '__no_existe__', 'documentos', '*.{pdf,md,txt,PDF,MD,TXT}') } }];
""")
    f.nodo("Listar documentos", "n8n-nodes-base.readWriteFile", 1.1, {"operation": "read", "fileSelector": "={{ $json.ruta }}",
                                                                      "options": {}}, (440, -260),
           onError="continueRegularOutput", alwaysOutputData=True)
    f.code("Respuesta (documentos)", (660, -260), r"""
const docs = $input.all().filter((x) => x.binary && x.binary.data).map((x) => ({ nombre: x.binary.data.fileName,
  tam: x.binary.data.fileSize || '', extension: x.binary.data.fileExtension || '' })).sort((a, b) => a.nombre.localeCompare(b.nombre));
return [{ json: { respuesta: { ok: true, documentos: docs } } }];
""")
    f.responder("Responder (documentos)", (880, -260))
    f.cadena("Webhook documentos", "Ruta documentos", "Listar documentos", "Respuesta (documentos)", "Responder (documentos)")
    for ruta, (pedir, responder) in rutas.items():
        wh = f.webhook(f"Webhook {ruta}", (0, y), "GET", f"pims/{ruta}")
        p = f.code(f"Pedir ({ruta})", (220, y), pedir)
        l = f.llamar(f"Leer ({ruta})", (440, y), "leer")
        c = f.code(f"Respuesta ({ruta})", (660, y), responder, "perfil")
        r = f.responder(f"Responder ({ruta})", (880, y))
        f.cadena(wh, p, l, c, r)
        y += 220
    return f


# --------------------------------------------------------------------------- Administración (POST)
def flujo_admin():
    f = Flujo("admin", "PIMS · Administración (configuración, organizaciones, documentos)",
              "POST /webhook/pims/config · POST /webhook/pims/organizacion · POST /webhook/pims/documento")
    # --- config del modelo
    f.webhook("Webhook config", (0, 0), "POST", "pims/config")
    f.code("Pedir config actual", (220, 0), r"""
return [{ json: { clave: 'config', ruta: R('datos', 'config_modelo.json') } }];
""")
    f.llamar("Leer config", (440, 0), "leer")
    f.code("Fusionar config", (660, 0), r"""
const b = $('Webhook config').first().json.body || {};
let actual = {}; try { actual = jsonDe($input.all().map((x) => x.json), 'config') || {}; } catch (e) { actual = {}; }
const PROV = ['ollama', 'anthropic', 'openai', 'claude_code'];
const n = Object.assign({}, actual);
const err = [];
if (b.proveedor !== undefined) { if (PROV.includes(b.proveedor)) n.proveedor = b.proveedor; else err.push(`proveedor debe ser uno de ${PROV.join(', ')}`); }
if (b.modelo !== undefined) { if (/^[A-Za-z0-9._:\-\/\[\]]{1,120}$/.test(String(b.modelo))) n.modelo = String(b.modelo); else err.push('modelo no válido'); }
for (const k of ['url_ollama', 'url_openai', 'url_anthropic']) if (b[k] !== undefined) { if (/^https?:\/\/[^\s"']{3,300}$/.test(String(b[k]))) n[k] = String(b[k]); else err.push(`${k} debe ser una URL http(s)`); }
for (const [k, min, max] of [['num_ctx', 2048, 1048576], ['max_tokens', 256, 200000], ['timeout_s', 60, 7200]]) {
  if (b[k] !== undefined) { const v = Number(b[k]); if (Number.isInteger(v) && v >= min && v <= max) n[k] = v; else err.push(`${k} debe ser entero entre ${min} y ${max}`); } }
if (b.temperatura !== undefined) { const v = Number(b.temperatura); if (v >= 0 && v <= 1) n.temperatura = v; else err.push('temperatura entre 0 y 1'); }
if (b.formato_correccion !== undefined) { if (['json', 'esquema', 'ninguno'].includes(b.formato_correccion)) n.formato_correccion = b.formato_correccion; else err.push('formato_correccion debe ser json, esquema o ninguno'); }
if (b.claude_bin !== undefined) { if (/^[A-Za-z0-9._:\\\/ \-]{1,300}$/.test(String(b.claude_bin))) n.claude_bin = String(b.claude_bin); else err.push('claude_bin no válido'); }
if (typeof b.api_key === 'string' && b.api_key && !b.api_key.startsWith('****')) n.api_key = b.api_key.trim();
if (b.api_key === '') n.api_key = '';
if (err.length) return [{ json: { ok: false, codigo: 400, respuesta: { ok: false, errores: err } } }];
n.actualizado = ahora();
const visible = Object.assign({}, n); if (visible.api_key) visible.api_key = '********' + visible.api_key.slice(-4);
return [{ json: { ok: true, ruta: R('datos', 'config_modelo.json'), texto: JSON.stringify(n, null, 2), visible } }];
""")
    f.si("¿Config válida?", (880, 0), "={{ $json.ok }}")
    f.llamar("Guardar config", (1100, -100), "guardar")
    f.code("Respuesta config", (1320, -100), r"""
const g = $input.first().json;
if (!g.ok) return [{ json: { codigo: 500, respuesta: { ok: false, error: g.error } } }];
return [{ json: { codigo: 200, respuesta: { ok: true, modelo: $('Fusionar config').first().json.visible } } }];
""")
    f.responder("Responder (config)", (1540, 0))
    f.cadena("Webhook config", "Pedir config actual", "Leer config", "Fusionar config", "¿Config válida?")
    f.unir("¿Config válida?", "Guardar config", 0)
    f.unir("¿Config válida?", "Responder (config)", 1)
    f.cadena("Guardar config", "Respuesta config", "Responder (config)")

    # --- crear organización
    f.webhook("Webhook organizacion", (0, 450), "POST", "pims/organizacion")
    f.code("Pedir plantilla", (220, 450), r"""
const b = $('Webhook organizacion').first().json.body || {};
const id = idValido(b.id) ? b.id : '__invalido__';
return [{ json: { clave: 'plantilla', ruta: R('organizaciones', '_plantilla', 'config_organizacion.json') } },
        { json: { clave: 'existente', ruta: R('organizaciones', id, 'config_organizacion.json') } },
        { json: { clave: 'jur', ruta: R('pims-dpa-auditor', 'jurisdicciones', '*', 'parametros_legales.json') } }];
""")
    f.llamar("Leer plantilla", (440, 450), "leer")
    f.code("Preparar organización", (660, 450), r"""
const b = $('Webhook organizacion').first().json.body || {};
const L = $input.all().map((x) => x.json);
const id = String(b.id || ''), nombre = String(b.nombre || '').trim(), jur = String(b.jurisdiccion || 'peru');
const errorDe = (codigo, error) => [{ json: { ok: false, codigo, respuesta: { ok: false, error } } }];
if (!idValido(id) || id.startsWith('_')) return errorDe(400, "'id' debe tener 2-60 caracteres: minúsculas, números y _ (sin empezar por _).");
if (!nombre) return errorDe(400, "Falta 'nombre'.");
if (textoDe(L, 'existente') !== null) return errorDe(409, `La organización '${id}' ya existe.`);
const js = todosDe(L, 'jur').map((a) => { try { return Object.assign(JSON.parse(a.texto), { _id: a.ruta_real.split('/').slice(-2)[0] }); } catch (e) { return null; } }).filter(Boolean);
const j = js.find((x) => x._id === jur);
if (!j || !['Borrador', 'En uso', 'Verificada'].includes(j.estado)) return errorDe(400, `Jurisdicción '${jur}' inexistente o no utilizable. Disponibles: ${js.filter((x) => x.estado !== 'Plantilla').map((x) => x._id).join(', ')}`);
const cfg = jsonDe(L, 'plantilla');
if (!cfg) return errorDe(500, 'Falta organizaciones/_plantilla/config_organizacion.json');
Object.assign(cfg, { _descripcion: `Configuración de ${nombre}. Creada desde la página el ${hoy()}; revisar la política interna con el DPO.`,
  id_organizacion: id, organizacion: nombre, jurisdiccion: jur, pais_responsable: j.pais || cfg.pais_responsable,
  aprobadores_cargos: { DPO: String(b.cargo_dpo || 'DPO').slice(0, 150), Legal: String(b.cargo_legal || 'Área legal').slice(0, 150) } });
return [{ json: { ok: true, organizacion: id, config: cfg } }];
""")
    f.si("¿Organización válida?", (880, 450), "={{ $json.ok }}")
    f.llamar("Crear carpetas", (1100, 350), "carpetas", onError="continueRegularOutput")
    f.code("Config nueva", (1320, 350), r"""
const r = $input.first().json;
const p = $('Preparar organización').first().json;
if (!r.ok) return [{ json: { ok: false, codigo: 501, respuesta: { ok: false, error: 'No se pudieron crear las carpetas. ' +
  'Habilita Execute Command (NODES_EXCLUDE="[]") o crea a mano organizaciones/' + p.organizacion + '/ copiando _plantilla/. Detalle: ' + (r.error || JSON.stringify(r)) } } }];
return [{ json: { ok: true, ruta: R('organizaciones', p.organizacion, 'config_organizacion.json'), texto: JSON.stringify(p.config, null, 2) } }];
""")
    f.si("¿Carpetas creadas?", (1540, 350), "={{ $json.ok }}")
    f.llamar("Guardar config org", (1760, 250), "guardar")
    f.code("Respuesta organización", (1980, 250), r"""
const g = $input.first().json, p = $('Preparar organización').first().json;
if (!g.ok) return [{ json: { codigo: 500, respuesta: { ok: false, error: g.error } } }];
return [{ json: { codigo: 201, respuesta: { ok: true, organizacion: p.organizacion, config: p.config } } }];
""")
    f.responder("Responder (organización)", (2200, 450))
    f.cadena("Webhook organizacion", "Pedir plantilla", "Leer plantilla", "Preparar organización", "¿Organización válida?")
    f.unir("¿Organización válida?", "Crear carpetas", 0)
    f.unir("¿Organización válida?", "Responder (organización)", 1)
    f.cadena("Crear carpetas", "Config nueva", "¿Carpetas creadas?")
    f.unir("¿Carpetas creadas?", "Guardar config org", 0)
    f.unir("¿Carpetas creadas?", "Responder (organización)", 1)
    f.cadena("Guardar config org", "Respuesta organización", "Responder (organización)")

    # --- subir documento institucional
    f.webhook("Webhook documento", (0, 900), "POST", "pims/documento")
    f.code("Validar documento", (220, 900), r"""
const b = $('Webhook documento').first().json.body || {};
const org = String(b.organizacion || '');
let nombre = nombreSeguro(b.nombre || '');
const err = (e) => [{ json: { ok: false, codigo: 400, respuesta: { ok: false, error: e } } }];
if (!idValido(org)) return err("Falta 'organizacion' válida.");
if (typeof b.texto === 'string' && b.texto.trim()) { if (!/\.(md|txt)$/i.test(nombre)) nombre = nombre.replace(/\.[^.]*$/, '') + '.txt'; }
else if (typeof b.base64 !== 'string' || !b.base64) return err("Envía 'texto' o 'base64'.");
else if (!/\.(pdf|md|txt)$/i.test(nombre)) return err('Solo .pdf, .md o .txt (los .docx se convierten a texto en la página).');
else if (b.base64.length > 40000000) return err('Archivo demasiado grande (~30 MB máx.).');
if (!nombre || nombre.length < 3) return err("Falta 'nombre' de archivo.");
const ruta = R('organizaciones', org, 'documentos', nombre);
return [{ json: { ok: true, org, nombre, item: typeof b.texto === 'string' && b.texto.trim() ? { ruta, texto: b.texto } : { ruta, b64: b.base64 } } }];
""")
    f.si("¿Documento válido?", (440, 900), "={{ $json.ok }}")
    f.code("Archivo documento", (660, 800), r"""
return [{ json: $input.first().json.item }];
""")
    f.llamar("Guardar documento", (880, 800), "guardar")
    f.code("Respuesta documento", (1100, 800), r"""
const g = $input.first().json, v = $('Validar documento').first().json;
if (!g.ok) return [{ json: { codigo: 404, respuesta: { ok: false, error: `No se pudo guardar (¿existe la organización '${v.org}'?): ${g.error}` } } }];
return [{ json: { codigo: 201, respuesta: { ok: true, organizacion: v.org, nombre: v.nombre } } }];
""")
    f.responder("Responder (documento)", (1320, 900))
    f.cadena("Webhook documento", "Validar documento", "¿Documento válido?")
    f.unir("¿Documento válido?", "Archivo documento", 0)
    f.unir("¿Documento válido?", "Responder (documento)", 1)
    f.cadena("Archivo documento", "Guardar documento", "Respuesta documento", "Responder (documento)")
    return f


def flujo_pagina():
    f = Flujo("pagina", "PIMS · Página web",
              "GET /webhook/pims/app sirve la página (web/index.html con marked y DOMPurify incrustados). "
              "GET /webhook/pims/app/mammoth sirve el lector de .docx. n8n la entrega con su sandbox CSP: "
              "la página no tiene localStorage y llama a la API como origen 'null'.", guardar_exitos=False)
    f.webhook("Webhook página", (0, 0), "GET", "pims/app")
    f.code("Pedir página", (220, 0), r"""
return [{ json: { clave: 'html', ruta: R('web', 'index.html') } },
        { json: { clave: 'marked', ruta: R('web', 'vendor', 'marked.umd.js') } },
        { json: { clave: 'purify', ruta: R('web', 'vendor', 'purify.min.js') } }];
""")
    f.llamar("Leer página", (440, 0), "leer")
    f.code("Componer página", (660, 0), r"""
const L = $input.all().map((x) => x.json);
let html = textoDe(L, 'html');
if (html === null) html = '<!doctype html><meta charset=utf-8><h1>Falta web/index.html en el proyecto</h1>';
for (const lib of ['marked', 'purify']) {
  const js = (textoDe(L, lib) || `console.error('Falta web/vendor/${lib}')`).replace(/<\/script/gi, '<\\/script');
  html = html.replace(`<!-- VENDOR:${lib} -->`, () => `<script>\n${js}\n</script>`);
}
return [{ json: { html } }];
""")
    f.nodo("Responder página", "n8n-nodes-base.respondToWebhook", 1.5, {
        "respondWith": "text", "responseBody": "={{ $json.html }}",
        "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "text/html; charset=utf-8"},
                                                    {"name": "Cache-Control", "value": "no-store"}]}}}, (880, 0))
    f.cadena("Webhook página", "Pedir página", "Leer página", "Componer página", "Responder página")
    f.webhook("Webhook mammoth", (0, 250), "GET", "pims/app/mammoth")
    f.code("Pedir mammoth", (220, 250), r"""
return [{ json: { clave: 'js', ruta: R('web', 'vendor', 'mammoth.browser.min.js') } }];
""")
    f.llamar("Leer mammoth", (440, 250), "leer")
    f.code("Script mammoth", (660, 250), r"""
return [{ json: { js: textoDe($input.all().map((x) => x.json), 'js') || 'console.error("Falta web/vendor/mammoth.browser.min.js")' } }];
""")
    f.nodo("Responder mammoth", "n8n-nodes-base.respondToWebhook", 1.5, {
        "respondWith": "text", "responseBody": "={{ $json.js }}",
        "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "application/javascript; charset=utf-8"},
                                                    {"name": "Cache-Control", "value": "max-age=3600"}]}}}, (880, 250))
    f.cadena("Webhook mammoth", "Pedir mammoth", "Leer mammoth", "Script mammoth", "Responder mammoth")
    return f

# --------------------------------------------------------------------------- Chat
def flujo_chat():
    f = Flujo("chat", "PIMS · Chat (preguntas sobre un expediente o una organización)",
              "POST /webhook/pims/chat {ambito: expediente|organizacion, id, organizacion, pregunta, usuario?} → 202 {trabajo}; "
              "la respuesta queda en GET /webhook/pims/trabajo?id= y la conversación en datos/chats/. "
              "GET /webhook/pims/chat?ambito=&id= devuelve la conversación. El chat no modifica expedientes ni perfiles.")
    f.webhook("Webhook chat", (0, 0), "POST", "pims/chat")
    f.code("Validar petición", (220, 0), r"""
const b = $input.first().json.body || {};
const r = { ok: false, codigo: 400 };
const ambito = String(b.ambito || '');
const id = String(b.id || '');
const org = String(b.organizacion || '');
const pregunta = typeof b.pregunta === 'string' ? b.pregunta.trim() : '';
if (!['expediente', 'organizacion'].includes(ambito)) r.error = "'ambito' debe ser expediente u organizacion.";
else if (ambito === 'expediente' && !/^[A-Za-z0-9_.-]{3,140}$/.test(id)) r.error = "Falta 'id' del expediente o no es válido.";
else if (!idValido(org)) r.error = "Falta 'organizacion' o no es un id válido.";
else if (!pregunta) r.error = 'Escribe una pregunta.';
else if (pregunta.length > 4000) r.error = 'La pregunta supera 4 000 caracteres.';
if (r.error) return [{ json: Object.assign(r, { respuesta: { ok: false, error: r.error } }) }];
const t = nuevoTrabajo();
const clave = ambito === 'expediente' ? `exp_${nombreSeguro(id)}` : `org_${org}`;
return [{ json: { ok: true, codigo: 202, trabajo: t, inicio: ahora(), ambito, id: ambito === 'expediente' ? id : org, organizacion: org,
  pregunta, usuario: String(b.usuario || '').slice(0, 120), clave,
  respuesta: { ok: true, trabajo: t, consultar: `/webhook/pims/trabajo?id=${t}` } } }];
""")
    f.si("¿Petición válida?", (440, 0), "={{ $json.ok }}")
    f.responder("Responder error", (660, 200))
    f.code("Registrar trabajo", (660, -100), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'chat', ambito: v.ambito, id_contexto: v.id, organizacion: v.organizacion,
  estado: 'en_cola', mensaje: 'Pregunta recibida', inicio: v.inicio })];
""")
    f.llamar("Guardar trabajo", (880, -100), "guardar")
    f.code("Respuesta 202", (1100, -100), r"""
return [{ json: { codigo: 202, respuesta: $('Validar petición').first().json.respuesta } }];
""")
    f.responder("Responder aceptado", (1320, -100))
    f.code("Pedir archivos", (1540, -100), r"""
const v = $('Validar petición').first().json;
const p = (clave, ...r) => ({ json: { clave, ruta: R(...r) } });
const items = [
  p('config', 'organizaciones', v.organizacion, 'config_organizacion.json'),
  p('perfil', 'organizaciones', v.organizacion, 'perfil_organizacion.md'),
  p('modelo', 'datos', 'config_modelo.json'),
  p('chat', 'datos', 'chats', `${v.clave}.json`),
];
if (v.ambito === 'expediente') items.push(p('registro', 'datos', 'registro', `${v.id}.json`), p('informe', 'datos', 'registro', `${v.id}.md`),
  p('contrato', 'datos', 'registro', `${v.id}.contrato.txt`));
else items.push(p('registros', 'datos', 'registro', '*.json'));
return items;
""")
    f.llamar("Leer archivos", (1760, -100), "leer")
    f.code("Construir pregunta", (1980, -100), r"""
const v = $('Validar petición').first().json;
const L = $input.all().map((x) => x.json);
const fallo = (msg) => [{ json: { ok: false, error: msg } }];
try {
  const config = jsonDe(L, 'config');
  if (!config) return fallo(`La organización '${v.organizacion}' no existe.`);
  let cfgModelo = {}; try { cfgModelo = jsonDe(L, 'modelo') || {}; } catch (e) { cfgModelo = {}; }
  let conv = { ambito: v.ambito, id: v.id, organizacion: v.organizacion, mensajes: [] };
  try { conv = jsonDe(L, 'chat') || conv; } catch (e) { /* conversación ilegible: se empieza de nuevo */ }
  const cx = { ambito: v.ambito, organizacion: { id: v.organizacion, nombre: config.organizacion || v.organizacion, config },
    perfil: textoDe(L, 'perfil') };
  if (v.ambito === 'expediente') {
    const reg = jsonDe(L, 'registro');
    if (!reg) return fallo(`No existe el expediente ${v.id}.`);
    const orgReg = (reg.organizacion || {}).id || (reg._registro || {}).organizacion;
    if (orgReg && orgReg !== v.organizacion) return fallo(`El expediente ${v.id} es de la organización '${orgReg}', no de '${v.organizacion}'.`);
    Object.assign(cx, { registro: reg, informe: textoDe(L, 'informe'), contrato: textoDe(L, 'contrato') });
  } else {
    cx.registros = todosDe(L, 'registros').map((a) => { try { return JSON.parse(a.texto); } catch (e) { return null; } })
      .filter((r) => r && ((r.organizacion || {}).id || (r._registro || {}).organizacion) === v.organizacion)
      .sort((a, b) => String((b._registro || {}).creado || '').localeCompare(String((a._registro || {}).creado || '')));
  }
  const q = PIMS_PROMPTS.chat({ contexto: cx, historial: conv.mensajes, pregunta: v.pregunta, cfgModelo });
  return [{ json: { ok: true, system: q.system, mensaje: q.mensaje, etiqueta: 'chat', recortes: q.recortes, conv } }];
} catch (e) { return fallo(`Error al preparar la pregunta: ${e.message}`); }
""", "prompts")
    f.si("¿Contexto listo?", (2200, -100), "={{ $json.ok }}")
    f.code("Estado: pensando", (2420, -200), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'chat', ambito: v.ambito, id_contexto: v.id, organizacion: v.organizacion,
  estado: 'pensando', mensaje: 'El modelo está redactando la respuesta', inicio: v.inicio })];
""")
    f.llamar("Guardar estado", (2640, -200), "guardar")
    f.code("Petición al modelo", (2860, -200), r"""
const c = $('Construir pregunta').first().json;
return [{ json: { system: c.system, mensaje: c.mensaje, etiqueta: 'chat' } }];
""")
    f.llamar("Modelo", (3080, -200), "modelo")
    f.code("Guardar respuesta", (3300, -200), r"""
const r = $input.first().json;
const v = $('Validar petición').first().json;
const c = $('Construir pregunta').first().json;
const base = { tipo: 'chat', ambito: v.ambito, id_contexto: v.id, organizacion: v.organizacion, inicio: v.inicio, fin: ahora() };
if (!r.ok) return [archivoTrabajo(v.trabajo, Object.assign(base, { estado: 'error', mensaje: r.error }))];
const texto = String(r.texto || '').trim();
const conv = c.conv;
conv.mensajes = (conv.mensajes || []).concat([
  { rol: 'usuario', texto: v.pregunta, usuario: v.usuario || null, fecha: v.inicio },
  { rol: 'asistente', texto, fecha: ahora(), modelo: r.modelo, proveedor: r.proveedor, truncado: !!r.truncado,
    contexto_recortado: c.recortes.length ? c.recortes : undefined },
]).slice(-200);
conv.actualizado = ahora();
return [
  { json: { ruta: R('datos', 'chats', `${v.clave}.json`), texto: JSON.stringify(conv, null, 2) } },
  archivoTrabajo(v.trabajo, Object.assign(base, { estado: 'terminado', mensaje: 'Respuesta lista', respuesta_chat: texto,
    modelo: r.modelo, proveedor: r.proveedor, contexto_recortado: c.recortes })),
];
""")
    f.code("Error de contexto", (2420, 50), r"""
const v = $('Validar petición').first().json;
return [archivoTrabajo(v.trabajo, { tipo: 'chat', ambito: v.ambito, id_contexto: v.id, organizacion: v.organizacion,
  estado: 'error', mensaje: $input.first().json.error, inicio: v.inicio, fin: ahora() })];
""")
    f.llamar("Guardar resultado", (3520, -100), "guardar")
    f.cadena("Webhook chat", "Validar petición", "¿Petición válida?")
    f.unir("¿Petición válida?", "Registrar trabajo", 0)
    f.unir("¿Petición válida?", "Responder error", 1)
    f.cadena("Registrar trabajo", "Guardar trabajo", "Respuesta 202", "Responder aceptado", "Pedir archivos",
             "Leer archivos", "Construir pregunta", "¿Contexto listo?")
    f.unir("¿Contexto listo?", "Estado: pensando", 0)
    f.unir("¿Contexto listo?", "Error de contexto", 1)
    f.cadena("Estado: pensando", "Guardar estado", "Petición al modelo", "Modelo", "Guardar respuesta", "Guardar resultado")
    f.unir("Error de contexto", "Guardar resultado")

    # ---- GET: conversación guardada
    f.webhook("Webhook conversación", (0, 500), "GET", "pims/chat")
    f.code("Pedir conversación", (220, 500), r"""
const q = $('Webhook conversación').first().json.query || {};
const ambito = String(q.ambito || ''), id = String(q.id || '');
const valido = (ambito === 'expediente' && /^[A-Za-z0-9_.-]{3,140}$/.test(id)) || (ambito === 'organizacion' && idValido(id));
const clave = ambito === 'expediente' ? `exp_${nombreSeguro(id)}` : `org_${id}`;
return [{ json: { clave: 'chat', ruta: valido ? R('datos', 'chats', `${clave}.json`) : R('datos', 'chats', '__no_valido__'), valido } }];
""")
    f.llamar("Leer conversación", (440, 500), "leer")
    f.code("Conversación", (660, 500), r"""
const ok = $('Pedir conversación').first().json.valido;
if (!ok) return [{ json: { codigo: 400, respuesta: { ok: false, error: "Indica 'ambito' (expediente u organizacion) e 'id'." } } }];
const L = $input.all().map((x) => x.json);
let conv = null; try { conv = jsonDe(L, 'chat'); } catch (e) { conv = null; }
return [{ json: { codigo: 200, respuesta: { ok: true, mensajes: conv ? conv.mensajes || [] : [] } } }];
""")
    f.responder("Responder conversación", (880, 500))
    f.cadena("Webhook conversación", "Pedir conversación", "Leer conversación", "Conversación", "Responder conversación")
    return f


FLUJOS = [flujo_leer, flujo_guardar, flujo_claude, flujo_carpetas, flujo_modelo, flujo_bd, flujo_auditar,
          flujo_perfilar, flujo_aprobar, flujo_renovar, flujo_consultas, flujo_admin, flujo_pagina, flujo_chat]
ORDEN_ARCHIVO = {"leer": "01", "guardar": "02", "claude": "03", "carpetas": "04", "modelo": "05", "bd": "06", "auditar": "10",
                 "perfilar": "11", "aprobar": "12", "renovar": "13", "consultas": "20", "admin": "21", "pagina": "30", "chat": "14"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=str(AQUI.parent), help="Ruta absoluta del proyecto (carpeta que contiene pims-dpa-auditor/)")
    ap.add_argument("--salida", default=str(AQUI / "flujos_listos"))
    ap.add_argument("--puerto", type=int, default=5678, help="Puerto de n8n (para la lista de orígenes permitidos)")
    a = ap.parse_args()
    raiz = str(Path(a.raiz).resolve()).replace("\\", "/").rstrip("/")
    if not (Path(raiz) / "pims-dpa-auditor" / "SKILL.md").is_file():
        sys.exit(f"La raíz indicada no contiene pims-dpa-auditor/SKILL.md: {raiz}")
    if re.search(r"[*?{}!]", raiz):
        sys.exit(f"La ruta del proyecto contiene caracteres especiales de patrones (* ? {{ }} !): muévelo a otra carpeta. {raiz}")
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    for viejo in salida.glob("*.json"):
        viejo.unlink()
    clave_de = {v: k for k, v in IDS.items()}
    for fn in FLUJOS:
        flujo = fn()
        nombre = f"{ORDEN_ARCHIVO[clave_de[flujo.id]]}_{clave_de[flujo.id]}.json"
        origenes = f"null,http://localhost:{a.puerto},http://127.0.0.1:{a.puerto}"
        (salida / nombre).write_text(flujo.json(raiz, origenes), encoding="utf-8")
        print(f"  {nombre:<18} {len(flujo.nodos):>3} nodos  {flujo.nombre}")
    print(f"\nRAIZ = {raiz}\nFlujos escritos en {salida}\nPágina: http://localhost:{a.puerto}/webhook/pims/app")


if __name__ == "__main__":
    main()
