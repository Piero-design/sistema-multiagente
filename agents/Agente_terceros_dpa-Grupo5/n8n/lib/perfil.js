/* =============================================================================
   perfil.js — Port de pims-perfilador-organizacion/scripts/validar_perfil.py
   y utilidades para editar el estado del perfil (validación del DPO).
   Equivalencia con Python verificada en n8n/pruebas/equivalencia_perfil.py.
   ========================================================================== */

const PIMS_PERFIL = (() => {
  'use strict';

  const CAMPOS_CABECERA = ['Organización', 'Id', 'Jurisdicción', 'Versión', 'Estado', 'Fecha',
    'Generado por', 'Validado por'];
  const SECCIONES = { 1: 'Identificación', 2: 'Estructura', 3: 'Aprobadores', 4: 'Procesos',
    5: 'Condiciones de riesgo', 6: 'Terceros', 7: 'Supuestos', 8: 'Observaciones' };
  const SECCIONES_CON_FUENTE = new Set([1, 2, 3, 4, 5, 6]);
  const VALORES_DPA = new Set(['sí', 'si', 'no', 'desconocido']);
  const JUICIO = () => /(?<![\p{L}\p{N}_])(cumplen?|conformes?|aprobad[oa]s?|homologad[oa]s?|exent[oa]s?|no\s+requieren?\s+(?:un\s+)?(?:dpa|contrato|evaluaci[oó]n))(?![\p{L}\p{N}_])/giu;
  const REF_DOC = () => /(?<![\p{L}\p{N}_])D(\d+)(?![\p{L}\p{N}_])/gu;

  const celdas = (l) => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
  const esFila = (l) => l.trim().startsWith('|') && !/^\|\s*:?-{2,}/.test(l.trim());
  const esMarcador = (c) => /\[[^\]]*\]/.test(c) && !REF_DOC().test(c) && c.startsWith('[');

  function tablas(lineas) {
    const res = [];
    let actual = [];
    for (const ln of lineas) {
      if (ln.trim().startsWith('|')) {
        if (esFila(ln)) actual.push(celdas(ln));
      } else if (actual.length) {
        res.push(actual);
        actual = [];
      }
    }
    if (actual.length) res.push(actual);
    return res;
  }

  function validar(texto) {
    const errores = [], advertencias = [];
    const lineas = texto.split(/\r?\n/);

    const pos = {};
    lineas.forEach((ln, i) => {
      const m = /^##\s+(\d+)\.\s/.exec(ln);
      if (m) pos[+m[1]] = i;
    });
    for (const [n, nombre] of Object.entries(SECCIONES)) {
      if (!(n in pos)) errores.push(`Falta la sección '## ${n}. ${nombre}…'.`);
    }
    const orden = Object.keys(pos).map(Number).sort((a, b) => a - b).filter((n) => n in SECCIONES).map((n) => pos[n]);
    if (JSON.stringify(orden) !== JSON.stringify([...orden].sort((a, b) => a - b))) {
      errores.push('Las secciones numeradas no están en orden.');
    }

    let inicioDoc = lineas.findIndex((ln) => ln.trim().toLowerCase().startsWith('## documentos fuente'));
    if (inicioDoc < 0) inicioDoc = null;
    const valoresPos = Object.values(pos);
    const primeraSec = valoresPos.length ? Math.min(...valoresPos) : lineas.length;

    // Cabecera
    const cab = {};
    for (const t of tablas(lineas.slice(0, inicioDoc !== null ? inicioDoc : primeraSec))) {
      const filas = t.length && t[0][0] === 'Campo' ? t.slice(1) : t;
      for (const fila of filas) if (fila.length >= 2) cab[fila[0]] = fila[1];
    }
    for (const campo of CAMPOS_CABECERA) {
      const valor = cab[campo] || '';
      if (!valor) errores.push(`Cabecera: falta el campo '${campo}'.`);
      else if (valor.startsWith('[')) errores.push(`Cabecera: el campo '${campo}' conserva el marcador de plantilla (${valor}).`);
    }
    const estado = (cab['Estado'] || '').replace(/[*`]/g, '').trim();
    if (estado && !(estado === 'Borrador' || estado.toLowerCase().startsWith('validado por dpo'))) {
      errores.push(`Cabecera: estado '${estado}' no válido (usa 'Borrador' o 'Validado por DPO (nombre, fecha)').`);
    }
    if (estado === 'Borrador') advertencias.push('Perfil en estado Borrador: debe validarlo el DPO antes de un uso formal.');

    // Documentos fuente
    const docs = new Set();
    if (inicioDoc === null) {
      errores.push("Falta la sección '## Documentos fuente'.");
    } else {
      for (const t of tablas(lineas.slice(inicioDoc, primeraSec))) {
        for (const fila of t.slice(1)) {
          const m = fila.length ? /^D(\d+)$/.exec(fila[0]) : null;
          if (!m) continue;
          docs.add(+m[1]);
          if (fila.slice(1, 3).some((c) => c.startsWith('['))) errores.push(`Documentos fuente: D${m[1]} conserva marcadores de plantilla.`);
          const h = fila.length >= 6 ? fila[fila.length - 1] : '';
          if (h.toLowerCase() === 'pendiente') advertencias.push(`Documentos fuente: D${m[1]} sin hash SHA-256.`);
          else if (!/^[0-9a-fA-F]{64}$/.test(h)) errores.push(`Documentos fuente: D${m[1]} con hash inválido (${h || 'vacío'}).`);
        }
      }
      if (!docs.size) errores.push('Documentos fuente: no hay ningún documento D1, D2…');
    }

    // Secciones con tablas
    const limites = Object.entries(pos).map(([n, i]) => [+n, i]).sort((a, b) => a[1] - b[1]);
    limites.forEach(([n, ini], idx) => {
      const fin = idx + 1 < limites.length ? limites[idx + 1][1] : lineas.length;
      const bloque = lineas.slice(ini, fin);
      if (SECCIONES_CON_FUENTE.has(n)) {
        let filasValidas = 0;
        for (const t of tablas(bloque)) {
          const cabecera = t[0].map((c) => c.toLowerCase());
          if (!cabecera.includes('fuente')) continue;
          const iF = cabecera.indexOf('fuente');
          const iD = cabecera.findIndex((c) => c.includes('dpa'));
          for (const fila of t.slice(1)) {
            if (!fila.some((c) => c)) {
              errores.push(`Sección ${n}: fila vacía (borra las filas de plantilla no usadas).`);
              continue;
            }
            filasValidas++;
            const etq = `Sección ${n}, fila '${[...fila[0]].slice(0, 40).join('')}'`;
            if (fila.some(esMarcador)) errores.push(`${etq}: conserva marcadores de plantilla.`);
            const fuente = iF < fila.length ? fila[iF] : '';
            const refs = new Set([...fuente.matchAll(REF_DOC())].map((m) => +m[1]));
            if (!refs.size && !fuente.toLowerCase().includes('supuesto')) errores.push(`${etq}: sin fuente [Dn …] ni 'Supuesto'.`);
            for (const r of [...refs].filter((x) => !docs.has(x)).sort((a, b) => a - b)) {
              errores.push(`${etq}: cita D${r}, que no está en 'Documentos fuente'.`);
            }
            if (iD >= 0 && iD < fila.length) {
              const v = fila[iD].replace(/^[* ]+|[* ]+$/g, '').toLowerCase();
              if (!VALORES_DPA.has(v)) errores.push(`${etq}: '¿DPA localizado?' = '${fila[iD]}'; solo se admite Sí / No / Desconocido.`);
            }
            for (const c of fila) {
              for (const m of c.matchAll(JUICIO())) {
                errores.push(`${etq}: juicio de cumplimiento no permitido ('${m[0]}'). El perfil es contexto, no evidencia.`);
              }
            }
          }
        }
        if (filasValidas === 0) advertencias.push(`Sección ${n}: sin filas con datos.`);
      } else if (n === 7) {
        for (const ln of bloque.slice(1)) {
          for (const m of ln.matchAll(JUICIO())) advertencias.push(`Sección 7: posible juicio de cumplimiento ('${m[0]}'); revísalo.`);
        }
      }
    });

    return { valido: errores.length === 0, estado: estado || null, documentos: docs.size, errores, advertencias };
  }

  /** Cambia los campos Estado y Validado por de la cabecera (lo hace el DPO desde la página). */
  function marcarValidado(texto, validadoPor, fecha) {
    const reemplazar = (t, campo, valor) => t.replace(
      new RegExp(`^(\\|\\s*${campo}\\s*\\|)\\s*.*?\\s*(\\|)\\s*$`, 'm'), `$1 ${valor} $2`);
    let t = reemplazar(texto, 'Estado', `Validado por DPO (${validadoPor}, ${fecha})`);
    t = reemplazar(t, 'Validado por', `${validadoPor} (${fecha})`);
    return t;
  }

  /** Lista de terceros de la sección 6 (para la vista de brechas: terceros sin DPA evaluado). */
  function terceros(texto) {
    const lineas = texto.split(/\r?\n/);
    const ini = lineas.findIndex((l) => /^##\s+6\.\s/.test(l));
    if (ini < 0) return [];
    let fin = lineas.findIndex((l, i) => i > ini && /^##\s/.test(l));
    if (fin < 0) fin = lineas.length;
    const t = tablas(lineas.slice(ini, fin))[0];
    if (!t) return [];
    const cab = t[0].map((c) => c.toLowerCase());
    return t.slice(1).filter((f) => f.some((c) => c)).map((f) => Object.fromEntries(cab.map((c, i) => [c, f[i] || ''])));
  }

  return { validar, marcarValidado, terceros };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = PIMS_PERFIL;
