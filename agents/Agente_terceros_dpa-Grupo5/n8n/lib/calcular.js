/* =============================================================================
   calcular.js — Port fiel de pims-dpa-auditor/scripts/calcular_resultado.py (v2.0)
   -----------------------------------------------------------------------------
   Se embebe en los nodos Code de n8n (construir_flujos.py lo inserta).
   Sin dependencias: ni require() ni módulos externos, para que funcione con los
   task runners de n8n 2.x sin variables de entorno adicionales.

   Equivalencia con Python verificada por n8n/pruebas/probar_lib.js:
   mismos resultados en los 5 registros de referencia y en miles de casos
   aleatorios. Detalle crítico: Python redondea con "half to even"
   (round(22.5) == 22); JavaScript con Math.round daría 23. pyRound() lo replica.
   ========================================================================== */

const PIMS_CALC = (() => {
  'use strict';

  const VERSION_LIB = '2.0';
  const CRITICOS = new Set(['A.2.2.2', 'A.2.2.3', 'A.2.4.3', 'A.2.5.3', 'A.2.5.7',
    'A.2.5.8', 'A.2.5.9', 'A.3.10', 'A.3.12']);
  const PROPIOS_AGENTE_7 = new Set(['A.1.2.7', 'A.2.5.7', 'A.2.5.8', 'A.2.5.9', 'A.3.10']);
  const FACTOR = { 'Cumple': 1.0, 'Parcial': 0.5, 'Sin evidencia': 0.25, 'No cumple': 0.0 };
  const SEVERIDAD = {
    'No cumple|Alto': 'Crítica', 'No cumple|Medio': 'Alta', 'No cumple|Bajo': 'Media',
    'Parcial|Alto': 'Alta', 'Parcial|Medio': 'Media', 'Parcial|Bajo': 'Baja',
    'Sin evidencia|Alto': 'Alta', 'Sin evidencia|Medio': 'Media', 'Sin evidencia|Bajo': 'Baja',
  };
  const ORDEN_DICTAMEN = ['Recomendable', 'Recomendable con condiciones', 'No recomendable sin enmiendas'];
  const ESTADOS_JURISDICCION_USABLES = new Set(['Borrador', 'En uso', 'Verificada']);

  /* --- Redondeo idéntico a round() de Python (half to even) --------------- */
  function pyRound(x, nd = 0) {
    const m = Math.pow(10, nd);
    const y = x * m;
    const f = Math.floor(y);
    if (y - f === 0.5) {                       // empate exacto: al par
      return (f % 2 === 0 ? f : f + 1) / m;
    }
    return nd === 0 ? Math.round(y) : Number(x.toFixed(nd));
  }

  /* --- Fechas (AAAA-MM-DD, sin zona horaria) ------------------------------ */
  function parseFecha(v) {
    if (!v) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
    if (!m) throw new Error(`Fecha inválida: ${v}`);
    return Date.UTC(+m[1], +m[2] - 1, +m[3]);
  }
  const DIA = 86400000;
  function iso(ms) { return new Date(ms).toISOString().slice(0, 10); }

  /* Dimensiones del desglose: las secciones del Anexo A de ISO/IEC 27701:2025 (Tablas A.2 y A.3),
     en el orden de la norma. Títulos parafraseados en español. */
  const DIMENSIONES = [
    ['A.2.2', 'Condiciones de recolección y tratamiento'],
    ['A.2.3', 'Obligaciones con los titulares'],
    ['A.2.4', 'Privacidad desde el diseño y por defecto'],
    ['A.2.5', 'Compartición, transferencia y comunicación'],
    ['A.3', 'Consideraciones de seguridad'],
  ];
  function dimension(control) {
    for (const [sec, nombre] of DIMENSIONES) if (control.startsWith(sec + '.')) return nombre;
    return 'Marco';
  }

  function alertasRenovacion(contrato, refIso, dias) {
    const alertas = [];
    const ref = parseFecha(refIso);
    const fin = parseFecha(contrato.fecha_vigencia_fin);
    const renov = contrato.renovacion_automatica;
    const preaviso = contrato.preaviso_terminacion_dias;
    const ventana = ref + dias * DIA;
    const nueva = (prioridad, texto) => alertas.push({
      prioridad, tipo: 'Renovación', descripcion: texto,
      controles_relacionados: ['A.1.2.7'], origen: 'script',
    });

    if (fin === null) {
      nueva('Media', 'Sin fecha de fin de vigencia ni mecanismo de revisión periódica definido.');
      return alertas;
    }
    if (fin < ref && !renov) {
      nueva('Alta', `Contrato vencido el ${iso(fin)} sin renovación automática.`);
    } else if (fin <= ventana) {
      nueva('Media', `Fin de vigencia el ${iso(fin)}, dentro de los próximos ${dias} días.`);
    }
    if (renov && preaviso !== null && preaviso !== undefined) {
      const limite = fin - preaviso * DIA;
      if (ref <= limite && limite <= ventana) {
        nueva('Media', `Renovación automática: el plazo para preavisar termina el ${iso(limite)}.`);
      }
    }
    return alertas;
  }

  function getOr(obj, clave, defecto) {           // dict.get(clave, defecto) de Python
    return obj && Object.prototype.hasOwnProperty.call(obj, clave) ? obj[clave] : defecto;
  }

  /* --- Núcleo determinista (idéntico a calcular() de Python) -------------- */
  function calcular(res, cfg, refIso) {
    const riesgo = res.nivel_riesgo_pii;

    for (const c of res.controles) {
      c.ambito = PROPIOS_AGENTE_7.has(c.control) ? 'Propio Agente 7' : 'Insumo SoA (Agente 3)';
      c.severidad = SEVERIDAD[`${c.estado}|${riesgo}`] || 'Ninguna';
    }

    res.alertas = res.alertas.filter((a) => getOr(a, 'origen', undefined) !== 'script');
    res.alertas = res.alertas.concat(alertasRenovacion(res.contrato, refIso, getOr(cfg, 'dias_alerta_renovacion', 60)));

    const estados = res.controles.map((c) => c.estado);
    const cuenta = (e) => estados.filter((x) => x === e).length;
    const altas = res.alertas.filter((a) => a.prioridad === 'Alta').length;
    res.resumen = {
      cumple: cuenta('Cumple'), parcial: cuenta('Parcial'), no_cumple: cuenta('No cumple'),
      sin_evidencia: cuenta('Sin evidencia'), no_aplica: cuenta('No aplica'), alertas_altas: altas,
    };

    const baseDe = (controles) => {
      let num = 0, den = 0;
      for (const c of controles) {
        if (c.estado === 'No aplica') continue;
        const peso = CRITICOS.has(c.control) ? 3 : 1;
        if (!(c.estado in FACTOR)) throw new Error(`Estado desconocido: ${c.estado}`);
        num += peso * FACTOR[c.estado];
        den += peso;
      }
      return den ? pyRound(num / den * 100, 1) : null;
    };

    const base = baseDe(res.controles);
    const penal = Math.min(5 * altas, 20);
    const valor = Math.max(0, pyRound((base || 0) - penal));
    const banda = valor >= 80 ? 'Riesgo bajo' : valor >= 50 ? 'Riesgo medio' : 'Riesgo alto';
    const porDimension = {};
    for (const [, nombre] of DIMENSIONES) porDimension[nombre] = baseDe(res.controles.filter((c) => dimension(c.control) === nombre));
    res.puntaje_proveedor = { valor, banda, base, penalizacion: penal, por_dimension: porDimension };

    const sevs = new Set(res.controles.map((c) => c.severidad));
    let reglaA;
    if (altas || sevs.has('Crítica')) reglaA = 'No recomendable sin enmiendas';
    else if (sevs.has('Alta') || sevs.has('Media')) reglaA = 'Recomendable con condiciones';
    else reglaA = 'Recomendable';
    const reglaB = valor >= 80 ? 'Recomendable' : valor >= 50 ? 'Recomendable con condiciones' : 'No recomendable sin enmiendas';
    res.dictamen = ORDEN_DICTAMEN.indexOf(reglaA) >= ORDEN_DICTAMEN.indexOf(reglaB) ? reglaA : reglaB;

    res.aprobacion = {
      requiere_decision_dpo: true, requiere_aprobacion_legal: true,
      secuencia: getOr(cfg, 'aprobadores', ['DPO', 'Legal']),
      estado: getOr(getOr(res, 'aprobacion', {}), 'estado', 'Pendiente DPO'),
    };
    res.contrato.estado_dpa = getOr(res.contrato, 'estado_dpa', null) || 'Pendiente DPO';
    const traz = res.trazabilidad = res.trazabilidad || {};
    traz.version_config = getOr(cfg, 'version_config', 'sin versión');
    traz.calculo = 'script';
    const params = {};
    for (const [k, v] of Object.entries(cfg)) if (!k.startsWith('_') && k !== 'paises_aprobados') params[k] = v;
    params.n_paises_aprobados = (getOr(cfg, 'paises_aprobados', []) || []).length;
    traz.parametros_aplicados = params;
    traz.fecha_referencia = refIso;
    return res;
  }

  /* --- Contexto v2.0 ------------------------------------------------------- */
  function cargarJurisdiccion(cfg, params, advertencias) {
    let jid = cfg.jurisdiccion;
    if (!jid) {
      jid = 'peru';
      advertencias.push("La configuración no indica 'jurisdiccion'; se asumió 'peru' (comportamiento de la v1.1).");
    }
    if (!params) throw new Error(`No se encontró la jurisdicción '${jid}'.`);
    const estado = params.estado;
    if (!ESTADOS_JURISDICCION_USABLES.has(estado)) {
      throw new Error(`La jurisdicción '${jid}' está en estado ${JSON.stringify(estado)} y no se puede usar. ` +
        "Complétala y márcala como 'Borrador' o superior (ver jurisdicciones/LEEME.md).");
    }
    if (estado === 'Borrador') advertencias.push(`Jurisdicción '${jid}' en estado Borrador: pendiente de verificación legal.`);
    return params;
  }

  function leerPerfil(texto, ruta, advertencias, bytes, sha256) {
    const campo = (nombre) => {
      const m = new RegExp(`^\\|\\s*${nombre}\\s*\\|\\s*(.+?)\\s*\\|\\s*$`, 'mi').exec(texto);
      return m ? m[1].replace(/[*`]/g, '').trim() : null;
    };
    const estado = campo('Estado');
    if (!estado || !estado.toLowerCase().startsWith('validado')) {
      advertencias.push(`Perfil de la organización sin validar por el DPO (estado: ${estado || 'no indicado'}).`);
    }
    // El hash se calcula sobre los bytes del archivo (como Python); si no se entregan, sobre el texto UTF-8.
    return { ruta, version: campo('Versión'), estado, hash_sha256: sha256 || sha256Hex(bytes || texto) };
  }

  function coherenciaPolitica(cfg, jur, advertencias) {
    const interno = cfg.plazo_max_aviso_incidente_horas;
    const legal = (jur.incidentes || {}).plazo_notificacion_autoridad_horas;
    if (typeof interno === 'number' && typeof legal === 'number' && interno >= legal) {
      advertencias.push(`Política interna incoherente con la ley: el plazo máximo de aviso del encargado ` +
        `(${interno} h) no es menor que el plazo legal de notificación a la autoridad (${legal} h).`);
    }
  }

  function aplicarContexto(res, cfg, jur, perfil, advertencias) {
    res.organizacion = {
      id: getOr(cfg, 'id_organizacion', 'sin id'),
      nombre: getOr(cfg, 'organizacion', 'Organización usuaria'),
      perfil,
    };
    res.jurisdiccion = {};
    for (const k of ['id', 'pais', 'ley_aplicable', 'autoridad', 'version', 'estado']) res.jurisdiccion[k] = jur[k] ?? null;
    const traz = res.trazabilidad;
    traz.version_jurisdiccion = `${jur.id} ${jur.version}`;
    traz.version_perfil = perfil ? perfil.version : null;
    const previas = (traz.advertencias || []).filter((a) => !advertencias.includes(a));
    traz.advertencias = previas.concat(advertencias);
    return res;
  }

  /* --- Validador mínimo de JSON Schema (mismo subconjunto que Python) ----- */
  function tipoDe(v) {
    if (v === null) return 'null';
    if (Array.isArray(v)) return 'array';
    if (typeof v === 'boolean') return 'boolean';
    if (typeof v === 'number') return Number.isInteger(v) ? 'integer' : 'number';
    if (typeof v === 'string') return 'string';
    return 'object';
  }
  function validar(dato, esquema, ruta = '$') {
    let errores = [];
    if (esquema.type) {
      const tipos = Array.isArray(esquema.type) ? esquema.type : [esquema.type];
      const t = tipoDe(dato);
      const ok = tipos.some((x) => x === t || (x === 'number' && t === 'integer'));
      if (!ok) return [`${ruta}: tipo ${t} no es ${JSON.stringify(tipos)}`];
    }
    if ('const' in esquema && JSON.stringify(dato) !== JSON.stringify(esquema.const)) {
      errores.push(`${ruta}: debe ser ${JSON.stringify(esquema.const)}`);
    }
    if (esquema.enum && !esquema.enum.some((e) => JSON.stringify(e) === JSON.stringify(dato))) {
      errores.push(`${ruta}: ${JSON.stringify(dato)} no está en ${JSON.stringify(esquema.enum)}`);
    }
    if (typeof dato === 'string' && esquema.pattern && !new RegExp(esquema.pattern).test(dato)) {
      errores.push(`${ruta}: ${JSON.stringify(dato)} no cumple el patrón`);
    }
    if (typeof dato === 'number') {
      if ('minimum' in esquema && dato < esquema.minimum) errores.push(`${ruta}: menor que ${esquema.minimum}`);
      if ('maximum' in esquema && dato > esquema.maximum) errores.push(`${ruta}: mayor que ${esquema.maximum}`);
    }
    if (dato && typeof dato === 'object' && !Array.isArray(dato)) {
      for (const req of esquema.required || []) if (!(req in dato)) errores.push(`${ruta}: falta '${req}'`);
      for (const [k, sub] of Object.entries(esquema.properties || {})) {
        if (k in dato) errores = errores.concat(validar(dato[k], sub, `${ruta}.${k}`));
      }
    }
    if (Array.isArray(dato)) {
      if (dato.length < (esquema.minItems || 0)) errores.push(`${ruta}: mínimo ${esquema.minItems} elementos`);
      if (esquema.items) dato.forEach((el, i) => { errores = errores.concat(validar(el, esquema.items, `${ruta}[${i}]`)); });
    }
    return errores;
  }

  const CALCULADOS = new Set(['resumen', 'puntaje_proveedor', 'dictamen', 'aprobacion', 'organizacion', 'jurisdiccion']);
  function validarEntrada(res, esquema) {
    const previo = Object.assign({}, esquema, {
      required: esquema.required.filter((k) => !CALCULADOS.has(k)),
      properties: Object.fromEntries(Object.entries(esquema.properties).filter(([k]) => !CALCULADOS.has(k))),
    });
    return validar(res, previo).filter((e) => !e.includes('severidad') && !e.includes('ambito'));
  }

  /* --- SHA-256 en JavaScript puro (texto UTF-8 o bytes) -------------------- */
  function sha256Hex(entrada) {
    const bytes = typeof entrada === 'string' ? new TextEncoder().encode(entrada) : Uint8Array.from(entrada);
    const K = new Uint32Array([
      0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]);
    const H = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
    const len = bytes.length;
    const total = Math.ceil((len + 9) / 64) * 64;
    const msg = new Uint8Array(total);
    msg.set(bytes);
    msg[len] = 0x80;
    const bits = len * 8;
    const dv = new DataView(msg.buffer);
    dv.setUint32(total - 8, Math.floor(bits / 0x100000000));
    dv.setUint32(total - 4, bits >>> 0);
    const W = new Uint32Array(64);
    const rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let off = 0; off < total; off += 64) {
      for (let t = 0; t < 16; t++) W[t] = dv.getUint32(off + t * 4);
      for (let t = 16; t < 64; t++) {
        const s0 = rotr(W[t - 15], 7) ^ rotr(W[t - 15], 18) ^ (W[t - 15] >>> 3);
        const s1 = rotr(W[t - 2], 17) ^ rotr(W[t - 2], 19) ^ (W[t - 2] >>> 10);
        W[t] = (W[t - 16] + s0 + W[t - 7] + s1) >>> 0;
      }
      let [a, b, c, d, e, f, g, h] = H;
      for (let t = 0; t < 64; t++) {
        const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
        const ch = (e & f) ^ (~e & g);
        const t1 = (h + S1 + ch + K[t] + W[t]) >>> 0;
        const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const t2 = (S0 + maj) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
    return Array.from(H, (x) => x.toString(16).padStart(8, '0')).join('');
  }

  /* --- Ejecución completa, equivalente a main() del script ---------------- */
  /**
   * @param {object} p
   *   resultado   JSON del modelo (se clona; no se modifica el original)
   *   config      config_organizacion.json
   *   jurisdiccion parametros_legales.json de la jurisdicción (o null si no existe)
   *   esquema     esquema_salida.json
   *   perfil      {texto, ruta, bytes?, sha256?} o null
   *   hashDocumento SHA-256 ya calculado del contrato (opcional; prevalece sobre documento)
   *   documento   texto o bytes del contrato, para su hash (opcional)
   *   fechaRef    'AAAA-MM-DD'
   * @returns {ok, codigo, resultado, errores, advertencias, resumenTexto}
   *   codigo: 0 correcto · 1 errores de esquema en la salida · 2 entrada o contexto inválidos
   */
  function ejecutar(p) {
    const advertencias = [];
    let jur, perfil = null;
    try {
      perfil = p.perfil ? leerPerfil(p.perfil.texto, p.perfil.ruta, advertencias, p.perfil.bytes, p.perfil.sha256) : null;
      jur = cargarJurisdiccion(p.config, p.jurisdiccion, advertencias);
      coherenciaPolitica(p.config, jur, advertencias);
    } catch (e) {
      return { ok: false, codigo: 2, resultado: null, errores: [`CONTEXTO INVÁLIDO: ${e.message}`], advertencias };
    }
    const res = JSON.parse(JSON.stringify(p.resultado));
    if (p.hashDocumento) {                       // calculado por n8n sobre los bytes del archivo
      res.contrato = res.contrato || {};
      res.contrato.hash_documento_sha256 = p.hashDocumento;
    } else if (p.documento !== undefined && p.documento !== null) {
      res.contrato = res.contrato || {};
      res.contrato.hash_documento_sha256 = sha256Hex(p.documento);
    }
    if ((!res.marco_legal || !res.marco_legal.length) && jur.marco_legal) res.marco_legal = jur.marco_legal.slice();

    const errEntrada = validarEntrada(res, p.esquema);
    if (errEntrada.length) return { ok: false, codigo: 2, resultado: null, errores: errEntrada, advertencias };

    try {
      calcular(res, p.config, p.fechaRef);
    } catch (e) {
      return { ok: false, codigo: 2, resultado: null, errores: [e.message], advertencias };
    }
    aplicarContexto(res, p.config, jur, perfil, advertencias);
    const errores = validar(res, p.esquema);
    const pp = res.puntaje_proveedor;
    return {
      ok: errores.length === 0, codigo: errores.length ? 1 : 0, resultado: res, errores, advertencias,
      resumenTexto: `Puntaje: ${pp.valor} (${pp.banda}) | base ${pp.base} - ${pp.penalizacion} | Dictamen: ${res.dictamen}`,
    };
  }

  return {
    VERSION_LIB, pyRound, alertasRenovacion, calcular, validar, validarEntrada, sha256Hex,
    leerPerfil, cargarJurisdiccion, coherenciaPolitica, aplicarContexto, ejecutar, dimension, DIMENSIONES,
  };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = PIMS_CALC;
