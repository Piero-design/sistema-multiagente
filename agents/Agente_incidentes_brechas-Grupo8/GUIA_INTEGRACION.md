# Guía de integración — Grupo 8 / Agente de Incidentes y Brechas

Describe cómo usar este agente dentro del sistema de ocho agentes. Es orientativa: el equipo integrador puede adaptar la forma de ejecución (servicio HTTP, skills con un ejecutor común o módulo propio). El README de esta carpeta describe el desarrollo completo; esta guía resume lo que necesita quien lo integre.

## 1. Qué hace y qué no

- **Hace:** recibe el reporte de un evento (correo mal enviado, ransomware, laptop robada, phishing, acceso indebido, aviso de un proveedor), lo clasifica (evento / incidente / brecha de datos personales), evalúa la severidad para los titulares (ENISA), decide si hay que notificar (art. 34 del Reglamento de la Ley 29733, D.S. 016-2024-JUS), controla el plazo de 48 horas, redacta los borradores (ANPD, titulares, CNSD), propone contención y erradicación y elabora el informe de cierre con causa raíz y controles ISO/IEC 27002.
- **No hace:** enviar notificaciones, ejecutar contención ni cambiar sistemas. Todo sale como **borrador o acción propuesta** que aprueba el Oficial de Datos Personales o el responsable de seguridad. Los conectores a sistemas son de **solo lectura**.
- Todos los casos de demostración son ficticios (UNSA simulada).

## 2. Qué aporta cada carpeta

| Ruta | Contenido |
|---|---|
| `.claude/agents/agente-incidentes-brechas.md` | Agente coordinador del ciclo completo |
| `.claude/skills/brecha-triaje/` | Clasificación, prioridad y ficha del incidente; inicia el reloj de 48 h |
| `.claude/skills/brecha-evaluacion-severidad/` | Severidad ENISA y decisión de notificar |
| `.claude/skills/brecha-notificacion/` | Borradores ANPD, titulares y CNSD |
| `.claude/skills/brecha-respuesta-cierre/` | Plan de respuesta, evidencia, causa raíz, lecciones aprendidas |
| `.claude/commands/gestionar-incidente.md` | Comando `/gestionar-incidente` |
| `knowledge/` | Normativa peruana, estándares, taxonomía y severidad |
| `web/` | Interfaz React + servidor Node (puerto 3100), motor de autonomía en `web/autonomia/` |
| `config/` | Conectores (buzón de quejas, base de conocimiento, sistemas); copiar `conectores.ejemplo.json` a `conectores.json` |
| `demo/`, `examples/`, `archivos-demo/` | Organización simulada (inventario, contactos, políticas, logs) y reportes de ejemplo |
| `docs/`, `pruebas/` | Informe TIF, documentos de diseño y registro de pruebas |

> Las skills viven en `.claude/skills/` (convención de Claude Code) y no en `skills/<nombre>/` como propone `structure.md`. Equivalencia con esa estructura: `registrar_incidentes` = `brecha-triaje`, `evaluar_brechas` = `brecha-evaluacion-severidad` + `brecha-notificacion`, `gestionar_respuesta` = `brecha-respuesta-cierre`.

## 3. Instalación y ejecución

Desde esta carpeta (`agents/Agente_incidentes_brechas-Grupo8/`):

```bash
cp .env.example .env        # poner UNA credencial: GEMINI_API_KEY, GROQ_API_KEY, ANTHROPIC_API_KEY o CLAUDE_CODE_OAUTH_TOKEN
docker compose up --build   # http://localhost:3100
```

Sin Docker: Node 20+, `npm install` en la raíz y en `web/client`, `npm run build` en `web/client` y `node web/server.js`.

El puerto 3100 es una propuesta para correr el agente de forma independiente; se cambia con la variable `PORT`. El proveedor de IA se elige solo según la credencial presente (Gemini o Groq primero, luego Claude). Las credenciales nunca se versionan (`.env`, `config/conectores.json` y `buzon/` están en `.gitignore`).

## 4. API HTTP para los demás agentes

Base: `http://localhost:3100`. Sin autenticación: usarla solo en local o detrás de un proxy (el despliegue con Traefik y tinyauth está en `deploy/`).

| Ruta | Para qué |
|---|---|
| `POST /api/analizar` | Envía el reporte del incidente y arranca el análisis. Responde con un `job` |
| `GET /api/job/{job}` | Estado y avance del análisis. `DELETE` lo cancela |
| `GET /api/expediente/{id}` | Expediente generado (ficha, severidad, borradores, plan, cierre) |
| `GET /api/acciones/{expediente}` | Acciones propuestas por el agente |
| `POST /api/acciones/{expediente}/{A#}` | Aprobar o rechazar una acción (decisión humana) |
| `POST /api/buzon/webhook/{conector}` | Deposita una queja desde otro sistema (cabecera `X-Webhook-Token`) |
| `POST /api/buzon/{Q…}/analizar` | Analiza una queja ya recibida |
| `GET/POST /api/autonomia` | Estado y activación del modo autónomo |
| `GET /api/estado` | Estado del proveedor de IA y de la conexión |

Los expedientes se guardan como archivos en `salidas/` (no se versionan).

## 5. Herramientas del agente (MCP interno)

El agente usa un servidor MCP propio (`web/autonomia/mcp.js`) con estas herramientas:

| Herramienta | Qué hace |
|---|---|
| `BuscarConocimiento` | Busca en la base de conocimiento (BM25 o wiki HTTP) |
| `ListarSistemas` | Lista los sistemas y subsistemas declarados en `config/conectores.json` |
| `ConsultarSistema` | Consulta logs o APIs de un sistema, solo lectura |
| `BuscarQuejas` | Busca en el buzón de quejas |
| `ProponerAccion` | Registra una acción propuesta que debe aprobar una persona |

Otros grupos pueden declarar sus propios servicios como sistemas en `config/conectores.json` para que el agente los consulte.

## 6. Relación con otros agentes

| Agente | Qué le entrega este agente | Qué le puede dar |
|---|---|---|
| **Grupo 3 · DSAR** | Aviso de brecha que afecta a titulares con derechos en trámite; titulares notificados | Expedientes DSAR relacionados con los titulares afectados |
| **Grupo 4 · Evidencia/Auditoría** | Expediente del incidente, línea de tiempo y cadena de custodia como evidencia de los controles 5.24–5.28 y 6.8 | Hallazgos de auditoría que pueden originar incidentes |
| **Grupo 5 · Terceros/DPA** | Incidentes originados en un proveedor y obligaciones de aviso del DPA | Cláusulas de notificación de brechas y contactos del encargado |
| **Grupo 6 · Inventario** | Activos y categorías de datos afectados | Inventario de activos y datos para evaluar el contexto de la brecha |
| **Grupo 2 · Riesgos** | Causa raíz y lecciones aprendidas para actualizar el análisis de riesgos | Nivel de riesgo de los activos afectados |
| **Grupo 7 · Controles/SoA** | Controles ISO/IEC 27002 propuestos tras el incidente | Estado de implementación de los controles |
| **Grupo 1 · Formación** | Lecciones aprendidas para capacitaciones (p. ej. phishing) | — |

El intercambio es por referencias (id de expediente, activos, categorías de datos), nunca con valores de datos personales. Hoy no hay una conexión automática con los demás agentes ni con la base común: se hace por la API de la sección 4 o declarando sus servicios como conectores.

## 7. Reglas que deben respetarse

1. **Plazo de 48 horas** desde que se tiene conocimiento de la brecha: el reloj se inicia en el triaje y no se reinicia.
2. **Ninguna notificación sale sin aprobación humana** (Oficial de Datos Personales).
3. **No incluir datos personales de los titulares** en expedientes, borradores ni mensajes a otros agentes.
4. El filtro del buzón **nunca descarta ante la duda**: una queja dudosa se analiza.
5. Los resultados son **borradores de apoyo**, no asesoría legal.
