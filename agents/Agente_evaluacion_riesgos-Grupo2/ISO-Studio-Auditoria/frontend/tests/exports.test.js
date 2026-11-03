import test from 'node:test';
import assert from 'node:assert/strict';
import {createPdf,createDocx} from '../server/lib/exporters.js';
const sample = '# Evaluación de prueba\n\nEste es un **documento de prueba** para ISO Studio.\n\n| Riesgo | Nivel |\n| --- | --- |\n| Acceso indebido | Alto |\n\n## Acciones\n\n- Registrar evidencias\n- Verificar controles\n';
test('generates a binary PDF with expected header', async()=>{
 const file=await createPdf({title:'Evaluación de prueba',markdown:sample});
 assert.equal(file.subarray(0,5).toString(),'%PDF-');
 assert.ok(file.length>500,'expected non-empty PDF');
});
test('generates a DOCX ZIP structure', async()=>{
 const file=await createDocx({title:'Evaluación de prueba',markdown:sample});
 assert.equal(file.subarray(0,2).toString(),'PK');
 assert.ok(file.length>1000,'expected non-empty DOCX');
});
