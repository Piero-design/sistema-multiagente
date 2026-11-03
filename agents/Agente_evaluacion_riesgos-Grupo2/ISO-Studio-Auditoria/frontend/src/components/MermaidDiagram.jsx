import {useEffect,useState} from 'react';
import mermaid from 'mermaid';
import DOMPurify from 'dompurify';
import {Download, Image as ImageIcon, AlertTriangle} from 'lucide-react';

mermaid.initialize({startOnLoad:false,securityLevel:'strict',htmlLabels:false,theme:'neutral',flowchart:{useMaxWidth:true},maxTextSize:16000});

function cleanSVG(text){return DOMPurify.sanitize(text,{USE_PROFILES:{svg:true,svgFilters:true}});}
export async function makeMermaidSVG(source){
  if(typeof source!=='string'||source.length>16000) throw new Error('El diagrama es demasiado grande.');
  const id=`iso-${crypto.randomUUID().replace(/-/g,'')}`;
  const result=await mermaid.render(id,source);
  return cleanSVG(result.svg);
}
export async function svgToPNG(svg){
  const blob=new Blob([svg],{type:'image/svg+xml;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  try {
    const img=new Image();
    await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('No se pudo convertir el SVG a PNG'));img.src=url;});
    const w=Math.max(450,Math.min(1600,img.naturalWidth||850));
    const h=Math.max(250,Math.min(1000,img.naturalHeight||500));
    const scale=Math.min(w/(img.naturalWidth||w),h/(img.naturalHeight||h));
    const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
    const context=canvas.getContext('2d');context.fillStyle='#ffffff';context.fillRect(0,0,w,h);
    context.drawImage(img,(w-img.naturalWidth*scale)/2,(h-img.naturalHeight*scale)/2,img.naturalWidth*scale,img.naturalHeight*scale);
    return canvas.toDataURL('image/png');
  } finally{URL.revokeObjectURL(url);}
}
export async function captureDiagrams(markdown){
  const codes=[...markdown.matchAll(/```mermaid\s*\n([\s\S]*?)```/gi)].slice(0,4).map(m=>m[1]);
  const files=[];
  for(const code of codes){
    try{const svg=await makeMermaidSVG(code);files.push({png:await svgToPNG(svg)});}
    catch{files.push({png:''});}
  }
  return files;
}
function download(data,type,file){
  const url=URL.createObjectURL(new Blob([data],{type}));
  const a=document.createElement('a');a.href=url;a.download=file;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
}
export default function MermaidDiagram({source}){
  const [svg,setSVG]=useState('');const [error,setError]=useState('');const [busy,setBusy]=useState(true);
  useEffect(()=>{
    let active=true;setBusy(true);setError('');
    makeMermaidSVG(source).then(s=>{if(active)setSVG(s);}).catch(e=>{if(active)setError(e.message||'Diagrama inválido');}).finally(()=>{if(active)setBusy(false);});
    return()=>{active=false;};
  },[source]);
  async function png(){try{const data=await svgToPNG(svg);const a=document.createElement('a');a.href=data;a.download='iso-studio-diagrama.png';a.click();}catch(e){setError(e.message);}}
  return <div className="mermaid-shell">
    <div className="diagram-toolbar"><span><ImageIcon size={15}/> Diagrama renderizado · Mermaid</span><div><button disabled={!svg} onClick={()=>download(svg,'image/svg+xml','iso-studio-diagrama.svg')}><Download size={14}/> SVG</button><button disabled={!svg} onClick={png}><Download size={14}/> PNG</button></div></div>
    {busy?<div className="diagram-loading">Renderizando diagrama…</div>: error?<div className="diagram-error"><AlertTriangle size={17}/> {error}<pre>{source}</pre></div>:<div className="mermaid-svg" dangerouslySetInnerHTML={{__html:svg}}/>}
  </div>;
}
