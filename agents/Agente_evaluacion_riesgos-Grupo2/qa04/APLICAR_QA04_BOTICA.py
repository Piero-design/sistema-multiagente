# -*- coding: utf-8 -*-
"""QA-04: arregla el falso rechazo de procesos comerciales con datos personales.
Modifica solamente server/lib/scope.js y añade una prueba automática.
La operación es transaccional: respalda y revierte si falla cualquier prueba.
"""
from pathlib import Path
from datetime import datetime
import shutil, subprocess, sys

ROOT = Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
JS = ROOT / 'server' / 'lib' / 'scope.js'
TEST = ROOT / 'tests' / 'scope-qa04.test.js'
MARK = '// ISO-QA04: evitar falso positivo comercial/clinico'

TEST_SOURCE = '''import {test} from 'node:test';
import assert from 'node:assert/strict';
import {classifyScope} from '../server/lib/scope.js';

const caso = `Botica Misti S.A.C. es una cadena de 12 farmacias en Arequipa con 85 empleados y unos 40 000 clientes registrados. Trata nombre, DNI, teléfono, correo, dirección de delivery, historial de compras y recetas médicas. Usa un sistema de ventas en cada botica, un servidor en la nube de un proveedor externo, un call center tercerizado y repartidores contratados. Según ISO/IEC 27701:2025, ¿actúa como responsable o encargado del tratamiento de datos, quiénes son sus partes interesadas y qué debe definir sobre el alcance del PIMS? Cita las cláusulas. Crea una matriz 5x5 de riesgos de privacidad. Identifica cinco riesgos, calcula sus niveles, explica los supuestos y propone tratamientos.`;

test('QA04 permite el caso integral de Botica Misti',()=>{
 const r=classifyScope(caso);assert.equal(r.allowed,true,JSON.stringify(r));assert.equal(r.topicId,'GR-06');
});
test('QA04 no rechaza sistemas de ventas que tratan PII',()=>{
 const r=classifyScope('Evalúa los riesgos de privacidad del sistema de ventas de una farmacia');
 assert.equal(r.allowed,true,JSON.stringify(r));
});
test('QA04 no rechaza receta médica como dato sensible',()=>{
 const r=classifyScope('Identifica los riesgos de privacidad asociados a una receta médica de pacientes');
 assert.equal(r.allowed,true,JSON.stringify(r));
});
test('QA04 evita falsos positivos al solicitar matrices de riesgos como artefacto',()=>{
 const r=classifyScope('Crea una matriz 5x5 de riesgos de privacidad y propone tratamientos');
 assert.equal(r.allowed,true,JSON.stringify(r));assert.equal(r.topicId,'GR-06');
});
for (const q of ['Dame una receta de pizza','Escribe una receta de sopa para disminuir riesgos','Dame estrategias de ventas','Explica marketing y riesgos deportivos','Resume todo el manual CISA']) {
 test('QA04 conserva bloqueo externo: '+q,()=>assert.equal(classifyScope(q).allowed,false));
}
'''

def one(src, before, after, desc):
    n=src.count(before)
    if n!=1:raise RuntimeError(f'{desc}: se esperaba una coincidencia, encontradas {n}. Ningún archivo modificado.')
    return src.replace(before,after,1)

def main():
    print('ISO STUDIO 7.2 - QA04: FALSO RECHAZO BOTICA Y MATRICES')
    if not JS.is_file() or not (ROOT / 'tests' / 'scope-qa03.test.js').exists():
        raise RuntimeError('No se detectó instalación compatible con QA03. Proyecto intacto.')
    src=JS.read_text(encoding='utf-8-sig')
    if '// ISO-QA03:' not in src or '// ISO-QA01:' not in src:
        raise RuntimeError('No se reconocen los parches QA01/QA03 existentes. Proyecto intacto.')
    if MARK in src:
        print('QA04 ya está instalado; se repetirán las pruebas.')
        updated=src
    else:
        # Una palabra como "ventas" no es motivo de rechazo por sí sola;
        # el guard ya exige propósito de riesgos / privacidad o referencia autorizada.
        updated=one(src,'|marketing|ventas|gato','|marketing|gato','excluir ventas como veto universal')
        # Receta de cocina sigue bloqueada, receta médica puede analizarse como dato de salud.
        updated=one(updated,'|receta|cocina','|receta(?!\\s+medica)|cocina','permitir receta médica')
        # Cuando se solicita crear una matriz/diagrama de riesgos, pertenece a GR-06.
        updated=one(updated,"  if(naturalRiskMatrix) topicId='GR-06';", "  if(createsArtifact) topicId='GR-06';\n  if(naturalRiskMatrix) topicId='GR-06';",'clasificacion de artefactos')
        updated=updated.replace('export function classifyScope(value', MARK+'\nexport function classifyScope(value',1)
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
    backup=ROOT/'.scope-backups'/('pre_qa04_'+stamp)
    backup.mkdir(parents=True,exist_ok=False)
    paths=[JS,TEST]
    before={p:p.exists() for p in paths}
    for p in paths:
        if p.exists():
            b=backup/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    try:
        JS.write_text(updated,encoding='utf-8')
        TEST.write_text(TEST_SOURCE,encoding='utf-8')
        testfiles=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('scope*.test.js'))
        proc=subprocess.run(['node','--test',*testfiles],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=120)
        print(proc.stdout[-9500:])
        if proc.returncode: raise RuntimeError('Pruebas fallidas; se restaurarán los archivos anteriores.')
    except BaseException:
        for p,existed in before.items():
            b=backup/p.relative_to(ROOT)
            if existed:shutil.copy2(b,p)
            elif p.exists():p.unlink()
        print('REVERSION COMPLETADA. El proyecto previo se conserva.')
        raise
    print('OK QA04: filtro actualizado y todas las pruebas de alcance PASS.')
    print('Solo modificados scope.js y tests/scope-qa04.test.js. No se tocó n8n, Qdrant ni .env.')
    print('Respaldo:',backup)
    print('Reinicia solamente node server/index.js (puerto 4317).')

if __name__=='__main__':
    try:main()
    except Exception as e:print('ERROR:',e,file=sys.stderr);sys.exit(1)
