# MCP_SETUP.md — La skill `pims-dpa-auditor` vía MCP en Claude Code

> **Lugar de este documento en la v2.0.** Es una **ruta alternativa**: usar la skill conversando dentro de
> Claude Code, sin n8n ni página web. La ruta principal es n8n (`n8n/INSTALACION_N8N.md`).
> Las secciones 2 a 8 registran la configuración hecha el 07/10/2026 con la v1.1 y se conservan como
> evidencia; lo que cambió con la v2.0 está en la sección 9 y en las notas marcadas **v2.0**.

> Registro de la configuración realizada el **7 de octubre de 2026** sobre Windows 11,
> Claude Code 2.1.292, Python 3.14.0.
> Objetivo: ejecutar la auditoría de DPAs sin API Key de Anthropic, de forma
> compatible con los Términos de Servicio (sin `claude-max-mcp` ni ningún wrapper
> que enrute tokens OAuth de suscripción a terceros).

---

## 1. Qué resuelve esta configuración, y qué no

| | |
|---|---|
| ✅ **La skill corre sin API Key** | Instalada en `~/.claude/skills/`, Claude Code la carga y la ejecuta autenticado con la sesión del usuario. Es el camino "sin API Key". |
| ✅ **Catálogo de skills por MCP** | El servidor `skillkit mcp` expone `list_skills`, `read_skill` y `lint_skill` a cualquier cliente MCP. |
| ✅ **Cálculo determinista** | Dentro de Claude Code sí se puede ejecutar `calcular_resultado.py`, así que el Paso 8 usa el script y no el cálculo manual. |
| ℹ️ **La web no usa MCP** | MCP no transporta inferencia (§7). La página de la v2.0 usa n8n, que llama a Claude Code, Ollama o una API. |

**Lo esencial en una frase:** lo que elimina la API Key es tener la skill instalada en
Claude Code, no el servidor MCP. El servidor MCP añade un catálogo consultable de
skills; es útil, pero no es la pieza que quita la clave.

---

## 2. Resumen de lo instalado

| Componente | Valor |
|---|---|
| Paquete | `skillkit-cli` 1.0.2 (MIT, sin dependencias de runtime) |
| Ejecutable | `C:\Users\ttvhe\AppData\Roaming\Python\Python314\Scripts\skillkit.exe` |
| Skill instalada | `~/.claude/skills/pims-dpa-auditor/` — 8 archivos, byte a byte idénticos al origen |
| Puntaje del linter | **100/100 · grado A** · 0 errores · 0 advertencias · 0 notas (también con `--strict`) |
| Servidor MCP | `skillkit`, ámbito **user**, stdio, con `PYTHONUTF8=1` |
| Config escrita en | `~/.claude.json` → `mcpServers.skillkit` (**no** en `settings.json`, ver §4) |
| Estado | `claude mcp list` → `skillkit: ... ✔ Connected` |

### Revisión de compatibilidad con los ToS

Se inspeccionaron los 8 módulos del paquete instalado:

- Ningún `import` de `urllib`, `http`, `socket`, `requests`, `httpx`, `ssl`, `ftplib` ni `smtplib`.
- Un único `subprocess`, en `installer.py:53`: un `git clone --depth 1` que solo se
  ejecuta al instalar una skill **desde una URL**. Aquí se instaló desde carpeta local,
  así que no se invoca.
- `mcp_server.py` solo lee archivos locales de skills y habla JSON-RPC por stdin/stdout.

No hay enrutamiento de tokens OAuth, ni endpoints de terceros, ni acceso a credenciales
de Anthropic.

---

## 3. Paso a paso (comandos verificados)

### 3.1 Instalar skillkit-cli

`pipx` no estaba disponible en el equipo, así que se usó `pip`:

```bash
pip install skillkit-cli
```

> `pip` avisa de que `skillkit.exe` queda en un directorio fuera del `PATH`
> (`...\Python314\Scripts`). Esto importa en §4: la entrada MCP debe usar la **ruta
> absoluta** del ejecutable, o el servidor no arranca.

### 3.2 Exportar la variable de codificación (Windows)

Antes de cualquier comando de skillkit en una consola Windows:

```bash
set PYTHONUTF8=1                      # cmd
$env:PYTHONUTF8 = "1"                 # PowerShell
export PYTHONUTF8=1                   # Git Bash
```

Sin esto, **todos** los subcomandos que imprimen el informe fallan. Ver §5.

### 3.3 Validar la skill

```bash
skillkit lint pims-dpa-auditor
```

```
skillkit lint: pims-dpa-auditor
  ✓ no issues found

  score: 100/100 (grade A) · 0 errors · 0 warnings · 0 notes
```

También limpio en modo estricto (`skillkit lint --strict --json pims-dpa-auditor` →
`{"score": 100, "grade": "A", "ok": true, "findings": []}`). **No hubo ningún
SKILL001/SKILL002 que corregir**, así que `SKILL.md` no se modificó.

> `lint` recibe una **ruta** a la carpeta de la skill, no un nombre: funciona como
> `skillkit lint pims-dpa-auditor` porque se ejecuta desde la raíz del proyecto.

### 3.4 Instalar la skill

Se validó **antes** de instalar, para no copiar una versión que luego habría que corregir:

```bash
skillkit install ./pims-dpa-auditor
# installed: C:\Users\ttvhe\.claude\skills\pims-dpa-auditor
```

Verificación de la copia:

```bash
diff -r pims-dpa-auditor ~/.claude/skills/pims-dpa-auditor   # sin diferencias
skillkit list
```

Los 8 archivos (`SKILL.md`, 3 de `references/`, 3 de `assets/`, 1 de `scripts/`)
quedaron idénticos al origen.

### 3.5 Registrar el servidor MCP

```bash
claude mcp add -s user skillkit -e PYTHONUTF8=1 -- \
  "C:/Users/ttvhe/AppData/Roaming/Python/Python314/Scripts/skillkit.exe" mcp
```

Resultado:

```
Added stdio MCP server skillkit with command: ...\skillkit.exe mcp to user config
File modified: C:\Users\ttvhe\.claude.json
```

Comprobación:

```bash
claude mcp list
# skillkit: ...\skillkit.exe mcp - ✔ Connected
```

Y la prueba directa por stdio, que es la que de verdad confirma que sirve:

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_skill","arguments":{"name":"pims-dpa-auditor"}}}' \
 | skillkit mcp
```

Las tres herramientas responden: `list_skills`, `read_skill` (devuelve SKILL.md íntegro,
9 950 caracteres con acentos y flechas intactos) y `lint_skill` (100/100).

---

## 4. La ubicación correcta de la configuración MCP

**Claude Code no lee `mcpServers` desde `settings.json`.** La entrada se ignora en
silencio: no hay error, no hay advertencia, el servidor simplemente nunca existe.

| Ámbito | Archivo real |
|---|---|
| `local` y `user` | `~/.claude.json` → clave `mcpServers` |
| `project` | `.mcp.json` en la raíz del proyecto |
| ❌ **No** | `~/.claude/settings.json` ni `.claude/settings.local.json` |

El `settings.json` sí controla *otras* cosas de MCP (por ejemplo
`enabledMcpjsonServers`), pero no define servidores.

### Issue de referencia

> **[anthropics/claude-code#24477](https://github.com/anthropics/claude-code/issues/24477)**
> — *"[DOCS] Add warning that mcpServers in settings.json / settings.local.json is
> silently ignored"*. Abierto el 09/02/2026, cerrado. Etiquetas: `documentation`,
> `platform:windows`, `area:mcp`, `stale`.
>
> Pide exactamente lo que aquí se documenta: que la documentación advierta de forma
> visible que esa clave en `settings.json` no hace nada. La información correcta
> (`~/.claude.json` para user/local, `.mcp.json` para project) sí está en los docs,
> pero enterrada.

**Nota de atribución:** este issue corresponde al hallazgo de la *ubicación de la
configuración*. El bug de codificación de skillkit (§5) es un asunto distinto y no
tiene relación con #24477.

### Entrada resultante en `~/.claude.json`

```json
{
  "mcpServers": {
    "skillkit": {
      "type": "stdio",
      "command": "C:/Users/ttvhe/AppData/Roaming/Python/Python314/Scripts/skillkit.exe",
      "args": ["mcp"],
      "env": { "PYTHONUTF8": "1" }
    }
  }
}
```

Dos detalles deliberados:

1. **Ruta absoluta al ejecutable.** `skillkit` no está en el `PATH`, así que
   `"command": "skillkit"` habría fallado al arrancar el subproceso.
2. **Ámbito `user`, no `project`.** La ruta absoluta es específica de esta máquina;
   en `.mcp.json` viajaría con el repositorio y se rompería en cualquier otro equipo.
   Además, la skill está instalada en el directorio global `~/.claude/skills/`, que es
   lo que este servidor sirve.

---

## 5. El bug de codificación de skillkit y el fix `PYTHONUTF8=1`

### Síntoma

Cualquier subcomando de skillkit cuya salida contenga un carácter no ASCII aborta con:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 35
```

En el servidor MCP el fallo es peor, porque ocurre **en plena respuesta JSON-RPC**:

```
File "...\skillkit\mcp_server.py", line 201, in serve
  output_stream.write(json.dumps(response, ensure_ascii=False) + "\n")
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 2677
```

### Causa

`mcp_server.py:201` serializa con `ensure_ascii=False` y escribe a un `sys.stdout` que
en Windows es **cp1252** por defecto. Cualquier carácter fuera de ese juego mata el
proceso.

Con esta skill el fallo era **determinista, no intermitente**:

- `lint` y `list` revientan en el `✓` (U+2713) de su propio informe.
- `read_skill` revienta en la flecha `→` (U+2192) de *"DPO → Legal"*, en la posición
  2677 de `SKILL.md`. Es decir: **leer esta skill por MCP fallaba siempre**.

Un `SKILL.md` en español está lleno de disparadores: `→`, `·`, `≤`, `🅰`, `🟢`, y todas
las tildes y eñes.

### Fix aplicado

Forzar el modo UTF-8 de Python en el entorno del servidor, que es lo que hace la
clave `env` de la entrada MCP de §4:

```json
"env": { "PYTHONUTF8": "1" }
```

Para los comandos interactivos, exportar la variable en la consola (§3.2).
`PYTHONIOENCODING=utf-8` también funciona; se eligió `PYTHONUTF8=1` por ser la bandera
canónica del modo UTF-8.

### Comprobación

```bash
# sin la variable
skillkit lint pims-dpa-auditor     # -> UnicodeEncodeError, exit 1
# con la variable
PYTHONUTF8=1 skillkit lint pims-dpa-auditor   # -> 100/100, exit 0
```

Y sobre el servidor MCP, con `read_skill`: sin la variable, 1 línea de salida y
exit 1 con 1 638 bytes en stderr; con ella, 2 líneas, exit 0 y stderr vacío.

### Estado upstream

No se encontró un issue público para este bug. `skillkit-cli` no publica
`project_urls`, `home_page` ni repositorio en su metadata de PyPI, así que no hay un
rastreador donde reportarlo. El `fix` de §4 es una mitigación local, no una corrección
del paquete: **si se reinstala o actualiza skillkit, la variable `env` de la entrada MCP
sigue siendo necesaria.**

---

## 6. El mismo bug cp1252 en `calcular_resultado.py`

> **v2.0: corregido.** El script de la v2.0 imprime solo caracteres ASCII; ya no hace falta `-X utf8`. Una prueba de `ejecutar_pruebas.py` lo comprueba con una consola cp1252. Lo que sigue describe la v1.1.

Conviene dejarlo registrado: **el script del propio proyecto tiene exactamente el mismo
problema**, por la misma causa, y se arregla de la misma manera.

| | `skillkit mcp_server.py` | `pims-dpa-auditor/scripts/calcular_resultado.py` |
|---|---|---|
| Línea | 201 | 224 |
| Código | `output_stream.write(json.dumps(..., ensure_ascii=False))` | `print(f"Puntaje: ... base {p['base']} − {p['penalizacion']}")` |
| Carácter que rompe | `→` U+2192, `✓` U+2713 | **`−` U+2212** (signo menos tipográfico) |
| Momento del fallo | Al escribir la respuesta JSON-RPC: **se pierde la respuesta** | Al imprimir el resumen final: el **JSON ya se escribió correctamente** |
| Gravedad | Bloqueante | Cosmético, pero deja código de salida 1 |

La diferencia importante es *cuándo* falla. En `calcular_resultado.py` el
`Path(...).write_text(...)` ocurre **antes** del `print`, así que el resultado queda
bien guardado en disco y solo se pierde la línea de resumen; el proceso, eso sí,
termina con `exit 1`, lo que puede hacer que un script que lo invoque crea que el
cálculo falló.

Dos formas de evitarlo:

```bash
python -X utf8 scripts/calcular_resultado.py resultado.json --config assets/config_organizacion.json
# o
PYTHONUTF8=1 python scripts/calcular_resultado.py resultado.json --config assets/config_organizacion.json
```

Arreglo de raíz, si se quiere corregir el script: sustituir el `−` (U+2212) de la
línea 224 por un guion ASCII `-`. Es un único carácter y elimina la dependencia del
entorno.

> **Patrón general.** Ambos casos son el mismo error de diseño: escribir caracteres
> tipográficos a un stdout cuya codificación no se ha fijado. En un proyecto en
> español sobre Windows esto no es un caso límite, es el caso normal.

---

## 7. MCP no transporta inferencia

Conviene tenerlo claro porque cambia qué resuelve esta configuración.

Un servidor MCP expone **herramientas y recursos** a un *cliente* que ya tiene acceso al
modelo. No entrega completions. Claude Code es el cliente, y es él quien aporta el
modelo y la autenticación.

```
Claude Code  ──(ya autenticado: suscripción del usuario)──>  modelo
     │
     └──(MCP, stdio)──> skillkit mcp ──> lee ~/.claude/skills/
                        (list_skills, read_skill, lint_skill)
```

De ahí se sigue:

- **La skill en Claude Code: sin API Key.** Funciona hoy, verificado en §8.
- **Una página web no obtiene inferencia por MCP:** no hay servidor MCP que devuelva
  completions, y el navegador no es un cliente MCP con acceso al modelo. Por eso las dos
  interfaces web del proyecto usan un proceso local que sí llama al modelo:
  - `demo/servidor_demo.py` lanza `claude -p` con la suscripción del usuario (sin API Key);
  - **v2.0:** n8n llama a Claude Code (también `claude -p`, sin API Key), a Ollama o a una
    API, según lo que se elija en la página.

---

## 8. Verificación de extremo a extremo (sin API Key)

Las dos ejecuciones se hicieron con la skill cargada desde
`~/.claude/skills/pims-dpa-auditor` y el Paso 8 resuelto con el script
(`trazabilidad.calculo: "script"`). Resultados en
`pims-dpa-auditor_pruebas/ejecuciones_2026-10-07/`, sin tocar los resultados de
referencia del TIF.

| Contrato | Puntaje | Dictamen | Esquema | ¿Reproduce la referencia del TIF? |
|---|---|---|---|---|
| NubeAndina | **22/100** · Riesgo alto (base 37,5 − 15) | No recomendable sin enmiendas | válido | **Sí, exacta**: 24/24 controles con el mismo estado, mismo resumen (1 🟢 · 12 🟡 · 4 🔴 · 7 ⚪), mismas 4 dimensiones, mismo dictamen |
| AndesCloud | **100/100** · Riesgo bajo (base 100 − 0) | Recomendable | válido | 24/24 controles iguales y mismo puntaje; **una alerta de más**, explicada abajo |

Comandos:

```bash
python -X utf8 scripts/calcular_resultado.py \
  .../ejecuciones_2026-10-07/resultado_NubeAndina.json \
  --config assets/config_organizacion.json \
  --documento .../contratos/dpa_nubeandina.md \
  --fecha-ref 2026-10-07
```

### La diferencia en AndesCloud no es un fallo: es la fecha

La referencia del TIF se calculó con `--fecha-ref 2026-10-01` y tenía **0 alertas**. Hoy
aparece una **Media de Renovación**:

> *Renovación automática: el plazo para preavisar termina el 2026-12-02.*

Aritmética (criterios §7, `dias_alerta_renovacion = 60`):

| | 01/10/2026 (TIF) | 07/10/2026 (hoy) |
|---|---|---|
| Fin de vigencia | 2027-01-31 | 2027-01-31 |
| Límite para preavisar (fin − 60 días) | 2026-12-02 | 2026-12-02 |
| Ventana de alerta (ref + 60 días) | hasta 2026-11-30 | hasta **2026-12-06** |
| ¿Límite dentro de la ventana? | **No** | **Sí** → alerta Media |

En seis días la fecha límite de preaviso entró en la ventana de 60 días. Es el
comportamiento correcto y además el que anticipaba el caso 4 de
`casos_de_prueba.json`: *"alerta Media de preaviso **si la fecha límite cae en la
ventana**"*.

El puntaje no cambia porque solo las alertas **Altas** penalizan (−5 cada una, hasta
−20); las Medias informan al DPO sin restar.

**Conclusión de la validación:** el determinismo del script se sostiene. Lo único que
varía entre ejecuciones es lo que depende de la fecha de referencia, que es
precisamente lo que debe variar.

---

## 9. Mantenimiento

### Con la v2.0

- **Instalar las dos skills.** La v2.0 añade el perfilador:
  ```bash
  PYTHONUTF8=1 skillkit install ./pims-dpa-auditor
  PYTHONUTF8=1 skillkit install ./pims-perfilador-organizacion
  ```
  Las jurisdicciones (`jurisdicciones/peru/`) viajan dentro de la carpeta de la skill.
- **Las organizaciones no viajan con la skill.** Están en `organizaciones/<id>/` del proyecto.
  Abre Claude Code **en la raíz del proyecto** y nombra la organización en el pedido, por ejemplo:
  *"Evalúa este DPA para la organización `organizaciones/unsa`"*. Si no se nombra ninguna, la
  skill usa la configuración genérica y lo anota como supuesto.
- **Calcular con el contexto de la organización:**
  ```bash
  python pims-dpa-auditor/scripts/calcular_resultado.py resultado.json --org organizaciones/unsa
  ```
- La doble aprobación, el registro y las renovaciones automáticas existen solo en la ruta n8n.

### Desde la v1.1

- **La skill instalada es una copia.** Tras editar `pims-dpa-auditor/` en el
  repositorio, hay que resincronizar:
  ```bash
  PYTHONUTF8=1 skillkit install ./pims-dpa-auditor
  ```
- **Tras actualizar o reinstalar skillkit**, la entrada MCP conserva su `env`, pero
  conviene reconfirmar con `claude mcp list` que sigue en `✔ Connected`.
- **`skillkit list` marca `✗ synced — broken`.** Es la carpeta de skills sincronizadas
  de la cuenta (`~/.claude/skills/synced/`, estructura anidada por bucket). skillkit
  espera un `SKILL.md` directamente dentro de cada carpeta de primer nivel y no
  entiende ese layout. **Falso positivo, no tocar.**
- **Quitar el servidor MCP:**
  ```bash
  claude mcp remove skillkit -s user
  ```
- **Desinstalar la skill:**
  ```bash
  PYTHONUTF8=1 skillkit remove pims-dpa-auditor
  ```

---

## 10. Entorno verificado

| | |
|---|---|
| SO | Windows 11 Pro 10.0.26300 |
| Claude Code | 2.1.292 |
| Python | 3.14.0 · pip 26.2.1 |
| skillkit-cli | 1.0.2 |
| Codificación por defecto de la consola | cp1252 (origen de §5 y §6) |
| Fecha de la configuración | 2026-10-07 |
