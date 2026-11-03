import React, { useEffect, useMemo, useRef, useState } from 'react';
import MermaidDiagram, {captureDiagrams} from './components/MermaidDiagram.jsx';
import VisualStudioPanel from './components/VisualStudioPanel.jsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ArrowDown, ArrowLeft, ArrowRight, ArrowUp, BookOpen, Check, CheckCheck, ChevronDown,
  ChevronLeft, ChevronRight, CircleHelp, Clock3, CloudOff, Command, Copy, Database,
  FileCheck2, FileClock, FileText, Fingerprint, Globe2, History, Layers3, LayoutGrid,
  LibraryBig, LockKeyhole, Menu, MessageCircleMore, MoreHorizontal, PanelLeftClose,
  PanelLeftOpen, Plus, Search, Send, Settings2, Shield, ShieldCheck, Sparkles, Sun,
  Moon, Workflow, X, Zap, RotateCw, ExternalLink, Trash2, Wifi, WandSparkles,
  Download, FileDown, Image as ImageIcon, FilePlus2, Network, Paperclip, FileSpreadsheet, UploadCloud,
} from 'lucide-react';

const STARTERS = [
  { icon: ShieldCheck, title: 'Evaluación de riesgos', detail: 'Analizar un sistema o proceso', prompt: 'Quiero evaluar los riesgos de privacidad de un sistema. ¿Qué información necesitas para comenzar?' },
  { icon: BookOpen, title: 'Consultar la norma', detail: 'Preguntar sobre ISO/IEC 27701', prompt: '¿Qué establece ISO/IEC 27701:2025 sobre la evaluación de riesgos de privacidad? Usa solo información documental verificada.' },
  { icon: FileCheck2, title: 'Controles y tratamiento', detail: 'Preparar medidas y controles', prompt: '¿Cómo puedo documentar un plan de tratamiento de riesgos de privacidad? Indica qué información necesitas.' },
  { icon: Network, title: 'Diagramar un proceso', detail: 'Visualización Mermaid en el chat', prompt: 'Crea un diagrama Mermaid de flujo sobre las etapas de evaluación de riesgos de privacidad. Usa un bloque ```mermaid y no inventes referencias ISO.' },
];

const METHODS = [
  { title: 'Definir el alcance', body: 'Delimitar el proceso, los activos y el papel de la organización.' },
  { title: 'Comprender el contexto', body: 'Identificar partes interesadas y requisitos relevantes.' },
  { title: 'Identificar riesgos', body: 'Documentar amenazas, vulnerabilidades y consecuencias.' },
  { title: 'Analizar riesgos', body: 'Examinar impacto, probabilidad y nivel de riesgo.' },
  { title: 'Evaluar y priorizar', body: 'Comparar los niveles con los criterios de aceptación.' },
  { title: 'Proponer tratamiento', body: 'Evaluar opciones de tratamiento y controles apropiados.' },
  { title: 'Documentar aplicabilidad', body: 'Justificar los controles e identificar aprobaciones pendientes.' },
];

const readStore = () => {
  try {
    const data = JSON.parse(sessionStorage.getItem('iso-studio-sessions-v1') || 'null');
    if (Array.isArray(data) && data.length) return data;
  } catch {}
  return [{ id: crypto.randomUUID(), title: 'Nueva conversación', messages: [], created: Date.now() }];
};

function BrandIcon({ size = 39 }) {
  return <span className="brand-icon" style={{ width: size, height: size }} aria-hidden="true"><Shield size={size * .53} strokeWidth={1.95} /><span className="brand-dot" /></span>;
}

function StatusPill({ demo, configured, compact = false }) {
  const label = demo ? 'Vista previa' : configured ? 'API configurada' : 'Sin conexión';
  return <span className={`status-pill ${demo ? 'status-preview' : configured ? 'status-ready' : 'status-off'}`}>
    <span className="status-dot" />{compact ? null : label}
  </span>;
}

function Sidebar({ view, setView, sessions, activeId, selectSession, addSession, removeSession, collapsed, setCollapsed, mobileOpen, setMobileOpen, dark, setDark }) {
  const [query, setQuery] = useState('');
  const visible = sessions.filter(s => s.title.toLocaleLowerCase().includes(query.toLocaleLowerCase())).slice(0, 12);
  const pickView = next => { setView(next); setMobileOpen(false); };
  return <>
    {mobileOpen && <button className="mobile-scrim" aria-label="Cerrar menú" onClick={() => setMobileOpen(false)} />}
    <aside className={`sidebar ${collapsed ? 'sidebar-closed' : ''} ${mobileOpen ? 'sidebar-mobile-open' : ''}`}>
      <div className="sidebar-brand">
        <BrandIcon size={41} />
        {!collapsed && <div className="brand-copy"><strong>iso<span>studio</span></strong><small>GESTIÓN DE RIESGOS</small></div>}
        {!collapsed && <button className="icon-btn side-collapse" aria-label="Contraer menú" onClick={() => setCollapsed(true)}><PanelLeftClose size={18}/></button>}
      </div>
      {collapsed && <button className="icon-btn reopen" aria-label="Expandir menú" onClick={() => setCollapsed(false)}><PanelLeftOpen size={19}/></button>}
      <div className="sidebar-content">
        {!collapsed && <div className="section-heading">ESPACIO DE TRABAJO</div>}
        <nav className="nav-main" aria-label="Navegación principal">
          {[
            {id:'chat', icon: MessageCircleMore, label:'Asistente IA'},
            {id:'knowledge', icon: LibraryBig, label:'Base de conocimiento'},
            {id:'method', icon: Workflow, label:'Metodología'},
            {id:'skills', icon: WandSparkles, label:'Herramientas y archivos'},
            {id:'visual', icon: ImageIcon, label:'Estudio visual'},
          ].map(item => <button key={item.id} title={item.label} className={`nav-item ${view === item.id ? 'selected' : ''}`} onClick={() => pickView(item.id)}><item.icon size={19} strokeWidth={1.9}/>{!collapsed && <span>{item.label}</span>}{!collapsed && item.id === 'chat' && <span className="nav-meta">01</span>}</button>)}
        </nav>
        {!collapsed && <>
          <div className="history-head"><span>CONVERSACIONES</span><button title="Nueva conversación" className="subtle-icon" onClick={() => { addSession(); pickView('chat'); }}><Plus size={16}/></button></div>
          <div className="search-box"><Search size={15}/><input aria-label="Buscar conversaciones" placeholder="Buscar conversación" value={query} onChange={e => setQuery(e.target.value)}/><span>⌘ K</span></div>
          <div className="sessions">
            {visible.map(s => <div key={s.id} className={`session-wrap ${activeId === s.id && view === 'chat' ? 'session-active' : ''}`}>
              <button className="session-title" onClick={() => { selectSession(s.id); pickView('chat'); }} title={s.title}><MessageCircleMore size={15}/><span>{s.title}</span></button>
              <button className="session-delete" title="Eliminar conversación" aria-label={`Eliminar ${s.title}`} onClick={() => removeSession(s.id)}><X size={14}/></button>
            </div>)}
            {visible.length === 0 && <p className="no-sessions">No se encontraron conversaciones</p>}
          </div>
        </>}
      </div>
      <div className="sidebar-bottom">
        {!collapsed && <div className="sidebar-tip"><span className="tip-orbit"><Sparkles size={18}/></span><strong>Un espacio para pensar mejor.</strong><p>Privacidad, evidencia y criterio en un solo lugar.</p></div>}
        <button className={`nav-item ${view === 'settings' ? 'selected' : ''}`} title="Configuración" onClick={() => pickView('settings')}><Settings2 size={19}/>{!collapsed && <span>Configuración</span>}</button>
        <button className="nav-item" title={dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'} onClick={() => setDark(!dark)}>{dark ? <Sun size={19}/> : <Moon size={19}/>} {!collapsed && <span>{dark ? 'Modo claro' : 'Modo oscuro'}</span>}</button>
        {!collapsed && <div className="sidebar-footer"><div className="profile-avatar">IS</div><div><strong>Mi espacio local</strong><small>Auditoría de sistemas</small></div><MoreHorizontal size={17}/></div>}
      </div>
    </aside>
  </>;
}

function NavTop({ view, configured, demo, onMenu, addSession, setView, showContext, setShowContext, copied, copyCurrent }) {
  const labels = { chat: 'Asistente IA', knowledge: 'Base de conocimiento', method: 'Metodología de riesgos', skills: 'Herramientas y archivos', visual: 'Estudio visual', settings: 'Configuración' };
  return <header className="topbar">
    <div className="topbar-left"><button className="icon-btn mobile-menu" aria-label="Abrir menú" onClick={onMenu}><Menu size={21}/></button><span className="crumb-muted">Workspace</span><ChevronRight size={14} className="crumb-chevron"/><strong>{labels[view]}</strong><span className="topbar-version">/ GR-01 a GR-06</span></div>
    <div className="topbar-right"><StatusPill demo={demo} configured={configured}/>{view === 'chat' && <><button className="top-action" onClick={copyCurrent} title="Copiar conversación">{copied ? <Check size={16}/> : <Copy size={16}/>}<span>{copied ? 'Copiado' : 'Copiar chat'}</span></button><button className="icon-btn context-toggle" onClick={() => setShowContext(!showContext)} title="Mostrar/ocultar contexto"><LayoutGrid size={19}/></button><button className="new-chat-action" onClick={() => { addSession(); setView('chat'); }}><Plus size={17}/><span>Nuevo chat</span></button></>}</div>
  </header>;
}

function MarkdownMessage({ content }) {
  return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{
    a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer"/>,
    pre: ({children}) => {
      const child=React.Children.toArray(children)[0];
      const klass=child?.props?.className||'';
      if (/language-mermaid\b/i.test(klass)) return <MermaidDiagram source={String(child.props.children||'').trim()}/>;
      return <pre>{children}</pre>;
    },
  }}>{content}</ReactMarkdown></div>;
}

function ChatMessage({ message, onCopy, copied, onExport, exporting, onVisual }) {
  const assistant = message.role === 'assistant';
  return <div className={`chat-message ${assistant ? 'assistant-message' : 'user-message'}`}>
    <div className={`message-avatar ${assistant ? 'assistant-avatar' : 'user-avatar'}`}>{assistant ? <Sparkles size={17}/> : 'TÚ'}</div>
    <div className="message-content"><div className="message-byline"><strong>{assistant ? 'ISO Studio' : 'Tú'}</strong><span>{assistant ? 'Asistente de auditoría' : 'Consulta'}</span>{message.demo && <span className="demo-tag">Vista previa</span>}</div>
      {assistant ? <div className="message-body"><MarkdownMessage content={message.text}/></div> : <><div className="message-user-bubble">{message.text}</div>{message.sources?.length>0 && <div className="message-sources">{message.sources.map(f=><span key={f.id}><Paperclip size={13}/>{f.name}</span>)}</div>}</>}
      {assistant && message.webSearched && <div className="web-results"><div className="web-results-title"><Globe2 size={15}/> Fuentes consultadas en Internet {message.webCached && <small>· Caché de 10 min</small>}</div>
        {message.webSources?.length ? <div className="web-results-grid">{message.webSources.map(source=><a key={source.id} className="web-source-link" href={source.url} target="_blank" rel="noopener noreferrer" title={source.excerpt}><span className="web-source-ref">{source.id}</span><span className="web-source-detail"><strong>{source.title}</strong><small>{(()=>{try{return new URL(source.url).hostname}catch{return 'Fuente web'}})()}</small></span><ExternalLink size={14}/></a>)}</div> : <div className="web-empty">No se recuperaron fuentes relevantes. Revisa la respuesta antes de utilizarla como evidencia.</div>}
      </div>}
      {assistant && <div className="message-actions">
        <button onClick={() => onCopy(message.id, message.text)} aria-label="Copiar respuesta">{copied === message.id ? <Check size={14}/> : <Copy size={14}/>} {copied === message.id ? 'Copiado' : 'Copiar'}</button>
        <button disabled={Boolean(exporting)||message.demo} onClick={() => onExport(message,'pdf')}><FileDown size={14}/>{exporting===`${message.id}:pdf`?'Generando…':'PDF'}</button>
        <button disabled={message.demo} onClick={() => onVisual(message.text)}><ImageIcon size={14}/> Crear imagen</button>
        <button disabled={Boolean(exporting)||message.demo} onClick={() => onExport(message,'docx')}><FileText size={14}/>{exporting===`${message.id}:docx`?'Generando…':'Word'}</button>
        <button disabled={Boolean(exporting)||message.demo} onClick={() => onExport(message,'xlsx')} title="Exportar tablas a Excel editable"><FileSpreadsheet size={14}/>{exporting===`${message.id}:xlsx`?'Generando…':'Excel'}</button>
      </div>}
      {assistant && message.attachments?.length>0 && <div className="generated-files">{message.attachments.map(f=><a key={f.id} className="generated-file" href={f.url} download><FileDown size={18}/><span><strong>{f.name}</strong><small>Archivo generado · {f.format.toUpperCase()}</small></span><Download size={16}/></a>)}</div>}
    </div>
  </div>;
}

function Compose({ value, setValue, send, loading, demo, inputRef, onSettings, files, onUpload, onRemove, uploading, uploadError, webMode, setWebMode, webAvailable, visionEnabled, setVisionEnabled, visionAvailable }) {
  const fileInput = useRef(null);
  const [dragging, setDragging] = useState(false);
  function pick(inputFiles) {
    if (!inputFiles?.length) return;
    onUpload(Array.from(inputFiles));
    if (fileInput.current) fileInput.current.value = '';
  }
  return <div className="compose-wrap">
    <form className={`compose ${dragging?'compose-dragging':''}`} onSubmit={e => { e.preventDefault(); send(); }}
      onDragEnter={e=>{e.preventDefault();setDragging(true)}}
      onDragOver={e=>{e.preventDefault();setDragging(true)}}
      onDragLeave={e=>{e.preventDefault();if(!e.currentTarget.contains(e.relatedTarget))setDragging(false)}}
      onDrop={e=>{e.preventDefault();setDragging(false);pick(e.dataTransfer.files)}}>
      <input ref={fileInput} className="hidden-upload-input" type="file" accept=".pdf,.docx,.xlsx,.txt,.md,.csv,.png,.jpg,.jpeg,.webp" multiple onChange={e=>pick(e.target.files)} aria-label="Seleccionar documentos para analizar"/>
      {files.length>0 && <div className="compose-files" aria-label="Archivos adjuntos">{files.map(file=><div key={file.id} className="compose-file">
        {file.type==='xlsx'?<FileSpreadsheet size={17}/>:['png','jpg','jpeg','webp'].includes(file.type)?<ImageIcon size={17}/>:<FileText size={17}/>}
        <span title={file.name}><strong>{file.name}</strong><small title={file.note||''}>{file.type.toUpperCase()} · {Math.max(1,Math.round(file.size/1024))} KB{file.note?.includes('Gemini')?' · IA':''}</small></span>
        <button type="button" onClick={()=>onRemove(file.id)} disabled={loading||uploading} title={`Quitar ${file.name}`} aria-label={`Quitar ${file.name}`}><X size={15}/></button>
      </div>)}</div>}
      {dragging && <div className="drop-indicator"><UploadCloud size={19}/> Suelta los documentos aquí</div>}
      <textarea ref={inputRef} rows={2} maxLength={8000} value={value} onChange={e => setValue(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(); } }} placeholder="Pregunta, crea una matriz Excel o solicita un diagrama..." aria-label="Escribe una consulta al agente" />
      <div className="compose-toolbar"><div className="compose-label"><button type="button" className="attach-button" title="Adjuntar documentos, imágenes o PDF escaneados" aria-label="Adjuntar archivo" disabled={loading||uploading||files.length>=4} onClick={()=>fileInput.current?.click()}>
        {uploading?<RotateCw size={17} className="spin"/>:<Paperclip size={17}/>} <span>{uploading?'Procesando…':'Adjuntar'}</span>
      </button><button type="button" className={`web-mode web-mode-${webMode}`} onClick={()=>setWebMode(webMode==='auto'?'on':webMode==='on'?'off':'auto')} title={webMode==='auto'?'Auto: busca solo cuando la consulta pide información de Internet. Haz clic para forzar búsqueda.':webMode==='on'?'Activada: busca para esta consulta. Haz clic para desactivar.':'Desactivada: no consulta Internet. Haz clic para automático.'} aria-label={`Búsqueda web: ${webMode}`}>
        <Globe2 size={15}/>{webMode==='auto'?'Web: auto':webMode==='on'?'Web: activada':'Web: apagada'}{!webAvailable && <span className="web-warning" title="Falta configurar TAVILY_API_KEY">!</span>}
      </button><button type="button" className={`web-mode ${visionEnabled?'web-mode-on':'web-mode-off'}`} onClick={()=>setVisionEnabled(!visionEnabled)} disabled={!visionAvailable || loading || uploading} title={visionAvailable?'Al activarlo se enviarán imágenes nuevas a Gemini para analizar su contenido. No se aplica retroactivamente.': 'Sin GEMINI_VISION_API_KEY: disponible solo OCR local.'} aria-label="Activar análisis visual con Gemini" aria-pressed={visionEnabled}>
        <ImageIcon size={15}/>{visionEnabled?'Visión IA: sí':'Visión IA: no'}{!visionAvailable && <span className="web-warning" title="Configura GEMINI_VISION_API_KEY">!</span>}
      </button><span className="compose-agent"><Sparkles size={15}/>{demo ? 'Vista previa del agente' : 'Agente ISO 27701'}</span></div><div className="compose-right"><span>↵ para enviar</span><button disabled={loading || uploading || (!value.trim()&&!files.length)} aria-label="Enviar consulta" type="submit" className="send-button">{loading ? <RotateCw size={19} className="spin"/> : <ArrowUp size={20}/>}</button></div></div>
    </form>
    {uploadError && <div className="upload-error" role="alert">{uploadError}</div>}
    <div className="compose-note"><LockKeyhole size={13}/>PDF, Word, Excel, imágenes y texto (máx. 8 MB, 4 por chat). OCR local; Visión IA envía las imágenes a Gemini cuando está activada. No adjuntes información confidencial.{demo && <button onClick={onSettings}>Conectar a n8n <ArrowRight size={12}/></button>}</div>
  </div>;
}

function ChatScreen({ session, send, loading, text, setText, inputRef, onSettings, demo, error, copyMessage, copied, onExport, exporting, onVisual, onUpload, onRemove, uploading, uploadError, webMode, setWebMode, webAvailable, visionEnabled, setVisionEnabled, visionAvailable }) {
  const endRef = useRef(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [session.id, session.messages.length, loading]);
  return <div className="chat-layout">
    <div className="chat-scroll" aria-live="polite">
      {session.messages.length === 0 ? <div className="welcome-wrap"><div className="welcome-top"><div className="hero-emblem"><BrandIcon size={61}/><span className="hero-spark"><Sparkles size={17}/></span></div><div className="eyebrow"><span className="eyebrow-line"/> TU ASISTENTE DE PRIVACIDAD <span className="eyebrow-line"/></div><h1>Audita con más<br/><em>claridad.</em></h1><p>Explora la norma ISO/IEC 27701, estructura evaluaciones de riesgos y convierte preguntas complejas en respuestas accionables.</p></div><div className="starter-intro"><span>EMPIEZA POR AQUÍ</span><div className="starter-dash"/></div><div className="starter-grid">{STARTERS.map(s => <button key={s.title} className="starter-card" onClick={() => { setText(s.prompt); inputRef.current?.focus(); }}><span className="starter-icon"><s.icon size={19}/></span><span className="starter-content"><strong>{s.title}</strong><small>{s.detail}</small></span><ArrowUp size={16} className="starter-arrow"/></button>)}</div></div> : <div className="messages-list"><div className="conversation-meta"><span className="dot-teal"/> CONVERSACIÓN ACTIVA <span className="meta-rule"/></div>{session.messages.map(msg => <ChatMessage key={msg.id} message={msg} onCopy={copyMessage} copied={copied} onExport={onExport} exporting={exporting} onVisual={onVisual}/>)}{loading && <div className="thinking"><div className="message-avatar assistant-avatar"><Sparkles size={17}/></div><div><strong>ISO Studio está analizando tu consulta</strong><div className="typing"><span/><span/><span/></div></div></div>}{error && <div className="inline-error"><CloudOff size={17}/><span>{error}</span></div>}<div ref={endRef}/></div>}
    </div>
    <Compose value={text} setValue={setText} send={send} loading={loading} demo={demo} inputRef={inputRef} onSettings={onSettings} files={session.files||[]} onUpload={onUpload} onRemove={onRemove} uploading={uploading} uploadError={uploadError} webMode={webMode} setWebMode={setWebMode} webAvailable={webAvailable} visionEnabled={visionEnabled} setVisionEnabled={setVisionEnabled} visionAvailable={visionAvailable}/>
  </div>;
}

function ContextPanel({ configured, demo, setView, setShowContext }) {
  return <aside className="context-panel"><div className="context-top"><span>CONTEXTO DEL AGENTE</span><button className="subtle-icon" onClick={() => setShowContext(false)} aria-label="Cerrar contexto"><X size={17}/></button></div>
    <div className="context-card context-identity"><span className="context-icon"><Fingerprint size={20}/></span><div><small>ENTORNO DE TRABAJO</small><strong>Auditoría inteligente</strong><p>ISO/IEC 27701:2025</p></div><span className="identity-ornament"/></div>
    <div className="context-section-title"><span>CAPACIDADES</span><Sparkles size={15}/></div>
    <div className="capability-row"><span className="cap-icon purple"><MessageCircleMore size={18}/></span><div><strong>Consultas inteligentes</strong><p>Conversaciones con Gemini vía n8n.</p></div></div>
    <div className="capability-row"><span className="cap-icon teal"><Database size={18}/></span><div><strong>Recuperación RAG</strong><p>Consulta a la base vectorial Qdrant.</p></div></div>
    <div className="capability-row"><span className="cap-icon peach"><Workflow size={18}/></span><div><strong>Evaluación de riesgos</strong><p>Procedimiento guiado de 7 etapas.</p></div></div>
    <div className="capability-row"><span className="cap-icon purple"><FileDown size={18}/></span><div><strong>PDF, Word y Excel</strong><p>Informes y matrices editables, con cálculos referenciales.</p></div></div>
    <div className="capability-row"><span className="cap-icon teal"><Network size={18}/></span><div><strong>Diagramas Mermaid</strong><p>Visualización y descargas SVG/PNG.</p></div></div>
    <div className="capability-row"><span className="cap-icon peach"><Paperclip size={18}/></span><div><strong>Lectura de archivos</strong><p>PDF, Word, Excel y archivos de texto por conversación.</p></div></div>
    <div className="capability-row"><span className="cap-icon teal"><Globe2 size={18}/></span><div><strong>Investigación web</strong><p>Busca fuentes actuales usando Tavily desde Node.js.</p></div></div>
    <div className="context-divider"/>
    <div className="context-section-title"><span>FUENTES DEL AGENTE</span><span className="help-icon" title="Las referencias deben verificarse contra el PDF original"><CircleHelp size={15}/></span></div>
    <button className="source-card" onClick={() => setView('knowledge')}><span className="source-icon"><BookOpen size={18}/></span><div><strong>Biblioteca normativa</strong><p>{demo ? 'Vista previa · sin búsqueda real' : 'Conectada a tu workflow RAG'}</p></div><ChevronRight size={17}/></button>
    <div className="context-note"><span className="note-light"><Zap size={15}/></span><strong>Importante</strong><p>Las referencias a cláusulas deben contrastarse con el texto original de la norma antes de utilizarlas como evidencia.</p></div>
    <button className="view-workflow" onClick={() => window.open('http://localhost:5678', '_blank', 'noopener,noreferrer')}><Workflow size={17}/> Abrir panel de n8n <ExternalLink size={14}/></button>
  </aside>;
}

function SubpageHeader({ eyebrow, title, description, icon: Icon }) {
  return <div className="subpage-head"><div className="subpage-icon"><Icon size={24}/></div><div className="eyebrow sub-eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>;
}

function KnowledgePage({ configured, demo, setView }) {
  return <div className="content-page"><SubpageHeader eyebrow="RAG · CONOCIMIENTO" title="Una biblioteca con criterio." description="El conocimiento especializado se consulta desde Qdrant. La carga y validación de los PDF se administra actualmente desde n8n." icon={LibraryBig}/>
    <div className="knowledge-grid"><div className="library-card"><div className="library-illustration"><div className="stacked-doc doc-a"/><div className="stacked-doc doc-b"/><div className="stacked-doc doc-c"><BookOpen size={35}/></div><span className="library-spark"><Sparkles size={17}/></span></div><h2>Tu conocimiento, organizado.</h2><p>La biblioteca ISO se administra desde el workflow <code>RAG_ISO27701</code>. Los documentos adjuntos en el chat se analizan temporalmente y no se guardan automáticamente en Qdrant.</p><button className="primary-btn" onClick={() => window.open('http://localhost:5678', '_blank', 'noopener,noreferrer')}><ExternalLink size={16}/> Abrir RAG en n8n</button></div>
    <div className="library-aside"><h3>Arquitectura RAG</h3><div className="pipeline-step"><span className="pipeline-num">01</span><div><strong>Ingesta de documentos</strong><p>Lectura del PDF y fragmentación contextual.</p></div></div><div className="pipeline-step"><span className="pipeline-num">02</span><div><strong>Embeddings de Gemini</strong><p>Representación vectorial de cada fragmento.</p></div></div><div className="pipeline-step"><span className="pipeline-num">03</span><div><strong>Persistencia en Qdrant</strong><p>Recuperación semántica desde disco local.</p></div></div><div className="pipeline-step"><span className="pipeline-num">04</span><div><strong>Respuesta fundamentada</strong><p>El agente recibe el contexto recuperado.</p></div></div></div></div>
    <div className="notification-row"><ShieldCheck size={18}/><span>**Estado:** la interfaz no puede verificar por sí sola qué documentos están cargados ni su integridad.</span><button onClick={() => setView('chat')}>Ir al chat <ArrowRight size={14}/></button></div>
  </div>;
}

function MethodPage({ setView }) {
  return <div className="content-page"><SubpageHeader eyebrow="SKILL · METODOLOGÍA" title="Del riesgo a la decisión." description="Un proceso organizado para apoyar la evaluación de riesgos de privacidad. Cada conclusión debe validarse con la norma y los responsables correspondientes." icon={Workflow}/>
    <div className="method-grid">{METHODS.map((s,i) => <div className="method-card" key={s.title}><span className="method-index">{String(i+1).padStart(2,'0')}</span><div><h3>{s.title}</h3><p>{s.body}</p></div><ArrowUp size={16}/></div>)}</div>
    <div className="method-cta"><div><span className="cta-icon"><Sparkles size={21}/></span><strong>¿Quieres iniciar una evaluación?</strong><p>El Skill ya está integrado como herramienta del agente.</p></div><button className="primary-btn" onClick={() => setView('chat')}>Abrir asistente <ArrowRight size={16}/></button></div>
  </div>;
}

function SkillsPage({startPrompt}) {
  const tools=[
    {icon:FileText,name:'Generador Word',tag:'.docx',description:'Redacta informes, procedimientos o matrices. Descarga un Word editable desde la respuesta.',prompt:'Redacta un informe de auditoría de riesgos de privacidad de ejemplo en formato Word, con resumen, metodología, tabla de riesgos y conclusiones. Señala claramente los datos ficticios.'},
    {icon:FileDown,name:'Generador PDF',tag:'.pdf',description:'Crea documentos imprimibles con portada, encabezados, tablas y numeración de páginas.',prompt:'Crea un informe ejecutivo en PDF sobre buenas prácticas de privacidad de datos, con título, resumen, tabla comparativa y recomendaciones.'},
    {icon:FileSpreadsheet,name:'Generador Excel',tag:'.xlsx',description:'Exporta tablas, matrices de riesgos y un resumen con fórmulas y mapa de calor referencial.',prompt:'Crea una matriz de riesgos ficticios de un sistema de matrícula universitaria en una tabla Markdown, con 6 riesgos, columnas ID, Riesgo, Impacto, Probabilidad, Afectado, Responsable y Tratamiento. Después la descargaré como Excel.'},
    {icon:Network,name:'Diagramador',tag:'Mermaid',description:'Representa flujos, arquitecturas y secuencias directamente en la conversación.',prompt:'Crea un diagrama Mermaid de flujo para explicar una evaluación de riesgos. Usa un bloque ```mermaid y explica cada paso brevemente.'},
    {icon:Paperclip,name:'Lectura de archivos',tag:'Adjuntar',description:'Analiza PDF, Word, Excel, imágenes y documentos de texto. OCR local para escaneos.',prompt:'Voy a adjuntar un archivo. Ayúdame a resumirlo con referencias verificables a sus páginas o secciones.'},
    {icon:ImageIcon,name:'Visión y OCR',tag:'Imagen',description:'Lee capturas y escaneos con OCR local. Con Gemini Vision activado interpreta diagramas e imágenes.',prompt:'Voy a adjuntar una imagen para que extraigas su texto y analices su contenido.'},
    {icon:Globe2,name:'Investigación web',tag:'Tavily',description:'Busca información reciente y muestra fuentes con enlaces verificables debajo de la respuesta.',prompt:'Busca en Internet las novedades recientes en auditoría de sistemas y privacidad. Incluye fuentes con enlaces y fecha.'},
  ];
  return <div className="content-page"><SubpageHeader eyebrow="HERRAMIENTAS · DOCUMENTOS Y DIAGRAMAS" title="De respuestas a entregables." description="Genera documentos descargables y diagramas visuales sin salir de ISO Studio. El contenido lo redacta el agente; el servidor local produce los archivos." icon={WandSparkles}/>
  <div className="tools-grid">{tools.map(t=><div className="tool-card" key={t.name}><div className="tool-card-top"><span className="tool-card-icon"><t.icon size={23}/></span><span className="tool-card-tag">{t.tag}</span></div><h3>{t.name}</h3><p>{t.description}</p><button onClick={()=>startPrompt(t.prompt)}>Probar herramienta <ArrowRight size={15}/></button></div>)}</div>
  <div className="skills-guide"><h3>¿Cómo se utilizan?</h3><p>Escribe <strong>«Genera un informe en Word»</strong>, <strong>«Crea un PDF»</strong>, <strong>«Genera una matriz Excel»</strong> o <strong>«Dibuja un diagrama de flujo»</strong>. Las solicitudes PDF/Word/Excel generan un archivo automáticamente cuando la respuesta real de n8n termina. También puedes usar los botones PDF/Word/Excel bajo cualquier respuesta. Los diagramas se renderizan cuando el agente entrega un bloque <code>```mermaid</code>.</p><p className="skills-caution">Las citas normativas necesitan evidencia del RAG. Estas herramientas no comprueban por sí solas la exactitud del contenido generado.</p></div></div>;
}

function SettingsPage({ configured, demo, setDemo, webAvailable, webMode, setWebMode }) {
  return <div className="content-page"><SubpageHeader eyebrow="PREFERENCIAS · CONEXIÓN" title="Control total, en local." description="Este frontend funciona en Windows. La generación de respuestas se realiza desde el workflow de n8n configurado en el servidor local." icon={Settings2}/>
    <div className="settings-grid"><div className="settings-main"><div className="settings-row"><div className="settings-row-icon"><Workflow size={20}/></div><div><h3>Conexión con n8n</h3><p>{configured ? 'Se detectó una URL configurada. Aún es necesario probar la comunicación con el agente.' : 'Falta configurar N8N_CHAT_URL en .env.'}</p></div><span className={`setting-mark ${configured ? 'mark-ready' : ''}`}>{configured ? 'Configurada' : 'Pendiente'}</span></div>
    <div className="settings-row"><div className="settings-row-icon"><WandSparkles size={20}/></div><div><h3>Vista previa de diseño</h3><p>Muestra respuestas simuladas, claramente identificadas, sin consultar Gemini.</p></div><button role="switch" aria-checked={demo} className={`switch ${demo ? 'switch-on' : ''}`} onClick={() => setDemo(!demo)}><span/></button></div>
    <div className="settings-row"><div className="settings-row-icon"><Globe2 size={20}/></div><div><h3>Investigación web</h3><p>{webAvailable?'Tavily configurado en Node.js. Fuentes y enlaces visibles debajo de cada respuesta.':'Para buscar en Internet, añade TAVILY_API_KEY a .env y reinicia Node.js.'}</p><p>Modo: {webMode==='auto'?'Automático':webMode==='on'?'Siempre buscar':'Desactivado'}. También puedes alternarlo desde el chat.</p></div><span className={`setting-mark ${webAvailable?'mark-ready':''}`}>{webAvailable?'Disponible':'Sin clave'}</span></div>
    <div className="settings-row"><div className="settings-row-icon"><LockKeyhole size={20}/></div><div><h3>Historial temporal</h3><p>Las conversaciones se guardan únicamente durante la sesión de esta pestaña.</p></div><span className="setting-mark">Temporal</span></div></div>
    <div className="settings-guide"><h3>Conectar con tu agente</h3><div className="settings-step"><span>1</span><p>En el nodo <strong>When chat message received</strong> de n8n, activa <strong>Embedded Chat</strong>.</p></div><div className="settings-step"><span>2</span><p>Publica el workflow y copia la <strong>Chat URL</strong> de producción.</p></div><div className="settings-step"><span>3</span><p>Pégala en <code>N8N_CHAT_URL</code> del archivo <code>.env</code> y reinicia <code>npm run dev</code>.</p></div><a href="https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/" target="_blank" rel="noopener noreferrer">Documentación oficial <ExternalLink size={14}/></a></div></div>
  </div>;
}

export default function App() {
  const [sessions, setSessions] = useState(readStore);
  const [activeId, setActiveId] = useState(() => sessions[0].id);
  const [view, setView] = useState('chat');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [configured, setConfigured] = useState(false);
  const [scopeState, setScopeState] = useState({ enabled:false, state:'awaiting_n8n_review', reason:'Falta verificar la especialización de n8n/RAG.' });
  const [webAvailable,setWebAvailable] = useState(false);
  const [visionAvailable,setVisionAvailable] = useState(false);
  const [visionEnabled,setVisionEnabled] = useState(false);
  const [visualDraft,setVisualDraft] = useState('');
  const [webMode,setWebMode] = useState(() => {const m=localStorage.getItem('iso-studio-web-mode');return ['auto','on','off'].includes(m)?m:'auto';});
  const [demo, setDemo] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showContext, setShowContext] = useState(true);
  const [dark, setDark] = useState(() => localStorage.getItem('iso-studio-theme') === 'dark');
  const [copied, setCopied] = useState(null);
  const [exporting, setExporting] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    fetch('/api/status').then(r => r.json()).then(s => { setConfigured(Boolean(s.configured));setScopeState(s.scope||{enabled:false,state:'awaiting_n8n_review',reason:'Alcance académico aún no habilitado.'}); setWebAvailable(Boolean(s.webSearch?.available));setVisionAvailable(Boolean(s.vision?.aiConfigured)); if (s.configured) setDemo(false); }).catch(() => {});
  }, []);
  useEffect(()=>{localStorage.setItem('iso-studio-web-mode',webMode)},[webMode]);
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; localStorage.setItem('iso-studio-theme', dark ? 'dark' : 'light'); }, [dark]);
  useEffect(() => { try { sessionStorage.setItem('iso-studio-sessions-v1', JSON.stringify(sessions.slice(0, 25).map(s => ({ ...s, messages: s.messages.slice(-40) })))); } catch {} }, [sessions]);
  useEffect(() => { const key = e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); inputRef.current?.focus(); setView('chat'); } }; window.addEventListener('keydown', key); return () => window.removeEventListener('keydown', key); }, []);
  const session = useMemo(() => sessions.find(s => s.id === activeId) || sessions[0], [sessions, activeId]);

  function addSession() { if (loading||uploading) return; const s = { id: crypto.randomUUID(), title: 'Nueva conversación', created: Date.now(), messages: [] }; setSessions(old => [s,...old].slice(0,25)); setActiveId(s.id); setText(''); setError(''); setUploadError(''); requestAnimationFrame(() => inputRef.current?.focus()); }
  function removeSession(id) { if (loading||uploading) return; const filtered = sessions.filter(s => s.id !== id); if (!filtered.length) { const next = { id: crypto.randomUUID(), title: 'Nueva conversación', messages: [], created: Date.now() }; setSessions([next]); setActiveId(next.id); setText(''); setError(''); return; } setSessions(filtered); if (id === activeId) setActiveId(filtered[0].id); }
  async function copyMessage(id, content) { try { await navigator.clipboard.writeText(content); setCopied(id); setTimeout(() => setCopied(null), 1800); } catch { setError('No se pudo copiar el texto.'); } }
  function copyCurrent() { const content = session.messages.map(m => `${m.role === 'user' ? 'Tú' : 'ISO Studio'}:\n${m.text}`).join('\n\n'); if (content) copyMessage('chat', content); }

  async function exportMessage(message,format,{sessionId=activeId,auto=false}={}){
    if(message.demo) return;
    setExporting(`${message.id}:${format}`);
    try{
      const diagrams=format==='xlsx'?[]:await captureDiagrams(message.text);
      const title=(message.text.match(/^#{1,2}\s+(.+)$/m)?.[1] || sessions.find(s=>s.id===sessionId)?.title || 'Informe ISO Studio').slice(0,160);
      const response=await fetch('/api/artifacts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({format,markdown:message.text,title,diagrams,scopeReceipt:message.scopeReceipt,sessionId})});
      const data=await response.json().catch(()=>({}));
      if(!response.ok) throw new Error(data.error||`Error HTTP ${response.status}`);
      setSessions(old=>old.map(s=>s.id===sessionId?{...s,messages:s.messages.map(m=>m.id===message.id?{...m,attachments:[...(m.attachments||[]),data]}:m)}:s));
      if(auto){const a=document.createElement('a');a.href=data.url;a.download=data.name;document.body.appendChild(a);a.click();a.remove();}
    }catch(err){setError(`Error al generar ${format.toUpperCase()}: ${err.message}`);}finally{setExporting('');}
  }
  function requestedFormat(message){
    const action=/(crea|crear|genera|generar|redacta|redactar|exporta|exportar|prepara|preparar|hazme|conviert[ea]|descarga|necesito un informe)/i.test(message);
    if(!action)return [];
    const results=[];
    if(/\b(docx|word)\b/i.test(message))results.push('docx');
    if(/\bpdf\b/i.test(message))results.push('pdf');
    if(/\b(excel|xlsx|hoja de c[aá]lculo|planilla)\b/i.test(message))results.push('xlsx');
    return results;
  }
  function openVisualFromChat(content){setVisualDraft('Crea una infografía profesional y clara basada en el siguiente contenido, sin inventar datos:\n\n'+content.slice(0,3000));setView('visual');}
  function startPrompt(prompt){addSession();setView('chat');setText(prompt);setTimeout(()=>inputRef.current?.focus(),100);}

  async function uploadFiles(selected) {
    if (loading || uploading || !selected?.length) return;
    const currentId=activeId;
    let count=session.files?.length||0;
    setUploadError('');setUploading(true);
    try {
      for(const file of selected){
        if(count>=4)throw new Error('Máximo cuatro documentos por conversación.');
        if(file.size>8*1024*1024)throw new Error(`${file.name} supera 8 MB.`);
        const form=new FormData();form.append('sessionId',currentId);form.append('file',file);form.append('analyzeVisual',visionEnabled?'1':'0');form.append('scopePurpose',text.trim());
        const response=await fetch('/api/uploads',{method:'POST',body:form});
        const data=await response.json().catch(()=>({}));
        if(!response.ok)throw new Error(data.error||`No se pudo procesar ${file.name}.`);
        count++;
        setSessions(old=>old.map(s=>s.id===currentId?{...s,files:[...(s.files||[]),data]}:s));
      }
    }catch(err){setUploadError(err.message||'No se pudo adjuntar el archivo.');}
    finally{setUploading(false);}
  }
  async function removeFile(id){
    const currentId=activeId;
    setSessions(old=>old.map(s=>s.id===currentId?{...s,files:(s.files||[]).filter(f=>f.id!==id)}:s));
    try{await fetch(`/api/uploads/${encodeURIComponent(id)}`,{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:currentId})});}catch{}
  }

  async function send() {
    const files=session.files||[];
    const message = text.trim() || (files.length ? 'Analiza los archivos adjuntos únicamente en relación con Gestión de Riesgos de información y privacidad; identifica evidencias y límites de las fuentes.' : '');
    if (!message || loading || uploading) return;
    setError(''); setText(''); setLoading(true);
    const targetId = activeId;
    const user = { id: crypto.randomUUID(), role: 'user', text: message, sources: files.map(f=>({id:f.id,name:f.name})) };
    setSessions(old => old.map(s => s.id === targetId ? {...s, title: s.messages.length === 0 ? (message.length > 33 ? message.slice(0, 33) + '…' : message) : s.title, messages: [...s.messages,user] } : s));
    try {
      let answer;
      let webSources=[]; let webSearched=false; let webCached=false; let scopeReceipt=null;
      if (demo) {
        await new Promise(resolve => setTimeout(resolve, 650));
        answer = `**Esto es una vista previa del diseño, no una respuesta real del agente.**\n\nTu consulta fue: “${message}”.\n\nCuando conectes el frontend con tu workflow de **n8n**, este espacio mostrará la respuesta de **Gemini**, utilizando **Qdrant** y el **Skill de evaluación** cuando corresponda.\n\nPuedes explorar la navegación, las conversaciones y el tema visual desde ahora.`;
      } else {
        const response = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ message, sessionId: targetId, fileIds: files.map(f=>f.id), webMode }) });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || `Error HTTP ${response.status}`);
        answer = data.answer; scopeReceipt=data.scopeReceipt||null;
        webSources = Array.isArray(data.webSources)?data.webSources:[];
        webSearched = Boolean(data.webSearched); webCached = Boolean(data.webCached);
      }
      const reply = { id: crypto.randomUUID(), role: 'assistant', text: answer, scopeReceipt, demo, attachments: [], webSources, webSearched, webCached };
      setSessions(old => old.map(s => s.id === targetId ? {...s, messages:[...s.messages,reply] } : s));
      const autoFormats = !demo ? requestedFormat(message) : [];
      for (const format of autoFormats) await exportMessage(reply,format,{sessionId:targetId,auto:true});
    } catch (err) { setError(err.message || 'No fue posible enviar el mensaje.'); }
    finally { setLoading(false); requestAnimationFrame(() => inputRef.current?.focus()); }
  }

  return <div className="app-shell"><Sidebar view={view} setView={setView} sessions={sessions} activeId={activeId} selectSession={setActiveId} addSession={addSession} removeSession={removeSession} collapsed={collapsed} setCollapsed={setCollapsed} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} dark={dark} setDark={setDark}/>
    <div className="workspace"><NavTop view={view} configured={configured} demo={demo} onMenu={() => setMobileOpen(true)} addSession={addSession} setView={setView} showContext={showContext} setShowContext={setShowContext} copied={copied === 'chat'} copyCurrent={copyCurrent}/>
      <div className="workspace-content">{!scopeState.enabled ? <section className="iso-scope-lock" role="status" aria-live="polite"><div className="iso-scope-lock-icon"><LockKeyhole size={38}/></div><span className="eyebrow">CONTROL DE ALCANCE ACADÉMICO</span><h1>Alcance aprobado: Gestión de Riesgos</h1><p>La política GR-01 a GR-06 está implementada. Para activar el agente falta comprobar que los workflows de n8n y la colección Qdrant utilizan únicamente las fuentes y apartados autorizados.</p><p><strong>Completa la revisión indicada en INSTALAR_PATCH_7_2_WINDOWS.md y configura SCOPE_N8N_REVIEWED=true en .env.</strong></p><p className="iso-scope-lock-note">El bloqueo protege la app hasta completar esa revisión. No borres tus workflows ni tu colección histórica.</p></section> : view === 'chat' ? <><main className="main-chat"><ChatScreen session={session} send={send} loading={loading} text={text} setText={setText} inputRef={inputRef} onSettings={() => setView('settings')} demo={demo} error={error} copyMessage={copyMessage} copied={copied} onExport={exportMessage} exporting={exporting} onVisual={openVisualFromChat} onUpload={uploadFiles} onRemove={removeFile} uploading={uploading} uploadError={uploadError} webMode={webMode} setWebMode={setWebMode} webAvailable={webAvailable} visionEnabled={visionEnabled} setVisionEnabled={setVisionEnabled} visionAvailable={visionAvailable}/></main>{showContext && <ContextPanel demo={demo} configured={configured} setView={setView} setShowContext={setShowContext}/>}</> : view === 'knowledge' ? <KnowledgePage demo={demo} configured={configured} setView={setView}/> : view === 'method' ? <MethodPage setView={setView}/> : view === 'skills' ? <SkillsPage startPrompt={startPrompt}/> : view === 'visual' ? <VisualStudioPanel initialPrompt={visualDraft}/> : <SettingsPage configured={configured} demo={demo} setDemo={setDemo} webMode={webMode} setWebMode={setWebMode} webAvailable={webAvailable}/>}</div>
    </div>
  </div>;
}
