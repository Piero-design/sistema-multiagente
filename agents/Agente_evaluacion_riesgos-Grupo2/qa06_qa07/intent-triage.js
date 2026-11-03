// QA-06: triage conversacional determinista de entrada, antes del modelo.
// Nunca toma decisiones normativas; solo pregunta, rechaza o pasa al guard existente.
const norm=(s)=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
const contains=(s,re)=>re.test(s);
const offTopic=/(?:\b(?:trucos?|cheats?|videojuegos?|juegos? favoritos?|activar trucos|codigo de trucos|minecraft|roblox|fortnite|poemas?|canciones?|peliculas?|recetas? (?:de |para )?(?:cocina|pizza|sopa|comida)|cocinar|pizza|futbol|partidos? deportivos?|turismo|viajes? turisticos?|horoscopo|criptomonedas|crucigramas?|programar (?:en )?(?:python|javascript)|noticias de inteligencia artificial|noticias de ia|iso(?:\/iec)?\s*(?:27001|27002|27005|31000|9001|14001)|mi mascota|mi gato se peleo|se peleo con)\b|\b(?:ignora|desactiva|omite|salta)\b.{0,65}\b(?:politica|instrucciones|restricciones|filtro|sistema)\b)/;
const animalArt=/(?:\b(?:dibuja|pinta|ilustra|imagen de)\s+(?:un|una|el|la)?\s*(?:gato|perro|gatito|perrito)\b)/;
const purpose=/(?:\b(?:riesgos?|privacidad|pii|datos personales?|pims|iso\s*(?:\/iec)?\s*27701|evaluacion de riesgos|evaluar riesgos|amenazas?|vulnerabilidades?|tratamiento de riesgos|seguridad de la informacion|auditoria de privacidad|clausula|controles de privacidad|matriz(?:\s+\d\s*(?:x|por)\s*\d)?)\b)/;
const business=/(?:\b(?:empresa|negocio|organizacion|botica|farmacia|drogueria|clinica|hospital|colegio|universidad|instituto|tienda|veterinaria|restaurante|matricula|admisiones|servicio|plataforma|aplicacion|sistema|proveedor|empleados?|trabajadores?|clientes?|pacientes?|alumnos?|usuarios?|registrados?)\b|\b\d[\d .,]{0,10}\s*(?:empleados|trabajadores|usuarios|clientes|personas)\b)/;
const namedShort=/^(?:[\p{L}\p{N}&.-]+\s*){1,5}$/u;
const task=/(?:\b(?:crea|elabora|haz|genera|construye|evalua|analiza|identifica|diseña|realiza|calcula|prepara|clasifica|establece|define|explica|compara|revisa|audita|describe|busca)\b)/;
const matrix=/(?:\b(?:matriz|matrices|evaluacion de riesgos|analisis de riesgos|riesgo residual|tratamiento de riesgos|plan de tratamiento)\b)/;
const specificReference=/(?:\b(?:[ab]\.)?\d+\.\d+(?:\.\d+){0,2}\b|\b(?:iso\s*(?:\/iec)?\s*27701|pims)\b)/;
const sensitiveData=/(?:\b(?:dni|identidad|nombres?|apellidos?|correos?|telefonos?|direcciones?|recetas? medicas?|historias? clinicas?|pagos?|tarjetas?|datos de salud|datos personales?|datos sensibles|expedientes|informacion personal|registros? de clientes?|empleados? identificables|nro de documento)\b)/;
const operationalDetail=/(?:\b(?:servidor|nube|cloud|proveedor|tercerizad|call center|repartidor|plataforma|base de datos|aplicacion|sistema de ventas|sistema de matricula|tratamiento de datos|recoleccion|almacenamiento|acceso|transferencia|envio|procesamiento)\b)/;
const assumes=/(?:\b(?:fictici[oa]s?|simulad[oa]s?|hipotetic[oa]s?|ejemplo didactico)\b)/;
const explicitAssumptions=/(?:\b(?:supuestos?|inventad[oa]s?|hipotesis|datos de ejemplo|simulad[oa]s?)\b)/;
const normative=/(?:\b(?:que establece|que indica|explica|segun|clausula|control|anexo|norma)\b.{0,75}\b(?:iso|27701|\d+\.\d+|pims)\b|\b(?:iso\s*(?:\/iec)?\s*27701|6\.1\.2|6\.1\.3|8\.2|8\.3|9\.2)\b)/;
const containsUserData=(s)=>sensitiveData.test(s);
const result=(kind,more={})=>({kind,...more});

// pending: {context, rounds, at}; vive solo en memoria de la API durante un tiempo acotado.
export function triageScopeMessage(input,{pending=null,hasFiles=false}={}){
  const current=String(input??'').trim();
  const now=norm(current);
  if(!now||current.length>8000)return result('pass'); // conserva validación HTTP existente
  if(offTopic.test(now)||animalArt.test(now))return result('deny',{reason:'ISO Studio se especializa en Gestión de Riesgos de información y privacidad; no atiende solicitudes ajenas a este ámbito.'});
  const previous=(pending&&pending.context&&Date.now()-pending.at<30*60*1000)?String(pending.context):'';
  const inherited=previous && !/^(?:nuevo tema|olvida lo anterior|cambia de tema)/.test(now);
  const full=inherited?`${previous}\nAclaración del usuario: ${current}`:current;
  const s=norm(full);
  if(offTopic.test(s)||animalArt.test(s))return result('deny',{reason:'ISO Studio solo desarrolla tareas de Gestión de Riesgos de información y privacidad.'});
  const isNormative=normative.test(now)||specificReference.test(now)&&/^(?:que|cual|explica|segun|clausula|control|como)/.test(now);
  const needsMatrix=matrix.test(s)||/\b(?:matriz|matrices)\b/.test(s);
  const hasBusiness=business.test(s);
  const hasObjective=purpose.test(s);
  const hasTask=task.test(s);
  const hasData=sensitiveData.test(s);
  const hasOperations=operationalDetail.test(s);
  const isFiction=assumes.test(s);
  const hasAssumptions=explicitAssumptions.test(s);
  const context=full.slice(0,3200);
  if(isNormative && !hasBusiness && !needsMatrix) return result('pass',{forward:inherited?full:null});
  // Un nombre comercial por sí solo nunca es una orden de elaborar matrices.
  if(!hasObjective && (hasBusiness||namedShort.test(now)||now.length<65)){
    return result('clarify',{context,reason:`Para ayudarte con «${current.slice(0,80)}», ¿se trata de una organización, proyecto o sistema? ¿Quieres delimitar el PIMS, identificar riesgos de privacidad o preparar una evaluación?`,topic:'GR-02'});
  }
  if(!hasObjective&&!hasBusiness){
    return result('clarify',{context,reason:'¿Qué proceso o actividad deseas analizar y cómo se relaciona con los riesgos de información o privacidad?',topic:'GR-02'});
  }
  // Con una matriz o evaluación de una organización, se necesita contexto suficiente.
  // Si hay un documento adjunto, permitir leerlo primero; la falta de evidencia se declara luego.
  const trivialContext=hasBusiness && (!hasData || !hasOperations);
  const organizationTask=hasBusiness && /\b(?:evalua|evaluar|analiza|analizar|audita|auditoria|prepara|elabora|genera|haz|crea|planifica|define|identifica|matriz|informe|plan de tratamiento)\b/.test(s);
  if((needsMatrix||organizationTask) && trivialContext && !hasFiles && !(isFiction&&hasAssumptions)){
    return result('clarify',{context,topic:'GR-03',reason:'Para elaborar una matriz sin inventar los hechos del caso necesito: 1) ¿Qué proceso o actividad evaluaremos? 2) ¿Qué datos personales o activos maneja? 3) ¿Qué sistemas, proveedores o controles existen? Si es un ejemplo completamente ficticio, puedes pedirme que use supuestos explícitos.'});
  }
  // Si el caso es real y solo hay nombre/tamaño, la falta de datos no se sustituye con puntuaciones ficticias.
  if(needsMatrix && !hasBusiness && !hasData && !hasOperations && !hasFiles && !(isFiction&&hasAssumptions)){
    return result('clarify',{context,topic:'GR-03',reason:'¿Qué proceso, datos o activos deben evaluarse? ¿Se trata de una organización real o de un ejemplo ficticio? Con esa información podré seleccionar los riesgos y justificar una matriz.'});
  }
  // Nunca atribuir certezas: para matrices hipotéticas dejar supuestos identificados.
  if(hasObjective || hasBusiness){
    let forward=inherited?full:null;
    // El guard n8n evalúa palabras clave. El contexto añadido es temático, no contenido normativo inventado.
    if(inherited&&!purpose.test(norm(current))&&purpose.test(s)) forward=`Consulta de Gestión de Riesgos de privacidad ISO/IEC 27701:2025. ${full}`;
    return result('pass',{forward});
  }
  return result('clarify',{context,reason:'¿Qué necesitas evaluar y qué relación tiene con Gestión de Riesgos de información o privacidad?',topic:'GR-02'});
}
