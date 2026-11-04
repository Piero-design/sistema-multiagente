# Guía Grupo 6 — Agente de Inventario de Datos

Tiempo sugerido: **2–3 min**. **Estado en la plataforma: no integrado en esta ronda**, aunque el grupo ya entregó una implementación propia. Hay que decirlo con claridad y no presentar a G6 como parte del flujo en vivo.

## Qué entregó el grupo (según su README y su contrato de integración)
- Un agente Python ejecutable con **API FastAPI** (puerto 8006 de ejemplo), **CLI** y **herramientas MCP** (servidor `inventario-agent`, seis herramientas: ejecutar, registrar activos, consultar, clasificar datos, mapear tratamientos y confirmar cobertura).
- **Motor de reglas locales, sin LLM**: calcula los resultados a partir de la entrada; no usa respuestas prefabricadas.
- **SQLite propia** (`inv6_assets`, `inv6_revisions`) con identificación estable de activos, registro idempotente e historial de revisiones.
- Skills de dominio: registrar activos, clasificar datos y mapear tratamientos. Panel de demostración (`agente.html`) y la herramienta original en `index.html`, que se conservan.
- **Receptor real del handoff de G3** (`confirmar_cobertura`): verifica el SHA-256 del sobre y dice qué sistemas están inventariados o pendientes. El grupo lo probó contra el generador real de handoffs de G3.
- Pruebas propias (16 según el grupo). **No las ejecuté yo**; no puedo afirmar su resultado.
- Reglas del agente: no conserva los valores originales de los datos, todo queda «pendiente de validación» y no emite aprobaciones.

## Por qué no está en la demo en vivo
En esta ronda se decidió no integrarlo. Su ruta `/agentes/inventario` en la plataforma sigue mostrando «fuera de alcance» y el handoff de G3 hacia inventario queda registrado como «sin receptor». **Ese texto de la plataforma está desactualizado respecto a lo que el grupo entregó.**

## Qué falta para integrarlo
1. Un adaptador y un contenedor, igual que los demás agentes (su API y su MCP ya están listos; no necesita LLM).
2. Conectar el handoff de G3 → G6 en el flujo existente de handoffs.
3. Opcional: escribir en Gestitel (`core_asset`, `core_process`, `core_personaldataoperation`) con un rol propio; hoy usa solo su SQLite.
4. Revisión humana autenticada de los activos: el propio grupo lo deja pendiente.

## Guion breve
"Nuestro agente inventaría los activos de datos personales y prepara el mapa de tratamientos con reglas, sin modelo, y puede confirmar la cobertura cuando el agente de derechos se lo pide. Está implementado con API, herramientas MCP y base propia; su conexión a la plataforma común es el siguiente paso."

## Preguntas probables
- *¿Por qué no está en la plataforma?* Alcance de esta ronda; la integración es corta porque ya expone API y MCP.
- *¿Usa un modelo?* No: son reglas locales.
- *¿Qué hace con los datos personales?* Guarda nombres de campos, ubicaciones y hashes, no los valores.
- *¿Y las pruebas?* Las reportó el grupo; no se ejecutaron en la integración.
