import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const uuidRe = /^[a-f0-9-]{36}$/i;
const sessionRe = /^[a-zA-Z0-9-]{8,100}$/;
export const validateVisualSession = id => typeof id === 'string' && sessionRe.test(id);

function escapeXml(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}
function linesOf(text,max=57) {
  const words = String(text).split(/\s+/); const lines=[]; let line='';
  for(const word of words) {const s=line?`${line} ${word}`:word;
    if(s.length>max&&line){lines.push(line);line=word;}else line=s;}
  if(line)lines.push(line); return lines.slice(0,11);
}

export function makeMockSvg(prompt,style) {
  const lines=linesOf(prompt,55);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#ede9fe"/><stop offset="1" stop-color="#ddd6fe"/></linearGradient></defs>
<rect width="1024" height="1024" fill="url(#bg)"/>
<rect x="64" y="64" width="896" height="896" rx="30" fill="#fff" stroke="#c4b5fd" stroke-width="3"/>
<rect x="90" y="92" width="844" height="70" rx="18" fill="#6047c2"/>
<text x="120" y="136" font-family="Arial" font-size="27" font-weight="bold" fill="white">ISO STUDIO · MODO DE PRUEBA</text>
<text x="96" y="224" font-family="Arial" font-size="34" font-weight="bold" fill="#342463">${escapeXml(style.toUpperCase().replace(/_/g,' '))}</text>
${lines.map((line,i)=>`<text x="96" y="${295+i*46}" font-family="Arial" font-size="24" fill="#514878">${escapeXml(line)}</text>`).join('\n')}
<text x="96" y="898" font-family="Arial" font-size="20" fill="#7c3aed">SIMULACIÓN SVG · No generada por inteligencia artificial</text>
</svg>`;
}

export function createVisualService({root,provider='mock',model='gpt-image-1',apiKey='',accessCode='',maxPerHour=8}) {
  const dir=path.join(root,'.local-visual'); fs.mkdirSync(dir,{recursive:true});
  const indexPath=path.join(dir,'index.json');
  let index={};try{index=JSON.parse(fs.readFileSync(indexPath,'utf8'));}catch{}
  const recent=[];
  let inFlight=false;
  function isProtected(){return provider==='openai';}
  function checkCode(value){
    if(!isProtected())return true;
    if(accessCode.length<12||typeof value!=='string')return false;
    const a=Buffer.from(value),b=Buffer.from(accessCode);
    return a.length===b.length&&crypto.timingSafeEqual(a,b);
  }
  const imageUrl=(id,sessionId)=>`/api/visual/image/${encodeURIComponent(id)}?sessionId=${encodeURIComponent(sessionId)}`;
  function publicRecord(record){return {id:record.id,title:record.title,style:record.style,provider:record.provider,url:imageUrl(record.id,record.sessionId),name:record.filename};}
  function history(sessionId){return Object.values(index).filter(x=>x.sessionId===sessionId).sort((a,b)=>b.createdAt-a.createdAt).slice(0,30).map(publicRecord);}
  async function generate({prompt,title,style,sessionId,authorization}) {
    if(!validateVisualSession(sessionId))return {code:400,error:'Sesión inválida.'};
    if(typeof prompt!=='string'||prompt.trim().length<3||prompt.length>3500)return {code:400,error:'Escribe un prompt de 3 a 3500 caracteres.'};
    if(typeof title!=='string'||title.length>120)return {code:400,error:'Título inválido.'};
    const styles=['infografia','portada','ilustracion','resumen_visual'];
    if(!styles.includes(style))return {code:400,error:'Estilo visual no admitido.'};
    if(!checkCode(authorization))return {code:403,error:'Código visual incorrecto o VISUAL_ACCESS_CODE no configurado.'};
    const now=Date.now(); for(let i=recent.length-1;i>=0;i--)if(now-recent[i].time>3600000)recent.splice(i,1);
    if(recent.length>=maxPerHour)return {code:429,error:'Se alcanzó el límite horario de generación visual.'};
    if(recent.filter(x=>x.sessionId===sessionId).length>=3)return {code:429,error:'Máximo tres generaciones por sesión y hora.'};
    if(inFlight)return {code:429,error:'Ya hay otra imagen generándose. Intenta de nuevo después.'};
    if(isProtected()&&!apiKey)return {code:503,error:'Falta configurar VISUAL_OPENAI_API_KEY.'};
    inFlight=true;recent.push({time:now,sessionId});
    try {
      const id=crypto.randomUUID();let bytes;let ext;
      if(provider==='mock'){
        ext='svg';bytes=Buffer.from(makeMockSvg(prompt,style),'utf8');
      }else if(provider==='openai'){
        const fullPrompt=`Crea una ${style.replace('_',' ')} profesional y visualmente clara. Prioriza precisión visual, jerarquía, composición limpia y legibilidad. ${prompt.trim()}`;
        const response=await fetch('https://api.openai.com/v1/images/generations',{
          method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${apiKey}`},
          body:JSON.stringify({model,prompt:fullPrompt,size:'1024x1024',quality:'low',n:1}),signal:AbortSignal.timeout(125000)
        });
        if(!response.ok){console.error('Visual provider HTTP status:',response.status);return {code:502,error:`El proveedor de imágenes devolvió HTTP ${response.status}. Comprueba permisos, saldo y modelo.`};}
        const result=await response.json();const b64=result?.data?.[0]?.b64_json;
        if(!b64)return {code:502,error:'El proveedor no devolvió una imagen.'};
        ext='png';bytes=Buffer.from(b64,'base64');
        if(!bytes.length||bytes.length>20_000_000)return {code:502,error:'La imagen devuelta es inválida o demasiado grande.'};
      }else return {code:503,error:'Proveedor visual no admitido.'};
      const filename=`${id}.${ext}`;
      await fs.promises.writeFile(path.join(dir,filename),bytes,{flag:'wx'});
      const record={id,filename,title:title||'Visual ISO Studio',style,sessionId,provider,createdAt:Date.now()};
      index[id]=record;await fs.promises.writeFile(indexPath,JSON.stringify(index,null,2),'utf8');
      return {code:200,asset:publicRecord(record)};
    }catch(err){console.error('Visual generation failed:',err?.name||'error',err?.message?.slice(0,100));return {code:502,error:'No se pudo generar la imagen. Revisa la conexión y los registros del servidor.'};}
    finally{inFlight=false;}
  }
  function fileFor(id,sessionId){if(!uuidRe.test(id)||!validateVisualSession(sessionId))return null;
    const rec=index[id];if(!rec||rec.sessionId!==sessionId)return null;
    const p=path.join(dir,rec.filename);if(!fs.existsSync(p))return null;
    return {path:p,name:rec.filename,contentType:rec.filename.endsWith('.svg')?'image/svg+xml':'image/png'};
  }
  return {generate,history,fileFor,provider,model,checkCode,isProtected};
}
