# Guía Grupo 6 — Agente de Inventario de Datos (fuera de alcance en esta ronda)

Tiempo sugerido: **1–2 min** (solo mencionarlo con claridad).

## Estado
**No se integró** en esta entrega, por decisión del alcance. Su ruta `/agentes/inventario` y su tarjeta en el panel existen y muestran el estado "fuera de alcance" con su responsabilidad. No se inventa ningún dato de inventario.

## Qué entregó el grupo (real)
- Un archivo único `index.html` («PII Privacy Assistant») que corre en el navegador, **basado en reglas de coincidencia por alias; no es un modelo de IA**.
- Permite pegar o subir TXT, MD, CSV, JSON o SQL; genera un inventario de datos personales con evidencia y SHA-256, campos editables y exportación CSV/JSON; usa `localStorage` opcional.
- `originales/` conserva el prototipo HTML y el informe PDF recibidos (intactos).
- Su README indica que **no está conectado** al orquestador ni a la base compartida.
- No tiene servidor, `SKILL.md` ni LLM; la skill «PII Inventory Analyzer» existe solo como prosa en el PDF.

## Qué falta para integrarlo
1. Un adaptador que ejecute su analizador original sin LLM (por ejemplo en un contenedor con un navegador sin cabeza o extrayendo su lógica sin modificarla).
2. Opcionalmente, escritura en `core_asset`, `core_process` y `core_personaldataoperation` de Gestitel mediante un rol propio.
3. Su relación con otros agentes: G3 le enviaría `confirmar_cobertura`, G5 le serviría el listado de terceros, G8 consultaría activos y categorías de datos afectados.

## Guion breve
"Nuestro agente es una herramienta del lado del cliente, basada en reglas. En esta ronda no se integró a la plataforma; su responsabilidad es el inventario de datos y su integración es el siguiente paso."

## Preguntas probables
- *¿Por qué no está?* Alcance acordado para esta entrega; su entrega no tiene backend ni modelo.
- *¿Sigue funcionando por su cuenta?* Sí, abriendo `index.html`; no se modificó.
