import test from 'node:test';
import assert from 'node:assert/strict';
import sharp from 'sharp';
import {describeImageWithGemini,extractImage,ocrPdfPages,validImageHeader,imageMime} from '../server/lib/vision.js';

test('detecta y valida encabezados PNG y JPEG',()=>{
  const png=Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),Buffer.alloc(6)]);
  assert.equal(imageMime('auditoria.PNG'),'image/png');
  assert.equal(validImageHeader(png,'image/png'),true);
  assert.equal(validImageHeader(Buffer.from('no es png............'),'image/png'),false);
});

test('extrae una descripción IA cuando se solicita expresamente, sin exponer clave',async()=>{
  const png=await sharp({create:{width:80,height:40,channels:4,background:'#fafafa'}}).png().toBuffer();
  let received=false;
  const result=await extractImage({buffer:png,originalname:'captura.png',geminiKey:'NO_REAL',useVision:true,ocr:async()=> 'Procesos y activos', describe: async(_,opts)=>{received=opts.apiKey==='NO_REAL';return 'Diagrama de controles y procesos';}});
  assert.equal(received,true);
  assert.match(result.sections.map(s=>s.text).join(' '),/Diagrama de controles/);
  assert.match(result.note,/Gemini/);
});

test('OCR local por defecto no llama a Gemini',async()=>{
  const png=await sharp({create:{width:60,height:30,channels:4,background:'#ffffff'}}).png().toBuffer();
  let calls=0;
  const parsed=await extractImage({buffer:png,originalname:'captura.png',ocr:async()=> 'Control de acceso',describe:async()=>{calls++;return '';}});
  assert.equal(calls,0);assert.equal(parsed.sections[0].text,'Control de acceso');
});

test('Gemini Vision envía la imagen como inlineData y devuelve la descripción',async()=>{
  const png=await sharp({create:{width:60,height:30,channels:4,background:'#eee'}}).png().toBuffer();
  const result=await describeImageWithGemini(png,{apiKey:'TEST_ONLY',fetchImpl:async(url,req)=>{
    assert.match(url,/generateContent$/);assert.equal(req.headers['x-goog-api-key'],'TEST_ONLY');
    const payload=JSON.parse(req.body);assert.equal(payload.contents[0].parts[1].inlineData.mimeType,'image/jpeg');
    return {ok:true,json:async()=>({candidates:[{content:{parts:[{text:'Captura de un dashboard'}]}}]})};
  }});
  assert.equal(result,'Captura de un dashboard');
});

test('PDF sin texto usa OCR máximo en páginas de prueba (sin red)',async()=>{
  let callCount=0;
  const fakePdf={numPages:8,getPage:async n=>({n,cleanup(){}})};
  const result=await ocrPdfPages(fakePdf,async()=>'',{ocrPagesLimit:3,worker:async(fn)=>fn(async()=> 'texto OCR'),ocrRenderer:async(pg,recognize)=>{callCount++;return recognize();}});
  assert.equal(callCount,3);assert.equal(result.omitted,5);assert.equal(result.sections.length,3);
});
