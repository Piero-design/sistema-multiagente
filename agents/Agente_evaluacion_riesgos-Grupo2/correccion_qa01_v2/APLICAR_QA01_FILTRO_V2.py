# -*- coding: utf-8 -*-
"""ISO Studio 7.2 - Hotfix QA-01 V2 (Oct 2026).
Solo corrige el guard del backend para referencias ISO incluidas en sourceSections.
NO modifica n8n, Qdrant, .env, credenciales ni amplía el alcance.
Ejecución Windows: python APLICAR_QA01_FILTRO.py
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import shutil, subprocess, sys, json

ROOT=Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
JS=ROOT/'server'/'lib'/'scope.js'
POLICY=ROOT/'scope-policy.json'
TEST=ROOT/'tests'/'scope-qa01.test.js'
MARK='// ISO-QA01: referencias normativas permitidas por la política local'


def single(text, old, new, desc):
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'{desc}: esperaba 1 coincidencia; encontré {n}. No se modificó el proyecto.')
    return text.replace(old,new,1)


def patch(src):
    if MARK in src: return src
    anchor='export function classifyScope(value,{operation=\'chat\'}={}){'
    preref=r'''// ISO-QA01: referencias normativas permitidas por la política local
// El conjunto viene del alcance aprobado, no de cualquier numeración de ISO.
const scopedReferenceTopics = (() => {
  const source=JSON.parse(fs.readFileSync(new URL('../../scope-policy.json', import.meta.url),'utf8'));
  const output=new Map();
  for(const topic of ['GR-01','GR-02','GR-03','GR-04','GR-05']) {
    for(const ref of (source.sourceSections?.[topic]||[])) {
      const key=String(ref).toLowerCase();
      if(!output.has(key)) output.set(key,topic);
    }
  }
  return output;
})();
const sectionReferences=(s)=>[...s.matchAll(/\b(?:[ab]\.)?\d+\.\d+(?:\.\d+){0,2}\b/g)]
  .map(m=>({ref:m[0],topicId:scopedReferenceTopics.get(m[0])}))
  .filter(m=>Boolean(m.topicId));
'''
    src=single(src,anchor,preref+anchor,'insercion de referencias autorizadas')
    # El filtro original exigía palabras clave y dejaba fuera cláusulas válidas.
    src=single(src,
       '  const hasMethod=any(s,',
       '  const matchedSections=sectionReferences(s);\n  const hasAuthorizedReference=matchedSections.length>0;\n  const hasMethod=any(s,',
       'deteccion de secciones')
    src=single(src,
       '  if (!hasRisk&&!hasMethod)return {allowed:false,code:\'OUT_OF_SCOPE\',reason:REFUSAL};',
       '  if (!hasRisk&&!hasMethod&&!hasAuthorizedReference)return {allowed:false,code:\'OUT_OF_SCOPE\',reason:REFUSAL};',
       'permitir referencia seleccionada')
    src=single(src,
       "  if(['web','visual','artifact'].includes(operation)&& !/(?:riesg|privacidad|dato personal|27701|pims)/.test(s)) return {allowed:false,code:'OUT_OF_SCOPE',reason:REFUSAL};",
       "  if(['web','visual','artifact'].includes(operation)&& !/(?:riesg|privacidad|dato personal|27701|pims)/.test(s) && !hasAuthorizedReference) return {allowed:false,code:'OUT_OF_SCOPE',reason:REFUSAL};",
       'herramientas con referencia explicita')
    src=single(src,
       '  let topicId=categories.find(([,pat])=>pat.test(s))?.[0];',
       "  let topicId=categories.find(([,pat])=>pat.test(s))?.[0];\n  const createsArtifact=/\\b(?:crea|crear|genera|generar|elabora|elaborar|disena|disenar|produce|prepara|exporta)\\b/.test(s) && /\\b(?:pdf|word|excel|docx|xlsx|diagrama|matriz|tabla|infografia|imagen|informe|archivo)\\b/.test(s);\n  if(hasAuthorizedReference && !createsArtifact) topicId=matchedSections[0].topicId;",
       'clasificacion por cláusula')
    return src


TESTS=r'''import {test} from 'node:test';
import assert from 'node:assert/strict';
import {classifyScope,scopeStatus} from '../server/lib/scope.js';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const permitidas=[
 ['Explica la cláusula 6.1.2 y la página del PDF','GR-03'],
 ['¿Cuándo repetir una evaluación según 8.2?','GR-03'],
 ['Control A.2.2.7 y registros del encargado','GR-05'],
 ['Explica A.3.11 en la norma','GR-04'],
 ['¿Qué indica 6.1.3?','GR-04'],
 ['Explica la cláusula 9.2.1','GR-05']
];
for (const [q,tema] of permitidas) test('QA01 permite: '+q,()=>{
 const d=classifyScope(q);
 assert.equal(d.allowed,true,JSON.stringify(d));
 assert.equal(d.topicId,tema);
});
test('QA01 permite artefacto referido a cláusula autorizada',()=>assert.equal(classifyScope('Crea un diagrama de 6.1.2',{operation:'visual'}).allowed,true));
test('QA01 indica GR-06 si se crea un artefacto de 6.1.2',()=>assert.equal(classifyScope('Crea un diagrama de 6.1.2').topicId,'GR-06'));
test('QA01 indica GR-03 si solo se cita página del PDF',()=>assert.equal(classifyScope('Explica la cláusula 6.1.2 y la página del PDF').topicId,'GR-03'));
test('QA01 mantiene fuera de alcance sin referencia',()=>assert.equal(classifyScope('Explícame las leyes del fútbol').allowed,false));
test('QA01 no legitima referencia de anexo no aprobada',()=>assert.equal(classifyScope('Explica A.1.2.4').allowed,false));
test('QA01 no permite citar el anexo completo',()=>assert.equal(classifyScope('Dame todos los controles del anexo A de ISO 27701').allowed,false));
test('QA01 no valida n8n por error',()=>{
 const s=scopeStatus(root,{SCOPE_N8N_REVIEWED:'false',SCOPE_PUBLIC_TESTING:'true',SCOPE_LOCAL_TESTING:'false',NODE_ENV:'development'});
 assert.equal(s.n8nReviewed,false);assert.equal(s.mode,'public_testing');
});
'''


def main():
    print('ISO STUDIO 7.2 - HOTFIX QA-01 V2: REFERENCIAS ISO Y CLASIFICACION CORRECTA')
    if not JS.is_file() or not POLICY.is_file() or not (ROOT/'tests').is_dir():
        raise RuntimeError('Falta instalación ISO Studio 7.2 en la ruta esperada.')
    pol=json.loads(POLICY.read_text(encoding='utf-8-sig'))
    if (pol.get('scopeId')!='ISO-GR-2026'
        or pol.get('corpusReview',{}).get('collection')!='iso_gr_2026'
        or '6.1.2' not in pol.get('sourceSections',{}).get('GR-03',[])):
        raise RuntimeError('Política de 72 páginas no coincide con la versión esperada. No cambiar.')
    src=JS.read_text(encoding='utf-8-sig')
    updated=patch(src)
    if updated==src:
        print('QA-01 ya estaba instalado; reejecutando pruebas.')
    backup=ROOT/'.scope-backups'/('pre_qa01_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    before={JS:JS.exists(),TEST:TEST.exists()}
    for file in before:
        if file.exists():
            target=backup/file.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target)
    try:
        JS.write_text(updated,encoding='utf-8')
        TEST.write_text(TESTS,encoding='utf-8')
        command=['node','--test','tests/scope.test.js','tests/scope-72.test.js','tests/scope-public.test.js','tests/scope-qa01.test.js']
        result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=90)
        print(result.stdout[-6000:])
        if result.returncode:
            raise RuntimeError('Pruebas fallidas. Se conserva el proyecto original.')
    except BaseException:
        for file,existed in before.items():
            old=backup/file.relative_to(ROOT)
            if existed:shutil.copy2(old,file)
            elif file.exists():file.unlink()
        print('REVERSION COMPLETADA: archivos originales restaurados.')
        raise
    print('OK QA01 V2: filtro corregido y pruebas aprobadas. Backend permite referencias seleccionadas.')
    print('No se modificó n8n/Qdrant; la segunda falla RAG requiere revisar Executions.')
    print('Respaldo: '+str(backup))
    print('Siguiente paso: reiniciar SOLO Node.js (puerto 4317), conservar Cloudflare si está activo.')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('ERROR: '+str(e),file=sys.stderr)
        sys.exit(1)
