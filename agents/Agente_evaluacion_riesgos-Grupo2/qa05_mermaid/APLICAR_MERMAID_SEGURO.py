# ISO Studio 7.2 - QA-05: render Mermaid sin errores globales en la pagina.
# Unicamente parchea frontend React + CSS y agrega tests. No modifica backend ni n8n.
from pathlib import Path
from datetime import datetime
import sys, shutil, subprocess

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
component=root/'src'/'components'/'MermaidDiagram.jsx'
css=root/'src'/'styles.css'
helper=root/'src'/'components'/'mermaid-safe.js'
tests=root/'tests'/'mermaid-safe.test.js'
package_dir=Path(__file__).resolve().parent
marker='suppressErrorRendering:true'
print('ISO STUDIO 7.2 - QA-05: Mermaid seguro, sin errores gigantes fuera del chat')
if not component.is_file() or not css.is_file():
    sys.exit('ERROR: no se encuentra la instalacion en '+str(root))
orig=component.read_text(encoding='utf-8')
css_orig=css.read_text(encoding='utf-8')
if marker in orig:
    print('QA-05 ya aplicado; no se duplica. Para recompilar ejecuta npm run build.')
    sys.exit(0)
if helper.exists() or tests.exists():
    sys.exit('ERROR: existen archivos mermaid-safe; revision manual antes de sobrescribir.')

old_init="mermaid.initialize({startOnLoad:false,securityLevel:'strict',htmlLabels:false,theme:'neutral',flowchart:{useMaxWidth:true},maxTextSize:16000});"
old_render='''export async function makeMermaidSVG(source){
  if(typeof source!=='string'||source.length>16000) throw new Error('El diagrama es demasiado grande.');
  const id=`iso-${crypto.randomUUID().replace(/-/g,'')}`;
  const result=await mermaid.render(id,source);
  return cleanSVG(result.svg);
}'''
new_render='''// Se serializan los renderizados para evitar interferencia entre varios diagramas del chat.
let renderQueue = Promise.resolve();
async function validatedRender(source){
  if(typeof source!=='string'||!source.trim()||source.length>16000)
    throw new Error('El diagrama está vacío o excede el tamaño permitido.');
  let code=source.trim();
  // Meridian v11: evita que el renderizador inyecte su SVG global de error.
  const originalValid=await mermaid.parse(code,{suppressErrors:true});
  if(!originalValid){
    const repaired=normalizeFlowchartLabels(code);
    const fixedValid=repaired!==code && await mermaid.parse(repaired,{suppressErrors:true});
    if(!fixedValid) throw new Error('Sintaxis Mermaid no válida. Solicita regenerar el diagrama.');
    code=repaired;
  }
  const id=`iso-${crypto.randomUUID().replace(/-/g,'')}`;
  const result=await mermaid.render(id,code);
  const safeSVG=cleanSVG(result.svg);
  if(!/^\\s*<svg\\b/i.test(safeSVG)) throw new Error('No se pudo representar el diagrama.');
  return safeSVG;
}
export function makeMermaidSVG(source){
  const task=renderQueue.then(()=>validatedRender(source));
  renderQueue=task.catch(()=>{});
  return task;
}'''
old_effect="let active=true;setBusy(true);setError('');"
new_effect="let active=true;setBusy(true);setError('');setSVG('');"
old_ui='error?<div className="diagram-error"><AlertTriangle size={17}/> {error}<pre>{source}</pre></div>'
new_ui='error?<div className="diagram-error"><AlertTriangle size={17}/> <span>{error}</span><details><summary>Ver código Mermaid</summary><pre>{source}</pre></details></div>'
for label,needle in [('initialize',old_init),('render',old_render),('efecto',old_effect),('interfaz',old_ui)]:
    if orig.count(needle)!=1:
        sys.exit(f'ERROR: el componente no coincide con la versión esperada ({label}); sin cambios.')
if css_orig.count('.diagram-error pre { white-space: pre-wrap; overflow-wrap: anywhere; }')!=1:
    sys.exit('ERROR: estilos distintos; sin cambios.')

patched=orig.replace("import mermaid from 'mermaid';", "import mermaid from 'mermaid';\nimport {normalizeFlowchartLabels} from './mermaid-safe.js';",1)
patched=patched.replace(old_init,"mermaid.initialize({startOnLoad:false,securityLevel:'strict',htmlLabels:false,theme:'neutral',flowchart:{useMaxWidth:true},maxTextSize:16000,suppressErrorRendering:true});",1)
patched=patched.replace(old_render,new_render,1)
patched=patched.replace(old_effect,new_effect,1).replace(old_ui,new_ui,1)
css_patched=css_orig.replace('.diagram-error pre { white-space: pre-wrap; overflow-wrap: anywhere; }', '''.diagram-error { max-width: 100%; min-width: 0; overflow: hidden; }
.diagram-error details { margin-top: 9px; max-width: 100%; }
.diagram-error summary { cursor: pointer; font-weight: 650; }
.diagram-error pre { white-space: pre-wrap; overflow-wrap: anywhere; max-height: 220px; overflow-y: auto; font-size: 11px; }''',1)
backup=root/'.scope-backups'/('pre_mermaid_QA05_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True,exist_ok=False)
shutil.copy2(component,backup/'MermaidDiagram.jsx')
shutil.copy2(css,backup/'styles.css')
try:
    component.write_text(patched,encoding='utf-8')
    css.write_text(css_patched,encoding='utf-8')
    shutil.copy2(package_dir/'mermaid-safe.js',helper)
    shutil.copy2(package_dir/'mermaid-safe.test.js',tests)
    test_cmd=['node','--test','tests/mermaid-safe.test.js']
    print('Ejecutando pruebas QA-05...')
    result=subprocess.run(test_cmd,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=75)
    print('\n'.join(result.stdout.splitlines()[-23:]))
    if result.returncode: raise RuntimeError('Fallo en pruebas unitarias.');
    print('Compilando interfaz React...')
    build=subprocess.run(['npm.cmd','run','build'],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=200)
    print('\n'.join(build.stdout.splitlines()[-15:]))
    if build.returncode: raise RuntimeError('Error en npm run build.');
except Exception as e:
    shutil.copy2(backup/'MermaidDiagram.jsx',component)
    shutil.copy2(backup/'styles.css',css)
    helper.unlink(missing_ok=True)
    tests.unlink(missing_ok=True)
    print('REVERSION AUTOMATICA: se restauraron los archivos originales.')
    sys.exit('ERROR: '+str(e))
print('\nOK QA-05: frontend corregido, pruebas PASS, compilacion completada.')
print('Respaldo:',backup)
print('Accion: Ctrl+Shift+R en navegador; no reiniciar n8n ni Qdrant.')
print('Los diagramas erroneos mostraran aviso compacto. No se garantiza reparar todo codigo generado incorrectamente.')
