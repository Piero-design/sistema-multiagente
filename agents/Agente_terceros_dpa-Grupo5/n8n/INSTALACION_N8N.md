# n8n como motor del PIMS — instalación y uso

n8n ejecuta todo el proceso:

- recibe las peticiones,
- lee la skill, la organización, su jurisdicción y su perfil,
- llama al modelo de IA que elijas,
- calcula el puntaje de forma determinista,
- guarda el registro y gestiona la doble puerta DPO → Legal.

La página web (Etapa 3) también la sirve n8n: **http://localhost:5678/webhook/pims/app**. Su documentación está en `web/LEEME.md` y el guion de la demo en `GUIA_DEMO.md`.

```
                 ┌──────────────── n8n (http://localhost:5678) ───────────────────┐
 página / curl ─►│ webhooks /pims/*  →  Auditar · Perfilar · Aprobar · Consultas   │
                 │        │                          │                            │
                 │  Leer / Guardar archivos      Modelo de IA ── Switch ──┬─ Ollama           │
                 │  (dentro del proyecto)        (selector)               ├─ Anthropic API    │
                 │        │                                               ├─ API tipo OpenAI  │
                 │  Cálculo determinista (JS idéntico al .py)             └─ Claude Code (CLI)│
                 └────────┼───────────────────────────────────────────────────────────────┘
                          ▼
            datos/registro/<id>.json y .md · datos/trabajos/ · organizaciones/<id>/
```

---

## 1. Requisitos

| | |
|---|---|
| **Node.js 24 o superior** | n8n 2.43 no arranca con Node 22 ("Your Node.js version … is not supported"). Comprueba con `node --version`. |
| **n8n 2.x** | `npm install -g n8n` (probado con **2.43.4**). |
| **Python 3.9+** | Para el instalador. |
| **Un modelo** (uno basta) | Claude Code con sesión iniciada (`claude --version`), **o** Ollama corriendo, **o** una API key de Anthropic u otro proveedor compatible con OpenAI. |

> n8n avisa al arrancar que ejecutarlo fuera de Docker está *deprecated* y que versiones futuras lo exigirán. Hoy funciona. Dentro de Docker, n8n no ve el `claude` de tu equipo, así que en ese caso usa Ollama o una API.

## 2. Instalación (Windows)

En una terminal (PowerShell o cmd), dentro de la carpeta del proyecto:

```powershell
# 1. Generar los flujos con la ruta de ESTA carpeta y los scripts de arranque
python n8n\instalar_flujos.py

# 2. Con n8n DETENIDO: importarlos y publicarlos (activarlos)
python n8n\instalar_flujos.py --importar

# 3. Arrancar n8n con la configuración correcta
n8n\iniciar_n8n.bat
```

4. La primera vez, abre **http://localhost:5678** y crea la cuenta de propietario de n8n. Es local.
5. Verás 13 flujos **PIMS · …** publicados.
6. Abre la página: **http://localhost:5678/webhook/pims/app**. Para comprobar solo la API: http://localhost:5678/webhook/pims/estado debe responder `{"ok":true,"version":"2.0",…}`.

**Arranca siempre con `iniciar_n8n.bat`**, no con `n8n start` a secas, porque el script fija:

| Variable | Valor | Por qué |
|---|---|---|
| `N8N_RESTRICT_FILE_ACCESS_TO` | la carpeta del proyecto | n8n 2.x solo deja leer y escribir en `~/.n8n-files` por defecto |
| `NODES_EXCLUDE` | `[]` | habilita el nodo *Execute Command*, desactivado por defecto en 2.x. Lo usan **Claude Code** y **crear organización** |
| `GENERIC_TIMEZONE` | `America/Lima` | fecha de referencia de las auditorías y de las renovaciones |
| `N8N_LISTEN_ADDRESS` | `127.0.0.1` | n8n solo es accesible desde tu equipo |

Si prefieres no habilitar *Execute Command*, usa `python n8n\instalar_flujos.py --sin-execute-command`. Todo funciona con Ollama o una API; Claude Code y "crear organización" responden con un mensaje explicando qué falta (probado).

**Si mueves la carpeta del proyecto**, repite los pasos 1 y 2: la ruta va dentro de los flujos y del `.bat`.

**Si modificas la skill o la jurisdicción**, no hace falta reinstalar: n8n lee esos archivos en cada ejecución. Solo hay que reinstalar si cambias `n8n/lib/*.js` o `construir_flujos.py`.

## 3. Elegir y cambiar el modelo

El modelo vive en `datos/config_modelo.json` y se cambia **sin tocar los flujos**: desde la pantalla **Configuración** de la página, editando el archivo o con la API:

```powershell
# Claude Code con tu suscripción (por defecto)
Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/pims/config -ContentType application/json `
  -Body '{"proveedor":"claude_code","modelo":"sonnet"}'

# Ollama local
Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/pims/config -ContentType application/json `
  -Body '{"proveedor":"ollama","modelo":"qwen2.5:14b","url_ollama":"http://127.0.0.1:11434","num_ctx":49152}'

# Anthropic API
Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/pims/config -ContentType application/json `
  -Body '{"proveedor":"anthropic","modelo":"claude-sonnet-5-5","api_key":"sk-ant-..."}'
```

| Proveedor | Necesita | Notas |
|---|---|---|
| `claude_code` | `claude` en el PATH del proceso de n8n y *Execute Command* | El modelo no recibe herramientas (Bash, Read, etc. bloqueadas). Deja archivos temporales en `datos/tmp/`, que puedes borrar. |
| `ollama` | Ollama corriendo | El prompt de auditoría ocupa unos 20 000 tokens: usa `num_ctx` de 32 768 o más (por defecto 49 152). Con modelos pequeños, la calidad baja. |
| `anthropic` | `api_key` | `url_anthropic` es configurable, por si usas un proxy. |
| `openai` | `url_openai` y, según el caso, `api_key` | Sirve para OpenAI, Groq, LM Studio, vLLM y cualquier API compatible. |

La `api_key` se guarda en texto plano en `datos/config_modelo.json` y nunca se devuelve completa por la API: se enmascara como `********1234`. No compartas esa carpeta.

### Ollama: memoria de la tarjeta gráfica

El prompt de auditoría ocupa unos 20 000 tokens y la respuesta (informe + JSON) varios miles más, y el contexto (`num_ctx`) debe contener ambos: **32 768 es el mínimo**, y se recomienda **40 960 o 49 152** para que el informe no salga cortado. El contexto también ocupa VRAM, además del modelo. Valores aproximados para un modelo de 14B comprimido (Q4):

| | VRAM aproximada |
|---|---|
| Modelo | ~9 GB |
| Contexto de 49 152 tokens (valor por defecto) | ~9-10 GB más |
| Contexto de 32 768 tokens | ~6 GB más |

- Si no cabe, Ollama pasa parte del modelo a la RAM y al procesador y todo va mucho más lento. Compruébalo con `ollama ps`: la columna PROCESSOR debe decir `100% GPU`.
- Para ahorrar: baja `num_ctx` a 32 768 en Configuración y, antes de iniciar Ollama, define las variables de entorno `OLLAMA_FLASH_ATTENTION=1` y `OLLAMA_KV_CACHE_TYPE=q8_0`, que reducen a la mitad, más o menos, la memoria del contexto.
- Con 12 GB de VRAM o menos, un 14B no cabe entero con ese contexto: usa un modelo de 7-8B (por ejemplo `qwen2.5:7b`, unos 5 GB más 2-3 GB de contexto) y mide su calidad con `pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py`.
- Windows y el navegador ya usan 0,5-1,5 GB de VRAM; compruébalo con `nvidia-smi`.

### ¿Docker?

Se recomienda instalar n8n y Ollama **directamente en Windows**. Dentro de Docker, n8n no ve el `claude` del equipo (solo funcionarían Ollama o una API), la ruta del proyecto cambia y habría que reinstalar los flujos con la ruta del contenedor. Esa variante no está probada. Si aun así n8n va en Docker y Ollama en Windows, la URL de Ollama es `http://host.docker.internal:11434`. Docker no limita la VRAM: un contenedor con GPU la usa completa.

## 4. Cómo se usa (API)

Todas las rutas empiezan por `http://localhost:5678/webhook/`.

| Método y ruta | Cuerpo / parámetros | Respuesta |
|---|---|---|
| `POST pims/auditar` | `{organizacion, proveedor?, contrato_texto}` o `{organizacion, archivo:{nombre, base64}}` (.pdf/.md/.txt), `fecha_ref?` | `202 {trabajo}`. Sigue en segundo plano |
| `GET pims/trabajo?id=T…` | | `{estado: en_cola, evaluando, terminado o error, mensaje, id_registro, puntaje, dictamen}` |
| `GET pims/registro?organizacion=&estado=` | | Lista de evaluaciones |
| `GET pims/registro/detalle?id=` | | `{resultado (JSON del registro), informe (Markdown)}` |
| `POST pims/aprobar` | `{id_registro, rol: DPO o Legal, decision: aprobar o rechazar, usuario, comentario?}` | Nuevo estado e historial. Fuera de turno devuelve 409 |
| `POST pims/perfilar` | `{organizacion}` | `202 {trabajo}`. Genera `perfil_organizacion.md` en Borrador |
| `GET pims/perfil?organizacion=` | | Texto, validación, terceros |
| `POST pims/perfil/validar` | `{organizacion, validado_por}` | El DPO marca el perfil como validado |
| `GET pims/organizaciones` | | Configuración, perfil, registros y **terceros sin DPA evaluado** de cada organización |
| `POST pims/organizacion` | `{id, nombre, jurisdiccion, cargo_dpo, cargo_legal}` | Crea `organizaciones/<id>/` |
| `POST pims/documento` | `{organizacion, nombre, texto}` o `{…, base64}` | Guarda un documento institucional |
| `GET pims/renovaciones` | | Alertas de renovación con la fecha de hoy. También corre **cada lunes a las 07:52** y escribe `datos/alertas_renovacion.json` |
| `GET pims/estado`, `GET pims/jurisdicciones` | | Estado general, modelo configurado y jurisdicciones disponibles |
| `GET pims/documentos?organizacion=` | | Documentos institucionales de la organización (nombre y tamaño) |
| `GET pims/app`, `GET pims/app/mammoth` | | La página y el lector de `.docx` que carga bajo demanda |
| `POST pims/config` | campos del modelo | Cambia el modelo |
| `POST pims/chat` | `{ambito: expediente u organizacion, id, organizacion, pregunta, usuario?}` | `202 {trabajo}`; la respuesta queda en `pims/trabajo` (`respuesta_chat`) |
| `GET pims/chat?ambito=&id=` | | Conversación guardada (`datos/chats/`) |

Ejemplo completo en PowerShell:

```powershell
$contrato = Get-Content -Raw -Encoding UTF8 pims-dpa-auditor_pruebas\contratos\dpa_nubeandina.md
$body = @{ organizacion = "inversiones_altiplano"; proveedor = "NubeAndina"; contrato_texto = $contrato } | ConvertTo-Json
$t = Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/pims/auditar -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body))
do { Start-Sleep 5; $e = Invoke-RestMethod "http://localhost:5678/webhook/pims/trabajo?id=$($t.trabajo)"; $e.estado } while ($e.estado -notin "terminado","error")
$e   # puntaje, dictamen e id_registro; el informe está en datos\registro\<id_registro>.md
```

Con un modelo real, una auditoría tarda **2-5 minutos**. Con Ollama puede tardar más, según el equipo.

## 5. Qué hay dentro de cada flujo

| Flujo | Qué hace |
|---|---|
| **PIMS · Auditar contrato** | Valida la petición y responde 202. Lee la skill, la organización, la jurisdicción, el perfil y el contrato (los PDF con marcadores `[Página N]`). Arma el prompt y llama al modelo. Si el JSON no cumple el esquema, pide **una** corrección. **Calcula de forma determinista** e inserta las cifras en el informe. Guarda el registro. |
| **PIMS · Perfilar organización** | Lee `documentos/`, los trocea (~18 000 caracteres), extrae notas por parte, redacta el perfil, lo **valida con el mismo validador que Python**, pide una corrección si hace falta y lo guarda en Borrador. Si había un perfil anterior, lo conserva como `.anterior.md`. |
| **PIMS · Aprobaciones** | Máquina de estados Pendiente DPO → Pendiente Legal → Aprobado o Rechazado, con historial. También permite que el DPO valide el perfil. |
| **PIMS · Chat** | Preguntas sobre un expediente o una organización. Arma el contexto (registro, contrato, informe, perfil, configuración o la tabla de expedientes), lo recorta si no cabe en el modelo, llama al modelo y guarda la conversación en `datos/chats/`. No modifica expedientes ni perfiles. |
| **PIMS · Renovaciones** | Cada lunes recalcula las alertas de vencimiento de todos los registros con la fecha del día. |
| **PIMS · Consultas / Administración** | La API de lectura y escritura que usa la página. Cada webhook solo deja leer sus respuestas a la página y al propio n8n (`allowedOrigins`). |
| **PIMS · Página web** | Sirve `web/index.html` con sus librerías incrustadas. |
| **PIMS · Modelo de IA** | Selector: un nodo *Switch* envía a Ollama, Anthropic, la API tipo OpenAI o Claude Code según `datos/config_modelo.json`. |
| **PIMS · Leer / Guardar archivos** | Subflujos reutilizables. Toda lectura y escritura queda **dentro del proyecto**. |
| **PIMS · Claude Code / Crear carpetas** | Los únicos que usan *Execute Command*. Están aislados para que el resto funcione sin él. |

**El número lo pone el código, no el modelo.** El cálculo de `n8n/lib/calcular.js` es un port de `calcular_resultado.py`, verificado como **idéntico en 5 012 casos**: referencias, variantes y aleatorios, incluidos 476 empates de redondeo como 22,5. El modelo solo aporta la calificación cualitativa de cada control.

## 6. Probar sin modelo (modelo simulado)

Sirve para comprobar que n8n, los archivos y el cálculo funcionan, sin gastar cuota. **No evalúa contratos**: devuelve los resultados de referencia de los tres contratos de prueba y de los cinco contratos supuestos de la UNSA.

```powershell
# Terminal 1
python n8n\pruebas\modelo_simulado.py --puerto 11435
# Terminal 2 (con n8n arrancado)
Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/pims/config -ContentType application/json -Body '{"proveedor":"ollama","url_ollama":"http://127.0.0.1:11435"}'
```

Después audita NubeAndina (debe dar 22), AndesCloud (100) o DigiServ (0), o con la organización *UNSA* sus contratos (50, 46, 99, 0 y 31). **Vuelve a configurar tu modelo real al terminar.**

Pruebas automáticas, todas verificadas en un n8n 2.43.4 real:

```
python n8n\pruebas\equivalencia_py_js.py      # cálculo JS = Python (5 012 casos)
python n8n\pruebas\equivalencia_perfil.py     # validador de perfiles JS = Python (1 503 casos)
python n8n\pruebas\probar_flujos.py --raiz <COPIA del proyecto>   # 30 pruebas de extremo a extremo
```

`probar_flujos.py` crea registros y organizaciones de prueba: ejecútalo sobre una **copia** del proyecto, instalada con su propio `instalar_flujos.py`.

## 7. Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `Your Node.js version … is not supported` | Instala Node.js 24 o superior. |
| `/webhook/pims/...` devuelve *Cannot GET* o 404 | Los flujos no están publicados: `python n8n\instalar_flujos.py --importar` con n8n detenido, o publícalos desde la interfaz. |
| `Access to the file is not allowed` | n8n no se arrancó con `iniciar_n8n.bat`, o el proyecto se movió (repite la instalación). También ocurre si alguna carpeta de la ruta es un enlace simbólico o una *junction*: n8n 2.x lo bloquea. Copia el proyecto a una ruta normal, por ejemplo `C:\TIF\`. |
| Trabajo en error: *Claude Code no disponible: Unrecognized node type* | *Execute Command* deshabilitado: arranca con `iniciar_n8n.bat` (incluye `NODES_EXCLUDE=[]`). |
| Trabajo en error: salida inesperada de claude | El proceso de n8n no encuentra `claude` o la sesión expiró. Abre una terminal, comprueba `claude --version` y arranca n8n desde ella, o pon la ruta completa en `claude_bin`. |
| Trabajo en error: *Error de red con ollama: connect ECONNREFUSED ::1:11434* | n8n intentó `localhost` por IPv6 y Ollama solo escucha en IPv4. Usa `http://127.0.0.1:11434`. Desde esta versión n8n lo cambia solo. |
| Trabajo en error: *Error de red con ollama* | Ollama no está corriendo o la URL es incorrecta. |
| Trabajo en error: *El JSON del modelo no cumple el esquema incluso tras una corrección* | Habitual con modelos pequeños (7-8B): el JSON de 24 controles es largo y estricto. Los errores salen en el trabajo y en `datos\fallidos\<trabajo>.md`, junto con las dos respuestas del modelo. Con Ollama, la corrección usa **salida estructurada**: por defecto `json` (JSON válido, rápido); en Configuración → *Corrección del JSON* se puede elegir el esquema completo, más estricto pero mucho más lento con modelos locales. Si aún falla, prueba un modelo mayor o Claude Code, y anótalo como tasa de fallo del modelo. |
| *No se pudo extraer texto del archivo (¿PDF escaneado?)* | El PDF es una imagen. Pega el texto o usa un PDF con texto. |
| El informe sale cortado o con `truncado: true` | El modelo alcanzó su límite de salida: sube `max_tokens` o, en Ollama, `num_ctx`. |
| La ruta del proyecto tiene `*`, `?`, `{` o `}` | El instalador lo rechaza porque n8n usa esos caracteres como patrones. Mueve el proyecto. |
