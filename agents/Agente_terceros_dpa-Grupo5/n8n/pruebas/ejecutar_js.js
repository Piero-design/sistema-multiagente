// Ejecuta PIMS_CALC.ejecutar() sobre un lote de casos (JSON por stdin) y devuelve los resultados (stdout).
const CALC = require('../lib/calcular.js');
let entrada = '';
process.stdin.on('data', (d) => { entrada += d; });
process.stdin.on('end', () => {
  const lote = JSON.parse(entrada);
  const salida = lote.casos.map((c) => {
    const r = CALC.ejecutar({ resultado: c.resultado, config: c.config, jurisdiccion: c.jurisdiccion,
      esquema: lote.esquema, perfil: c.perfil || null, documento: c.documento, fechaRef: c.fechaRef });
    return { codigo: r.codigo, resultado: r.resultado, advertencias: r.advertencias, nerr: r.errores.length };
  });
  process.stdout.write(JSON.stringify(salida));
});
