// Markdown subset supported for document export. Does not execute code/HTML.
export function plainText(value = '') {
  return String(value)
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\*\*|__|(?<!\*)\*(?!\*)|(?<!_)_(?!_)/g, '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/<[^>]*>/g, '')
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '')
    .trim();
}

function tableCells(line) { return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(v => plainText(v.trim())); }
function isTableSeparator(line) { return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line); }
function isSpecial(line) { return /^(#{1,6}\s|\s*[-*+]\s+|\s*\d+[.)]\s+|```|>\s+|---+$)/.test(line) || line.trim().startsWith('|'); }

export function parseBlocks(markdown) {
  const lines = String(markdown || '').replace(/\r\n?/g, '\n').split('\n');
  const blocks = [];
  for (let i=0; i<lines.length;) {
    const line = lines[i];
    if (!line.trim()) {i++; continue;}
    const fence = /^\s*```\s*([\w-]*)\s*$/.exec(line);
    if (fence) {
      let j = i + 1;
      while(j<lines.length && !/^\s*```\s*$/.test(lines[j])) j++;
      const raw = lines.slice(i+1,j).join('\n');
      blocks.push({type:fence[1].toLowerCase()==='mermaid'?'diagram':'code', language:fence[1].toLowerCase(), text: raw });
      i = Math.min(j+1,lines.length); continue;
    }
    const h = /^(#{1,6})\s+(.+)/.exec(line);
    if (h) { blocks.push({type:'heading', level:h[1].length, text:plainText(h[2])}); i++;continue; }
    if (line.trim().startsWith('|') && i+1<lines.length && isTableSeparator(lines[i+1])) {
      const headers=tableCells(line); i+=2;
      const rows=[];
      while(i<lines.length && lines[i].trim().startsWith('|')) { rows.push(tableCells(lines[i]).slice(0,headers.length)); i++; }
      blocks.push({type:'table', headers, rows}); continue;
    }
    const bullet = /^\s*([-*+]|\d+[.)])\s+(.+)/.exec(line);
    if (bullet) {
      const items=[]; const numbered=/\d/.test(bullet[1]);
      while(i<lines.length) {
        const next=/^\s*([-*+]|\d+[.)])\s+(.+)/.exec(lines[i]);
        if(!next) break;
        items.push(plainText(next[2])); i++;
      }
      blocks.push({type:'list', ordered:numbered, items}); continue;
    }
    if (/^\s*>\s+/.test(line)) {blocks.push({type:'quote',text:plainText(line.replace(/^\s*>\s+/,''))}); i++;continue;}
    if (/^---+$/.test(line.trim())) {blocks.push({type:'rule'});i++;continue;}
    const paragraph=[];
    while(i<lines.length && lines[i].trim() && (!isSpecial(lines[i]) || paragraph.length===0)) { paragraph.push(lines[i]);i++; }
    if (!paragraph.length) {i++;continue;}
    blocks.push({type:'paragraph',text:plainText(paragraph.join(' '))});
  }
  return blocks;
}
export function suggestedTitle(markdown) {
  return parseBlocks(markdown).find(b=>b.type==='heading' && b.level<=2)?.text || 'Documento de ISO Studio';
}
export function safeBaseName(name) {
  const clean = String(name||'documento').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zA-Z0-9_-]+/g,'-').replace(/-+/g,'-').replace(/^-|-$/g,'').slice(0,72);
  return clean || 'documento';
}
