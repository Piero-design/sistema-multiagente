import React from 'react';
import { nivel } from '../data.js';

export default function Expedientes({ lista, abre }) {
  if (!lista.length) return <div className="card"><div className="body empty">Aún no hay expedientes. Analice un caso y aparecerá aquí.</div></div>;
  return (
    <div className="exps">
      {lista.map(e => (
        <button key={e.id} className="exp" onClick={() => abre(e.id)}>
          <span className={'dot ' + nivel(e.sev || e.clasif)} />
          <span className="gr"><b>{e.id}</b><small>{(e.sev || e.clasif || 'Sin datos').slice(0, 90)}</small></span>
          <span className="pill">{e.files.length} documentos</span>
        </button>
      ))}
    </div>
  );
}
