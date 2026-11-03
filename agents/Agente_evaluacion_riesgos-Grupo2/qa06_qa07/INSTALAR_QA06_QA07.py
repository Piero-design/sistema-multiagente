# -*- coding: utf-8 -*-
"""ISO Studio 7.2 - QA06 clasificador conversacional / QA07 contención visual.
No modifica Qdrant, la norma, .env, workflows ni credenciales. Instalación transaccional.
"""
from pathlib import Path
from datetime import datetime
import re,sys,shutil,subprocess

HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
SCOPE=ROOT/'server/lib/scope.js'; INDEX=ROOT/'server/index.js'; MAIN=ROOT/'src/main.jsx'; APP=ROOT/'src/App.jsx'; CSS=ROOT/'src/styles.css'
TRIAGE=ROOT/'server/lib/intent-triage.js'; TEST=ROOT/'tests/intent-triage.test.js'; BOUNDARY=ROOT/'src/components/AppErrorBoundary.jsx'
MARK='// ISO-QA06: puerta conversacional para consultas ambiguas'

def one(text,old,new,description):
    count=text.count(old)
    if count!=1: raise RuntimeError(description+': coincidencias '+str(count)+' (se esperaba exactamente 1). No se aplica el parche.')
    return text.replace(old,new,1)

def scope_patch(src):
    if '// ISO-QA04' not in src:raise RuntimeError('Se necesita QA04 instalado antes de este parche.')
    src=one(src,'|gato|gatito|perro|perrito|animales','', 'retirar veto nominal sobre animales (no aplica a consultas no relacionadas)')
    anchor='  if(any(s,irrelevant))return {allowed:false,code:\'OUT_OF_SCOPE\',reason:REFUSAL};'
    new='''  // ISO-QA06: nombres de negocios con animales no son automáticamente ajenos a privacidad.
  // Se siguen rechazando dibujos de animales como objeto principal, aunque mencionen riesgos.
  if(/\\b(?:dibuja|pinta|ilustra|imagen de)\\b.{0,45}\\b(?:gato|gatito|perro|perrito)\\b/.test(s))return {allowed:false,code:'OUT_OF_SCOPE',reason:REFUSAL};
'''+anchor
    return one(src,anchor,new,'restricción contextual')

def index_patch(src):
    # Registra el middleware ANTES del endpoint existente y DESPUÉS del gate de /api.
    import_anchor="import {createScopeGate,scopeStatus,classifyScope,reviewAnswer,scopeSystemMessage,scopedWebQuery} from './lib/scope.js';"
    src=one(src,import_anchor,import_anchor+"\nimport {triageScopeMessage} from './lib/intent-triage.js';", 'import de triage')
    existing="app.post('/api/chat', async (req, res) => {"
    insert=r'''// ISO-QA06: puerta conversacional para consultas ambiguas
// Tiene tres estados: aceptar mediante guard existente, preguntar o rechazar.
// No almacena documentos ni información permanentemente y no llama a Gemini si pide aclaración.
const pendingScopeDialogs=new Map();
const scopeQuestionRate=new Map();
app.post('/api/chat',(req,res,next)=>{
  const {message,sessionId,fileIds=[],webMode='auto'}=req.body||{};
  if(typeof message!=='string'||!message.trim()||message.length>8000||
      typeof sessionId!=='string'||!/^[a-zA-Z0-9-]{8,100}$/.test(sessionId)||
      !['auto','on','off'].includes(webMode)||!Array.isArray(fileIds)||fileIds.length>4||fileIds.some(id=>typeof id!=='string'))return next();
  const now=Date.now();
  // Purga de estados viejos para que la memoria de prueba sea limitada.
  for(const [k,v] of pendingScopeDialogs)if(now-v.at>30*60*1000)pendingScopeDialogs.delete(k);
  if(pendingScopeDialogs.size>400)pendingScopeDialogs.delete(pendingScopeDialogs.keys().next().value);
  const prior=pendingScopeDialogs.get(sessionId)||null;
  const decision=triageScopeMessage(message,{pending:prior,hasFiles:fileIds.length>0});
  if(decision.kind==='deny'){
    pendingScopeDialogs.delete(sessionId);
    return res.status(403).json({error:decision.reason,code:'UNRELATED_REQUEST'});
  }
  if(decision.kind==='clarify'){
    const who=req.ip||'local';const times=(scopeQuestionRate.get(who)||[]).filter(t=>now-t<60000);
    if(times.length>=18)return res.status(429).json({error:'Demasiadas consultas seguidas. Espera un minuto.'});
    scopeQuestionRate.set(who,[...times,now]);
    if(scopeQuestionRate.size>300)scopeQuestionRate.clear();
    pendingScopeDialogs.set(sessionId,{context:decision.context,at:now,rounds:(prior?.rounds||0)+1});
    return res.json({answer:decision.reason,source:'scope-clarification',scopeTopic:decision.topic,
      filesUsed:[],webSearched:false,webSources:[],webCached:false,needsClarification:true});
  }
  pendingScopeDialogs.delete(sessionId);
  if(decision.forward) req.body.message=decision.forward;
  next();
});
'''
    return one(src,existing,insert+'\n'+existing,'middleware de chat')

def main_patch(src):
    anchor="import App from './App.jsx';"
    src=one(src,anchor,anchor+"\nimport {AppErrorBoundary,RuntimeErrorNotice} from './components/AppErrorBoundary.jsx';",'import boundary')
    old='''  <React.StrictMode>
    <App />
  </React.StrictMode>'''
    new='''  <React.StrictMode>
    <AppErrorBoundary>
      <RuntimeErrorNotice />
      <App />
    </AppErrorBoundary>
  </React.StrictMode>'''
    return one(src,old,new,'cobertura react')

CSS_EXTRA='''
/* ISO-QA07: errores de interfaz discretos, accesibles y contenidos */
.iso-error-boundary {max-width:630px;margin:12vh auto;padding:22px;display:flex;align-items:flex-start;gap:13px;border:1px solid var(--line,#ddd);border-radius:14px;background:var(--elevated,#fff);color:var(--ink,#222);font:14px/1.55 system-ui,sans-serif;}
.iso-error-boundary p {margin:5px 0 0;}
.iso-error-boundary button {display:inline-flex;align-items:center;gap:6px;margin-left:auto;border:1px solid var(--line,#ddd);background:transparent;border-radius:8px;padding:8px 10px;color:inherit;white-space:nowrap;cursor:pointer;}
.iso-runtime-notice {position:fixed;right:16px;bottom:16px;max-width:min(420px,calc(100vw - 32px));z-index:9999;display:flex;align-items:center;gap:10px;box-shadow:0 8px 30px #0002;padding:11px 13px;border-radius:11px;border:1px solid #d977063b;background:var(--elevated,#fff);color:var(--ink,#222);font:12px/1.4 system-ui,sans-serif;overflow-wrap:anywhere;}
.iso-runtime-notice button {margin-left:auto;display:flex;align-items:center;border:0;background:transparent;color:inherit;cursor:pointer;}
.diagram-error,.upload-error,.chat-error,.message-body,.markdown {min-width:0;max-width:100%;overflow-wrap:anywhere;}
@media(max-width:520px){.iso-error-boundary{margin:8vh 12px;flex-wrap:wrap;}.iso-error-boundary button{margin-left:0;}}
'''

def app_patch(src):
    old='const autoFormats = !demo ? requestedFormat(message) : [];'; new='const autoFormats = (!demo && scopeReceipt) ? requestedFormat(message) : [];'; return one(src,old,new,'exportación solo tras respuesta generada')

def main():
    print('ISO STUDIO 7.2 - QA06 DIALOGO GUIADO + QA07 ERRORES CONTROLADOS')
    for p in [SCOPE,INDEX,MAIN,APP,CSS]:
        if not p.is_file():raise RuntimeError('Falta archivo esperado: '+str(p))
    orig={p:p.read_text(encoding='utf-8-sig') for p in [SCOPE,INDEX,MAIN,APP,CSS]}
    if MARK in orig[INDEX]:
        print('El parche ya está aplicado; no se duplican reglas.');return
    if 'suppressErrorRendering:true' not in (ROOT/'src/components/MermaidDiagram.jsx').read_text(encoding='utf-8-sig'):
        raise RuntimeError('Instala primero QA-05 Mermaid. No se alteró ningún archivo.')
    if TRIAGE.exists() or TEST.exists() or BOUNDARY.exists():raise RuntimeError('Los archivos destino ya existen, revisar antes de sobrescribir.')
    changed={SCOPE:scope_patch(orig[SCOPE]),INDEX:index_patch(orig[INDEX]),MAIN:main_patch(orig[MAIN]),APP:app_patch(orig[APP]),CSS:orig[CSS]+CSS_EXTRA}
    back=ROOT/'.scope-backups'/('pre_qa06_qa07_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    back.mkdir(parents=True,exist_ok=False)
    for p in changed:
        b=back/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    dist=ROOT/'dist';dist_backup=back/'dist_previous'
    try:
        for p,body in changed.items():p.write_text(body,encoding='utf-8')
        shutil.copy2(HERE/'intent-triage.js',TRIAGE)
        shutil.copy2(HERE/'intent-triage.test.js',TEST)
        shutil.copy2(HERE/'AppErrorBoundary.jsx',BOUNDARY)
        testfiles=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('scope*.test.js'))
        testfiles.append('tests/intent-triage.test.js')
        r=subprocess.run(['node','--test',*testfiles],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=120)
        print('\n'.join(r.stdout.splitlines()[-45:]))
        if r.returncode:raise RuntimeError('Fallaron las pruebas; revisa el fallo.')
        if dist.exists():dist.rename(dist_backup)
        print('Compilando React...')
        build=subprocess.run(['npm.cmd' if sys.platform=='win32' else 'npm','run','build'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=210)
        print('\n'.join(build.stdout.splitlines()[-17:]))
        if build.returncode:raise RuntimeError('Compilación fallida, se restaurará la versión anterior.')
    except BaseException:
        for p in changed:shutil.copy2(back/p.relative_to(ROOT),p)
        TRIAGE.unlink(missing_ok=True);TEST.unlink(missing_ok=True);BOUNDARY.unlink(missing_ok=True)
        if dist.exists():shutil.rmtree(dist)
        if dist_backup.exists():dist_backup.rename(dist)
        print('REVERSIÓN: se restauró el código y, si existía, la interfaz anterior.')
        raise
    print('OK QA06/QA07: tests PASS, React compilado. Respaldo:',back)
    print('Reinicia SOLO node server/index.js y recarga la web con Ctrl+Shift+R.')
    print('No se han modificado n8n, Qdrant, ni credenciales. SCOPE_N8N_REVIEWED permanece igual.')

if __name__=='__main__':
    try:main()
    except Exception as e:print('ERROR:',str(e),file=sys.stderr);sys.exit(1)
