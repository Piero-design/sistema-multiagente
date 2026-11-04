# Guía de integración · Agente Terceros/DPA (Grupo 5)

Este agente es **PIMS Privacy Guard**: audita los contratos de encargo de tratamiento (DPA) que la organización firma con sus proveedores contra ISO/IEC 27701:2025 y la Ley 29733. La descripción completa está en [README.md](README.md) y [PROYECTO.md](PROYECTO.md); esta guía resume lo que necesita quien lo integre al sistema multiagente.

## 1. Nombres: Grupo 5 = «Agente 7» en el código

En el repositorio común este agente es **Grupo 5** (`Agente_terceros_dpa-Grupo5`). En el código se llama **Agente 7**, porque así se numeró en el proyecto original: el rol PostgreSQL `agente7`, las funciones `agente7_*`, el usuario autor `agente7` y los textos de la skill. **No tiene relación con el Grupo 7 (Controles/SoA).**

Del mismo modo, el README llama «Agente 1» a la skill `pims-perfilador-organizacion/`, que convierte documentos institucionales en un perfil de la organización. Es parte de este agente y no tiene relación con el Grupo 1 (Formación y conciencia).

## 2. Cómo se ejecuta

El motor es **n8n** (puerto 5678). La página web y la API los sirve el propio n8n; no hay otro servidor.

```powershell
python n8n\instalar_flujos.py              # genera los flujos con la ruta de esta carpeta
python n8n\instalar_flujos.py --importar   # con n8n detenido
n8n\iniciar_n8n.bat
```

- Página: <http://localhost:5678/webhook/pims/app>
- Comprobación: `GET http://localhost:5678/webhook/pims/estado` → `{"ok":true,…}`
- Requisitos: Node.js 24+, n8n 2.x, Python 3.9+ y un modelo (Claude Code, Ollama, API de Anthropic o API tipo OpenAI). El modelo se elige en `datos/config_modelo.json` o desde la página.
- Sin modelo: `python n8n\pruebas\modelo_simulado.py` (ver `n8n/INSTALACION_N8N.md`, §6).

**Si la carpeta cambia de lugar, hay que repetir los dos comandos del instalador**, porque la ruta queda dentro de los flujos.

## 3. API para los demás agentes

Todas las rutas empiezan con `http://localhost:5678/webhook/`. La tabla completa está en `n8n/INSTALACION_N8N.md`, §4.

| Ruta | Para qué |
|---|---|
| `POST pims/auditar` | `{organizacion, contrato_texto}` o `{organizacion, archivo:{nombre, base64}}`, más `proveedor?`, `fecha_ref?` y `contexto?` (`perfil` por defecto, `bd` o `ambos`: ver §4). Responde `202 {trabajo}` y sigue en segundo plano (30 s a 5 min con un modelo real). |
| `GET pims/trabajo?id=` | Estado del trabajo; al terminar trae `id_registro`, `puntaje` y `dictamen`. |
| `GET pims/registro?organizacion=` | Lista de expedientes. |
| `GET pims/registro/detalle?id=` | Expediente completo (JSON) e informe (Markdown). |
| `POST pims/aprobar` | Decisión humana `{id_registro, rol: DPO o Legal, decision, usuario}`. Primero el DPO y después Legal; fuera de turno responde 409. |
| `GET pims/organizaciones` | Organizaciones, con la lista de **terceros sin DPA evaluado**. |
| `GET pims/renovaciones` | Contratos por vencer o renovar. |

El formato del expediente está en `pims-dpa-auditor/assets/esquema_salida.json`.

## 4. Base de datos: Gestitel (PIMS del docente)

El agente puede guardar sus expedientes en la base **Gestitel** (PostgreSQL), que es el PIMS del docente. Todo está en `bd/` (ver [bd/LEEME.md](bd/LEEME.md)):

- `gestitel_base_de_datos.sql`: script del docente.
- `agente7_terceros_dpa.sql`: extensión de este agente (6 tablas, 5 vistas y las funciones `agente7_guardar_auditoria` y `agente7_registrar_decision`).
- `roles_agente7.sql`: rol `agente7`, que lee todo el PIMS y escribe solo en sus tablas, y rol `agente7_lectura`.
- `instalar_bd.ps1`: instala todo en orden. Necesita PostgreSQL 17.6+ o 16.10+.

**En este repositorio la base está apagada** (`"activo": false` en `datos/config_bd.json`): el agente guarda sus resultados solo en archivos (`datos/registro/`). Para activarla, después de instalar la base, ejecutar `python n8n\configurar_bd.py`.

Si el sistema común usa Gestitel, los scripts de `bd/` pueden servir de modelo para los demás grupos: Gestitel ya tiene tablas para cada agente (`core_arcorequest` para DSAR, `core_incident` para incidentes, `core_asset` para inventario, `core_annexacontrol` para controles, `core_training` para formación, `core_audit` para evidencia, `core_riskevaluation` para riesgos).

### 4.1 En el sistema multiagente (rama `grupo5-terceros-dpa`)

- **No se crean tablas en la base del docente.** Las auditorías se guardan en archivos (`datos/registro/`), como en la v2.0, y se descargan desde la página de G5 (informe `.md`, expediente `.json`, listado `.csv`). La extensión de §4 se activa solo con `G5_BD_EXTENSION=true`.
- **Contexto desde la base (solo lectura).** Al auditar se elige la fuente del contexto de la organización: `perfil` (el perfil de siempre), `bd` (tablas del script del docente: procesos, activos de datos, operaciones con datos personales, evaluaciones de impacto, riesgos, aplicabilidad del Anexo A y documentos) o `ambos`. La consulta usa el rol `agente_g5_lectura`, que no puede escribir. Se controla con `contexto_bd.activo` en `datos/config_bd.json` y queda registrada en `_registro.contexto` del expediente (fuente, esquema, filas por tabla y hash SHA-256 del contexto). Si la base no responde, la auditoría sigue con el perfil y lo advierte.
- **Corrección del JSON forzada.** Con proveedores tipo OpenAI (Gemini por el gateway), la segunda llamada (corrección) pide `response_format: json_object`, así el modelo devuelve un objeto JSON válido. `formato_correccion: "ninguno"` lo desactiva.
- **Página en la plataforma:** `frontend/pages/terceros.js` (Auditar con archivo y contexto, Expedientes con descargas, Organización y perfil, Renovaciones, Chat). Las decisiones humanas (DPO → Legal y validar el perfil) están en «Revisión humana».

## 5. Relación con otros agentes

| Agente | Relación | Estado |
|---|---|---|
| Grupo 3 · Derechos DSAR | Envía un handoff `to_agent: "terceros"` con la acción `notificar_destinatarios` cuando se aprueba una rectificación, supresión u oposición. | **No implementado aquí todavía.** Este agente no recibe handoffs. |
| Grupo 6 · Inventario de datos | `GET pims/organizaciones` devuelve los terceros que tratan datos y no tienen DPA evaluado. | Disponible. |
| Grupo 7 · Controles/SoA | Los 26 controles evaluados quedan ligados a `core_annexacontrol` en Gestitel. | Disponible si la base está activa. |
| Grupo 4 · Evidencia | Cada expediente guarda el hash SHA-256 del contrato evaluado. | Disponible en el JSON del expediente. |

## 6. Reglas que la integración no debe romper

1. **El número lo pone el código, no el modelo.** El modelo solo califica cada control; puntaje, dictamen y alertas los calcula `n8n/lib/calcular.js` (idéntico a `pims-dpa-auditor/scripts/calcular_resultado.py`).
2. **Ninguna aprobación automática.** Todo expediente nace *Pendiente DPO* y necesita la decisión del DPO y después la de Legal. `POST pims/aprobar` no debe exponerse como herramienta de un modelo.
3. **El texto del contrato no es confiable.** Si trae instrucciones, se reportan como alerta y no se obedecen.

## 7. Pendiente

- Recibir los handoffs del Grupo 3 (§5).
- Con la base activa, Renovaciones, Consultas y Chat todavía leen de los archivos, no de Gestitel.
- El caso UNSA laboratorio clínico da 44 en `esperado_unsa_02_laboratorio_clinico.json` y 46 en README y PROYECTO; falta confirmar cuál es el correcto.
