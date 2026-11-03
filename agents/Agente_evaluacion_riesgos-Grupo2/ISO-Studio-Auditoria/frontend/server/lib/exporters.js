import PDFDocument from 'pdfkit';
import {
  Document, Packer, Paragraph, HeadingLevel, AlignmentType, TextRun,
  Table, TableRow, TableCell, WidthType, BorderStyle, ImageRun,
  Header, Footer, PageNumber, ShadingType,
} from 'docx';
import {parseBlocks,plainText} from './markdown.js';

const INK='20243D', PURPLE='7061D8', MUTED='747B90', LINE='E4E4EF', LIGHT='F4F2FC';
const pdfFont = str => String(str).replace(/[\u2013\u2014]/g,'-').replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/\u2022/g,'*').replace(/[\u200b-\u200d]/g,'');

function getImage(base64) {
  if (typeof base64 !== 'string' || !/^data:image\/png;base64,/.test(base64)) return null;
  const raw=base64.slice('data:image/png;base64,'.length);
  if (raw.length>3_200_000) return null;
  const buf=Buffer.from(raw,'base64');
  return buf.length>24 && buf.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))?buf:null;
}

export function createPdf({title,markdown,diagrams=[]}) {
 return new Promise((resolve,reject)=>{
  const doc = new PDFDocument({size:'A4',margins:{top:64,bottom:63,left:57,right:57},bufferPages:true, info:{Title:title,Author:'ISO Studio'}});
  const chunks=[]; doc.on('data',c=>chunks.push(c));doc.on('error',reject);doc.on('end',()=>resolve(Buffer.concat(chunks)));
  const W=doc.page.width-doc.page.margins.left-doc.page.margins.right;
  const x=doc.page.margins.left;
  function check(h){if(doc.y+h>doc.page.height-doc.page.margins.bottom) doc.addPage();}
  function body(text,opts={}){doc.fillColor(INK).font('Helvetica').fontSize(10.4).text(pdfFont(text), x,doc.y,{width:W,lineGap:4,paragraphGap:9,...opts});doc.moveDown(.35);}
  function heading(text,lvl){check(lvl<=2?55:36);doc.moveDown(lvl===1?.8:.55).fillColor(INK).font('Helvetica-Bold').fontSize(lvl===1?19:lvl===2?14:11.7).text(pdfFont(text),x,doc.y,{width:W});doc.moveDown(.5);}
  doc.save().rect(0,0,doc.page.width,12).fill(`#${PURPLE}`).restore();
  doc.fillColor(`#${PURPLE}`).font('Helvetica-Bold').fontSize(9).text('ISO STUDIO  /  DOCUMENTO GENERADO',x,doc.y,{characterSpacing:1.3});
  doc.moveDown(.8).fillColor(`#${INK}`).font('Helvetica-Bold').fontSize(24).text(pdfFont(title),x,doc.y,{width:W});
  doc.moveDown(.35).fillColor(`#${MUTED}`).font('Helvetica').fontSize(9).text(new Date().toLocaleDateString('es-PE'),x,doc.y);
  doc.moveDown(1.1).strokeColor(`#${LINE}`).moveTo(x,doc.y).lineTo(x+W,doc.y).stroke();doc.moveDown(.65);
  let dia=0;
  for(const b of parseBlocks(markdown)){
    if(b.type==='heading'){ heading(b.text,b.level);continue; }
    if(b.type==='paragraph'){body(b.text);continue;}
    if(b.type==='quote'){check(40);doc.save().rect(x,doc.y,3,35).fill(`#${PURPLE}`).restore();doc.x=x+13;doc.fillColor(`#${MUTED}`).font('Helvetica-Oblique').fontSize(10).text(pdfFont(b.text),x+13,doc.y,{width:W-13});doc.x=x;doc.moveDown(.8);continue;}
    if(b.type==='list'){for(let i=0;i<b.items.length;i++){check(20);const prefix=b.ordered?`${i+1}.`:'-';doc.fillColor(`#${INK}`).font('Helvetica').fontSize(10.4).text(pdfFont(`${prefix} ${b.items[i]}`),x+12,doc.y,{width:W-12,lineGap:3});doc.moveDown(.18);}doc.moveDown(.5);continue;}
    if(b.type==='rule'){check(24);doc.moveDown(.4).strokeColor(`#${LINE}`).moveTo(x,doc.y).lineTo(x+W,doc.y).stroke();doc.moveDown(.6);continue;}
    if(b.type==='code'||b.type==='diagram'){
      const png=b.type==='diagram'?getImage(diagrams[dia++]?.png):null;
      if(png){try{const iw=png.readUInt32BE(16),ih=png.readUInt32BE(20);const scale=Math.min(W/iw,320/ih,1);const height=Math.round(ih*scale);check(height+20);doc.image(png,x,doc.y,{width:Math.round(iw*scale),height});doc.y+=height+15;}catch{body(b.text);}}
      else {check(50);doc.fillColor(`#${MUTED}`).font('Courier').fontSize(8).text(pdfFont(b.text),x+9,doc.y,{width:W-18,lineGap:3});doc.moveDown(.8);}
      continue;
    }
    if(b.type==='table'){
      const cols=b.headers.length; if(!cols || cols>10){continue;}
      const widths=Array(cols).fill(W/cols);const rows=[b.headers,...b.rows];
      for (let r=0;r<rows.length;r++){
        const cells=rows[r]; const fontSize=cols>6?7:8.5;doc.font(r===0?'Helvetica-Bold':'Helvetica').fontSize(fontSize);
        const height=Math.max(30,...widths.map((wid,k)=>doc.heightOfString(pdfFont(cells[k]||''),{width:wid-16,lineGap:2})+16));
        check(Math.min(height,doc.page.height-145));const y=doc.y;
        if(r===0) doc.save().rect(x,y,W,height).fill(`#${LIGHT}`).restore();
        let cx=x;
        for(let k=0;k<cols;k++){
          doc.save().rect(cx,y,widths[k],height).lineWidth(.5).strokeColor(`#${LINE}`).stroke().restore();
          doc.fillColor(`#${INK}`).font(r===0?'Helvetica-Bold':'Helvetica').fontSize(fontSize).text(pdfFont(cells[k]||''),cx+8,y+8,{width:widths[k]-16,lineGap:2});cx+=widths[k];
        }
        doc.y=y+height;
      }
      doc.moveDown(.9);
    }
  }
  const count=doc.bufferedPageRange().count;
  for(let p=0;p<count;p++){
    doc.switchToPage(p);
    doc.save().strokeColor(`#${LINE}`).moveTo(x,doc.page.height-44).lineTo(x+W,doc.page.height-44).stroke().restore();
    const previousBottom=doc.page.margins.bottom;doc.page.margins.bottom=0;
    doc.fillColor(`#${MUTED}`).font('Helvetica').fontSize(8).text('ISO Studio  -  Verificar fuentes y conclusiones.',x,doc.page.height-37,{width:W-60,lineBreak:false});
    doc.text(`${p+1} / ${count}`,x+W-39,doc.page.height-37,{width:39,align:'right',lineBreak:false});
    doc.page.margins.bottom=previousBottom;
  }
  doc.end();
 });
}

const tx=(text,bold=false,size=20,color=INK)=>new TextRun({text, bold,size,color});
const para=(text,{heading,bold=false,indent=0,spacingBefore=0,spacingAfter=140,color=INK}={})=>new Paragraph({heading,indent:{left:indent},spacing:{before:spacingBefore,after:spacingAfter,line:330},children:[tx(text,bold,21,color)]});
export async function createDocx({title,markdown,diagrams=[]}) {
  const blocks=parseBlocks(markdown);const children=[];let di=0;
  children.push(new Paragraph({spacing:{after:120},children:[tx('ISO STUDIO  /  DOCUMENTO GENERADO',true,16,PURPLE)]}));
  children.push(new Paragraph({heading:HeadingLevel.TITLE,spacing:{after:80},children:[tx(title,true,36,INK)]}));
  children.push(new Paragraph({spacing:{after:260},children:[tx(new Date().toLocaleDateString('es-PE'),false,18,MUTED)]}));
  for(const b of blocks){
    if(b.type==='heading'){
      const hl=b.level===1?HeadingLevel.HEADING_1:b.level===2?HeadingLevel.HEADING_2:HeadingLevel.HEADING_3;
      children.push(new Paragraph({heading:hl,spacing:{before:250,after:100},children:[tx(b.text,true,b.level===1?30:b.level===2?26:23,INK)]}));continue;
    }
    if(b.type==='paragraph'){children.push(para(b.text));continue;}
    if(b.type==='quote'){children.push(para(b.text,{indent:340,color:MUTED}));continue;}
    if(b.type==='list'){b.items.forEach((t,i)=>children.push(para(`${b.ordered?`${i+1}.`:'•'} ${t}`,{indent:300,spacingAfter:90})));continue;}
    if(b.type==='rule'){children.push(new Paragraph({border:{bottom:{color:LINE,size:5,style:BorderStyle.SINGLE}},spacing:{after:150}}));continue;}
    if(b.type==='code'||b.type==='diagram'){
      const png=b.type==='diagram'?getImage(diagrams[di++]?.png):null;
      if(png){
        const originalW=png.readUInt32BE(16), originalH=png.readUInt32BE(20);const ratio=Math.min(1,560/originalW,410/originalH);
        children.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:120,after:160},children:[new ImageRun({data:png,type:'png',transformation:{width:Math.round(originalW*ratio),height:Math.round(originalH*ratio)}})]}));
      } else children.push(new Paragraph({spacing:{before:110,after:160},children:[tx(b.text,false,17,MUTED)]}));
      continue;
    }
    if(b.type==='table'&&b.headers.length&&b.headers.length<=10){
      const rows=[b.headers,...b.rows].map((cells,r)=>new TableRow({children:b.headers.map((_,c)=>new TableCell({
        shading:r===0?{type:ShadingType.CLEAR,fill:LIGHT}:undefined,
        margins:{top:95,bottom:95,left:105,right:105},
        children:[new Paragraph({children:[tx(cells[c]||'',r===0,18,INK)]})],
      }))}));
      children.push(new Table({rows,width:{size:100,type:WidthType.PERCENTAGE},borders:{top:{style:BorderStyle.SINGLE,color:LINE,size:5},bottom:{style:BorderStyle.SINGLE,color:LINE,size:5},left:{style:BorderStyle.SINGLE,color:LINE,size:5},right:{style:BorderStyle.SINGLE,color:LINE,size:5},insideHorizontal:{style:BorderStyle.SINGLE,color:LINE,size:5},insideVertical:{style:BorderStyle.SINGLE,color:LINE,size:5}}}));
      children.push(new Paragraph({text:'',spacing:{after:200}}));
    }
  }
  const document=new Document({creator:'ISO Studio',title,description:'Documento creado desde ISO Studio',sections:[{
    properties:{page:{margin:{top:1030,bottom:990,left:1040,right:1040}}},
    headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[tx('ISO STUDIO',true,15,PURPLE)]})]})},
    footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[tx('ISO Studio · Verificar fuentes  |  Página ',false,16,MUTED),new TextRun({children:[PageNumber.CURRENT],color:MUTED,size:16})]})]})},
    children,
  }]});
  return Buffer.from(await Packer.toBuffer(document));
}
