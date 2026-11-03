# 02 · Evaluación de severidad — INC-20261008-campus-virtual-proveedor

> BORRADOR para revisión del ODP. Metodología: ENISA 2013 (`knowledge/metodologia-severidad.md`). Severidad medida sobre los titulares.

## Reloj
Hora límite: **2026-10-13 17:55 (-05)** · Hora actual: 09:00 · **Restan 8 h 55 min**.

## Puntuación: SE = DPC × EI + CB

| Componente | Valor | Justificación |
|---|---|---|
| DPC | **3** | Base 2 (datos de comportamiento: actividad en aulas) +1 por contexto: relación de dependencia docente-estudiante, posibles menores `[VERIFICAR]`, y el conjunto (DNI + notas + mensajes) permite perfilar. No hay datos sensibles confirmados |
| EI | **1** | Identificación directa: nombre + DNI + correo institucional |
| CB confidencialidad | +0,5 | Posible descarga por destinatario desconocido |
| CB integridad | 0 | Sin indicios de alteración `[VERIFICAR]` |
| CB disponibilidad | 0 | El servicio no se reporta caído; el proveedor conserva copia `[VERIFICAR]` |
| CB intención maliciosa | +0,5 | Acceso no autorizado deliberado |
| **CB total** | **1** | |

**SE = 3 × 1 + 1 = 4 → MUY ALTA** (≥ 4).

Sensibilidad del resultado:
- Si se aplica DPC = 2 (sin ajuste): SE = 3 → **Alta**. La decisión legal no cambia.
- Si se confirman contraseñas en claro/débiles o datos sensibles en mensajes: sube (DPC 4 → SE 5).
- Si el proveedor demuestra que no hubo descarga o que la BD estaba cifrada con clave no comprometida: EI 0,25 y CB conf. 0 → SE ≈ 1,75 (Baja). Hoy **no hay esa evidencia**, por lo que no se puede aplicar.

## Decisión según art. 34 (`marco-normativo-peru.md`)

| Pregunta | Respuesta | Consecuencia |
|---|---|---|
| ¿Datos sensibles? | No confirmado (mensajes `[VERIFICAR]`) | — |
| ¿Grandes volúmenes / gran número de personas? | **Sí / probable**: ~22 000 titulares, y datos de identidad completos. No hay umbral oficial `[VERIFICAR lineamientos ANPD]` | **Notificar a la ANPD (34.1)** |
| ¿Perjuicio evidente a otros derechos? | **Probable**: SE ≥ 3 (criterio de apoyo); riesgo de suplantación, phishing y acceso a cuentas | **Comunicar a titulares (34.3)** |
| ¿Entorno digital? | Sí | **Notificar al CNSD (34.5)** |
| ¿Superado totalmente? | No; ni siquiera confirmado | La excepción del 34.4 no aplica |
| ¿Duda razonable? | Sí (alcance real desconocido) | Ante la duda: **notificar** |

### Resultado
- **Notificar a la ANPD: SÍ**, antes de **2026-10-13 17:55**. Si faltan datos (no se sabe qué se descargó), enviar con lo disponible y marcar como parcial; completar después. No esperar al proveedor.
- **Comunicar a los titulares: SÍ (recomendado)**, mensaje claro con medidas (cambiar clave, cuidado con phishing). Es obligatorio si se confirma perjuicio evidente; ante la duda, comunicar.
- **Aviso al CNSD: SÍ**.
- **Documentar (art. 35): SÍ**, siempre.

## Riesgos de la lectura
- Notificar tarde equivale a infracción grave (art. 133 num. 12) `[VERIFICAR rango de multa]`.
- La demora previa (proveedor avisó 3 días después) debe explicarse con el correo como sustento.
- La UNSA no puede delegar la obligación en el proveedor, aun si este notifica por su cuenta.

## Siguiente paso
Redactar borradores: `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`.
