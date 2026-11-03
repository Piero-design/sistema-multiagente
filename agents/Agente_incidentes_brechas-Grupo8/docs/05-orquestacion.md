# Etapa 5 — Orquestación y automatización

**Objetivo:** coordinar skills, agente y flujos.

## Niveles de orquestación

| Nivel | Mecanismo | Qué automatiza |
|---|---|---|
| 1. Skill individual | Una frase del usuario activa el skill | Una fase (ej. solo la notificación) |
| 2. Agente | `agente-incidentes-brechas` decide y encadena los skills | El ciclo completo según el tipo de incidente |
| 3. Comando | `/gestionar-incidente <reporte>` | Lanza el agente en un solo paso |

## Reglas de enrutamiento

| Resultado del triaje | Secuencia |
|---|---|
| Evento sin incidente | Ficha → informe breve → cierre |
| Incidente sin datos personales | Ficha → respuesta y cierre (sin obligaciones de la Ley 29733) |
| Brecha, se cumple el art. 34.1 | Ficha → severidad → **notificación** → respuesta y cierre → informe |
| Brecha, no se cumple el art. 34.1 | Ficha → severidad → documentar (art. 35) → respuesta y cierre → informe |
| Falta la hora de conocimiento | Una sola pregunta; si no hay respuesta, se continúa con la alerta como pendiente crítico |

## Traspaso de datos entre skills
Los skills se comunican mediante **archivos** en la carpeta del incidente:

```
salidas/INC-20261011-ransomware-sra/
├── 00-informe.md                 ◄── agente (resumen de todo)
├── 01-ficha-incidente.md         ◄── triaje
├── 02-evaluacion-severidad.md    ◄── severidad (lee 01)
├── 03-notificacion-anpd.md       ◄── notificación (lee 01 y 02)
├── 03-comunicacion-titulares.md
├── 03-aviso-cnsd.md
└── 04-respuesta-y-cierre.md      ◄── respuesta (lee todo)
```

Ventajas: la carpeta **es** el registro que exige el art. 35, cada paso es auditable, un humano puede corregir la ficha antes de que la use la evaluación y el flujo se puede retomar a medias (ej. la notificación complementaria).

## Puntos de control humano
1. **Tras el triaje:** confirmar los hechos y la hora de conocimiento.
2. **Tras la severidad:** decidir si se notifica.
3. **Antes de enviar:** aprobar los borradores de notificación y comunicación.
4. **Al cierre:** aprobar el informe de lecciones aprendidas.

## Automatizaciones futuras (fuera del alcance actual)
- Recibir reportes desde un buzón o formulario y abrir la ficha automáticamente.
- Alertas cuando falten 12 h para la hora límite.
- Conexión con el SIEM o el sistema de tickets para importar evidencia.
- Tablero de incidentes abiertos y su estado.
