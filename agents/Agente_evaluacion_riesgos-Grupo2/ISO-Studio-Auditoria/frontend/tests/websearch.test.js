import assert from 'node:assert/strict';
import test from 'node:test';
import {shouldSearchWeb, validPublicSource, simplifyResults, createWebSearch, webContext} from '../server/lib/websearch.js';

test('detecta preguntas que solicitan actualidad o investigar',()=>{
  assert.equal(shouldSearchWeb('Busca en Internet noticias recientes de ISO'),true);
  assert.equal(shouldSearchWeb('¿Qué pasó hoy en auditoría?'),true);
  assert.equal(shouldSearchWeb('Resume mi archivo adjunto'),false);
  assert.equal(shouldSearchWeb('Haz un diagrama Mermaid'),false);
});
test('valida URLs y no expone direcciones internas',()=>{
  for (const u of ['http://localhost:5678/','https://127.0.0.1/','javascript:alert(1)','http://192.168.0.1/', 'https://admin:pw@example.com'])assert.equal(validPublicSource(u),null);
  assert.equal(validPublicSource('https://example.com/post'),'https://example.com/post');
});
test('reduce resultados a fuentes con identificadores estables',()=>{
  const items=simplifyResults({results:[
    {title:'Uno',url:'https://example.com/x',content:'Fuente de prueba'},
    {title:'Duplicado',url:'https://example.com/x',content:'...'},
    {title:'Local',url:'http://127.0.0.1/private',content:'...'},
    {title:'Dos',url:'https://example.org/y',content:'Otra fuente'},
  ]});
  assert.deepEqual(items.map(x=>x.id),['W1','W2']);
  assert.match(webContext(items,'consulta'),/\[W1\]/);
});
test('consulta Tavily sin exponer key, limita y almacena temporalmente', async()=>{
  let calls=0;
  const client=createWebSearch({key:'tvly-test',clock:()=>1234567890,fetcher:async(url,options)=>{
    calls++;
    assert.equal(url,'https://api.tavily.com/search');
    assert.equal(options.headers.Authorization,'Bearer tvly-test');
    const b=JSON.parse(options.body);
    assert.equal(b.search_depth,'basic');
    assert.equal(b.include_raw_content,false);
    return {ok:true,json:async()=>({results:[{title:'Fuente',url:'https://example.com/r',content:'Contenido actual'}]})};
  }});
  const one=await client('actualidad ISO','abc-session');
  const two=await client('actualidad ISO','abc-session');
  assert.equal(calls,1);
  assert.equal(one.sources[0].url,'https://example.com/r');
  assert.equal(two.cached,true);
});
test('informa cuando API Key no está configurada',async()=>{
  const client=createWebSearch({key:''});
  await assert.rejects(client('buscar','sesion'),/TAVILY_API_KEY/);
});
