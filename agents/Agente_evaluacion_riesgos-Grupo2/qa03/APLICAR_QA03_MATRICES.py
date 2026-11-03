# -*- coding: utf-8 -*-
"""ISO Studio 7.2 | QA-03: matrices naturales de riesgos en escenarios académicos.
Se requiere QA01 V2 aplicado y configuración local/publica de pruebas.
Conserva workflow n8n, colección Qdrant, .env, credenciales y los archivos recibidos.
"""
from pathlib import Path
from datetime import datetime
import shutil, subprocess, sys

ROOT = Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
SCOPE = ROOT / 'server' / 'lib' / 'scope.js'
SERVER = ROOT / 'server' / 'index.js'
TEST = ROOT / 'tests' / 'scope-qa03.test.js'
MARK = '// ISO-QA03: inferencia contextual acotada de matriz de riesgos'

def replace_one(value, old, new, name):
    n = value.count(old)
    if n != 1:
        raise RuntimeError(f'{name}: esperaba 1 coincidencia; encontradas {n}. Nada aplicado.')
    return value.replace(old, new, 1)

def patch_scope(source):
    if MARK in source:
        return source
    anchor = '  const hasAuthorizedReference=matchedSections.length>0;'
    block = r'''  const hasAuthorizedReference=matchedSections.length>0;
  // ISO-QA03: inferencia contextual acotada de matriz de riesgos
  // "Matriz 5x5 para matricula ficticia" es GR-06 aunque omita la palabra riesgo.
  // Se requieren simultaneamente estructura 3x3/5x5 y un contexto personal/académico.
  const naturalRiskMatrix=/\b(?:matriz|matrices)\b/.test(s) &&
    /\b(?:3\s*(?:x|por)\s*3|5\s*(?:x|por)\s*5)\b/.test(s) &&
    /\b(?:matricula|inscripciones?|admisiones?|estudiantes?|alumnos?|colegios?|universidades?|pacientes?|historia[s]? clinicas?|expedientes? personales?)\b/.test(s);'''
    source=replace_one(source, anchor,block,'contextual matrix')
    source=replace_one(source,
        "  if (!hasRisk&&!hasMethod&&!hasAuthorizedReference)return {allowed:false,code:'OUT_OF_SCOPE',reason:REFUSAL};",
        "  if (!hasRisk&&!hasMethod&&!hasAuthorizedReference&&!naturalRiskMatrix)return {allowed:false,code:'OUT_OF_SCOPE',reason:REFUSAL};",
        'guard contextual')
    source=replace_one(source,
        "  if(!topicId) topicId = 'GR-01';",
        "  if(naturalRiskMatrix) topicId='GR-06';\n  if(!topicId) topicId = 'GR-01';",
        'clasificacion GR06')
    source=replace_one(source,
        "  return {allowed:true,topicId,code:'ALLOWED',scopeId:'ISO-GR-2026'};",
        "  return {allowed:true,topicId,code:'ALLOWED',scopeId:'ISO-GR-2026',naturalRiskMatrix};",
        'indicador para el agente')
    return source

def patch_server(source):
    if 'ISO-QA03-CONTEXTO' in source:
        return source
    anchor = "    if (files.length) parts.push(`DOCUMENTOS ADJUNTOS"
    header = ("    // ISO-QA03-CONTEXTO: precisar el propósito sin ampliar GR-01 a GR-06.\n"
              "    if (decision.naturalRiskMatrix) parts.push('ALCANCE DE LA SOLICITUD: Interpretar matriz 3x3 o 5x5 como matriz DIDACTICA de evaluacion de RIESGOS de informacion y privacidad en el proceso del caso. Definir escalas de probabilidad e impacto, listar riesgos con supuestos explicitos y proponer valoraciones estimadas. No atribuir la escala 5x5 a una exigencia de ISO 27701. Si se adjunta un PDF, diferenciar hechos extraidos del documento de supuestos; no inventar lectura de contenido que no se haya extraido.');\n")
    return replace_one(source,anchor,header+anchor,'ayuda al agente')

TEST_SOURCE = r'''import {test} from 'node:test';
import assert from 'node:assert/strict';
import {classifyScope,scopeStatus} from '../server/lib/scope.js';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const cases=[
 'crea una matriz 5x5 para matricula ficticia y explica supuestos',
 'Crea una matriz 5x5 para matrícula ficticia y explica supuestos',
 'Haz una matriz 5 x 5 de riesgos de una matrícula ficticia',
 'Elabora matriz 5 por 5 para estudiantes de un colegio ficticio',
 'Matriz 3x3 de un proceso de admisiones de la universidad'
];
for(const question of cases)test('QA03: matriz acotada '+question,()=>{
 const d=classifyScope(question,{operation:'chat'});
 assert.equal(d.allowed,true,JSON.stringify(d));assert.equal(d.topicId,'GR-06');
});
test('QA03 permite PDF contextual solo si consulta es de riesgo',()=>{
 const d=classifyScope('Crea una matriz 5x5 para matricula ficticia y explica supuestos utilizando el archivo adjunto');
 assert.equal(d.allowed,true);assert.equal(d.naturalRiskMatrix,true);
});
for(const question of [
 'Crea una matriz 5x5 de palabras de crucigrama',
 'Matriz 5x5 para resultados del futbol universitario',
 'Dame una receta de pizza y luego matriz 5x5 para matricula ficticia',
 'Haz un programa Python de matriz 5x5 para matricula',
 'Analiza mi documento completo sin contexto',
 'Resume todo el manual CISA para estudiantes',
 'Explica ISO 27001 para estudiantes'
])test('QA03 NO amplía a tema ajeno '+question,()=>{
 assert.equal(classifyScope(question).allowed,false);
});
test('QA03 conserva referencia cláusula 6.1.2',()=>{
 const d=classifyScope('Explica la cláusula 6.1.2 y la página del PDF');
 assert.equal(d.allowed,true);assert.equal(d.topicId,'GR-03');
});
test('QA03 no valida por error el trabajo de los compañeros',()=>{
 const d=scopeStatus(root,{SCOPE_N8N_REVIEWED:'false',SCOPE_PUBLIC_TESTING:'true',SCOPE_LOCAL_TESTING:'false',NODE_ENV:'development'});
 assert.equal(d.n8nReviewed,false);assert.equal(d.mode,'public_testing');
});
test('QA03 incluye contexto para Gemini sin alterar n8n',()=>{
 const s=fs.readFileSync(path.join(root,'server/index.js'),'utf8');
 assert.match(s,/ISO-QA03-CONTEXTO/);
 assert.match(s,/DIDACTICA de evaluacion de RIESGOS/);
});
'''

def main():
    print('ISO STUDIO 7.2 - QA03 MATRICES 5x5 + PDF (CORRECCION DE FILTRO)')
    if not SCOPE.is_file() or not SERVER.is_file() or not (ROOT/'tests').is_dir():
        raise RuntimeError('No se encontro la instalacion esperada.')
    scope=SCOPE.read_text(encoding='utf-8-sig')
    if '// ISO-QA01:' not in scope or 'iso_gr_2026' not in scope:
        raise RuntimeError('Primero instala QA01 V2 y la politica de 72 paginas. No se modifico nada.')
    server=SERVER.read_text(encoding='utf-8-sig')
    if "const decision=classifyScope(message,{operation:'chat'});" not in server:
        raise RuntimeError('No se reconoce el backend Express; archivos intactos.')
    new_scope=patch_scope(scope)
    new_server=patch_server(server)
    if (MARK in scope) != ('ISO-QA03-CONTEXTO' in server):
        raise RuntimeError('Parche QA03 anterior incompleto. Verifica antes de reintentar.')
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
    back=ROOT/'.scope-backups'/('pre_qa03_'+stamp)
    targets={SCOPE:new_scope,SERVER:new_server,TEST:TEST_SOURCE}
    exists={p:p.exists() for p in targets}
    back.mkdir(parents=True,exist_ok=False)
    for p in targets:
        if p.exists():
            b=back/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    try:
        for p,value in targets.items():p.write_text(value,encoding='utf-8')
        files=['tests/scope.test.js','tests/scope-72.test.js','tests/scope-public.test.js','tests/scope-qa01.test.js','tests/scope-qa03.test.js']
        r=subprocess.run(['node','--test',*files],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=120)
        print(r.stdout[-9000:])
        if r.returncode:raise RuntimeError('Pruebas fallidas, no se instala el parche.')
        print('OK QA03: pruebas PASS. Filtro permite matriz 5x5 para matricula; aplica contexto ISO de riesgos.')
        print('ATENCION: la lectura de PDF NO esta certificada por este hotfix; se verifica aparte.')
        print('SCOPE_N8N_REVIEWED no ha sido alterado; n8n, Qdrant, PDF y .env no han cambiado.')
        print('Respaldo:',back)
        print('Reinicia solamente el servidor Node.js del puerto 4317. Mantén el tunnel actual si sigue activo.')
    except BaseException:
        for p,was in exists.items():
            b=back/p.relative_to(ROOT)
            if was:shutil.copy2(b,p)
            elif p.exists():p.unlink()
        print('REVERSION COMPLETADA: se restauraron los archivos anteriores.')
        raise

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('ERROR:',e,file=sys.stderr);sys.exit(1)
