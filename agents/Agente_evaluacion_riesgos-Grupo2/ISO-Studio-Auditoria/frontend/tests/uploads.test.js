import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {extractDocument, UploadStore, findRelevantSections, validSession} from '../server/lib/uploads.js';

const session='cb3e99d5-2d10-4eb4-895c-785bc107a137';
test('extrae texto UTF-8 y conserva el nombre del archivo', async()=>{
  const r=await extractDocument({buffer:Buffer.from('ORION-8152\nResponsable: Unidad de Transformacion Digital'),originalname:'ensayo.txt'});
  assert.equal(r.type,'txt'); assert.equal(r.name,'ensayo.txt'); assert.match(r.sections[0].text,/ORION-8152/);
});
test('rechaza un PDF con cabecera incorrecta',async()=>{
  await assert.rejects(extractDocument({buffer:Buffer.from('falso'),originalname:'falso.pdf'}),/formato/);
});
test('asocia documentos a una sola conversación, permite recuperación y borrado',async()=>{
  const folder=fs.mkdtempSync(path.join(os.tmpdir(),'studio-upload-test-'));
  try{
    const store=new UploadStore(folder);const d=store.add(session,{name:'prueba.txt',type:'txt',size:20,characters:11,sections:[{label:'sección 1',text:'ORION-8152'}]});
    assert.equal(store.select(session,[d.id])[0].name,'prueba.txt');
    assert.throws(()=>store.select('other-session-000000',[d.id]),/otra conversación/);
    const storeRestarted=new UploadStore(folder);assert.equal(storeRestarted.select(session,[d.id]).length,1);
    assert.ok(storeRestarted.remove(d.id,session));assert.equal(storeRestarted.forSession(session).length,0);
  }finally{fs.rmSync(folder,{recursive:true,force:true});}
});
test('prioriza el fragmento que coincide con la consulta',()=>{
  const f=[{name:'prueba.txt',sections:[{label:'sección 1',text:'documento introductorio'},{label:'sección 2',text:'El identificador es ORION-8152 y el encargado es el área de sistemas.'}]}];
  const result=findRelevantSections(f,'¿Cuál es el identificador ORION?');
  assert.ok(result.indexOf('sección 2')<result.indexOf('sección 1'));
});
test('identificador de sesión válido',()=>{assert.ok(validSession(session));assert.equal(validSession('../../etc/passwd'),false);});
