import test from 'node:test';
import assert from 'node:assert/strict';
import {parseBlocks, safeBaseName} from '../server/lib/markdown.js';
test('parses reports, tables and diagrams', () => {
 const b=parseBlocks('# Informe\n\n**Resumen** con [fuente](https://site).\n\n| Riesgo | Nivel |\n| --- | --- |\n| Fuga | Alto |\n\n```mermaid\nflowchart TD\nA-->B\n```');
 assert.deepEqual(b.map(x=>x.type),['heading','paragraph','table','diagram']);
 assert.equal(b[1].text, 'Resumen con fuente.');
 assert.deepEqual(b[2].rows,[['Fuga','Alto']]);
});
test('sanitizes filenames',()=>assert.equal(safeBaseName('../../área de riesgos:1'),'area-de-riesgos-1'));
