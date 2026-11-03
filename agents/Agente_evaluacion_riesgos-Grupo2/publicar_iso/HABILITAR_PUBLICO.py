# -*- coding: utf-8 -*-
"""Habilita una prueba pública TEMPORAL en ISO Studio 7.2, sin afirmar QA completada.
No cambia Qdrant, n8n, la política del corpus ni las credenciales.
"""
from pathlib import Path
from datetime import datetime
import sys, shutil, subprocess, re

ROOT=Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
SCOPE=ROOT/'server'/'lib'/'scope.js'
ENV=ROOT/'.env'
TESTS=ROOT/'tests'/'scope-public.test.js'
PUBLIC=ROOT/'public'
DOC=Path(__file__).with_name('PLAN_PRUEBAS_ISO_STUDIO_7_2.docx')
DST=PUBLIC/DOC.name


def replace_once(text,old,new,description):
    n=text.count(old)
    if n != 1:
        raise RuntimeError(f'{description}: coincidencias esperadas 1, encontradas {n}. No se modificó nada.')
    return text.replace(old,new,1)


def main():
    if not (SCOPE.exists() and ENV.exists() and DOC.exists()):
        raise RuntimeError('Faltan los archivos del backend 7.2 o el documento del paquete.')
    src=SCOPE.read_text(encoding='utf-8')
    if "const corpusCorrect=" not in src or "sourcePages:72" not in src or "ISO_LOCAL_ONLY" not in src:
        raise RuntimeError('Instala antes el parche de 72 páginas. No se reconoce la versión actual de scope.js.')
    if "const publicTesting=" in src:
        print('El modo público ya estaba instalado; verificando configuración.')
        patched=src
    else:
        patched=replace_once(src,
          "  const localTesting=env.SCOPE_LOCAL_TESTING==='true' && env.NODE_ENV!=='production' && !n8nReviewed;",
          "  const publicTesting=env.SCOPE_PUBLIC_TESTING==='true' && env.NODE_ENV!=='production' && !n8nReviewed;\n  const localTesting=env.SCOPE_LOCAL_TESTING==='true' && env.NODE_ENV!=='production' && !n8nReviewed && !publicTesting;",
          'nuevo modo público')
        patched=replace_once(patched,
          '  const enabled=Boolean(correct&&corpusCorrect&&(n8nReviewed||localTesting));',
          '  const enabled=Boolean(correct&&corpusCorrect&&(n8nReviewed||localTesting||publicTesting));',
          'habilitar modo público')
        patched=replace_once(patched,
          "  const mode=enabled?(localTesting?'local_testing':'reviewed'):'locked';",
          "  const mode=enabled?(publicTesting?'public_testing':localTesting?'local_testing':'reviewed'):'locked';",
          'indicar modo público')
        patched=replace_once(patched,
          "return {enabled,mode,localTesting:enabled&&localTesting,state:enabled?(localTesting?'local_testing':'active'):'awaiting_n8n_review',code:enabled?(localTesting?'ISO_SCOPE_LOCAL_TEST':'ISO_SCOPE_ACTIVE'):'ISO_SCOPE_LOCKED'",
          "return {enabled,mode,publicTesting:enabled&&publicTesting,localTesting:enabled&&localTesting,state:enabled?(publicTesting?'public_testing':localTesting?'local_testing':'active'):'awaiting_n8n_review',code:enabled?(publicTesting?'ISO_SCOPE_PUBLIC_TEST':localTesting?'ISO_SCOPE_LOCAL_TEST':'ISO_SCOPE_ACTIVE'):'ISO_SCOPE_LOCKED'",
          'estado público')
        patched=replace_once(patched,
          "reason:localTesting?'Modo de pruebas locales; pendiente validación independiente de n8n, Skills y corpus. No publicar.':enabled?'Alcance académico revisado y habilitado.'",
          "reason:publicTesting?'ACCESO PÚBLICO TEMPORAL PARA PRUEBAS. n8n, Skills y corpus aún pendientes de validación por el equipo.':localTesting?'Modo de pruebas locales; pendiente validación independiente de n8n, Skills y corpus. No publicar.':enabled?'Alcance académico revisado y habilitado.'",
          'aviso de modo público')
        patched=replace_once(patched,
          "limitations:'Las llamadas directas a n8n no pasan por este backend. No exponer n8n ni este modo local a Internet.'",
          "limitations:'El enlace público carece de autenticación: cualquiera puede usar la API y consumir cuotas. No exponer n8n ni Qdrant directamente. No equivale a QA aprobada.'",
          'riesgos del modo público')
    original_env=ENV.read_text(encoding='utf-8-sig')
    lines=[x for x in original_env.splitlines() if not re.match(r'^\s*(SCOPE_LOCAL_TESTING|SCOPE_PUBLIC_TESTING|SCOPE_N8N_REVIEWED)\s*=',x)]
    cleaned='\n'.join(lines).rstrip()+"\nSCOPE_N8N_REVIEWED=false\nSCOPE_LOCAL_TESTING=false\nSCOPE_PUBLIC_TESTING=true\n"
    t="""import {test} from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {scopeStatus,createScopeGate} from '../server/lib/scope.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const pub={SCOPE_N8N_REVIEWED:'false',SCOPE_PUBLIC_TESTING:'true',SCOPE_LOCAL_TESTING:'false',NODE_ENV:'development'};
test('publico temporal habilitado solo por bandera explícita',()=>{const s=scopeStatus(root,pub);assert.equal(s.enabled,true);assert.equal(s.mode,'public_testing');assert.equal(s.publicTesting,true);assert.equal(s.n8nReviewed,false);assert.equal(s.corpusCollection,'iso_gr_2026');});
test('puerta permite host trycloudflare cuando publicTesting esta activo',()=>{let next=false;const res={status(){throw Error('no debe bloquear');}};createScopeGate(root,pub)({method:'POST',path:'/chat',get:()=> 'prueba.trycloudflare.com'},res,()=>{next=true});assert.equal(next,true);});
test('no abre acceso público sin permiso explícito',()=>{const s=scopeStatus(root,{...pub,SCOPE_PUBLIC_TESTING:'false'});assert.equal(s.enabled,false);});
test('nunca habilitar modo de prueba en production',()=>{const s=scopeStatus(root,{...pub,NODE_ENV:'production'});assert.equal(s.enabled,false);});
"""
    backup=ROOT/'.scope-backups'/('pre_public_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    oldfiles=[SCOPE,ENV,TESTS,DST]
    backup.mkdir(parents=True,exist_ok=False)
    existed={}
    for p in oldfiles:
        existed[p]=p.exists()
        if p.exists():
            q=backup/p.relative_to(ROOT)
            q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    try:
        PUBLIC.mkdir(parents=True,exist_ok=True)
        SCOPE.write_text(patched,encoding='utf-8')
        ENV.write_text(cleaned,encoding='utf-8')
        TESTS.write_text(t,encoding='utf-8')
        shutil.copy2(DOC,DST)
        r=subprocess.run(['node','--test','tests/scope.test.js','tests/scope-72.test.js','tests/scope-public.test.js'],cwd=ROOT,capture_output=True,text=True,errors='replace',timeout=90)
        print(r.stdout[-2000:])
        if r.returncode:raise RuntimeError('Fallaron pruebas unitarias: '+r.stderr[-1200:])
    except Exception:
        for p in oldfiles:
            old=backup/p.relative_to(ROOT)
            if existed[p]:shutil.copy2(old,p)
            elif p.exists():p.unlink()
        print('ERROR. Se restauró el estado anterior.');raise
    print('OK: acceso publico temporal activado con SCOPE_N8N_REVIEWED=false. No hay contraseña.')
    print('Documento: public/'+DOC.name)
    print('Respaldo:',backup)

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('ERROR:',e,file=sys.stderr);sys.exit(1)
