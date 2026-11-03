import React, { useEffect, useRef, useState } from 'react';
import { api, del } from '../api.js';
import { ETAPAS } from '../data.js';

export default function Progreso({ jobId, onDone, onBack }) {
  const [j, setJ] = useState(null);
  const logRef = useRef(null);

  useEffect(() => {
    let vivo = true, t;
    const poll = async () => {
      try {
        const x = await api('/api/job/' + jobId);
        if (!vivo) return;
        setJ(x);
        if (x.status === 'running') t = setTimeout(poll, 2000);
        else if (x.status === 'done' && x.incidente) onDone(x.incidente);
      } catch { if (vivo) t = setTimeout(poll, 3000); }
    };
    poll();
    return () => { vivo = false; clearTimeout(t); };
  }, [jobId]);

  useEffect(() => { if (logRef.current) logRef.current.scrollTop = 1e6; }, [j]);

  const ev = j ? j.eventos : [];
  const hechas = ETAPAS.map(e => ev.some(x => x.texto.startsWith('Escribiendo') && x.texto.includes('/' + e.p)));
  const ult = hechas.lastIndexOf(true);
  const act = hechas.every(Boolean) ? -1 : Math.max(ult + 1, 0);
  const corriendo = !j || j.status === 'running';
  const fallo = j && (j.status === 'error' || (j.status === 'done' && !j.incidente));

  return (
    <>
      <div className="steps">
        {ETAPAS.map((e, i) => (
          <div key={e.p} className={'step ' + (hechas[i] ? 'done' : i === act && corriendo ? 'now' : '')}>
            <small>{e.f}</small><b>{hechas[i] ? '✓ ' : ''}{e.t}</b>
          </div>
        ))}
      </div>
      <div className="card">
        <header>
          <h2>{corriendo && <span className="spin" />}{fallo ? 'No se pudo completar' : corriendo ? 'Analizando' : 'Listo'}{j ? ` · ${j.segundos} s` : ''}{j && j.incidente ? ` · ${j.incidente}` : ''}</h2>
          <span className="sp" />
          {corriendo ? (
            <button className="btn sm danger" onClick={async () => {
              try { await del('/api/job/' + jobId); } catch {}
              onBack();
            }}>Cancelar</button>
          ) : (
            <button className="btn sm" onClick={onBack}>Volver</button>
          )}
        </header>
        <div className="body">
          <p className="hint" style={{ margin: '0 0 10px' }}>{corriendo ? (ev.length ? ev[ev.length - 1].texto : 'Iniciando el agente…') : 'Análisis terminado.'}</p>
          <details><summary className="link" style={{ cursor: 'pointer' }}>Ver el detalle de lo que lee y escribe el agente</summary>
            <div className="log" ref={logRef} style={{ marginTop: 10 }}>
              {ev.length === 0 ? 'Iniciando el agente…' : ev.map((e, i) => <div key={i}>{String(Math.round(e.t / 1000)).padStart(3, ' ')} s  {e.texto}</div>)}
            </div>
          </details>
          {fallo && <div className="err">{j.error || 'El agente terminó sin generar un expediente. ' + (j.resultado || '')}</div>}
        </div>
      </div>
    </>
  );
}
