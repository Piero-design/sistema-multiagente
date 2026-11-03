import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api, post, store } from '../api.js';
import Markdown from './Markdown.jsx';
import { GRUPOS, NOMBRES, nivel, fmtRestante } from '../data.js';

function useAhora(ms = 30000) {
  const [n, setN] = useState(Date.now());
  useEffect(() => { const t = setInterval(() => setN(Date.now()), ms); return () => clearInterval(t); }, [ms]);
  return n;
}

function extraeDecisiones(texto = '') {
  const m = texto.match(/##\s*\d*\.?\s*Decisiones[^\n]*\n([\s\S]*?)(?=\n##\s|$)/i);
  return m ? [...m[1].matchAll(/^\s*\d+\.\s+(.*)$/gm)].map(x => x[1]) : [];
}

function Reloj({ limite }) {
  const ahora = useAhora();
  if (!limite) return (
    <div className="kpi"><small>Plazo de notificación · 48 h</small><b className="big">Sin plazo</b><small className="sub">Sin obligación de notificar en este caso</small></div>
  );
  const f = new Date(limite).getTime(), d = f - ahora, ini = f - 48 * 36e5;
  const cls = d < 0 ? 'bad' : d < 12 * 36e5 ? 'warn' : 'ok';
  const pct = Math.min(100, Math.max(2, ((ahora - ini) / (48 * 36e5)) * 100));
  return (
    <div className={'kpi ' + cls}>
      <small>Plazo de notificación · 48 h</small>
      <b className="big">{d < 0 ? 'Vencido hace ' : ''}{fmtRestante(d)}</b>
      <div className="bar"><i style={{ width: pct + '%' }} /></div>
      <small className="sub">Hora límite {limite.replace('T', ' ').slice(0, 16)}</small>
    </div>
  );
}

export default function Caso({ id }) {
  const nav = useNavigate();
  const { doc: docParam } = useParams();
  const [e, setE] = useState(null);
  const [err, setErr] = useState('');
  const [hechas, setHechas] = useState({});
  const [copiado, setCopiado] = useState('Copiar');

  useEffect(() => {
    setE(null); setErr('');
    api('/api/expediente/' + id).then(x => {
      setE(x);
      try { setHechas(JSON.parse(store.get('dec:' + id, '{}'))); } catch { setHechas({}); }
    }).catch(x => setErr(x.message));
  }, [id]);

  const doc = e ? (docParam && e.docs[docParam + '.md'] ? docParam + '.md' : e.docs['00-informe.md'] ? '00-informe.md' : e.files[0]) : '';
  const setDoc = f => nav(`/expedientes/${id}/${f.replace(/\.md$/, '')}`, { replace: true });
  const decisiones = useMemo(() => (e ? extraeDecisiones(e.docs['00-informe.md']) : []), [e]);
  if (err) return <div className="card"><div className="body err">{err}</div></div>;
  if (!e) return <div className="empty">Cargando expediente…</div>;

  const decide = async (aid, decision) => {
    try { const r = await post(`/api/acciones/${id}/${aid}`, { decision }); setE(x => ({ ...x, acciones: r.acciones })); } catch (x) { setErr(x.message); }
  };
  const marca = (i, v) => { const n = { ...hechas, [i]: v }; setHechas(n); store.set('dec:' + id, JSON.stringify(n)); };
  const pendientes = decisiones.filter((_, i) => !hechas[i]).length;
  const grupos = GRUPOS.map(([g, fs]) => [g, fs.filter(f => e.docs[f])]).filter(([, fs]) => fs.length);
  const otros = e.files.filter(f => !NOMBRES[f]);
  const copiar = async () => {
    try { await navigator.clipboard.writeText(e.docs[doc]); setCopiado('Copiado'); } catch { setCopiado('No se pudo copiar'); }
    setTimeout(() => setCopiado('Copiar'), 1500);
  };
  const descargar = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([e.docs[doc]], { type: 'text/markdown' }));
    a.download = `${id}-${doc}`; a.click(); URL.revokeObjectURL(a.href);
  };

  return (
    <>
      <div className="crumbs"><button className="btn sm" onClick={() => nav('/expedientes')}>← Expedientes</button><h2>{id}</h2><span className="sp" /><button className="btn sm primary" onClick={() => nav('/analizar')}>Nuevo análisis</button></div>
      <div className="sla">
        <Reloj limite={e.limite} />
        <div className={'kpi ' + nivel(e.sev)}><small>Severidad</small><b>{(e.sev || 'No aplica').slice(0, 70)}</b></div>
        <div className="kpi"><small>Clasificación</small><b style={{ fontSize: 14 }}>{(e.clasif || '—').slice(0, 150)}</b></div>
      </div>

      {decisiones.length > 0 && (
        <div className="card todo">
          <header><h2>Decisiones que debe tomar una persona</h2><span className="sp" /><span className={'pill ' + (pendientes ? 'warn' : 'ok')}>{pendientes ? `${pendientes} pendientes` : 'Todo revisado'}</span></header>
          <div className="body"><ol>
            {decisiones.map((d, i) => (
              <li key={i} className={hechas[i] ? 'd' : ''}>
                <input type="checkbox" id={'d' + i} checked={!!hechas[i]} onChange={ev => marca(i, ev.target.checked)} />
                <label htmlFor={'d' + i}>{d.replace(/\*\*/g, '').replace(/`/g, '')}</label>
              </li>
            ))}
          </ol></div>
        </div>
      )}

      {e.acciones?.length > 0 && (
        <div className="card todo" style={{ marginBottom: 20 }}>
          <header><h2>Acciones propuestas por el agente</h2><span className="sp" /><span className="pill">{e.acciones.filter(a => a.estado === 'pendiente').length} sin decidir</span></header>
          <div className="body">
            <p className="hint" style={{ marginTop: 0 }}>El agente no ejecuta nada. Aprobar aquí solo deja constancia de la decisión: la acción la realiza el responsable del sistema.</p>
            {e.acciones.map(a => (
              <div key={a.id} className="acc-item">
                <div><b>{a.accion}</b> <span className={'pill ' + (a.urgencia === 'alta' ? 'bad' : a.urgencia === 'media' ? 'warn' : '')}>{a.urgencia}</span> {a.sistema && <span className="pill">{a.sistema}</span>}</div>
                <small className="hint">{a.justificacion}</small>
                <div className="qa">
                  {a.estado === 'pendiente'
                    ? <><button className="btn sm primary" onClick={() => decide(a.id, 'aprobada')}>Aprobar</button><button className="btn sm" onClick={() => decide(a.id, 'rechazada')}>Rechazar</button></>
                    : <span className={'pill ' + (a.estado === 'aprobada' ? 'ok' : 'bad')}>{a.estado === 'aprobada' ? 'Aprobada' : 'Rechazada'} · {a.decidida}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="case-grid">
        <nav className="docnav" role="tablist">
          {grupos.map(([g, fs]) => (
            <React.Fragment key={g}>
              <h4>{g}</h4>
              {fs.map(f => <button key={f} role="tab" aria-selected={doc === f} onClick={() => setDoc(f)}>{NOMBRES[f]}</button>)}
            </React.Fragment>
          ))}
          {otros.map(f => <button key={f} role="tab" aria-selected={doc === f} onClick={() => setDoc(f)}>{f}</button>)}
        </nav>
        <div className="card">
          <header className="docbar"><span className="grow">{NOMBRES[doc] || doc}</span>
            <button className="btn sm" onClick={copiar}>{copiado}</button>
            <button className="btn sm" onClick={descargar}>Descargar .md</button>
          </header>
          <div className="body"><Markdown text={e.docs[doc] || ''} onDoc={f => e.docs[f] && setDoc(f)} /></div>
        </div>
      </div>
      <div className="notice">Borradores de apoyo. Nada fue notificado ni enviado: lo revisa y envía el Oficial de Datos Personales con el responsable de seguridad.</div>
    </>
  );
}
