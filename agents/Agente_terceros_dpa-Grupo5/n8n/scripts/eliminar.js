#!/usr/bin/env node
// eliminar.js — Borra los archivos de un expediente, el perfil de una organización o un documento institucional.
// Lo invoca el flujo "PIMS · Eliminar archivos" (nodo Execute Command). No recibe rutas: las arma él mismo a partir
// del tipo y del id, ya validados, y comprueba que cada una quede dentro del proyecto.
// Uso: node eliminar.js <RAIZ> expediente <id_registro>
//      node eliminar.js <RAIZ> perfil <id_organizacion>
//      node eliminar.js <RAIZ> documento <id_organizacion> <nombre_archivo>
'use strict';
const fs = require('fs');
const path = require('path');
const [raiz, tipo, id, nombre] = process.argv.slice(2);
const salir = (o) => { process.stdout.write(JSON.stringify(o)); process.exit(0); };
if (!raiz || !fs.existsSync(path.join(raiz, 'pims-dpa-auditor', 'SKILL.md'))) salir({ ok: false, error: 'RAIZ inválida' });

let archivos;
if (tipo === 'expediente') {
  // Mismo patrón que aceptan las consultas y el chat; sin '..' ni separadores.
  if (!/^[A-Za-z0-9][A-Za-z0-9_.-]{2,139}$/.test(id || '') || id.includes('..')) salir({ ok: false, error: 'id de expediente inválido' });
  archivos = [['datos', 'registro', `${id}.json`], ['datos', 'registro', `${id}.md`], ['datos', 'registro', `${id}.contrato.txt`],
    ['datos', 'chats', `exp_${id}.json`]];
} else if (tipo === 'perfil') {
  if (!/^[a-z0-9_]{2,60}$/.test(id || '') || id.startsWith('_')) salir({ ok: false, error: 'id de organización inválido' });
  // El perfil y lo que genera el perfilador. La configuración y los documentos de la organización se conservan.
  archivos = ['perfil_organizacion.md', 'perfil_organizacion.anterior.md', 'perfil_organizacion.borrador_invalido.md',
    'validacion_perfil.json'].map((f) => ['organizaciones', id, f]);
} else if (tipo === 'documento') {
  if (!/^[a-z0-9_]{2,60}$/.test(id || '') || id.startsWith('_')) salir({ ok: false, error: 'id de organización inválido' });
  // Solo un archivo de documentos/, por su nombre (sin rutas) y con las extensiones que acepta el agente.
  if (!/^[A-Za-z0-9][A-Za-z0-9 ._()-]{0,150}\.(pdf|md|txt)$/i.test(nombre || '') || nombre.includes('..')) salir({ ok: false, error: 'nombre de documento inválido' });
  archivos = [['organizaciones', id, 'documentos', nombre]];
} else salir({ ok: false, error: "tipo debe ser 'expediente', 'perfil' o 'documento'" });

const base = fs.realpathSync(raiz);
const eliminados = [], no_existian = [];
for (const partes of archivos) {
  const ruta = path.join(base, ...partes);
  const rel = partes.join('/');
  if (!fs.existsSync(ruta)) { no_existian.push(rel); continue; }
  const real = fs.realpathSync(ruta);
  if (!real.startsWith(base + path.sep) || !fs.statSync(real).isFile()) salir({ ok: false, error: `ruta fuera del proyecto: ${rel}` });
  fs.unlinkSync(real);
  eliminados.push(rel);
}
if (!eliminados.length) salir({ ok: false, codigo: 404, error: tipo === 'expediente' ? `No existe el expediente ${id}.`
  : tipo === 'documento' ? `No existe el documento '${nombre}' en '${id}'.` : `La organización '${id}' no tiene perfil.` });
salir({ ok: true, tipo, id, eliminados, no_existian });
