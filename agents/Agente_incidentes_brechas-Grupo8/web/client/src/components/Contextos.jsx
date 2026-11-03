import React, { useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { post } from '../api.js';

const CATS = [
  ['auto', 'Detectar por el nombre (recomendado)'], ['inventario', 'Inventario de sistemas y datos'], ['logs', 'Logs y registros'],
  ['politicas', 'Políticas y procedimientos'], ['app', 'Código o configuración'], ['otros', 'Otros'],
];
export const NOMBRE_CAT = { inventario: 'Inventario', logs: 'Logs', politicas: 'Políticas', app: 'Código', otros: 'Otros' };

export function detecta(nombre, sel = 'auto') {
  if (sel !== 'auto') return sel;
  const n = nombre.toLowerCase();
  if (/\.(log|out|evtx?|syslog)$|log|firewall|auth|access|acceso|antivirus|audit/.test(n)) return 'logs';
  if (/inventario|activos|rat|contactos|registro|datos/.test(n)) return 'inventario';
  if (/politic|procedimiento|plan|norma|seguridad|manual|documento/.test(n)) return 'politicas';
  if (/\.(py|js|ts|php|java|cs|go|rb|yml|yaml|conf|ini|env|sql|xml)$/.test(n)) return 'app';
  return 'otros';
}
export const grupoDe = ruta => (ruta.includes('/') ? ruta.split('/')[0] : 'otros');

/* Lista de contextos disponibles */
export function ListaContextos({ config }) {
  return (
    <>
      <div className="crumbs"><h2 style={{ fontSize: 22 }}>Contextos de organización</h2><span className="sp" /><Link className="btn primary" to="/contextos/nuevo">Nuevo contexto</Link></div>
      <p className="hint" style={{ maxWidth: '70ch', marginTop: -6 }}>Un contexto es lo que el agente sabe de una organización: inventario de sistemas y datos, contactos, políticas y logs. Con él verifica el reporte y cita <code>archivo:línea</code>.</p>
      {config.contextos.length === 0 && <div className="card"><div className="body empty">Aún no hay contextos.</div></div>}
      <div className="ctx-grid">
        {config.contextos.map(c => {
          const cuenta = {};
          c.archivos.forEach(a => { const g = grupoDe(a.ruta); cuenta[g] = (cuenta[g] || 0) + 1; });
          return (
            <Link key={c.ruta} to={`/contextos/${c.ruta}`} className="ctx-card">
              <span className={'pill ' + (c.propio ? 'acc' : '')}>{c.propio ? 'Subido' : 'Demo'}</span>
              <b>{c.nombre}</b>
              <small>{c.archivos.length} archivos</small>
              <span className="tg">{Object.entries(cuenta).map(([g, n]) => <span key={g}>{NOMBRE_CAT[g] || g} {n}</span>)}</span>
            </Link>
          );
        })}
      </div>
    </>
  );
}

/* Cargar un contexto nuevo (o agregar archivos a uno subido) */
export function NuevoContexto({ reload, setForm }) {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [nombre, setNombre] = useState(params.get('org') || '');
  const [cat, setCat] = useState('auto');
  const [pend, setPend] = useState([]);
  const [pegaN, setPegaN] = useState('');
  const [pega, setPega] = useState('');
  const [msg, setMsg] = useState('');
  const [on, setOn] = useState(false);
  const [busy, setBusy] = useState(false);
  const input = useRef(null);

  async function agrega(files) {
    const nuevos = [];
    for (const f of files) {
      if (f.size > 1.5e6) { setMsg(`${f.name} supera 1,5 MB y se omitió.`); continue; }
      const t = await f.text();
      if (t.includes('\u0000')) { setMsg(`${f.name} no es un archivo de texto y se omitió.`); continue; }
      nuevos.push({ nombre: f.name.split('/').pop(), texto: t });
    }
    setPend(p => [...p.filter(x => !nuevos.some(n => n.nombre === x.nombre)), ...nuevos]);
  }
  async function guardar() {
    const todos = [...pend];
    if (pega.trim()) todos.push({ nombre: pegaN.trim() || `nota-${Date.now()}.md`, texto: pega });
    if (!nombre.trim()) { setMsg('Escriba el nombre de la organización.'); return; }
    if (!todos.length) { setMsg('Agregue al menos un archivo o pegue un texto.'); return; }
    setBusy(true); setMsg('Guardando…');
    try {
      const r = await post('/api/contexto', { nombre, archivos: todos.map(x => ({ ruta: `${detecta(x.nombre, cat)}/${x.nombre}`, texto: x.texto })) });
      await reload();
      setForm(f => ({ ...f, contexto: r.ruta }));
      nav('/contextos/' + r.ruta);
    } catch (e) { setMsg(e.message); setBusy(false); }
  }

  return (
    <div className="analizar">
      <div className="crumbs"><Link className="btn sm" to="/contextos">← Contextos</Link><h2>Nuevo contexto</h2></div>
      <div className="card"><div className="body">
        <p className="hint" style={{ margin: '0 0 4px' }}>El agente lee estos archivos para verificar el reporte. Solo texto (.md, .txt, .log, .csv, .json, código). Use datos de prueba o anonimizados.</p>
        <label className="l" htmlFor="c-nombre">Organización</label>
        <input id="c-nombre" className="field" list="c-lista" value={nombre} onChange={e => setNombre(e.target.value)} placeholder="Ej.: Escuela de Posgrado (simulada)" />
        <label className="l" htmlFor="c-cat">Qué son estos archivos</label>
        <select id="c-cat" className="field" value={cat} onChange={e => setCat(e.target.value)}>{CATS.map(([v, t]) => <option key={v} value={v}>{t}</option>)}</select>
        <button type="button" className={'drop' + (on ? ' on' : '')} onClick={() => input.current.click()}
          onDragEnter={e => { e.preventDefault(); setOn(true); }} onDragOver={e => { e.preventDefault(); setOn(true); }} onDragLeave={() => setOn(false)}
          onDrop={e => { e.preventDefault(); setOn(false); agrega([...e.dataTransfer.files]); }}>
          <b>Arrastre archivos aquí</b> o pulse para elegirlos<br /><small>Varios a la vez · máximo 60 y 1,5 MB cada uno</small>
        </button>
        <input ref={input} type="file" multiple hidden onChange={async e => { await agrega([...e.target.files]); e.target.value = ''; }} />
        {pend.length > 0 && <div className="pend">{pend.map((x, i) => (
          <div key={x.nombre}><code>{detecta(x.nombre, cat)}/{x.nombre}</code><small>{(x.texto.length / 1024).toFixed(1)} KB</small>
            <button aria-label="Quitar" onClick={() => setPend(p => p.filter((_, j) => j !== i))}>✕</button></div>
        ))}</div>}
        <label className="l" htmlFor="c-pega">O pegue un texto <span className="hint">· se guarda como archivo</span></label>
        <input className="field" style={{ marginBottom: 8 }} value={pegaN} onChange={e => setPegaN(e.target.value)} placeholder="nombre.md" aria-label="Nombre del archivo pegado" />
        <textarea id="c-pega" className="field" style={{ minHeight: 100 }} value={pega} onChange={e => setPega(e.target.value)} placeholder="Ej.: inventario de sistemas, un fragmento de log, la política de respaldos…" />
        <div className="actions"><button className="btn primary" onClick={guardar} disabled={busy}>Guardar contexto</button><span className="grow hint">{msg}</span></div>
      </div></div>
    </div>
  );
}
