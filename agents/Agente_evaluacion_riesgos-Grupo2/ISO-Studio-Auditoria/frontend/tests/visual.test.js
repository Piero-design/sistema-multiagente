import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {createVisualService,makeMockSvg} from '../server/lib/visual.js';
test('SVG de prueba escapa contenido sin incluir código HTML',()=>{const s=makeMockSvg('<script>alert(1)</script>','portada');assert.ok(s.includes('&lt;script&gt;'));assert.ok(!s.includes('<script>'));});
test('genera e identifica imágenes por sesión',async()=>{const root=fs.mkdtempSync(path.join(os.tmpdir(),'iso-visual-'));try{
 const svc=createVisualService({root,provider:'mock'});const sid='d9c7617c-c12c-4ab7-a932-193ea59f78e6';
 const result=await svc.generate({prompt:'Proceso de auditoría de sistemas',title:'Prueba',style:'infografia',sessionId:sid});
 assert.equal(result.code,200);assert.equal(svc.history(sid).length,1);assert.equal(svc.history('38af8fb3-27c9-4583-abcd-c100b30e9264').length,0);
 assert.ok(svc.fileFor(result.asset.id,sid));assert.equal(svc.fileFor(result.asset.id,'38af8fb3-27c9-4583-abcd-c100b30e9264'),null);
}finally{fs.rmSync(root,{recursive:true,force:true})}});
test('requiere código fuerte para proveedor de pago',async()=>{const root=fs.mkdtempSync(path.join(os.tmpdir(),'iso-visual-'));try{
 const svc=createVisualService({root,provider:'openai',apiKey:'test-key',accessCode:'cortito'});
 const result=await svc.generate({prompt:'Una portada minimalista',title:'Prueba',style:'portada',sessionId:'d9c7617c-c12c-4ab7-a932-193ea59f78e6',authorization:'cortito'});
 assert.equal(result.code,403);
}finally{fs.rmSync(root,{recursive:true,force:true})}});
