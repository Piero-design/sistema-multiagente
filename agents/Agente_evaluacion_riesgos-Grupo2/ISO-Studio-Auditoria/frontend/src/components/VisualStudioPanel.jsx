import React,{useEffect,useState} from 'react';
import {Image as ImageIcon,Download,Sparkles,ShieldCheck,AlertTriangle,RefreshCw} from 'lucide-react';

const styles=[{id:'infografia',label:'Infografía'},{id:'portada',label:'Portada'},{id:'ilustracion',label:'Ilustración'},{id:'resumen_visual',label:'Resumen visual'}];
function sessionId(){
  const key='iso-studio-visual-session-v1';let s=sessionStorage.getItem(key);
  if(!s){s=crypto.randomUUID();sessionStorage.setItem(key,s);}return s;
}
export default function VisualStudioPanel({initialPrompt=''}){
  const [session]=useState(sessionId),[provider,setProvider]=useState('mock'),[needsCode,setNeedsCode]=useState(false);
  const [accessCode,setAccessCode]=useState(''),[style,setStyle]=useState('infografia');
  const [title,setTitle]=useState('Infografía de gestión de riesgos'),[prompt,setPrompt]=useState('Crea una infografía sobre la identificación, evaluación y tratamiento de riesgos de privacidad, según el alcance académico de ISO/IEC 27701:2025. Señala los ejemplos como ilustrativos.');
  const [items,setItems]=useState([]),[busy,setBusy]=useState(false),[error,setError]=useState('');
  useEffect(()=>{fetch('/api/visual/status').then(r=>r.json()).then(d=>{setProvider(d.provider||'mock');setNeedsCode(Boolean(d.requiresCode));}).catch(()=>setError('No se pudo comprobar la API visual.'));},[]);
  useEffect(()=>{if(initialPrompt)setPrompt(initialPrompt);},[initialPrompt]);
  async function reload(){try{const r=await fetch('/api/visual/history?sessionId='+encodeURIComponent(session));const d=await r.json();if(r.ok)setItems(d.items||[]);}catch{}}
  useEffect(()=>{reload();},[]);
  async function generate(){setError('');setBusy(true);
    try{
      const r=await fetch('/api/visual/generate',{method:'POST',headers:{'Content-Type':'application/json',...(needsCode?{'x-visual-access-code':accessCode}:{})},body:JSON.stringify({prompt,title,style,sessionId:session})});
      const d=await r.json();if(!r.ok)throw new Error(d.error||'Error de generación');await reload();
    }catch(err){setError(err.message||'No se pudo generar la imagen.');}finally{setBusy(false);}
  }
  return <main className="visual-page">
    <div className="visual-header"><span className="visual-hero-icon"><ImageIcon size={25}/></span><div><span className="visual-eyebrow">CAPACIDAD MULTIMODAL</span><h1>Estudio visual</h1><p>Infografías, portadas e ilustraciones para complementar respuestas y documentos de ISO Studio.</p></div></div>
    <div className="visual-columns"><section className="visual-card">
      <h2><Sparkles size={19}/> Crear imagen</h2>
      <p className="visual-muted">{provider==='mock'?'Modo de simulación: genera una tarjeta SVG para probar la integración, no una imagen creada por IA.':'Generación real con API de imágenes. Cada solicitud puede tener costo.'}</p>
      <label>Título</label><input value={title} onChange={e=>setTitle(e.target.value)} maxLength={120} />
      <label>Tipo de imagen</label><div className="visual-pills">{styles.map(x=><button key={x.id} onClick={()=>setStyle(x.id)} className={style===x.id?'active':''}>{x.label}</button>)}</div>
      <label>Describe lo que quieres generar</label><textarea rows={7} value={prompt} maxLength={3500} onChange={e=>setPrompt(e.target.value)} placeholder="Describe la imagen, su contenido y su estilo"/>
      {needsCode&&<><label>Código de acceso visual</label><input type="password" autoComplete="off" value={accessCode} onChange={e=>setAccessCode(e.target.value)} placeholder="Código privado configurado en .env"/><p className="visual-muted">Protege tu cuota de generación cuando compartes ISO Studio por Cloudflare.</p></>}
      <button className="visual-submit" onClick={generate} disabled={busy||!prompt.trim()|| (needsCode&&!accessCode)}>{busy?<RefreshCw size={17} className="spin"/>:<ImageIcon size={17}/>} {busy?'Generando imagen…':'Generar imagen'}</button>
      {error&&<div className="visual-error" role="alert"><AlertTriangle size={17}/>{error}</div>}
      <div className="visual-note"><ShieldCheck size={17}/> Al usar una API externa, el prompt se envía al proveedor configurado. No incluyas información confidencial.</div>
    </section><section className="visual-card visual-results">
      <h2><ImageIcon size={19}/> Resultados de esta sesión</h2>
      {items.length===0?<div className="visual-placeholder"><ImageIcon size={48}/><strong>Aquí aparecerán tus imágenes</strong><span>Crea tu primera ilustración o infografía.</span></div>:<div className="visual-gallery">{items.map(item=><article className="visual-image" key={item.id}><img src={item.url} alt={item.title}/><div><strong>{item.title}</strong><span>{item.style.replace('_',' ')} · {item.provider}</span></div><a download href={`${item.url}&download=1`}><Download size={16}/> Descargar</a></article>)}</div>}
    </section></div>
  </main>;
}
