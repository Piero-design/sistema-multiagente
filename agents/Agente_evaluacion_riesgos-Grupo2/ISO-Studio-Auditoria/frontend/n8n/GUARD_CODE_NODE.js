// NODO Code (Run Once for All Items), ANTES del AI Agent; seguido por un IF.
// Compatible con Chat Trigger, si el campo chatInput está disponible en $json.
// En el IF, condición booleana {{$json.scopeAllowed}} === true.
// Rama FALSE: nodo Set/Edit Fields con output = $json.scopeReason y responder sin AI Agent.
// Rama TRUE: conectar al AI Agent normal. Replicar en entrypoints propios de tools.
const input = $input.all();
const allowed = /\b(?:riesgos?|risk|privacidad|27701|datos? personales?|pims|apetito|tolerancia|amenazas?|vulnerabilidades?)\b/i;
const denied = /\b(?:receta|cocina|futbol|turismo|playa|poema|pelicula|marketing|criptomonedas|python|programar|noticias de inteligencia artificial)\b/i;
const bypass = /(?:ignora|olvida|desactiva|salta).{0,70}(?:reglas|restricciones|sistema|instrucciones)/i;
return input.map(item => {
  const q = String(item.json.chatInput ?? item.json.query ?? item.json.text ?? '');
  const scopeAllowed = allowed.test(q) && !denied.test(q) && !bypass.test(q) && q.length < 8000;
  return {json:{...item.json,scopeAllowed,scopeReason:scopeAllowed?'':'ISO Studio solo responde consultas sobre Gestión de Riesgos de información y privacidad.'}};
});
// Este nodo es una capa EXTRA. El backend 7.2 evalúa la intención más estrictamente.
// La validación no se considera completa hasta probar ambas ramas y cerrar accesos directos.
