# 02 · Evaluación de severidad — INC-20261009-fuga-correo-admision

> BORRADOR para revisión del ODP. Metodología: ENISA 2013 + art. 34.1 (`knowledge/metodologia-severidad.md`).

## 1. Cálculo SE = DPC × EI + CB

| Componente | Valor | Justificación |
|---|---|---|
| **DPC** | **4** | Base 4: hay datos sensibles de salud (condición de discapacidad, `activos-y-datos.md:25`). El ajuste +1 por ~40 menores se aplicaría, pero el tope es 4. Además el conjunto (nombre, DNI, fecha de nacimiento, celular, correo, colegio) permite perfilar a una persona |
| **EI** | **1** | Identificación directa: nombres completos, DNI y correo personal |
| **CB** | **+0,25** | Confidencialidad: expuesto a un número conocido (612) de destinatarios no autorizados a ver los datos de los demás. Integridad y disponibilidad: 0. Intención maliciosa: 0 (error humano) |

**SE = 4 × 1 + 0,25 = 4,25 → MUY ALTA** (≥ 4: consecuencias graves o irreversibles).

Sensibilidad del resultado: aun sin el dato de discapacidad (DPC = 2 por menores), SE = 2,25 (Media), pero la sensibilidad está confirmada por el reporte y por el inventario. Si se confirma un reenvío fuera del grupo o publicación en prensa, CB sube a +0,5 y SE = 4,5.

## 2. Supuestos del art. 34.1 (basta uno)

| Supuesto | ¿Se cumple? | Base |
|---|---|---|
| Grandes volúmenes de datos, en cantidad o tipo | **Sí** | 8 tipos de datos de identificación y contacto, más la condición, por persona |
| Gran número de personas | **Dudoso → se trata como sí** | 612 titulares. No hay umbral oficial `[VERIFICAR lineamientos ANPD]` |
| **Datos sensibles** | **Sí** | Discapacidad (salud) |
| Perjuicio evidente a otros derechos o libertades | **Probable** | SE ≥ 3. Hay menores. Exposición de discapacidad que puede causar discriminación. Riesgo de suplantación y de acoso con DNI y celular. Amenaza de difusión en prensa |

## 3. Decisión

| Obligación | ¿Corresponde? | Fundamento |
|---|---|---|
| Notificar a la ANPD | **SÍ, tardía y con justificación de la demora** | Art. 34.1: datos sensibles confirmados. Plazo vencido el 2026-10-11 14:20 |
| Comunicar a los titulares (612) | **SÍ** | Art. 34.3: SE Muy alta, sensibles, menores. La excepción del art. 34.4 no aplica: no fue superado totalmente (no se puede garantizar la eliminación) |
| Notificar al CNSD | **SÍ** | Art. 34.5: entorno digital (correo) |
| Documentar | **SÍ** | Art. 35 |

Para los ~40 menores de edad, la comunicación debe considerar a sus padres o representantes `[VERIFICAR requisito legal aplicable]`.

## 4. Riesgos para los titulares
- Discriminación o estigmatización por revelar discapacidad frente a sus compañeros de promoción.
- Suplantación de identidad o fraude con DNI, fecha de nacimiento y celular.
- Contacto no deseado, acoso o phishing dirigido (se conoce escuela, colegio y correo).
- Riesgo agravado en los menores.
- Pérdida de control sobre los datos si se reenvían o llegan a la prensa.

## 5. Riesgo de cumplimiento
No notificar cuando corresponde es infracción grave (art. 133 num. 12). La demora ya existe, así que cada hora adicional empeora la posición. Quedan dos causas probables para la justificación: ausencia de procedimiento y de responsable de notificación (`documento-seguridad-extracto.md:5.3`) y el filtro de la OTI antes del ODP (l. 18). Debe declararse con honestidad, sin ocultarlo.
