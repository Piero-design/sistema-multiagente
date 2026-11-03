import test from 'node:test';
import assert from 'node:assert/strict';
import ExcelJS from 'exceljs';
import {createXlsx} from '../server/lib/spreadsheets.js';

const sample=`# Auditoría de la Universidad Ejemplo

Evaluación con información ficticia, pendiente de validar.

| ID | Riesgo | Impacto | Probabilidad | Responsable | Tratamiento |
| --- | --- | --- | --- | --- | --- |
| R-01 | Pérdida de información | Alto | Media | Sistemas | Copias de seguridad |
| R-02 | Acceso indebido | Medio | Alta | Seguridad | MFA |
| R-03 | Fallo operativo | Bajo | Baja | Infraestructura | Pruebas |

## Recomendaciones

- Actualizar procedimientos
- Documentar controles
`;

test('genera un XLSX legible, hojas y formulas controladas', async()=>{
  const bytes=await createXlsx({title:'Matriz de auditoría',markdown:sample});
  assert.equal(bytes.subarray(0,2).toString(),'PK');
  const wb=new ExcelJS.Workbook();await wb.xlsx.load(bytes);
  const overview=wb.getWorksheet('Resumen');const risk=wb.getWorksheet('Matriz de riesgos');
  assert.ok(overview);assert.ok(risk);assert.ok(wb.getWorksheet('Contenido'));
  assert.equal(risk.getCell('A5').value,'R-01');
  assert.equal(risk.getCell('G5').value,3);
  assert.equal(risk.getCell('H5').value,2);
  assert.match(risk.getCell('I5').value.formula,/G5\*H5/);
  assert.match(risk.getCell('J5').value.formula,/IF/);
  assert.match(overview.getCell('B13').value.formula,/COUNTIF/);
  assert.ok(bytes.length>3000);
});

test('no interpreta formulas inyectadas desde Markdown',async()=>{
  const markdown='| Riesgo | Impacto | Probabilidad | Nota |\n| --- | --- | --- | --- |\n| Ejemplo | Alto | Baja | =HYPERLINK("http://example.com","click") |';
  const bytes=await createXlsx({title:'Prueba segura',markdown});
  const wb=new ExcelJS.Workbook();await wb.xlsx.load(bytes);
  const cell=wb.getWorksheet('Matriz de riesgos').getCell('D5');
  assert.equal(typeof cell.value,'string');
  assert.ok(!cell.formula);
  assert.ok(cell.value.startsWith("'="));
});

test('sin tablas produce hojas de resumen y contenido sin inventar riesgos',async()=>{
  const bytes=await createXlsx({title:'Informe narrativo',markdown:'# Resumen\n\nUna conclusión cualitativa.'});
  const wb=new ExcelJS.Workbook();await wb.xlsx.load(bytes);
  assert.deepEqual(wb.worksheets.map(s=>s.name).sort(),['Contenido','Resumen']);
});
