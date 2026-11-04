# Comunicación entre agentes

Qué agentes se relacionan y cómo. Ninguna conexión modifica el código de un agente: todas pasan por el orquestador (que transforma los datos en la frontera) o son consultas de solo lectura.

## 1. Relaciones entre agentes

```mermaid
flowchart LR
    G1["G1 · Formación"]
    G2["G2 · Riesgos"]
    G3["G3 · Derechos (DSAR)"]
    G4["G4 · Evidencia y auditoría"]
    G5["G5 · Terceros y DPA"]
    G6["G6 · Inventario de datos"]
    G7["G7 · Controles y SoA"]
    G8["G8 · Incidentes y brechas"]
    H(["Persona: DPO / Legal"])

    G8 -- "lecciones aprendidas<br/>(incidente_a_formacion)" --> G1
    G5 -- "resultados por control como evidencias<br/>(terceros_a_controles)" --> G7
    G6 -- "inventario como evidencia<br/>(inventario_a_auditoria)" --> G4
    G6 -- "sistema con sus campos y finalidad<br/>(inventario_a_riesgos)" --> G2
    G3 -- "sobre de evidencia" --> G4
    G3 -- "sobre de inventario" --> G6
    G3 -. "sobre de terceros: queda pendiente" .-> G5

    G8 -. "consulta de solo lectura" .-> G5
    G8 -. "consulta de solo lectura" .-> G6
    G8 -. "consulta de solo lectura" .-> G7

    H == "verifica identidad y decide casos" ==> G3
    H == "aprueba: primero DPO, luego Legal" ==> G5
    H == "aprueba o rechaza acciones propuestas" ==> G8
```

Línea continua = flujo orquestado (cada paso es una ejecución real del agente). Línea punteada = consulta de solo lectura o entrega que espera a una persona. Línea gruesa = decisión humana en `/revision`.

## 2. Quién participa en qué

| Flujo | Origen | Destino | Datos que viajan |
|---|---|---|---|
| `incidente_a_formacion` | G8 | G1 | Lecciones aprendidas del informe, sin datos personales |
| `terceros_a_controles` | G5 | G7 | Estado de cada control (Cumple → implementado, Parcial → parcial) |
| `inventario_a_auditoria` | G6 | G4 | Documento de evidencia con su SHA-256, sin valores de datos |
| `inventario_a_riesgos` | G6 | G2 | Nombres de campos, categorías, finalidad y titulares; nunca valores |
| `dsar_handoffs` | G3 | G4 / G6 / G5 | Sobres de handoff generados tras una decisión humana; el de G5 queda pendiente |
| Conectores de G8 | G8 | G5 / G6 / G7 | Consultas HTTP de solo lectura; las rutas que cambian estado están bloqueadas |

Los ocho agentes participan en al menos un flujo. G7 y G1 solo reciben; G2 solo recibe de G6; G8 y G3 son los que más envían.

## 3. Arquitectura que lo hace posible

```mermaid
flowchart TB
    U["Navegador<br/>(interfaz unificada)"] --> F["Frontend nginx"]
    F --> B["Backend FastAPI<br/>orquestador + adaptadores"]
    B --> A1["G1"] & A2["G2"] & A3["G3"] & A4["G4"] & A5["G5"] & A6["G6"] & A7["G7"] & A8["G8"]
    A1 & A2 & A3 & A4 & A5 & A6 & A7 & A8 --> GW["Gateway LLM<br/>clave y modelo por equipo"]
    GW --> P["Proveedor del modelo<br/>(Gemini, Ollama o simulado)"]
    B --> DB[("PostgreSQL Gestitel<br/>esquema orchestrator + bitácora")]
    A5 --> DB
    A2 --> Q[("Qdrant<br/>norma ISO/IEC 27701")]
```

- El **orquestador** registra cada ejecución, evento y handoff en PostgreSQL y deja una fila de metadatos (sin datos de entrada ni salida) en `demo.core_securitylog`.
- Todas las llamadas al modelo pasan por el **gateway**, que usa la clave de Gemini de cada equipo.
- Los demás agentes conservan su propio almacén (SQLite, archivos, n8n) y no se tocan.
