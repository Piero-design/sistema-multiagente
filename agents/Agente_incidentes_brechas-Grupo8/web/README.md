# Interfaz web del agente

Aplicación local (React + servidor Node sin dependencias) para usar el agente `agente-incidentes-brechas` sin la terminal: pegar un reporte, cargar el contexto de una organización y leer el expediente con la cuenta regresiva de 48 h.

## Cómo ejecutarla

### Opción 1: Docker (recomendada)
```
cp .env.example .env        # ponga una credencial (ver "Conexión con Claude")
docker compose up --build
```
Abrir **http://localhost:3100**. Los expedientes, contextos y la credencial guardada persisten en volúmenes de Docker. El puerto solo se publica en `127.0.0.1`.

### Opción 2: en su equipo
Requiere Node 18+ y Claude Code instalado.
```
npm start                   # compila la interfaz la primera vez
```
Abrir **http://localhost:3100**. Si ya usa Claude Code con su cuenta, no hay que configurar nada.
Otros valores: `PORT=4000`, `CLAUDE_BIN=ruta/a/claude`. Para desarrollar la interfaz: `npm --prefix web/client run dev` (puerto 5173, con proxy al servidor).

## Rutas
La interfaz usa React Router, así que cada pantalla tiene su URL y se puede compartir, recargar y navegar con atrás/adelante:

| Ruta | Pantalla |
|---|---|
| `/analizar` | Cargar un reporte desde archivo (o escribirlo) y analizarlo |
| `/analizando/:jobId` | Avance del análisis (se puede recargar sin perderlo) |
| `/expedientes` | Lista de análisis hechos |
| `/expedientes/:id` | Expediente: plazo, severidad, decisiones y documentos |
| `/expedientes/:id/:doc` | Un documento concreto, por ejemplo `/expedientes/INC-…/03-notificacion-anpd` |
| `/contextos` | Contextos disponibles |
| `/contextos/nuevo` | Cargar un contexto (arrastrar archivos) |
| `/contextos/:tipo/:nombre` | Ver un contexto completo: archivos agrupados, visor con números de línea y «Ver todo junto» |
| `/contextos/:tipo/:nombre/<archivo>` | Un archivo concreto del contexto |
| `/ajustes/conexion`, `/ajustes/acerca` | Conexión con Claude y acerca del agente |

El servidor devuelve la aplicación para cualquier ruta que no sea `/api/…`.

## Conexión con Claude
Hay tres formas, y la sección **Conexión** de la página muestra cuál está activa y tiene un botón *Probar conexión*:

| Forma | Cómo | Costo |
|---|---|---|
| **Su suscripción de Claude** | En su equipo ejecute `claude setup-token` y ponga el token en `.env` como `CLAUDE_CODE_OAUTH_TOKEN`, o péguelo en la página | Incluido en su plan |
| **API key** | Créela en console.anthropic.com y póngala en `.env` como `ANTHROPIC_API_KEY`, o péguela en la página | Por uso |
| **Sesión local** | Solo sin Docker: usa la sesión que ya tenga iniciada Claude Code | Incluido en su plan |

Lo que pegue en la página se guarda en `.ib-data/auth.json` (permisos 600) y solo se usa para lanzar al agente: nunca se devuelve al navegador. En Docker, un contenedor no ve la sesión de su equipo; por eso necesita el token o la API key.

## Qué evalúa
Un **reporte de incidente o evento de seguridad** (el correo o mensaje que alguien manda cuando "pasó algo" con información o sistemas). El agente determina:

| Pregunta | Resultado en la página |
|---|---|
| ¿Es evento, incidente o brecha de datos personales? | Clasificación y prioridad (P1 a P4) |
| ¿Qué tan grave es para los titulares? | Severidad ENISA: SE = DPC × EI + CB |
| ¿Hay que notificar? ¿A quién? ¿Hasta cuándo? | Obligación (art. 34 del D.S. 016-2024-JUS) y **cuenta regresiva de 48 h** |
| ¿Qué se dice a la ANPD, a los afectados y al CNSD? | Borradores listos para revisar |
| ¿Cómo se contiene y qué se aprende? | Plan de respuesta, causa raíz y controles ISO/IEC 27002 |

## Cargar el contexto de una organización
En **Contextos → Nuevo contexto**:
1. Escriba el nombre de la organización.
2. Arrastre los archivos (inventario de sistemas y datos, logs, políticas, código o configuración) o pegue un texto. Se clasifican por el nombre (`*.log` va a `logs/`, "inventario" a `inventario/`, etc.) o elija la categoría a mano.
3. Pulse **Guardar contexto**. Queda en `contextos/<organizacion>/` y aparece en el selector de *Nuevo análisis*.

Con contexto, el agente verifica el reporte contra esa evidencia y cita `archivo:línea`. Solo texto (.md, .txt, .log, .csv, .json, código), hasta 60 archivos y 1,5 MB cada uno. El agente **solo lee** esa carpeta (`.claude/settings.json` le prohíbe escribir) y `contextos/` no se versiona en git. Use datos de prueba o anonimizados. Los contextos `demo/` vienen incluidos y no se pueden borrar desde la página.

## Cómo probarlo
La carpeta [`archivos-demo/`](../archivos-demo/README.md) trae reportes listos para cargar desde archivo y un contexto nuevo para probar la subida. La guía está en [../examples/guia-de-pruebas.md](../examples/guia-de-pruebas.md).

## Cómo funciona
`web/server.js` guarda el reporte en `salidas/_entradas/`, ejecuta `claude -p --agent agente-incidentes-brechas` en la raíz del repo (con los skills y las reglas de `.claude/settings.json`: solo escribe en `salidas/`), muestra el avance leyendo el flujo de eventos y, al terminar, lee `salidas/INC-…/` y lo presenta en pestañas. La interfaz está en `web/client/` (React + Vite, tipografía IBM Plex incluida en el build, sin llamadas a internet).
