#!/usr/bin/env node
// crear_carpetas.js — Crea organizaciones/<id>/documentos y /contratos.
// Lo invoca el flujo "PIMS · Crear carpetas de organización" (nodo Execute Command).
// Uso: node crear_carpetas.js <RAIZ> <id_organizacion>
'use strict';
const fs = require('fs');
const path = require('path');
const [raiz, id] = process.argv.slice(2);
const salir = (o) => { process.stdout.write(JSON.stringify(o)); process.exit(o.ok ? 0 : 1); };
if (!raiz || !fs.existsSync(path.join(raiz, 'pims-dpa-auditor', 'SKILL.md'))) salir({ ok: false, error: 'RAIZ inválida' });
if (!/^[a-z0-9_]{2,60}$/.test(id || '') || id.startsWith('_')) salir({ ok: false, error: 'id de organización inválido' });
const base = path.join(raiz, 'organizaciones', id);
if (fs.existsSync(path.join(base, 'config_organizacion.json'))) salir({ ok: false, error: 'la organización ya existe' });
for (const sub of ['documentos', 'contratos']) fs.mkdirSync(path.join(base, sub), { recursive: true });
salir({ ok: true, carpeta: base.replace(/\\/g, '/') });
