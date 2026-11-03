# ISO Studio 7.2 — Instalación Windows (Gestión de Riesgos)

Este paquete es una **aplicación completa derivada de ISO Studio 7.1**, no solo un documento. Conserva la versión 7 para exposiciones y pruebas anteriores.

## A. Instalación local

1. Descomprime `iso-studio-7-2-gestion-riesgos` dentro de `C:\Auditoria Agente`.
2. No borres ningún volumen Docker; ejecuta `docker compose up -d` desde `C:\Auditoria Agente`.
3. Detén con Ctrl+C cualquier servidor ISO Studio previo (puertos 4317 y 5173).
4. PowerShell:

```powershell
cd 'C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos'
Copy-Item '..\iso-studio-7-excel\.env' '.env'
Add-Content '.env' "`nSCOPE_N8N_REVIEWED=false"
npm install
npm run test:scope
npm run build
npm run dev
```

Abre http://localhost:5173. Al iniciar estará BLOQUEADO hasta el paso B. En `http://localhost:4317/api/status` podrás revisar el estado; es normal.

## B. Revisión obligatoria de n8n y Qdrant

1. Abre http://localhost:5678 → Overview; entra al flujo `Agente_Evaluacion_Riesgos`.
2. Aplica `n8n/SYSTEM_MESSAGE_GR_7_2.md` al System Message del nodo AI Agent principal. Elimina instrucciones anteriores de temas generales. Aplica el mismo alcance a las skills `Skill_Evaluacion_Riesgos_27701`, `Skill_Artefactos_ISO_Studio` y a cualquier herramienta adicional que pueda producir respuestas.
3. En el Chat Trigger, coloca el Code de `n8n/GUARD_CODE_NODE.js` ANTES del AI Agent y un nodo IF para separar permitidas y rechazadas. La rama rechazadas debe responder texto fijo sin llamar a IA ni a herramientas. Repítelo en otros entrypoints independientes que puedan ser llamados directamente.
4. En Qdrant sigue `docs/PLAN_QDRANT_ETIQUETADO.md`. La colección aprobada es `iso_gr_2026`, distinta de `iso27701_2025`. Si no logras el filtro, no declares revisión terminada.
5. Realiza una pregunta permitida (matriz de riesgos de privacidad), otra fuera de alcance (receta de pizza), otra sobre el anexo A no entregado y otra por ruta n8n directa. Verifica rechazos, referencias y que no se invocan las tools al rechazar.
6. **Solo entonces** cambia en `.env`: `SCOPE_N8N_REVIEWED=true`, guarda, detén/reinicia `npm run dev`.

Si `SCOPE_N8N_REVIEWED` es falso, la app deliberadamente bloquea todas las operaciones salvo estado. **La variable es una declaración manual, no una prueba técnica automática de que n8n se haya actualizado**.

## C. Uso

- Consulta ejemplo: «Crea una matriz de evaluación de riesgos de privacidad de una matrícula universitaria ficticia, aclarando la escala y los supuestos».
- Web en modo ON: buscará solo sobre Gestión de Riesgos y citará resultados externos.
- Visual: «Genera infografía sobre identificación y tratamiento de riesgos de privacidad».
- Exportaciones PDF/Word/Excel: usan comprobante temporal de una respuesta emitida por `/api/chat`; las conversaciones antiguas no tienen ese comprobante y no pueden exportarse sin reconsultar.
- Adjuntos OCR: se cargan como datos, pero no autorizan respuestas generales.
- Visión Gemini: requiere que el campo de redacción tenga una pregunta de Gestión de Riesgos al adjuntar. Si no, usa OCR sin IA.

## D. Seguridad y regresiones

- No utilices Cloudflare Tunnel para una clase abierta hasta proteger n8n, autenticar usuarios y completar pruebas de seguridad.
- `/api/status` puede informar del estado, pero no prueba que Gemini ni Qdrant respondan bien.
- El guard local usa patrones estrictos y puede rechazar redacciones válidas o admitir un caso adversarial. Un filtro semántico con validación adicional será recomendable.
- NO sobrescribir colección ni workflows sin respaldo; estos archivos no conectan a tu Docker y no ejecutan modificaciones en n8n automáticamente.
- Las citas ISO solo pueden considerarse verificadas cuando los fragmentos correctos sean recuperados de la nueva colección con metadatos y se revisen.
