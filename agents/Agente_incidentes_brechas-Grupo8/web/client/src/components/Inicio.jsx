import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';

const ACEPTA = '.txt,.md,.log,.eml,.csv,.json,text/*';

export default function Inicio({ config, form, setForm, onRun }) {
  const [msg, setMsg] = useState('');
  const [archivo, setArchivo] = useState('');
  const [drag, setDrag] = useState(false);
  const [demo, setDemo] = useState(null);
  const input = useRef(null);
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  useEffect(() => { api('/api/archivos-demo').then(setDemo).catch(() => setDemo(null)); }, []);

  async function lee(file) {
    if (!file) return;
    if (file.size > 1.5e6) { setMsg(`${file.name} supera 1,5 MB.`); return; }
    const t = await file.text();
    if (t.includes('\u0000')) { setMsg(`${file.name} no es un archivo de texto.`); return; }
    set('reporte', t); setArchivo(file.name); setMsg('');
    // Si el correo tiene más de un día (casos de demostración), la hora actual se fija una hora después para que el plazo de 48 h tenga sentido.
    const m = t.match(/Fecha del (?:correo|mensaje)(?::\*\*|:)\s*(\d{4})-(\d{2})-(\d{2})[^\d]*(\d{2}):(\d{2})/);
    if (m) {
      const d = new Date(+m[1], +m[2] - 1, +m[3], +m[4] + 1, +m[5]);
      if (Date.now() - d.getTime() > 864e5) {
        const p = n => String(n).padStart(2, '0');
        set('ahora', `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())} (-0500)`);
        setMsg('El reporte tiene más de un día: la hora actual se ajustó a 1 h después de su fecha. Cámbiela si hace falta.');
      }
    }
  }
  function lanzar() {
    if (form.reporte.trim().length < 20) { setMsg('Cargue un archivo con el reporte o escríbalo en el cuadro.'); return; }
    onRun();
  }
  const ctx = config.contextos.find(c => c.ruta === form.contexto);

  return (
    <div className="analizar">
      <div className="hero">
        <h2>Analizar un incidente</h2>
        <p>Cargue el reporte (un correo, un mensaje o una nota del equipo) o escríbalo. El agente lo clasifica, mide su gravedad, calcula cuánto tiempo queda para notificar a la ANPD y deja redactados los avisos y el plan de respuesta.</p>
      </div>

      <div className="card">
        <div className="body">
          <div className="lbl-row">
            <label className="l" htmlFor="reporte" style={{ margin: 0 }}>Reporte del incidente</label>
            <span className="sp" />
            <button className="btn sm" onClick={() => input.current.click()}>Cargar desde archivo</button>
            <input ref={input} type="file" accept={ACEPTA} hidden onChange={e => { lee(e.target.files[0]); e.target.value = ''; }} />
          </div>
          <div className={'dz' + (drag ? ' on' : '')}
            onDragEnter={e => { e.preventDefault(); setDrag(true); }} onDragOver={e => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
            onDrop={e => { e.preventDefault(); setDrag(false); lee(e.dataTransfer.files[0]); }}>
            <textarea id="reporte" className="field" value={form.reporte} onChange={e => { set('reporte', e.target.value); setArchivo(''); }}
              placeholder="Escriba o pegue el reporte, o arrastre aquí un archivo .txt, .md o .log." />
            {drag && <div className="dz-over">Suelte el archivo para cargarlo</div>}
          </div>
          {archivo && <div className="chip-file"><span>📄 {archivo}</span><button aria-label="Quitar archivo" onClick={() => { set('reporte', ''); setArchivo(''); }}>✕</button></div>}

          <div className="row" style={{ marginTop: 18 }}>
            <div>
              <label className="l" htmlFor="contexto" style={{ marginTop: 0 }}>Contexto de la organización <span className="hint">· opcional</span></label>
              <select id="contexto" className="field" value={form.contexto} onChange={e => set('contexto', e.target.value)}>
                <option value="">Solo el reporte</option>
                {config.contextos.map(c => <option key={c.ruta} value={c.ruta}>{(c.propio ? 'Subido · ' : 'Demo · ') + c.nombre}</option>)}
              </select>
              <div className="hint" style={{ marginTop: 6, fontSize: 12.5 }}>
                {ctx ? <>{ctx.archivos.length} archivos. <Link to={`/contextos/${ctx.ruta}`}>Ver el contexto</Link></> : <>Con contexto, el agente verifica el reporte con inventario y logs. <Link to="/contextos">Ver contextos</Link></>}
              </div>
            </div>
            <div>
              <label className="l" htmlFor="ahora" style={{ marginTop: 0 }}>Fecha y hora actual <span className="hint">· base del plazo de 48 h</span></label>
              <input id="ahora" className="field" value={form.ahora} onChange={e => set('ahora', e.target.value)} />
            </div>
          </div>

          <button className="btn primary big" onClick={lanzar}>Analizar incidente</button>
          {msg && <div className={/ajust/.test(msg) ? 'hint' : 'err'} style={{ marginTop: 10 }}>{msg}</div>}
        </div>
      </div>

      {demo && demo.reportes.length > 0 && (
        <details className="demo">
          <summary>Archivos de demostración</summary>
          <p className="hint">Descargue un reporte y cárguelo arriba. Todo es simulado. La guía de uso está en <code>archivos-demo/README.md</code>.</p>
          <div className="demo-grid">
            <div><h4>Reportes</h4>{demo.reportes.map(f => <a key={f.nombre} href={`/api/archivos-demo/reportes/${f.nombre}`}>{f.nombre}</a>)}</div>
            <div><h4>Contexto nuevo (para probar la carga)</h4>{demo.contexto.map(f => <a key={f.nombre} href={`/api/archivos-demo/contexto-nuevo/${f.nombre}`}>{f.nombre}</a>)}</div>
          </div>
        </details>
      )}
    </div>
  );
}
