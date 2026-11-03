# Evaluación de severidad — INC-20260930-correo-equivocado-colegio

- **Insumo:** `salidas/INC-20260930-correo-equivocado-colegio/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB (ver `knowledge/metodologia-severidad.md`)

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 3 | Dato más delicado afectado: datos **financieros** (estado de deuda de la pensión y monto adeudado del apoderado). |
| Ajuste de contexto | +1 | Los titulares principales son **420 menores de edad**. Además, el conjunto (nombre + DNI + notas + deuda familiar) permite perfilar y estigmatizar al alumno dentro de la comunidad escolar. |
| **DPC final** | **4** | 3 + 1 (tope 4). |
| **EI** | **1** | Identificación directa: nombre completo + DNI del alumno, nombre y celular del apoderado. |
| CB — confidencialidad | +0,25 | Expuesto a un número conocido de destinatarios no autorizados (una empresa). No hay evidencia de publicación, pero tampoco confirmación escrita de eliminación. |
| CB — integridad | 0 | No hay indicios de alteración. |
| CB — disponibilidad | 0 | El colegio conserva el archivo original (inferencia razonable: lo envió desde su cuenta). |
| CB — intención maliciosa | 0 | Error humano; no se reporta mala fe. |
| **CB total** | **0,25** | |

**SE = 4 × 1 + 0,25 = 4,25 → Severidad Muy alta**

> Sensibilidad del cálculo: aunque se retirara el ajuste por menores (DPC = 3), SE = 3 × 1 + 0,25 = 3,25 → Alta. La conclusión de que hay perjuicio evidente probable no cambia.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Estigmatización, burla o discriminación del alumno por la deuda familiar o por sus notas | Media | La empresa de fotos tiene contacto directo con la comunidad escolar (promoción); la información puede circular. |
| Daño a la reputación y la privacidad del apoderado (situación económica expuesta) | Media | El estado de deuda y el monto quedan ligados a nombre y celular. |
| Fraude o engaños dirigidos a los apoderados (llamadas o mensajes que fingen ser del colegio para cobrar la pensión adeudada) | Media | Con el celular, el nombre del alumno, el grado y el monto exacto adeudado se pueden armar engaños muy creíbles. |
| Presión o extorsión a familias en deuda | Baja | Requiere mala fe del receptor; hoy no hay indicios. |
| Suplantación de identidad del menor usando el DNI | Baja | El DNI junto con el nombre facilita trámites fraudulentos, aunque con un menor el uso inmediato es limitado. |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Duda** | El reglamento considera sensibles los "ingresos económicos"; la deuda de la pensión es un dato financiero muy cercano, pero falta confirmar si la ANPD lo trata como sensible `[VERIFICAR]`. |
| | Grandes volúmenes (cantidad o tipo) | **Duda / probable** | 420 registros con 6 o más campos cada uno, combinando datos académicos y financieros. No hay umbral oficial `[VERIFICAR lineamientos ANPD]`. |
| | Gran número de personas | **Duda** | 420 alumnos más sus apoderados (hasta ~840 personas, estimado). No hay umbral oficial `[VERIFICAR lineamientos ANPD]`. |
| | Perjuicio evidente a derechos o libertades | **Sí (probable)** | SE = 4,25 (≥ 3, criterio de apoyo de la metodología); son menores; la deuda y las notas quedaron expuestas ante un tercero vinculado a la comunidad escolar. |
| **Resultado ANPD** | | **Notificar (obligación probable)** | Basta un supuesto. Además, en las dudas restantes la regla es recomendar notificar. |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí: comunicar** | Hay perjuicio evidente probable. No aplica la excepción del art. 34.4: el incidente **no** está superado totalmente, porque no existe confirmación escrita de eliminación. Se comunica a los apoderados, que también representan a los alumnos menores. |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Sí** | El incidente ocurrió mediante correo electrónico. |
| Documentar (art. 35) | Siempre | **Sí** | Ver `04-respuesta-y-cierre.md`, sección 5. |

> Aunque la empresa de fotos confirme por escrito la eliminación, la obligación de notificar a la ANPD **se mantiene** (art. 34.1: "aun cuando [...] haya sido subsanado o resuelto internamente"). Esa confirmación solo podría servir para reevaluar la comunicación a los titulares; aun así, con SE Muy alta se recomienda comunicar.

## 4. Plazos
- **Toma de conocimiento:** 2026-09-30, 15:30
- **Hora límite (48 h):** **2026-10-02, 15:30**. Tiempo restante: 47 h 10 min al momento del reporte (30/09 16:20); 39 h 30 min al inicio del 01/10/2026. Hay que recalcularlo con la hora real de aprobación. **Aún no vence.**
- La comunicación a los titulares tiene el mismo plazo de 48 h (art. 34.3).

## 5. Nota aparte: impacto para la organización
No notificar cuando corresponde es una **infracción grave** (art. 133 num. 12). La multa se gradúa según el art. 39 de la Ley 29733 y los arts. 123 y 124 del reglamento `[VERIFICAR rango en UIT]`. También hay riesgo reputacional ante las familias y posible tensión en la relación con la empresa de fotos. Nada de esto modifica la severidad para los titulares.

## 6. Supuestos e información pendiente
- Se supone que el archivo no estaba cifrado ni protegido con contraseña (si lo estaba y la clave no se envió, recalcular EI = 0,25 y CB conf. = 0).
- Se supone un solo destinatario externo (confirmar CC/CCO).
- Número real de apoderados distintos y de apoderados en deuda: NO INDICADO.
- Confirmación escrita de la empresa de fotos: pendiente.

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
