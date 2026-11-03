import React, { useCallback, useEffect, useState } from 'react';
import { Link, Navigate, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom';
import { api, post, store } from './api.js';
import Header from './components/Header.jsx';
import Inicio from './components/Inicio.jsx';
import Progreso from './components/Progreso.jsx';
import Caso from './components/Caso.jsx';
import Expedientes from './components/Expedientes.jsx';
import Ajustes from './components/Ajustes.jsx';
import { ListaContextos, NuevoContexto } from './components/Contextos.jsx';
import ContextoVer from './components/ContextoVer.jsx';
import Autonomia from './components/Autonomia.jsx';

function RutaProgreso({ onDone }) {
  const { jobId } = useParams();
  const nav = useNavigate();
  return <Progreso key={jobId} jobId={jobId} onDone={onDone} onBack={() => nav('/analizar')} />;
}
function RutaCaso() {
  const { id } = useParams();
  return <Caso key={id} id={id} />;
}
function RutaAjustes(props) {
  const { tab = 'conexion' } = useParams();
  const nav = useNavigate();
  return <Ajustes tab={tab} setTab={t => nav('/ajustes/' + t)} {...props} />;
}

const TITULO = { autonomia: 'Autonomía', analizar: 'Analizar', analizando: 'Analizando', expedientes: 'Expedientes', contextos: 'Contextos', ajustes: 'Ajustes' };

export default function App() {
  const nav = useNavigate();
  const { pathname } = useLocation();
  const [config, setConfig] = useState(null);
  const [estado, setEstado] = useState(null);
  const [form, setForm] = useState({ reporte: '', contexto: '', ahora: '' });
  const [error, setError] = useState('');
  const [tema, setTema] = useState(store.get('ib.tema', 'auto'));

  const cargaConfig = useCallback(async () => {
    const c = await api('/api/config');
    setConfig(c);
    setForm(f => ({ ...f, ahora: f.ahora || c.ahora, contexto: c.contextos.some(x => x.ruta === f.contexto) ? f.contexto : '' }));
    return c;
  }, []);
  const cargaEstado = useCallback(async fresh => { try { setEstado(await api('/api/estado' + (fresh ? '?fresh=1' : ''))); } catch { /* sin estado */ } }, []);

  useEffect(() => { cargaConfig().catch(e => setError(e.message)); cargaEstado(); }, []);
  useEffect(() => {
    if (tema === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.dataset.theme = tema;
    store.set('ib.tema', tema);
  }, [tema]);
  useEffect(() => {
    window.scrollTo({ top: 0 });
    const seg = pathname.split('/')[1];
    document.title = (TITULO[seg] ? TITULO[seg] + ' · ' : '') + 'Agente de Incidentes y Brechas';
  }, [pathname]);

  const oscuro = tema === 'dark' || (tema === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
  const esLlmExterno = !!estado && (estado.proveedor === 'gemini' || estado.proveedor === 'groq');
  const listo = !!estado && (
    esLlmExterno
      ? estado.credencial.fuente !== 'ninguna'
      : estado.claude.ok && (estado.sesion.logueado || estado.credencial.fuente !== 'ninguna')
  );

  async function lanzar() {
    setError('');
    try {
      const { job } = await post('/api/analizar', { reporte: form.reporte, contexto: form.contexto, ahora: form.ahora });
      nav('/analizando/' + job);
    } catch (e) { setError(e.message); }
  }
  const terminado = async id => { await cargaConfig(); nav('/expedientes/' + id, { replace: true }); };

  if (!config) return <div className="empty" style={{ paddingTop: 80 }}>{error || 'Cargando…'}</div>;

  return (
    <div className="app2">
      <Header oscuro={oscuro} setTema={setTema} conectado={listo} nExp={config.expedientes.length} />
      <main className="page">
        {estado && !listo && !pathname.startsWith('/ajustes') && (
          <div className="banner bad">
            {esLlmExterno
              ? `El agente no tiene API key de ${estado.proveedor === 'gemini' ? 'Gemini' : 'Groq'} configurada.`
              : !estado.claude.ok
                ? 'No se encontró Claude Code en este equipo.'
                : 'El agente aún no tiene credenciales para conectarse a Claude.'}
            <button className="btn sm" onClick={() => nav('/ajustes/conexion')}>Configurar conexión</button>
          </div>
        )}
        {estado && (!estado.agente || estado.skills < 4) && <div className="banner">Faltan piezas del agente ({estado.agente ? '' : 'agente, '}{estado.skills} de 4 skills).</div>}
        {error && <div className="banner bad">{error}</div>}
        <Routes>
          <Route path="/" element={<Navigate to="/analizar" replace />} />
          <Route path="/analizar" element={<Inicio config={config} form={form} setForm={setForm} onRun={lanzar} />} />
          <Route path="/autonomia" element={<Autonomia reloadConfig={cargaConfig} />} />
          <Route path="/analizando/:jobId" element={<RutaProgreso onDone={terminado} />} />
          <Route path="/contextos" element={<ListaContextos config={config} />} />
          <Route path="/contextos/nuevo" element={<NuevoContexto reload={cargaConfig} setForm={setForm} />} />
          <Route path="/contextos/:tipo/:nombre/*" element={<ContextoVer config={config} reload={cargaConfig} usar={r => { setForm(f => ({ ...f, contexto: r })); nav('/analizar'); }} />} />
          <Route path="/expedientes" element={<Expedientes lista={config.expedientes} abre={id => nav('/expedientes/' + id)} />} />
          <Route path="/expedientes/:id" element={<RutaCaso />} />
          <Route path="/expedientes/:id/:doc" element={<RutaCaso />} />
          <Route path="/ajustes" element={<Navigate to="/ajustes/conexion" replace />} />
          <Route path="/ajustes/:tab" element={<RutaAjustes estado={estado} recargaEstado={cargaEstado} />} />
          <Route path="*" element={<div className="card"><div className="body empty">Esta página no existe. <Link to="/analizar">Ir a Analizar</Link></div></div>} />
        </Routes>
      </main>
    </div>
  );
}
