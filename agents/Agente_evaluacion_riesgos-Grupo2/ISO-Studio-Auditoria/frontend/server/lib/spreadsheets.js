/**
 * ISO Studio: exportación local a XLSX a partir de tablas Markdown.
 * No interpreta ni ejecuta fórmulas procedentes del modelo: solo añade fórmulas
 * controladas por el servidor para una matriz de riesgos de demostración 3×3.
 */
import ExcelJS from 'exceljs';
import {parseBlocks,plainText} from './markdown.js';

const NAVY='FF20243D', PURPLE='FF6B5DD7', PALE='FFF0EDFF', WHITE='FFFFFFFF';
const INK='FF293147', GREY='FF667085', LINE='FFDDE2EE', YELLOW='FFFFF4CC';
const PALETTE={Alto:'FFFDE9EA',Medio:'FFFFF2CC',Bajo:'FFDBF5E9'};
const MAX_TABLES=6, MAX_ROWS=450, MAX_COLS=18, MAX_VALUE=500;

const normalize=(s='')=>String(s).toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim();
function riskValue(raw){
  const clean=normalize(raw);
  if(/^(alto|alta|3)(\b|$)/.test(clean))return 3;
  if(/^(medio|media|moderad[oa]|2)(\b|$)/.test(clean))return 2;
  if(/^(bajo|baja|1)(\b|$)/.test(clean))return 1;
  return null;
}
function typed(raw){
  let v=String(raw??'').slice(0,MAX_VALUE).trim();
  if (!v) return '';
  // Los datos del agente son texto no confiable. No se evaluarán expresiones del usuario.
  if (/^[=+@\t\r]/.test(v) || /^-(?!\d)/.test(v)) return `'${v}`;
  if (/^-?(?:0|[1-9]\d{0,8})(?:[.,]\d{1,4})?$/.test(v) && !/^0\d/.test(v)) {
    const n=Number(v.replace(',','.'));
    if(Number.isFinite(n))return n;
  }
  return v;
}
function styleTitle(ws,text,through=8){
  ws.mergeCells(1,1,1,through);
  const title=ws.getCell(1,1);title.value=text;
  title.font={name:'Aptos Display',size:19,bold:true,color:{argb:WHITE}};
  title.fill={type:'pattern',pattern:'solid',fgColor:{argb:NAVY}};
  title.alignment={vertical:'middle',indent:1};
  ws.getRow(1).height=46;
  ws.mergeCells(2,1,2,through);
  const info=ws.getCell(2,1);info.value='ISO STUDIO  •  Datos generados con IA: revisar y validar antes de utilizarlos en una auditoría.';
  info.font={name:'Aptos',size:10,color:{argb:GREY},italic:true};
  info.fill={type:'pattern',pattern:'solid',fgColor:{argb:'FFF5F6FA'}};
  ws.getRow(2).height=29;info.alignment={vertical:'middle',indent:1,wrapText:true};
}
function formatGrid(ws,headerRow,cols,totalRows){
  const h=ws.getRow(headerRow);
  h.height=32;
  for(let j=1;j<=cols;j++){
    const c=h.getCell(j);
    c.fill={type:'pattern',pattern:'solid',fgColor:{argb:PURPLE}};
    c.font={name:'Aptos',bold:true,color:{argb:WHITE},size:10};
    c.alignment={vertical:'middle',wrapText:true,indent:1};
  }
  for(let r=headerRow+1;r<=totalRows;r++){
    ws.getRow(r).height=34;
    for(let c=1;c<=cols;c++){
      const cell=ws.getCell(r,c);
      cell.font={name:'Aptos',size:10,color:{argb:INK}};
      cell.fill={type:'pattern',pattern:'solid',fgColor:{argb:r%2===0?'FFF8F9FD':'FFFFFFFF'}};
      cell.alignment={vertical:'middle',wrapText:true,indent:1};
      cell.border={bottom:{style:'hair',color:{argb:LINE}}};
    }
  }
  ws.views=[{state:'frozen',ySplit:headerRow,showGridLines:false}];
  ws.autoFilter={from:{row:headerRow,column:1},to:{row:Math.max(headerRow+1,totalRows),column:cols}};
}
function columnWidth(name){
  const n=normalize(name);
  if(/descripcion|recomendacion|tratamiento|evidencia|observaciones|detalle/.test(n))return 36;
  if(/riesgo|amenaza|vulnerabilidad|control|hallazgo/.test(n))return 30;
  if(/probabilidad|impacto|puntuacion|nivel/.test(n))return 20;
  if(/id|codigo|n°|nº/.test(n))return 13;
  return Math.max(17,Math.min(32,String(name||'').length+6));
}
function unique(name,used){
  let base=String(name||'Tabla').replace(/[\\\/?*\[\]:]/g,' ').trim().slice(0,28)||'Tabla';
  let candidate=base, k=2;
  while(used.has(candidate.toLowerCase())){candidate=base.slice(0,24)+` ${k++}`;}
  used.add(candidate.toLowerCase());return candidate;
}
function riskCols(headers){
  const impact=headers.findIndex(h=>/\bimpacto\b/.test(normalize(h)));
  const probability=headers.findIndex(h=>/\bprobabilidad\b/.test(normalize(h)));
  const risk=headers.findIndex(h=>/\briesgo\b/.test(normalize(h)));
  return risk>=0&&impact>=0&&probability>=0 ? {impact,probability} : null;
}
function colLetter(i){let s='';for(let n=i;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}

function addTable(wb,block,num,{used,sourceTitle}){
  const headers=block.headers.slice(0,MAX_COLS).map((h,j)=>h||`Columna ${j+1}`);
  const rows=block.rows.slice(0,MAX_ROWS).map(row=>headers.map((_,i)=>typed(row[i]??'')));
  if(!headers.length)return null;
  const risk=riskCols(headers);
  const name=unique(risk?'Matriz de riesgos':`Tabla ${num}`,used);
  const ws=wb.addWorksheet(name,{properties:{defaultRowHeight:18},pageSetup:{paperSize:9,orientation:'landscape',fitToPage:true,fitToWidth:1}});
  const additional=risk?4:0, total=headers.length+additional;
  styleTitle(ws,risk?'MATRIZ DE RIESGOS':`TABLA ${num}`,Math.max(8,total));
  const headerRow=4;
  const exportHeaders=[...headers,...(risk?['Impacto (1-3)','Probabilidad (1-3)','Puntuación referencial','Nivel referencial']:[])];
  exportHeaders.forEach((h,i)=>ws.getCell(headerRow,i+1).value=h);
  rows.forEach((values,idx)=>{
    const row=headerRow+1+idx;
    values.forEach((value,i)=>ws.getCell(row,i+1).value=value);
    if(risk){
      const b=headers.length+1;
      ws.getCell(row,b).value=riskValue(block.rows[idx]?.[risk.impact]);
      ws.getCell(row,b+1).value=riskValue(block.rows[idx]?.[risk.probability]);
      const ia=colLetter(b),pa=colLetter(b+1),score=colLetter(b+2);
      ws.getCell(row,b+2).value={formula:`IF(OR(${ia}${row}="",${pa}${row}=""),"",${ia}${row}*${pa}${row})`};
      ws.getCell(row,b+3).value={formula:`IF(${score}${row}="","Pendiente",IF(${score}${row}>=6,"Alto",IF(${score}${row}>=3,"Medio","Bajo")))`};
    }
  });
  const last=Math.max(headerRow+1,headerRow+rows.length);
  formatGrid(ws,headerRow,total,last);
  exportHeaders.forEach((h,i)=>ws.getColumn(i+1).width=columnWidth(h));
  if(risk){
    const n=headers.length;
    ws.getColumn(n+1).width=20;ws.getColumn(n+2).width=23;ws.getColumn(n+3).width=23;ws.getColumn(n+4).width=24;
    for(let r=5;r<=last;r++)for(let c=n+1;c<=n+2;c++){
      const cell=ws.getCell(r,c);cell.fill={type:'pattern',pattern:'solid',fgColor:{argb:YELLOW}};
      cell.numFmt='0';cell.protection={locked:false};
      cell.dataValidation={type:'whole',operator:'between',formulae:[1,3],allowBlank:true,showErrorMessage:true,error:'Introduce un valor entre 1 y 3.'};
    }
    ws.addConditionalFormatting({ref:`${colLetter(n+4)}5:${colLetter(n+4)}${last}`,rules:[
      {type:'expression',formulae:[`${colLetter(n+4)}5="Alto"`],style:{fill:{type:'pattern',pattern:'solid',bgColor:{argb:PALETTE.Alto}}}},
      {type:'expression',formulae:[`${colLetter(n+4)}5="Medio"`],style:{fill:{type:'pattern',pattern:'solid',bgColor:{argb:PALETTE.Medio}}}},
      {type:'expression',formulae:[`${colLetter(n+4)}5="Bajo"`],style:{fill:{type:'pattern',pattern:'solid',bgColor:{argb:PALETTE.Bajo}}}},
    ]});
    return {name, count:rows.length, impactCol:colLetter(n+1), probabilityCol:colLetter(n+2), levelCol:colLetter(n+4),last:headerRow+rows.length};
  }
  return {name,count:rows.length};
}
function addOverview(ws,title,risk,tables){
  ws.views=[{state:'frozen',ySplit:3,showGridLines:false}];
  styleTitle(ws,title.slice(0,90),8);
  ws.getColumn(1).width=27;ws.getColumn(2).width=21;ws.getColumn(3).width=24;
  for(let j=4;j<=8;j++)ws.getColumn(j).width=16;
  ws.getCell('A4').value='PANORAMA DE LA EXPORTACIÓN';
  ws.mergeCells('A4:H4');ws.getCell('A4').font={bold:true,color:{argb:PURPLE},size:12};ws.getRow(4).height=25;
  const metadata=[['Generado',new Date().toLocaleDateString('es-PE')],['Tablas detectadas',tables.length],['Filas exportadas',tables.reduce((s,t)=>s+t.count,0)],['Origen','Respuesta del chat ISO Studio']];
  metadata.forEach(([k,v],i)=>{ws.getCell(5+i,1).value=k;ws.getCell(5+i,1).font={bold:true,color:{argb:INK}};ws.getCell(5+i,2).value=v;});
  if(risk){
    const sheet=`'${risk.name.replace(/'/g,"''")}'`;
    ws.getCell('A11').value='RIESGO REFERENCIAL (MATRIZ 3×3)';ws.mergeCells('A11:H11');ws.getCell('A11').font={bold:true,color:{argb:PURPLE},size:12};
    const L=risk.levelCol, end=Math.max(5,risk.last);
    const formula=(label)=>`COUNTIF(${sheet}!${L}5:${L}${end},"${label}")`;
    for(const [idx,lab] of ['Alto','Medio','Bajo','Pendiente'].entries()){
      const row=13+idx;ws.getCell(row,1).value=lab;ws.getCell(row,2).value={formula:formula(lab)};
      ws.getCell(row,1).fill={type:'pattern',pattern:'solid',fgColor:{argb:PALETTE[lab]||'FFF2F4F7'}};
    }
    ws.getCell('A19').value='MAPA DE CALOR · IMPACTO × PROBABILIDAD';ws.mergeCells('A19:H19');ws.getCell('A19').font={bold:true,color:{argb:PURPLE},size:12};
    ws.getCell('B21').value='Baja (1)';ws.getCell('C21').value='Media (2)';ws.getCell('D21').value='Alta (3)';
    for(let impact=3;impact>=1;impact--){
      const row=25-impact;ws.getCell(row,1).value=['','Bajo (1)','Medio (2)','Alto (3)'][impact];
      for(let prob=1;prob<=3;prob++){
        const cell=ws.getCell(row,prob+1);
        cell.value={formula:`COUNTIFS(${sheet}!${risk.impactCol}5:${risk.impactCol}${end},${impact},${sheet}!${risk.probabilityCol}5:${risk.probabilityCol}${end},${prob})`};
        const score=impact*prob;
        cell.fill={type:'pattern',pattern:'solid',fgColor:{argb:score>=6?PALETTE.Alto:score>=3?PALETTE.Medio:PALETTE.Bajo}};
        cell.alignment={horizontal:'center',vertical:'middle'};cell.font={bold:true,size:14,color:{argb:INK}};
      }
      ws.getRow(row).height=42;
    }
    ws.mergeCells('A27:H28');ws.getCell('A27').value='Escala ilustrativa, NO prescrita por ISO 27701: impacto y probabilidad se codifican de 1 a 3, puntuación = impacto × probabilidad; Bajo 1-2, Medio 3-4, Alto 6-9. La organización debe definir y aprobar sus propios criterios.';
    ws.getCell('A27').alignment={wrapText:true,vertical:'middle'};
    ws.getCell('A27').font={italic:true,color:{argb:GREY},size:10};ws.getRow(27).height=40;
  }else{
    ws.mergeCells('A11:H13');ws.getCell('A11').value='No se detectó una tabla con las columnas Riesgo, Impacto y Probabilidad. Se exportan las tablas detectadas y el texto. Para generar una matriz calculada, solicita al agente una tabla Markdown con esas tres columnas.';
    ws.getCell('A11').alignment={wrapText:true,vertical:'middle'};
  }
  ws.getRow(30).height=20;
  ws.mergeCells('A30:H31');ws.getCell('A30').value='Nota: esta exportación no certifica cumplimiento normativo. Coteja los riesgos, las fuentes y los controles con la documentación original.';
  ws.getCell('A30').alignment={wrapText:true,vertical:'middle'};ws.getCell('A30').font={color:{argb:GREY},italic:true,size:10};
}
function addNotes(wb,blocks){
  const ws=wb.addWorksheet('Contenido',{views:[{showGridLines:false}]});
  styleTitle(ws,'NOTAS Y CONTENIDO',5);
  ws.getColumn(1).width=18;ws.getColumn(2).width=94;ws.getColumn(3).width=20;ws.getColumn(4).width=12;ws.getColumn(5).width=12;
  ws.getCell('A4').value='Tipo';ws.getCell('B4').value='Texto original (sin tablas)';
  formatGrid(ws,4,2,Math.min(4+blocks.length,355));
  let r=5;
  for(const b of blocks){
    if(r>354)break;
    if(b.type==='table')continue;
    const t= b.type==='list'?b.items.join(' | ') : b.text || '';
    if(!t.trim())continue;
    ws.getCell(r,1).value=b.type;
    ws.getCell(r,2).value=typed(t.slice(0,2000));
    ws.getRow(r).height=Math.min(80,Math.max(27,16+Math.ceil(t.length/96)*14));r++;
  }
}
export async function createXlsx({title,markdown}){
  if(typeof markdown!=='string'||!markdown.trim()||markdown.length>90000)throw new Error('El contenido de Excel debe tener entre 1 y 90 000 caracteres.');
  const blocks=parseBlocks(markdown);
  const wb=new ExcelJS.Workbook();wb.creator='ISO Studio';wb.created=new Date();wb.modified=new Date();wb.calcProperties.fullCalcOnLoad=true;
  const used=new Set(['resumen','contenido']);
  const wsOverview=wb.addWorksheet('Resumen');
  const tables=[];
  for(const b of blocks){if(b.type!=='table'||tables.length>=MAX_TABLES)continue;
    const t=addTable(wb,b,tables.length+1,{used,sourceTitle:title});if(t)tables.push(t);
  }
  const risk=tables.find(t=>Boolean(t.levelCol));
  addOverview(wsOverview,String(title||'Informe ISO Studio'),risk,tables);
  addNotes(wb,blocks);
  // Reordenar hojas: primero panorama, luego matriz/tablas, finalmente notas.
  wb.worksheets.forEach(s=>{s.pageSetup.fitToPage=true;});
  return Buffer.from(await wb.xlsx.writeBuffer());
}
