# Etapa 2 — Creación de skills

**Objetivo:** definir la activación, la estructura y los pasos de cada skill.

## Anatomía de un skill

```
.claude/skills/<nombre>/
├── SKILL.md           # frontmatter + instrucciones
└── plantilla-*.md     # formato de salida
```

`SKILL.md` tiene dos partes:

1. **Frontmatter YAML**
   - `name`: identificador (igual al nombre de la carpeta).
   - `description`: **qué hace y cuándo activarlo**. Claude la lee para decidir si usa el skill, por eso incluye las frases con las que alguien reportaría un incidente ("se perdió una laptop", "¿hay que notificar?").
2. **Cuerpo:** sustento normativo, cuándo se activa, entradas, pasos numerados, reglas y salida.

## Activación

| Skill | Se activa cuando... | Entrada | Salida |
|---|---|---|---|
| `brecha-triaje` | alguien reporta que "pasó algo" con información o sistemas | reporte libre | `salidas/<ID>/01-ficha-incidente.md` |
| `brecha-evaluacion-severidad` | preguntan qué tan grave es o si hay que notificar | ficha | `02-evaluacion-severidad.md` |
| `brecha-notificacion` | piden notificar o avisar a los afectados | ficha + evaluación | `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md` |
| `brecha-respuesta-cierre` | piden contener, un plan de respuesta, lecciones aprendidas o cerrar | expediente | `04-respuesta-y-cierre.md` |

## Pasos de cada skill

### brecha-triaje
1. Registrar el ID → 2. Línea de tiempo y **hora límite de 48 h** → 3. ¿Evento, incidente o brecha? → 4. Clasificar (CID y categoría) → 5. Datos y titulares afectados → 6. Rol del reportante (encargado, art. 36) → 7. ¿Entorno digital? → 8. Prioridad → 9. Acciones inmediatas que no destruyan evidencia → 10. Entregar.

### brecha-evaluacion-severidad
1. Leer la ficha → 2. DPC → 3. EI → 4. CB → 5. SE y nivel → 6. Consecuencias para los titulares → 7. Decisión legal supuesto por supuesto (art. 34.1, 34.3, 34.4, 34.5, 35) → 8. Plazos → 9. Entregar.

### brecha-notificacion
1. Confirmar destinatarios → 2. Notificación a la ANPD (contenido mínimo del art. 34.2) → 3. Comunicación a los titulares en lenguaje claro → 4. Aviso al CNSD → 5. Verificación del contenido → 6. Entregar.

### brecha-respuesta-cierre
1. Contención → 2. Preservación de evidencia (ISO/IEC 27037) → 3. Erradicación → 4. Recuperación → 5. Causa raíz (5 porqués) → 6. Lecciones aprendidas y controles ISO/IEC 27002 → 7. Registro del art. 35 → 8. Criterios de cierre → 9. Entregar.

## Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Un skill por fase de ISO/IEC 27035 | Da sustento normativo a la división y permite usar cada fase por separado |
| Criterios en `knowledge/`, no dentro del `SKILL.md` | Se actualizan en un solo lugar; los 4 skills comparten la normativa |
| Citas literales del D.S. 016-2024-JUS | Evitan que el modelo invente plazos o supuestos |
| Fórmula de severidad explícita con justificación por factor | La evaluación es reproducible y auditable |
| "Ante la duda, notificar" | La omisión es infracción grave (art. 133 num. 12); notificar de más tiene menor costo |
| Marcadores `NO INDICADO` y `[VERIFICAR]` | Separan lo que se sabe de lo que falta confirmar |
| Carpeta por incidente (`salidas/<ID>/`) | El expediente completo queda junto: es el registro del art. 35 |
