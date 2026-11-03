# ISO Studio 2.0 — Instalación en Windows

Este proyecto **amplía** la interfaz React que ya tienes. No modifica tus contenedores n8n y Qdrant.

## Requisitos

- Docker Desktop abierto, con n8n y Qdrant en ejecución.
- Node.js LTS (22 o superior recomendado) y npm.
- Los workflows originales `Agente_Evaluacion_Riesgos`, `Skill_Evaluacion_Riesgos_27701` y `RAG_ISO27701` configurados.
- El documento de ISO solo debe usarse cuando haya sido cargado y verificado en Qdrant.

## Paso 1. Descomprimir

Descomprime `ISO_Studio_2_Artefactos_Windows.zip` para obtener una carpeta `iso-studio-2`, por ejemplo:

`C:\Auditoria Agente\iso-studio-2`

**No reemplaces la carpeta original `iso-studio-react`:** servirá como respaldo.

## Paso 2. PowerShell

```powershell
cd 'C:\Auditoria Agente\iso-studio-2'
node --version
npm --version
npm install
```

### Reutilizar la configuración del frontend anterior

Si ya habías configurado la URL del Chat Trigger en el proyecto anterior:

```powershell
Copy-Item '..\iso-studio-react\.env' '.env'
```

Si no existe ese archivo, ejecuta:

```powershell
Copy-Item '.env.example' '.env'
notepad .env
```

Configura el campo `N8N_CHAT_URL` con la **URL de PRODUCCIÓN real** del nodo `When chat message received` de tu n8n local, en modo **Embedded Chat**, por ejemplo:

```
N8N_CHAT_URL=http://127.0.0.1:5678/webhook/IDENTIFICADOR-REAL/chat
PORT=4317
```

No utilices una URL inventada, la URL anterior de n8n Cloud o la de pruebas `webhook-test`.

## Paso 3. Iniciar

```powershell
npm run dev
```

Abre **http://localhost:5173**. En la vista de desarrollo podrás recorrer «Herramientas y archivos» y usar las opciones PDF / Word que aparecen debajo de las respuestas reales del agente.

Si el Chat Trigger aún no está conectado, el frontend quedará en modo **vista previa** y no presentará el texto simulado como una respuesta real.

## Paso 4. Añadir la Skill a n8n

1. Abre n8n en `http://localhost:5678`.
2. Crea un workflow nuevo y, desde `...`, elige **Import from File**.
3. Importa `skills/Skill_Artefactos_ISO_Studio.json`.
4. Verifica que tenga `When executed by another workflow → Edit Fields (Set)` y que el campo `skill` contenga las instrucciones. Guarda el workflow y publícalo si tu versión lo requiere.
5. Abre `Agente_Evaluacion_Riesgos` y agrega **Call n8n Workflow Tool** desde el conector **Tool** del `AI Agent`.
6. Pon como descripción del Tool: «Recupera instrucciones para crear documentos PDF/Word y diagramas Mermaid. Usa esta herramienta al solicitar el usuario un documento, diagrama, PDF o DOCX.»
7. Configura `Source=Database` y selecciona `Skill_Artefactos_ISO_Studio` de la lista. Puedes nombrar el nodo `obtener_skill_artefactos`.
8. Conserva intactas las herramientas actuales `Qdrant Vector Store` y `obtener_skill_evaluacion`.
9. **Añade el siguiente bloque al final de System Message** del `AI Agent`:

```
ISO STUDIO - SALIDAS EN DOCUMENTOS Y DIAGRAMAS:
Si el usuario pide PDF, Word, DOCX, informe formal o diagrama, usa obtener_skill_artefactos y sigue su procedimiento.
Para un documento, entrega contenido COMPLETO en Markdown con títulos, secciones, tablas y conclusiones. No afirmes que has adjuntado un archivo: ISO Studio exporta tu respuesta al formato pedido.
Para diagramas, incluye bloques de código ```mermaid válidos. No devuelvas únicamente una explicación textual.
Si citas ISO/IEC 27701, consulta Qdrant antes y no inventes cláusulas ni evidencias.
```

10. Guarda el agente. Ejecuta las pruebas siguientes desde **ISO Studio en React** (no desde el chat interno de n8n, que no tiene los controles de exportación).

## Paso 5. Pruebas funcionales

**A — Diagrama**

«Crea un diagrama de flujo Mermaid de un proceso de auditoría de sistemas, con inicio, recolección de evidencia, evaluación y reporte.»

Esperado: **bloque visual** en el chat y botones **SVG** / **PNG**.

**B — PDF**

«Genera un informe en PDF sobre el proceso de gestión de incidentes con título, tabla y recomendaciones. Usa un ejemplo ficticio.»

Esperado: respuesta en Markdown, seguido de archivo descargable **.pdf**. También verás un botón PDF bajo cada respuesta.

**C — Word**

«Redacta un plan de evaluación de riesgos en Word para un sistema universitario ficticio, con tabla de riesgos y conclusiones.»

Esperado: respuesta y archivo **.docx** que puedes abrir y editar en Microsoft Word o LibreOffice.

**D — Verificar formato**

Abre el .docx y el .pdf. Revisa manualmente tablas, saltos de página, títulos y diagramas. **No confundas generación del archivo con validación del contenido ISO.**

## Cómo funciona

- n8n + Gemini producen el contenido estructurado en Markdown.
- La Skill adicional hace que Gemini devuelva formato adecuado y bloques Mermaid.
- React dibuja los diagramas **Mermaid** en el chat. Permite exportar SVG y PNG.
- El backend Express local convierte el Markdown en **PDF** y **DOCX** usando bibliotecas específicas.
- Si pides PDF/Word explícitamente, React intenta generarlo automáticamente al recibir la respuesta. También puedes pulsar **PDF** / **Word** debajo de una respuesta existente.
- Las descargas quedan temporalmente en la carpeta `.local-artifacts`, con identificadores aleatorios, y se limpian después de 48 horas al reiniciar el servidor. Guarda tus entregables donde desees antes de ese plazo.
- El proyecto continúa funcionando con la misma `N8N_CHAT_URL` y no exige claves nuevas para generar documentos.

## Límites actuales

- **No** se han implementado edición directa de documentos subidos, ejecución de código, navegación autónoma, acceso a archivos arbitrarios del equipo, análisis de imágenes ni un sandbox tipo ChatGPT/Claude.
- El servidor de herramientas recibe el **texto devuelto por el modelo** y lo exporta; la Skill de n8n define el formato, pero las descargas las crea React/Node.js. La generación no es todavía una tool nativa de n8n con acceso binario.
- Mermaid no edita gráficos arrastrando objetos; edita el código Mermaid y vuelve a renderizar.
- La exportación admite títulos, secciones, tablas Markdown y hasta cuatro diagramas PNG embebidos si el navegador puede rasterizarlos; también permite guardar SVG por separado.
- Diagramas inválidos quedan visibles como código con un aviso, no como un gráfico falso.
- Las citas ISO deben comprobarse contra el PDF original. No se habilita RAG real con solo instalar esta interfaz.
- React y el backend escuchan en 127.0.0.1. No expongas los puertos ni claves a Internet sin autenticación, limitación de usuarios y HTTPS.

## Mantenimiento

```powershell
# Detener React + backend (en su ventana de PowerShell)
Ctrl+C

# Volver a iniciar
npm run dev

# Pruebas del parser sin conexión a Internet
npm run test:parsers
npm run test:exports
```

Para validar la generación de archivos antes de conectar n8n, ejecuta `npm run test:exports` después de `npm install`. La prueba comprueba que se construye un PDF válido y un DOCX tipo ZIP. Revisa visualmente los archivos reales producidos por una conversación en React.

Si aparece error `Cannot find package 'docx'`, `pdfkit`, `mermaid` o `dompurify`, ejecuta `npm install` de nuevo con una conexión a Internet.

Si aparece error 404 al descargar archivos, verifica que el servidor Express (`API` en `npm run dev`) siga abierto. Los archivos expiran a las 48 horas.

Si el agente responde en texto pero no aparece el diagrama, confirma que la respuesta incluye un bloque de código **```mermaid** delimitado correctamente.
