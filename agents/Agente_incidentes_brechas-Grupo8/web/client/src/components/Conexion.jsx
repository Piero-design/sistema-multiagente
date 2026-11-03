import React, { useState } from 'react';
import { post, del } from '../api.js';

const PROVEEDORES = [
  { id: 'claude', label: 'Claude', badge: null, desc: 'Suscripción o API key de Anthropic' },
  { id: 'gemini', label: 'Gemini', badge: 'Gratis', desc: 'Google AI Studio · gemini-flash' },
  { id: 'groq', label: 'Groq', badge: 'Gratis', desc: 'OpenAI GPT-OSS 120B · alta velocidad' },
];

const TIPO_CLAUDE = { api_key: 'API key de Anthropic', oauth_token: 'Token de suscripción' };
const FUENTE = { interfaz: 'Guardada desde esta página', entorno: 'Variable de entorno', ninguna: 'Ninguna' };
const TIPO_LABEL = {
  api_key: 'API key de Anthropic', oauth_token: 'Token de suscripción de Claude',
  gemini_api_key: 'API key de Gemini', groq_api_key: 'API key de Groq',
};
const PLACEHOLDERS = { claude: 'sk-ant-…', gemini: 'AIzaSy…', groq: 'gsk_…' };

export default function Conexion({ estado, recarga }) {
  const [prov, setProv] = useState('claude');
  const [claudeTipo, setClaudeTipo] = useState('api_key');
  const [valor, setValor] = useState('');
  const [msg, setMsg] = useState('');
  const [prueba, setPrueba] = useState(null);
  const [busy, setBusy] = useState(false);

  if (!estado) return <div className="empty">Comprobando…</div>;
  const { claude, sesion, credencial } = estado;
  const provActivo = estado.proveedor || 'claude';
  const esLlmExterno = provActivo === 'gemini' || provActivo === 'groq';
  const listo = esLlmExterno
    ? credencial.fuente !== 'ninguna'
    : claude.ok && (sesion.logueado || credencial.fuente !== 'ninguna');

  const tipoASalvar = prov === 'gemini' ? 'gemini_api_key' : prov === 'groq' ? 'groq_api_key' : claudeTipo;

  async function guardar() {
    setBusy(true); setMsg('');
    try {
      await post('/api/auth', { tipo: tipoASalvar, valor });
      setValor(''); setMsg('Credencial guardada.'); setPrueba(null);
      await recarga(true);
    } catch (e) { setMsg(e.message); }
    setBusy(false);
  }
  async function quitar() {
    await del('/api/auth'); setMsg('Credencial quitada.'); setPrueba(null);
    await recarga(true);
  }
  async function probar() {
    setBusy(true); setPrueba(null);
    try { setPrueba(await post('/api/auth/probar')); } catch (e) { setPrueba({ ok: false, mensaje: e.message }); }
    setBusy(false);
  }

  const provLabel = { claude: 'Claude', gemini: 'Gemini', groq: 'Groq' }[provActivo] || provActivo;

  return (
    <div className="grid2">
      <div style={{ display: 'grid', gap: 20 }}>

        {/* ── Estado de la conexión ── */}
        <div className="card">
          <header>
            <h2>Estado de la conexión</h2>
            <span className="sp" />
            <span className={'pill ' + (listo ? 'ok' : 'bad')}>{listo ? 'Listo para analizar' : 'Falta configurar'}</span>
          </header>
          <div className="body">
            <dl className="kv">
              <dt>Proveedor activo</dt>
              <dd>
                <strong>{provLabel}</strong>
                {provActivo === 'gemini' && <span className="pill acc" style={{ marginLeft: 8 }}>Gemini Flash</span>}
                {provActivo === 'groq' && <span className="pill acc" style={{ marginLeft: 8 }}>GPT-OSS 120B</span>}
              </dd>
              {provActivo === 'claude' && <>
                <dt>Claude Code</dt>
                <dd>{claude.ok
                  ? <>{`Instalado · ${claude.version}`}</>
                  : <span className="err" style={{ margin: 0 }}>No encontrado. {claude.detalle}</span>}
                </dd>
                <dt>Sesión de Claude</dt>
                <dd>{sesion.logueado
                  ? `Iniciada · ${sesion.metodo}${sesion.email ? ` · ${sesion.email}` : ''}`
                  : 'Sin sesión iniciada'}
                </dd>
              </>}
              <dt>Credencial</dt>
              <dd>{credencial.fuente === 'ninguna'
                ? 'Ninguna configurada'
                : <>{TIPO_LABEL[credencial.tipo] || credencial.tipo} · <code>{credencial.valor}</code> · {FUENTE[credencial.fuente]}</>}
              </dd>
              <dt>Agente y skills</dt>
              <dd>{estado.agente ? 'Agente cargado' : 'Falta el agente'} · {estado.skills} de 4 skills</dd>
              <dt>Entorno</dt>
              <dd>{estado.docker ? 'Contenedor Docker' : 'Equipo local'}</dd>
            </dl>
            <div className="actions">
              <button
                className="btn primary"
                onClick={probar}
                disabled={busy || (!esLlmExterno && !claude.ok)}
              >Probar conexión</button>
              <span className="grow hint">{busy && !prueba ? 'Probando…' : ''}</span>
            </div>
            {prueba && (
              <p className={prueba.ok ? 'ok-t' : 'err'} style={{ marginBottom: 0 }}>
                {prueba.ok ? `Conexión correcta (${(prueba.ms / 1000).toFixed(1)} s).` : prueba.mensaje}
              </p>
            )}
          </div>
        </div>

        {/* ── Configurar proveedor ── */}
        <div className="card">
          <header><h2>Configurar proveedor</h2></header>
          <div className="body">
            <label className="l">Proveedor LLM</label>
            <div className="seg" role="group">
              {PROVEEDORES.map(p => (
                <button
                  key={p.id}
                  aria-pressed={prov === p.id}
                  onClick={() => { setProv(p.id); setValor(''); setMsg(''); setPrueba(null); }}
                >
                  {p.label}
                  {p.badge && <span className="pill acc" style={{ marginLeft: 6, fontSize: '0.72em', verticalAlign: 'middle' }}>{p.badge}</span>}
                </button>
              ))}
            </div>

            {prov === 'claude' && (
              <>
                <label className="l" style={{ marginTop: 14 }}>Tipo de credencial</label>
                <div className="seg" role="group">
                  <button aria-pressed={claudeTipo === 'api_key'} onClick={() => setClaudeTipo('api_key')}>API key</button>
                  <button aria-pressed={claudeTipo === 'oauth_token'} onClick={() => setClaudeTipo('oauth_token')}>Token de suscripción</button>
                </div>
              </>
            )}

            {prov === 'gemini' && (
              <p className="hint" style={{ margin: '10px 0 0' }}>
                Obtén tu API key gratis en{' '}
                <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer">aistudio.google.com/apikey</a>.
                {' '}Límite gratuito: 1,500 req/día, 1M tokens/min.
              </p>
            )}
            {prov === 'groq' && (
              <p className="hint" style={{ margin: '10px 0 0' }}>
                Obtén tu API key gratis en{' '}
                <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer">console.groq.com/keys</a>.
                {' '}Nota: límite de 12k tokens/min — el análisis puede tardar más entre turnos.
              </p>
            )}

            <label className="l" htmlFor="cred" style={{ marginTop: 14 }}>
              {prov === 'claude' ? TIPO_CLAUDE[claudeTipo] : prov === 'gemini' ? 'API key de Gemini' : 'API key de Groq'}
            </label>
            <input
              id="cred"
              className="field"
              type="password"
              autoComplete="off"
              value={valor}
              onChange={e => setValor(e.target.value)}
              placeholder={PLACEHOLDERS[prov]}
            />
            <p className="hint" style={{ margin: '4px 0 0' }}>
              Se guarda en el servidor, en <code>.ib-data/</code>, y solo se usa para lanzar al agente. Nunca vuelve al navegador.
            </p>
            <div className="actions" style={{ marginTop: 12 }}>
              <button className="btn primary" onClick={guardar} disabled={busy || valor.length < 10}>Guardar</button>
              {credencial.fuente === 'interfaz' && (
                <button className="btn danger" onClick={quitar}>Quitar la guardada</button>
              )}
              <span className="grow hint">{msg}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Instrucciones ── */}
      <div className="card">
        <header><h2>Cómo conectar el agente</h2></header>
        <div className="body modes">
          <div className="mode">
            <h3>Gemini (gratis) <span className="pill acc">Recomendado sin tokens</span></h3>
            <p>
              Crea una API key en <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer">AI Studio</a>,
              selecciona "Gemini" arriba y pégala. Usa <code>gemini-flash-lite-latest</code>
              (1,500 req/día gratis, 1M tokens/min, contexto de 1M tokens).
            </p>
          </div>
          <div className="mode">
            <h3>Groq (gratis)</h3>
            <p>
              Crea una API key en <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer">console.groq.com</a>,
              selecciona "Groq" y pégala. Usa <code>openai/gpt-oss-120b</code>.
              Límite: 12k tokens/min — el análisis puede ser más lento.
            </p>
          </div>
          <div className="mode">
            <h3>Con su suscripción de Claude</h3>
            <p>
              Selecciona "Claude" → "Token de suscripción". En su equipo ejecute el comando,
              inicie sesión en el navegador y pegue el token aquí o en <code>.env</code>
              como <code>CLAUDE_CODE_OAUTH_TOKEN</code>.
            </p>
            <pre className="cmd">claude setup-token</pre>
          </div>
          <div className="mode">
            <h3>Con API key de Anthropic</h3>
            <p>Selecciona "Claude" → "API key". Se cobra por uso. Créela en <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">console.anthropic.com</a> y pégala aquí o en <code>.env</code> como <code>ANTHROPIC_API_KEY</code>.</p>
          </div>
          <div className="mode">
            <h3>Con Docker</h3>
            <p>El contenedor no ve su sesión. Copie <code>.env.example</code> a <code>.env</code>, configure el proveedor y la API key, y ejecute:</p>
            <pre className="cmd">docker compose up --build</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
