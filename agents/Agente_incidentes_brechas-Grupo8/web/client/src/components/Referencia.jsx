import React from 'react';

const PASOS = [
  ['Triaje', '¿Es un evento, un incidente o una brecha de datos personales? Clasifica, prioriza (P1 a P4) y arranca el reloj de 48 h.'],
  ['Severidad', 'Calcula SE = DPC × EI + CB (ENISA) y decide si hay que notificar según el art. 34 del reglamento.'],
  ['Notificación', 'Borradores para la ANPD, los titulares y el CNSD con el contenido mínimo del art. 34.2.'],
  ['Respuesta y cierre', 'Contención, evidencia, recuperación, causa raíz y controles ISO/IEC 27002 propuestos.'],
  ['Informe', 'Estado, decisiones humanas pendientes y trazabilidad normativa.'],
];

export default function Referencia() {
  return (
    <div className="grid2">
      <div className="card"><header><h2>Qué hace con un reporte</h2></header>
        <div className="body"><ul className="eval">{PASOS.map(([t, d], i) => <li key={t}><div className="ic">{i + 1}</div><div><b>{t}</b><span>{d}</span></div></li>)}</ul></div></div>
      <div className="card"><header><h2>Normas y límites</h2></header>
        <div className="body">
          <p style={{ marginTop: 0 }}><b>ISO/IEC 27035-1/-2/-3</b> (proceso), <b>27001/27002:2022</b> (controles 5.24 a 5.29, 6.8, 8.13, 8.15), <b>27701</b> (privacidad), <b>27037</b> (evidencia), <b>NIST SP 800-61 Rev. 3</b>, <b>ENISA</b> (severidad) y <b>D.S. 016-2024-JUS</b>, arts. 34 a 36.</p>
          <p className="hint">Cita solo lo que está en <code>knowledge/</code> y marca <code>[VERIFICAR]</code> lo que falta. Nunca dice que algo fue enviado, no recomienda pagar rescates y solo escribe en <code>salidas/</code>.</p>
          <p className="hint">No pegue datos personales reales de afectados: use categorías y cantidades.</p>
        </div></div>
    </div>
  );
}
