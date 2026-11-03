import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeFlowchartLabels} from '../src/components/mermaid-safe.js';

test('normaliza nodos con parentesis sin perder semantica',()=>{
 const bad='flowchart TD\n D1[Evaluar consecuencias (organizacion y titulares de PII)]\n D1 --> E[Fin]';
 const result=normalizeFlowchartLabels(bad);
 assert.match(result,/D1\["Evaluar consecuencias \(organizacion y titulares de PII\)"\]/);
 assert.match(result,/D1 --> E\["Fin"\]/);
});
test('respeta etiquetas ya entrecomilladas',()=>{
 const code='flowchart LR\n A["Identificar (riesgos)"] --> B["Evaluar"]';
 assert.equal(normalizeFlowchartLabels(code),code);
});
test('no cambia un sequenceDiagram',()=>{
 const code='sequenceDiagram\n A->>B: Riesgo (evento)';
 assert.equal(normalizeFlowchartLabels(code),code);
});
test('no cambia diagramas no compatibles',()=>{
 const code='classDiagram\n class Cliente';
 assert.equal(normalizeFlowchartLabels(code),code);
});
test('normaliza saltos CRLF',()=>{
 const code='graph TD\r\n A[Analisis (PII)]';
 assert.ok(normalizeFlowchartLabels(code).includes('A["Analisis (PII)"]'));
});
test('no crea etiquetas de nodos falsos',()=>{
 const code='flowchart TD\n A --> B\n classDef alto fill:#faa';
 assert.equal(normalizeFlowchartLabels(code),code);
});
