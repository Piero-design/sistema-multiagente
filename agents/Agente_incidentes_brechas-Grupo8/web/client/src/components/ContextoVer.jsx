import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, del } from '../api.js';
import Markdown from './Markdown.jsx';
import { NOMBRE_CAT, grupoDe } from './Contextos.jsx';

const ORDEN = ['inventario', 'politicas', 'logs', 'app', 'otros'];

function Visor({ ruta, texto }) {
  if (/\.md$/i.test(ruta)) return <Markdown text={texto} />;
  const lineas = texto.replace(/\r/g, '').split('\n');
  if (lineas[lineas.length - 1] === '') lineas.pop();
  return (
    <div className="code" role="region" aria-label={`Contenido de ${ruta}`}>
      {lineas.map((l, i) => <div key={i} className="ln"><span>{i + 1}</span><code>{l || ' '}</code></div>)}
    </div>
  );
}

export default function ContextoVer({ config, reload, usar }) {
  const { tipo, nombre, '*': archivoParam } = useParams();
  const nav = useNavigate();
  const ruta = `${tipo}/${nombre}`;
  const ctx = config.contextos.find(c => c.ruta === ruta);
  const [textos, setTextos] = useState({});
  const [todo, setTodo] = useState(false);
  const [arm, setArm] = useState(false);

  const grupos = useMemo(() => {
    const g = {};
    (ctx ? ctx.archivos : []).forEach(a => { (g[grupoDe(a.ruta)] ||= []).push(a); });
    return ORDEN.filter(k => g[k]).map(k => [k, g[k]]).concat(Object.keys(g).filter(k => !ORDEN.includes(k)).map(k => [k, g[k]]));
  }, [ctx]);
  const primero = grupos.length ? grupos[0][1][0].ruta : '';
  const actual = ctx && archivoParam && ctx.archivos.some(a => a.ruta === archivoParam) ? archivoParam : primero;

  const carga = async f => {
    if (textos[f] !== undefined) return;
    try { const r = await api(`/api/contexto-archivo?c=${encodeURIComponent(ruta)}&f=${encodeURIComponent(f)}`); setTextos(t => ({ ...t, [f]: r.texto })); }
    catch (e) { setTextos(t => ({ ...t, [f]: 'No se pudo leer el archivo: ' + e.message })); }
  };
  useEffect(() => { setTextos({}); }, [ruta]);
  useEffect(() => { if (ctx) { if (todo) ctx.archivos.forEach(a => carga(a.ruta)); else if (actual) carga(actual); } }, [ctx, actual, todo, ruta]);

  if (!ctx) return <div className="card"><div className="body empty">No existe el contexto «{ruta}». <Link to="/contextos">Ver contextos</Link></div></div>;

  const descarga = f => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([textos[f] || ''], { type: 'text/plain' }));
    a.download = f.split('/').pop(); a.click(); URL.revokeObjectURL(a.href);
  };
  const abre = f => nav(`/contextos/${ruta}/${f}`);
  const borrar = async () => {
    if (!arm) { setArm(true); setTimeout(() => setArm(false), 3000); return; }
    await del(`/api/contexto?c=${encodeURIComponent(ruta)}`); await reload(); nav('/contextos');
  };
  const total = ctx.archivos.reduce((s, a) => s + a.bytes, 0);

  return (
    <>
      <div className="crumbs">
        <Link className="btn sm" to="/contextos">← Contextos</Link>
        <h2>{ctx.nombre}</h2><span className={'pill ' + (ctx.propio ? 'acc' : '')}>{ctx.propio ? 'Subido' : 'Demo'}</span>
        <span className="hint">{ctx.archivos.length} archivos · {Math.max(1, Math.round(total / 1024))} KB</span>
        <span className="sp" />
        <button className="btn sm" onClick={() => setTodo(t => !t)}>{todo ? 'Ver un archivo' : 'Ver todo junto'}</button>
        {ctx.propio && <Link className="btn sm" to={`/contextos/nuevo?org=${encodeURIComponent(ctx.nombre)}`}>Agregar archivos</Link>}
        {ctx.propio && <button className="btn sm danger" onClick={borrar}>{arm ? 'Pulse otra vez para borrar' : 'Borrar'}</button>}
        <button className="btn sm primary" onClick={() => usar(ruta)}>Usar en un análisis</button>
      </div>

      <div className="ctx-view">
        <nav className="docnav" aria-label="Archivos del contexto">
          {grupos.map(([g, fs]) => (
            <React.Fragment key={g}>
              <h4>{NOMBRE_CAT[g] || g}</h4>
              {fs.map(a => (
                <button key={a.ruta} aria-selected={!todo && actual === a.ruta} onClick={() => { setTodo(false); abre(a.ruta); }} title={a.ruta}>
                  {a.ruta.split('/').slice(1).join('/') || a.ruta}
                </button>
              ))}
            </React.Fragment>
          ))}
        </nav>
        <div style={{ minWidth: 0, display: 'grid', gap: 16 }}>
          {(todo ? ctx.archivos.map(a => a.ruta) : [actual]).map(f => (
            <div className="card" key={f}>
              <header className="docbar"><span className="grow" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>{f}</span>
                {!todo && <small className="hint">{(textos[f] || '').replace(/\n$/, '').split('\n').length} líneas</small>}
                <button className="btn sm" onClick={() => descarga(f)} disabled={textos[f] === undefined}>Descargar</button></header>
              <div className="body">{textos[f] === undefined ? <div className="empty">Cargando…</div> : <Visor ruta={f} texto={textos[f]} />}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
