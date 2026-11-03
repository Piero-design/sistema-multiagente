# Página web del PIMS (Etapa 3)

La sirve el propio n8n en **http://localhost:5678/webhook/pims/app**. No hay un servidor aparte: si n8n está corriendo con los flujos instalados (ver `n8n/INSTALACION_N8N.md`), la página funciona.

| Archivo | Qué es |
|---|---|
| `index.html` | La página completa: HTML, CSS y JavaScript sin frameworks. |
| `vendor/` | marked, DOMPurify y mammoth, copiados de npm para no depender de un CDN (ver `vendor/LICENCIAS.md`). El flujo "PIMS · Página web" incrusta marked y DOMPurify; mammoth se carga solo al subir un `.docx`. |
| `capturas/` | Capturas reales de la página funcionando contra n8n, para el informe del TIF. Se tomaron con el modelo simulado, como indica el pie del riel. |
| `pruebas/probar_pagina.py` | Recorre la página en un Chromium real. |

**Si editas `index.html`, solo recarga la página.** n8n lee el archivo en cada visita, así que no hace falta reinstalar.

## Pantallas

| Pantalla | Para qué |
|---|---|
| **Auditar un contrato** | Pegar el texto o soltar un `.pdf`, `.docx`, `.md` o `.txt`. Los `.docx` se convierten a texto en el navegador; los PDF los lee n8n. Muestra el avance y avisa cuando el expediente está listo, aunque cambies de pantalla. |
| **Expedientes** | Todas las auditorías de la organización, con la proporción de controles por estado, el puntaje y el estado de aprobación. |
| **Expediente** | La *huella* del contrato (26 casillas del semáforo, con su detalle al pasar el cursor), el puntaje, el dictamen, el desglose por sección (barras y radar) y los **dos sellos de la doble puerta**. Tiene pestañas de informe, alertas, historial y JSON, y permite descargar el `.md` y el `.json` o imprimir. |
| **Por aprobar** | La bandeja del rol elegido en el riel, DPO o Legal. El contador muestra cuántos expedientes esperan su decisión. |
| **Organización y perfil** | Subir documentos institucionales, generar el perfil, validarlo como DPO, ver los terceros del perfil sin DPA evaluado (con un botón para auditarlos) y crear organizaciones nuevas. |
| **Preguntar** (pestaña del expediente y sección de *Organización y perfil*) | Chat con el modelo sobre el expediente o la organización, con sugerencias de preguntas. Las respuestas citan su fuente y la conversación queda guardada. El chat no cambia calificaciones ni aprueba. |
| **Renovaciones** | Contratos que vencen o cuyo plazo de preaviso llega pronto, calculados con la fecha de hoy. |
| **Configuración** | Elegir el modelo (Claude Code, Ollama, Anthropic o API compatible con OpenAI) y ver las jurisdicciones disponibles. |

El **rol** (DPO o Legal) y el **nombre** del riel son de la sesión: quedan en el historial de cada decisión. La página no tiene usuarios ni contraseñas. Es una herramienta local de demostración: la aprobación es un registro de quién decidió, no una firma electrónica.

## Seguridad

- **n8n entrega la página aislada** (cabecera `Content-Security-Policy: sandbox …`), el comportamiento por defecto de n8n 2.x. **No hace falta desactivarlo.** La página funciona igual; solo no puede usar `localStorage`, y no lo necesita.
- **Solo la página y el propio n8n pueden leer la API.** Cada webhook declara `allowedOrigins` = `null` (el origen de la página aislada), `http://localhost:5678` y `http://127.0.0.1:5678`. Verificado: un sitio externo recibe `Access-Control-Allow-Origin: null` y el navegador le bloquea la respuesta.
- **El informe es contenido derivado de un contrato no confiable.** Se convierte con marked y siempre pasa por DOMPurify antes de mostrarse.
- **n8n escucha solo en `127.0.0.1`** (lo fija `iniciar_n8n.bat`).

## Pruebas

```
python web/pruebas/probar_pagina.py --raiz <COPIA del proyecto>
```

Necesita n8n con los flujos instalados, el modelo simulado configurado y `pip install playwright` (más `python -m playwright install chromium`). Son 9 pasos:

- carga de la página desde n8n;
- auditoría por texto con progreso y expediente (22/100);
- doble aprobación con los dos sellos e historial;
- descargas `.md` y `.json`;
- `.docx` convertido en el navegador (AndesCloud, 100/100) y bandeja del DPO;
- generación y validación del perfil;
- creación de una organización con subida de documento;
- renovaciones, configuración y vista móvil sin desplazamiento horizontal;
- consola sin errores de JavaScript.

Resultado: **10/10** (el décimo recorrido es el chat; antes, 9/9 en tres corridas seguidas). Las pruebas encontraron y corrigieron dos carreras reales entre pantallas, cuando una respuesta tardía pisaba la pantalla nueva o borraba un formulario a medio llenar.
