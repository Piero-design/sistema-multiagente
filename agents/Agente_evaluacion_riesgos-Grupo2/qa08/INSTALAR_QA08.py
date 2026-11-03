# -*- coding: utf-8 -*-
"""QA-08: detener aclaraciones fuera de tema y normalizar matrices ficticias.
Solo modifica server/lib/intent-triage.js y agrega tests/intent-triage.qa08.test.js.
No altera el backend de QA04, Qdrant, n8n, .env ni la interfaz React.
"""
from pathlib import Path
from datetime import datetime
import subprocess,shutil,sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos')
SRC=ROOT/'server'/'lib'/'intent-triage.js'
TEST=ROOT/'tests'/'intent-triage.qa08.test.js'
INDEX=ROOT/'server'/'index.js'
NEW=HERE/'intent-triage.js'
NEW_TEST=HERE/'intent-triage.qa08.test.js'

def main():
    print('ISO STUDIO 7.2 | QA-08: CIERRE CONTEXTUAL Y MATRICES FICTICIAS')
    if not SRC.exists() or not INDEX.exists():
        raise RuntimeError('Falta el clasificador QA-06. Primero instala QA-06/QA-07.')
    original=SRC.read_text(encoding='utf-8-sig')
    if 'triageScopeMessage' not in original or 'pendingScopeDialogs' not in INDEX.read_text(encoding='utf-8-sig'):
        raise RuntimeError('La versión del clasificador o del backend no corresponde a QA-06. No se modificó nada.')
    desired=NEW.read_text(encoding='utf8')
    if original==desired and TEST.is_file() and TEST.read_text(encoding='utf8')==NEW_TEST.read_text(encoding='utf8'):
        print('QA-08 ya está instalado y coincide con el paquete; no se modifican archivos.');return
    backup=ROOT/'.scope-backups'/('pre_qa08_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    backup.mkdir(parents=True,exist_ok=False)
    had_test=TEST.is_file()
    old_test=TEST.read_bytes() if had_test else None
    old_src=SRC.read_bytes()
    try:
        SRC.write_text(desired,encoding='utf8')
        TEST.write_text(NEW_TEST.read_text(encoding='utf8'),encoding='utf8')
        rel=str(SRC.relative_to(ROOT));target=backup/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_src)
        if had_test:
            target=backup/str(TEST.relative_to(ROOT));target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_test)
        checks=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('scope*.test.js'))
        checks+=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('intent-triage*.test.js'))
        print('Ejecutando',len(checks),'archivos de pruebas (alcance anterior + QA-08)...')
        result=subprocess.run(['node','--test',*checks],cwd=ROOT,encoding='utf8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        print('\n'.join(result.stdout.splitlines()[-65:]))
        if result.returncode:raise RuntimeError('Fallaron las pruebas. Se revierte el cambio.')
    except BaseException:
        SRC.write_bytes(old_src)
        if had_test:TEST.write_bytes(old_test)
        else:TEST.unlink(missing_ok=True)
        print('REVERSIÓN COMPLETA: clasificador anterior restaurado.')
        raise
    print('OK QA-08: todas las pruebas PASS. Respaldo:',backup)
    print('Modificados exclusivamente: server/lib/intent-triage.js y tests/intent-triage.qa08.test.js')
    print('Reinicia el servidor node server/index.js. No reinicies n8n ni Qdrant.')
    print('No se habilita ningún clasificador Gemini adicional ni se altera SCOPE_N8N_REVIEWED.')

if __name__=='__main__':
    try:main()
    except Exception as ex:print('ERROR:',ex,file=sys.stderr);sys.exit(1)
