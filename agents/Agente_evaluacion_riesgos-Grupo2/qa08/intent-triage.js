// ISO Studio QA-08 — triaje contextual y cierre de aclaraciones.
// Solo clasifica intención. Nunca autoriza fuentes, controles o ejecución de herramientas.
const norm=(s)=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
const hit=(s,re)=>re.test(s);
const decision=(kind,extra={})=>({kind,...extra});

const BLOCKED=/(?:\b(?:trucos?|cheats?|videojuegos?|minecraft|roblox|fortnite|poemas?|canciones?|peliculas?|cocinar|pizza|futbol|horoscopo|criptomonedas|crucigramas?|noticias de inteligencia artificial|noticias de ia|iso\s*(?:\/iec)?\s*(?:27001|27002|27005|31000|9001|14001)|receta de sopa|receta de pizza|marketing deportivo|programar (?:en )?(?:python|javascript))\b|\b(?:ignora|desactiva|omite|salta)\b.{0,65}\b(?:politica|instrucciones|restricciones|filtro|sistema)\b)/;
const BLOCKED_ART=/\b(?:dibuja|pinta|ilustra|haz una imagen de)\b.{0,45}\b(?:gato|gatito|perro|perrito)\b/;
const PET=/(?:\b(?:mi|mis|el|la)\s+(?:bb\s*cat|gatito|gato|gatita|perrito|perro|mascota)\b|\b(?:bb\s*cat|gatito|gato|perro|mascota)\b.{0,70}\b(?:tiene hambre|esta hambriento|no come|comer|se muere|se murio|se va a morir)\b)/;
const CARE=/\b(?:tiene hambre|hambriento|no come|que (?:le|darle) (?:doy|de comer)|darle de comer|alimentar|comida|se va a morir|se muere|se murio|esta enfermo|veterinari[oa])\b/;
const URGENT=/\b(?:se va a morir|se muere|no come|esta en peligro|esta muy enfermo|no se que darle de comer|por favor ayuda)\b/;
const LOSS=/\b(?:se murio|ha muerto|murio mi|fallecio)\b/;
const BLAME=/\b(?:todo es tu culpa|no me ayudaste|por tu culpa)\b/;
const BUSINESS=/\b(?:empresa|negocio|organizacion|botica|farmacia|drogueria|clinica|hospital|colegio|universidad|instituto|tienda|veterinaria|restaurante|matricula|admisiones|servicio|plataforma|aplicacion|sistema|proveedor|empleados?|trabajadores?|clientes?|pacientes?|alumnos?|usuarios?|registrados?)\b|\b\d[\d .,]{0,10}\s*(?:empleados?|trabajadores?|usuarios?|clientes?|personas)\b/;
const GOAL=/\b(?:riesgos?|privacidad|pii|datos? personales?|pims|iso\s*(?:\/iec)?\s*27701|amenazas?|vulnerabilidades?|seguridad de la informacion|auditoria de privacidad|clausula|control(?:es)? de privacidad|evaluacion|tratamiento|matriz|matrices|informe de riesgos|plan de tratamiento)\b/;
const ACTION=/\b(?:crea|elabora|haz|genera|construye|evalua|evaluar|analiza|analizar|identifica|disena|realiza|calcula|prepara|clasifica|establece|define|explica|compara|revisa|audita|describe|busca)\b/;
const MATRIX=/\b(?:matriz|matrices|evaluacion de riesgos|analisis de riesgos|riesgo residual|plan de tratamiento|tratamiento de riesgos)\b/;
const DATA=/\b(?:dni|nombre|correo|telefono|direccion|recetas? medicas?|historias? clinicas?|pagos?|tarjetas?|datos (?:personales|sensibles|de salud)|expedientes|identidad|registros? de clientes?)\b/;
const SYSTEM=/\b(?:servidor|nube|cloud|proveedor|tercerizad|call center|repartidor|base de datos|aplicacion|sistemas? de ventas|sistemas? de matricula|almacenamiento|acceso|transferencia|procesamiento|plataforma|control(?:es)? existentes?)\b/;
const FICTION=/\b(?:fictici[oa]s?|simulad[oa]s?|hipotetic[oa]s?|ejemplo didactico)\b/;
const ASSUMPTIONS=/\b(?:supuestos?|inventad[oa]s?|hipotesis|datos de ejemplo|simulad[oa]s?)\b/;
const SUBJECT=/\b(?:matricula|admisiones|ventas|atencion|salud|historiales|recetas medicas|procesamiento|entrega|delivery|registro|usuarios|pacientes|clientes)\b/;
const NORMATIVE=/\b(?:iso\s*(?:\/iec)?\s*27701|pims|clausula\s+(?:\d+\.)+\d+|\b6\.1\.[123]\b|\b8\.[23]\b|\b9\.2\b)\b/;
const SHORT_NAME=/^[\p{L}\p{N}&.\-\s]{2,65}$/u;
const RESET=/^(?:nuevo tema|olvida lo anterior|cambia de tema|empecemos de nuevo)\b/;
const GR06_PREFIX='En el alcance académico ISO-GR-2026, solicita una matriz de EVALUACIÓN DE RIESGOS DE PRIVACIDAD (GR-06), no una matriz matemática genérica. Es un caso ficticio: utiliza supuestos didácticos explícitos sin afirmar hechos reales. Solicitud del usuario: ';

function petDenial(s){
  if(LOSS.test(s)) return 'Lamento lo que comentas. Este asistente está especializado en Gestión de Riesgos de información y privacidad y no puede ofrecer asistencia veterinaria.';
  if(URGENT.test(s)) return 'Si una mascota está en peligro o lleva tiempo sin comer, busca atención veterinaria de inmediato. ISO Studio no ofrece instrucciones de alimentación ni atención veterinaria; solo aborda Gestión de Riesgos de información y privacidad.';
  return 'Entiendo que hablas de tu mascota, no de una organización que desees evaluar. ISO Studio está limitado a Gestión de Riesgos de información y privacidad.';
}

function fullyOffTopic(s){return hit(s,BLOCKED)||hit(s,BLOCKED_ART);}
export function triageScopeMessage(input,{pending=null,hasFiles=false}={}){
  const current=String(input??'').trim();
  const now=norm(current);
  if(!now||current.length>8000)return decision('pass'); // validaciones API existentes
  if(BLAME.test(now))return decision('deny',{reason:'Lamento que las respuestas anteriores no fueran útiles. No continuaré preguntando sobre ISO si la consulta no tiene relación con el tema.'});
  if(PET.test(now)&&CARE.test(now))return decision('deny',{reason:petDenial(now)});
  if(LOSS.test(now)&&(/\b(?:bb cat|gato|gatito|mascota|perro)\b/.test(now)))return decision('deny',{reason:petDenial(now)});
  if(PET.test(now)&&!BUSINESS.test(now))return decision('deny',{reason:petDenial(now)});
  if(fullyOffTopic(now))return decision('deny',{reason:'ISO Studio se especializa en Gestión de Riesgos de información y privacidad y no atiende esa solicitud.'});
  const previous=(pending&&pending.context&&Date.now()-pending.at<30*60*1000)?String(pending.context):'';
  const rounds=previous?Math.max(0,Number(pending.rounds)||0):0;
  const inherited=Boolean(previous&&!RESET.test(now));
  const full=inherited?`${previous}\nAclaración del usuario: ${current}`:current;
  const s=norm(full), context=full.slice(0,3000);
  if(fullyOffTopic(s))return decision('deny',{reason:'Esta solicitud no corresponde a Gestión de Riesgos de información y privacidad.'});
  const goal=GOAL.test(s),business=BUSINESS.test(s),matrix=MATRIX.test(s),fiction=FICTION.test(s),assumptions=ASSUMPTIONS.test(s);
  const data=DATA.test(s),systems=SYSTEM.test(s),subject=SUBJECT.test(s);
  const standaloneISO=NORMATIVE.test(now)&&!matrix&&!business;
  const queryNormative=standaloneISO&&!(/\b(?:crea|matriz|evalua|trata)\b/.test(now));
  if(queryNormative)return decision('pass',{forward:inherited?full:null});

  const fictitiousMatrix=matrix&&fiction&&assumptions&&subject;
  if(fictitiousMatrix)return decision('pass',{forward:GR06_PREFIX+full});

  const wantsEvaluation=matrix||(goal&&ACTION.test(s)&&business);
  if(wantsEvaluation&&business&&!hasFiles&&!(data&&systems&&subject)){
    const reason='Para evaluar este caso sin inventar datos, necesito saber: 1) ¿Qué proceso evaluaremos? 2) ¿Qué datos personales o activos maneja? 3) ¿Qué sistemas o controles existen? Si es un ejercicio ficticio, indícalo y autoriza supuestos explícitos.';
    if(rounds>=3)return decision('deny',{reason:'No tengo suficiente información para elaborar una evaluación fiable. Cuando dispongas del proceso, los datos tratados y los controles, podrás iniciar una nueva consulta de Gestión de Riesgos.'});
    return decision('clarify',{context,rounds:rounds+1,topic:'GR-03',reason});
  }
  if(wantsEvaluation&&business&&(data&&systems&&subject||hasFiles))return decision('pass',{forward:inherited?full:null});
  if(matrix&&!business&&!hasFiles&&!fictitiousMatrix){
    if(rounds>=2)return decision('deny',{reason:'Aún no se identifica qué proceso o información debe evaluarse. Puedes iniciar una nueva consulta indicando el proceso y los activos.'});
    return decision('clarify',{context,rounds:rounds+1,topic:'GR-03',reason:'¿Qué proceso o actividad debe evaluar la matriz, qué datos maneja y es un caso real o ficticio?'});
  }
  if(goal&&ACTION.test(s))return decision('pass',{forward:inherited?full:null});
  if(goal&&!business)return decision('pass',{forward:inherited?full:null});
  if(business&&!goal){
    if(rounds>=2)return decision('deny',{reason:'No se ha identificado una solicitud sobre privacidad o Gestión de Riesgos. No continuaré solicitando lo mismo; puedes iniciar una nueva consulta con un objetivo concreto.'});
    return decision('clarify',{context,rounds:rounds+1,topic:'GR-02',reason:'¿Quieres analizar el alcance del PIMS o evaluar riesgos de información y privacidad de este negocio? Indica qué proceso y datos trata.'});
  }
  if(!goal&&!business){
    if(rounds>=2)return decision('deny',{reason:'No se ha identificado una relación con Gestión de Riesgos de información o privacidad. No continuaré preguntando; si más adelante necesitas una evaluación de estos temas, formula una nueva consulta.'});
    if(now.length>120&&!SHORT_NAME.test(now))return decision('deny',{reason:'No identifico una tarea de Gestión de Riesgos de información o privacidad en tu solicitud.'});
    return decision('clarify',{context,rounds:rounds+1,topic:'GR-02',reason:`¿«${current.slice(0,60)}» se refiere a una organización, un sistema o algo personal? Solo puedo ayudarte con privacidad y Gestión de Riesgos de información.`});
  }
  return decision('deny',{reason:'No se ha identificado una solicitud relacionada con Gestión de Riesgos de información o privacidad.'});
}
