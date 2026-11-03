import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, post } from '../api.js';

const ESTADO = {
  nueva: ['Pendiente', 'warn'], en_analisis: ['Analizando…', 'acc'], analizada: ['Analizada', 'ok'],
  descartada: ['Sin señales', ''], error: ['Con error', 'bad'],
};
const CLASIF = { seguridad: ['Posible incidente', 'bad'], dudosa: ['Por verificar', 'warn'], ajena: ['Ajena', ''] };
const TIPO = { carpeta: 'Carpeta', webhook: 'Webhook', imap: 'Correo (IMAP)', http: 'API', archivos: 'Logs / archivos' };

function Fuentes({ titulo, ayuda, items, vacio }) {
  return (
    <div className="card">
      <header><h2>{titulo}</h2></header>
      <div className="body fuentes">
        <p className="hint">{ayuda}</p>
        {items.length === 0 && <div className="empty" style={{ padding: 8 }}>{vacio}</div>}
        {items.map(s => (
          <div key={s.id} className="fuente">
            <div><b>{s.id}</b> <span className="pill">{TIPO[s.tipo] || s.tipo}</span>{s.error && <span className="pill bad" title={s.error}>Falla</span>}</div>
            {s.descripcion && <small>{s.descripcion}</small>}
            {s.destino && <small><code>{s.destino}</code></small>}
            {s.error && <small className="err">{s.error}</small>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Autonomia({ reloadConfig }) {
  const nav = useNavigate();
  const [r, setR] = useState(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState('');
  const [q, setQ] = useState({ buzon: '', asunto: '', texto: '' });
  const [ok, setOk] = useState('');

  const carga = useCallback(() => api('/api/autonomia').then(x => { setR(x); setErr(''); }).catch(e => setErr(e.message)), []);
  useEffect(() => { carga(); const t = setInterval(carga, 4000); return () => clearInterval(t); }, [carga]);
  useEffect(() => { if (r && !q.buzon) { const b = r.buzones.find(x => x.admite_deposito); if (b) setQ(v => ({ ...v, buzon: b.id })); } }, [r]);
  const hay = r && r.quejas.some(x => x.estado === 'en_analisis');
  useEffect(() => { if (r && !hay) reloadConfig?.(); }, [hay]);

  const accion = async (nombre, fn) => { setBusy(nombre); setErr(''); try { await fn(); await carga(); } catch (e) { setErr(e.message); } setBusy(''); };
  const alternar = () => accion('sw', () => post('/api/autonomia', { activo: !r.activo }));
  const sondear = () => accion('sondeo', () => post('/api/autonomia/sondear'));
  const analizar = id => accion(id, async () => { const { job } = await post(`/api/buzon/${id}/analizar`); nav('/analizando/' + job); });
  const enviar = ev => {
    ev.preventDefault();
    accion('dep', async () => { await post('/api/buzon/depositar', q); setQ(v => ({ ...v, asunto: '', texto: '' })); setOk('Queja depositada. Se procesa en el próximo sondeo.'); setTimeout(() => setOk(''), 4000); await post('/api/autonomia/sondear'); });
  };

  if (!r) return <div className="empty">{err || 'Cargando…'}</div>;
  const pendientes = r.quejas.filter(x => x.estado === 'nueva').length;

  return (
    <>
      <div className="auto-head">
        <div>
          <h2 style={{ fontSize: 22, margin: 0 }}>Autonomía</h2>
          <p className="hint" style={{ maxWidth: '72ch', margin: '4px 0 0' }}>
            El agente revisa el buzón de quejas, decide qué sistemas consultar y deja el expediente listo. Solo lee: cualquier contención llega como <b>propuesta</b> que una persona aprueba.
          </p>
        </div>
        <span className="sp" />
        <button className="btn" onClick={sondear} disabled={!!busy}>{busy === 'sondeo' ? 'Sondeando…' : 'Sondear ahora'}</button>
        <button className={'btn ' + (r.activo ? '' : 'primary')} onClick={alternar} disabled={!!busy}>{r.activo ? 'Pausar autonomía' : 'Activar autonomía'}</button>
      </div>

      {err && <div className="banner bad">{err}</div>}
      {r.error_config && <div className="banner bad">Configuración inválida ({r.config}): {r.error_config}</div>}

      <div className="sla">
        <div className={'kpi ' + (r.activo ? 'ok' : '')}><small>Estado</small><b>{r.activo ? 'Activa' : 'En pausa'}</b><small className="sub">{r.activo ? `Revisa cada ${r.intervalo_seg} s · máx. ${r.max_por_hora} análisis/h` : 'Las quejas se registran pero no se analizan solas'}</small></div>
        <div className="kpi"><small>Último sondeo</small><b style={{ fontSize: 15 }}>{r.ultimo_sondeo || 'Aún no'}</b><small className="sub">Config: <code>{r.config || 'por defecto'}</code></small></div>
        <div className={'kpi ' + (pendientes ? 'warn' : '')}><small>Quejas por analizar</small><b className="big">{pendientes}</b><small className="sub">{hay ? 'Hay un análisis en curso' : 'Ninguno en curso'}</small></div>
      </div>

      <div className="auto-grid">
        <Fuentes titulo="Buzones" ayuda="De dónde llegan las quejas." items={r.buzones} vacio="Sin buzones configurados." />
        <Fuentes titulo="Base de conocimiento" ayuda="Lo que el agente consulta para entender la organización." items={r.conocimiento} vacio="Sin fuentes configuradas." />
        <Fuentes titulo="Sistemas y subsistemas" ayuda="Acceso de solo lectura para verificar los hechos." items={r.sistemas} vacio="Sin sistemas configurados." />
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <header><h2>Quejas recibidas</h2><span className="sp" /><span className="pill">{r.quejas.length}</span></header>
        <div className="body">
          {r.quejas.length === 0 && <div className="empty">Todavía no llegó ninguna queja.</div>}
          {r.quejas.map(x => {
            const [el, ec] = ESTADO[x.estado] || [x.estado, ''];
            const [cl, cc] = CLASIF[x.clasificacion] || [x.clasificacion, ''];
            return (
              <div key={x.id} className="queja">
                <div className="qh">
                  <b>{x.asunto}</b>
                  <span className={'pill ' + cc} title={x.senales?.join(', ')}>{cl}</span>
                  <span className={'pill ' + ec}>{el}</span>
                  <span className="sp" />
                  <small>{x.buzon} · {x.fecha}</small>
                </div>
                <p>{x.extracto}</p>
                {x.nota && <small className="hint">{x.nota}</small>}
                {x.error && <small className="err">{x.error}</small>}
                <div className="qa">
                  {x.incidente && <Link className="btn sm primary" to={'/expedientes/' + x.incidente}>Ver expediente</Link>}
                  {x.estado === 'en_analisis' && x.job && <Link className="btn sm" to={'/analizando/' + x.job}>Ver avance</Link>}
                  {['nueva', 'descartada', 'error', 'analizada'].includes(x.estado) && (
                    <button className="btn sm" disabled={!!busy} onClick={() => analizar(x.id)}>{x.estado === 'analizada' ? 'Reanalizar' : 'Analizar ahora'}</button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {r.buzones.some(b => b.admite_deposito) && (
        <form className="card" style={{ marginTop: 18 }} onSubmit={enviar}>
          <header><h2>Simular una queja</h2></header>
          <div className="body">
            <p className="hint">Para probar sin conectar el formulario real: la queja entra al buzón como si la hubiera enviado una persona.</p>
            <div className="row">
              <label className="lbl">Buzón<select className="field" value={q.buzon} onChange={e => setQ({ ...q, buzon: e.target.value })}>
                {r.buzones.filter(b => b.admite_deposito).map(b => <option key={b.id} value={b.id}>{b.id}</option>)}
              </select></label>
              <label className="lbl">Asunto<input className="field" value={q.asunto} onChange={e => setQ({ ...q, asunto: e.target.value })} placeholder="Ej. Mi nota fue cambiada sin avisarme" /></label>
            </div>
            <label className="lbl" style={{ display: 'block', marginTop: 12 }}>Mensaje<textarea className="field" rows={4} value={q.texto} onChange={e => setQ({ ...q, texto: e.target.value })} placeholder="Describa lo ocurrido como lo haría un estudiante o docente…" /></label>
            <div style={{ marginTop: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
              <button className="btn primary" disabled={!!busy || q.texto.trim().length < 10}>Enviar al buzón</button>
              {ok && <small className="hint">{ok}</small>}
            </div>
          </div>
        </form>
      )}
    </>
  );
}
