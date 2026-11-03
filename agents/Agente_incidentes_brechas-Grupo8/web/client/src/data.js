/* Metadatos de presentación: nada de esto altera lo que decide el agente. */

export const ETAPAS = [
  { p: '01-', t: 'Triaje', f: 'Detectar y evaluar' },
  { p: '02-', t: 'Severidad', f: 'Evaluar y decidir' },
  { p: '03-', t: 'Notificación', f: 'Responder' },
  { p: '04-', t: 'Respuesta y cierre', f: 'Responder · aprender' },
  { p: '00-', t: 'Informe', f: 'Decisión humana' },
];

export const NOMBRES = {
  '00-informe.md': 'Informe',
  '01-ficha-incidente.md': 'Ficha de triaje',
  '02-evaluacion-severidad.md': 'Severidad y decisión',
  '03-notificacion-anpd.md': 'Notificación a la ANPD',
  '03-comunicacion-titulares.md': 'Aviso a los titulares',
  '03-aviso-cnsd.md': 'Aviso al CNSD',
  '04-respuesta-y-cierre.md': 'Respuesta y cierre',
};

export const GRUPOS = [
  ['Resumen', ['00-informe.md']],
  ['Evaluación', ['01-ficha-incidente.md', '02-evaluacion-severidad.md']],
  ['Notificaciones', ['03-notificacion-anpd.md', '03-comunicacion-titulares.md', '03-aviso-cnsd.md']],
  ['Respuesta', ['04-respuesta-y-cierre.md']],
];

export const NORMAS = ['ISO/IEC 27035', 'ISO/IEC 27001/27002', 'ISO/IEC 27701', 'ISO/IEC 27037', 'NIST SP 800-61r3', 'ENISA', 'D.S. 016-2024-JUS'];

export const nivel = s => (/muy alta|cr[ií]tica/i.test(s || '') ? 'bad' : /alta|media/i.test(s || '') ? 'warn' : s ? 'ok' : '');

export const fmtRestante = ms => {
  const a = Math.abs(ms), h = Math.floor(a / 36e5), m = Math.floor((a % 36e5) / 6e4);
  return `${h} h ${String(m).padStart(2, '0')} min`;
};
