import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
import mammoth from 'mammoth';
import ExcelJS from 'exceljs';

export const MAX_FILE_BYTES = 8 * 1024 * 1024;
export const MAX_SESSION_FILES = 4;
export const MAX_TEXT_CHARS = 180_000;
export const UPLOAD_TTL_MS = 2 * 60 * 60 * 1000;
export const ACCEPTED_EXTENSIONS = ['.pdf','.docx','.xlsx','.txt','.md','.csv','.png','.jpg','.jpeg','.webp'];
const SAFE_SESSION = /^[a-zA-Z0-9-]{8,100}$/;
const FILE_ID = /^[a-f0-9-]{36}$/;
const stopWords = new Set('de la el los las un una unos unas y o en por para con del al que como cual cuales donde cuando quien quienes sobre quiero dame haz realiza genera explica resume resumen archivo archivos documento documentos mi mis este esta estos estas se lo es son a me necesito puedes favor segun usando dentro acerca informacion'.split(' '));

export function validSession(id) { return typeof id === 'string' && SAFE_SESSION.test(id); }
export function acceptedFile(name) {return ACCEPTED_EXTENSIONS.includes(path.extname(String(name||'')).toLowerCase());}
export function cleanName(name) {return path.basename(String(name||'archivo')).replace(/[<>:"/\\|?*\x00-\x1f]/g,'_').slice(0,100)||'archivo';}

function enoughMagic(bytes,extension){
  if(extension==='.pdf') return bytes.subarray(0,5).toString('latin1')==='%PDF-';
  if(['.docx','.xlsx'].includes(extension)) return bytes.subarray(0,4).toString('hex')==='504b0304';
  if(extension==='.png')return bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]));
  if(['.jpg','.jpeg'].includes(extension))return bytes[0]===255&&bytes[1]===216&&bytes[2]===255;
  if(extension==='.webp')return bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP';
  return !bytes.includes(0);
}

const truncate = (txt,max) => String(txt||'').slice(0,max).replace(/\u0000/g,'');
export async function extractDocument({buffer,originalname},options={}) {
  const name=cleanName(originalname); const ext=path.extname(name).toLowerCase();
  if(!acceptedFile(name)) throw new Error('Formato no admitido. Usa PDF, DOCX, XLSX, TXT, MD, CSV, PNG, JPG o WEBP.');
  if(!buffer?.length || buffer.length>MAX_FILE_BYTES) throw new Error('El archivo debe pesar menos de 8 MB.');
  if(!enoughMagic(buffer,ext)) throw new Error('El archivo no coincide con el formato indicado o está dañado.');
  const sections=[]; let note='';
  if(['.png','.jpg','.jpeg','.webp'].includes(ext)){
    const {extractImage}=await import('./vision.js');
    const visual=await extractImage({buffer,originalname:name,geminiKey:options.geminiKey,geminiModel:options.geminiModel,useVision:Boolean(options.useVision)});
    sections.push(...visual.sections);note=visual.note;
  }else if(ext==='.pdf'){
    let pdf;
    try {
      pdf=await getDocument({data:new Uint8Array(buffer),useSystemFonts:true,disableFontFace:true}).promise;
      if(pdf.numPages>120) throw new Error('El PDF supera el máximo de 120 páginas.');
      // Mantiene la extracción original de texto y aplica OCR solo en páginas sin texto.
      const {ocrPdfPages}=await import('./vision.js');
      const parsed=await ocrPdfPages(pdf,async pg=>{
        const tc=await pg.getTextContent();
        return tc.items.map(i=>i.str||'').join(' ').replace(/\s+/g,' ').trim();
      });
      let length=0;
      for(const section of parsed.sections){if(length>=MAX_TEXT_CHARS)break;const text=section.text.slice(0,MAX_TEXT_CHARS-length);if(text.trim())sections.push({...section,text});length+=text.length;}
      if(parsed.ocrPages)note=`OCR local aplicado a ${parsed.ocrPages} página(s) sin texto seleccionable.`;
      if(parsed.omitted)note+=` Quedaron ${parsed.omitted} páginas escaneadas sin OCR por límite de seguridad; divide el PDF en partes.`;
      if(!sections.length) throw new Error('No se detectó texto; prueba un PDF con mayor resolución o utiliza imágenes individuales.');
    }finally{try{await pdf?.destroy();}catch{}}
  } else if(ext==='.docx') {
    const result=await mammoth.extractRawText({buffer});
    const text=truncate(result.value,MAX_TEXT_CHARS);
    if(text.trim()) sections.push(...groupLines(text,'sección',3000));
    note=result.messages?.some(m=>m.type==='warning')?'Se omitieron elementos no textuales del Word.':'';
  } else if(ext==='.xlsx'){
    const wb=new ExcelJS.Workbook();await wb.xlsx.load(buffer);
    let total=0;
    for(const sheet of wb.worksheets.slice(0,10)){
      const rows=[];
      sheet.eachRow({includeEmpty:false}, (row,index)=> {
        if(rows.length>=220 || total>=MAX_TEXT_CHARS) return;
        const values=row.values.slice(1).map(v=> typeof v==='object'&&v!==null ? (v.text??v.result??v.formula??JSON.stringify(v)) : String(v??''));
        const str=`Fila ${index}: ${values.join(' | ')}`;
        rows.push(truncate(str,900));total+=str.length;
      });
      if(rows.length) sections.push(...groupLines(rows.join('\n'),`hoja ${sheet.name}`,3100));
    }
    note='Se leen valores y fórmulas visibles; no se analizan macros, gráficos o formatos visuales.';
  } else {
    const text=new TextDecoder('utf-8',{fatal:false}).decode(buffer).replace(/\r\n?/g,'\n');
    if(text.trim()) sections.push(...groupLines(truncate(text,MAX_TEXT_CHARS),'sección',3200));
  }
  if(!sections.length) throw new Error('No se encontró texto utilizable en el archivo.');
  return {name, type:ext.slice(1), size:buffer.length, sections, characters:sections.reduce((n,s)=>n+s.text.length,0),note};
}

function groupLines(content,prefix,max){
  const lines=content.split(/\n/);let result=[],part='';let i=1;
  for(const line of lines){
    if((part.length+line.length+1)>max && part){result.push({label:`${prefix} ${i++}`,text:part});part='';}
    if(line.length>max){if(part){result.push({label:`${prefix} ${i++}`,text:part});part='';}for(let start=0;start<line.length;start+=max)result.push({label:`${prefix} ${i++}`,text:line.slice(start,start+max)});continue;}
    part+=(part?'\n':'')+line;
  }
  if(part)result.push({label:`${prefix} ${i}`,text:part});
  return result;
}

function terms(s){return [...new Set(String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').match(/[a-z0-9]{3,}/g)?.filter(w=>!stopWords.has(w))||[])];}
export function findRelevantSections(files,question,{maxCharacters=16000}={}) {
  const words=terms(question);
  const matches=[];
  for(const file of files){
    for(let index=0;index<file.sections.length;index++) {
      const section=file.sections[index];const lower=section.text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
      let score=words.reduce((n,t)=>n+(lower.includes(t)?1:0),0);
      if(index===0)score+=0.25;
      matches.push({...section,fileName:file.name,score,index});
    }
  }
  matches.sort((a,b)=>b.score-a.score||a.index-b.index);
  let context='', count=0;
  for(const section of matches){
    if(count>=12 || context.length>maxCharacters-650) break;
    const left=maxCharacters-context.length;
    const body=section.text.slice(0,Math.max(0,left-250));
    if(!body) break;
    context+=`\n[ARCHIVO: ${section.fileName} | ${section.label}]\n${body}\n`;
    count++;
  }
  return context;
}

export class UploadStore {
  constructor(folder){this.folder=folder;fs.mkdirSync(folder,{recursive:true});this.records=new Map();this.recover();}
  recover(){
    for(const name of fs.readdirSync(this.folder)){
      if(!FILE_ID.test(name.replace(/\.json$/,''))||!name.endsWith('.json'))continue;
      try{const data=JSON.parse(fs.readFileSync(path.join(this.folder,name),'utf8'));
        if(Date.now()-data.created<UPLOAD_TTL_MS&&validSession(data.sessionId))this.records.set(data.id,data);
        else fs.unlinkSync(path.join(this.folder,name));
      }catch{try{fs.unlinkSync(path.join(this.folder,name));}catch{}}
    }
  }
  prune(){for(const [id,item] of this.records){if(Date.now()-item.created>UPLOAD_TTL_MS)this.remove(id,item.sessionId);}}
  forSession(sessionId){this.prune();return [...this.records.values()].filter(r=>r.sessionId===sessionId);}
  add(sessionId,parsed){this.prune();if(this.forSession(sessionId).length>=MAX_SESSION_FILES)throw new Error('Máximo cuatro documentos por conversación.');
    const id=crypto.randomUUID();const item={id,sessionId,created:Date.now(),...parsed};
    fs.writeFileSync(path.join(this.folder,`${id}.json`),JSON.stringify(item),{flag:'wx'});
    this.records.set(id,item);return {id,name:item.name,type:item.type,size:item.size,characters:item.characters,note:item.note};
  }
  select(sessionId,ids){this.prune();const unique=[...new Set(ids)];if(unique.length>MAX_SESSION_FILES)throw new Error('Demasiados archivos seleccionados.');
    return unique.map(id=>{const item=this.records.get(id);if(!item||item.sessionId!==sessionId)throw new Error('Archivo no disponible, caducado o perteneciente a otra conversación.');return item;});
  }
  remove(id,sessionId){const item=this.records.get(id);if(!item||item.sessionId!==sessionId)return false;this.records.delete(id);try{fs.unlinkSync(path.join(this.folder,`${id}.json`));}catch{}return true;}
}
