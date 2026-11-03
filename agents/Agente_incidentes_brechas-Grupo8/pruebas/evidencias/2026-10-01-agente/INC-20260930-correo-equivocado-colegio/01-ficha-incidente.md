# Ficha de incidente — INC-20260930-correo-equivocado-colegio

> Caso ficticio de prueba (`examples/entradas/caso-02-correo-equivocado-colegio.md`). La entrada no trae datos personales reales de afectados: se trabaja solo con categorías y cantidades.

- **Organización (responsable del tratamiento):** Colegio Los Andes (RUC: NO INDICADO)
- **Reportado por:** Secretaria académica (personal del propio colegio) — ¿Es encargado del tratamiento? **No.** Es personal del responsable; la obligación de notificar recae en el colegio (art. 34.1). No aplica el art. 36.
- **Canal de reporte:** reporte escrito interno (medio exacto NO INDICADO)

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Ocurrencia del incidente (envío del correo) | 2026-09-29, 17:05 | Hecho (reportado) |
| **Toma de conocimiento** (inicia el plazo) | **2026-09-30, 15:30** | Hecho (reportado: la contadora avisa que no recibió el archivo) |
| Llamada a la empresa de fotos | 2026-09-30, entre 15:30 y 16:20 | Inferencia (hora exacta NO INDICADA) |
| Reporte al responsable (canal interno) | 2026-09-30, 16:20 | Hecho |
| **Hora límite de notificación (48 h, art. 34.1)** | **2026-10-02, 15:30** | Calculada (15:30 del 30/09 + 48 h) |

> Nota: el archivo estuvo en poder de un tercero no autorizado unas 22 h 25 min antes de que el colegio lo advirtiera (17:05 del 29/09 a 15:30 del 30/09).

## 2. Descripción de lo ocurrido
El 29/09/2026 a las 17:05, la secretaria académica envió desde su cuenta de correo institucional el archivo `notas_y_pensiones_2026.xlsx` a la empresa que hace las fotos de promoción, en lugar de a la contadora. El archivo contiene una hoja por sección con datos de 420 alumnos de primaria y secundaria y de sus apoderados, incluido si estos están al día o en deuda con la pensión y el monto adeudado. El error se detectó el 30/09 a las 15:30. La secretaria llamó a la empresa de fotos; la persona que contestó dijo que "seguro lo borran", pero **no hay confirmación escrita** de la eliminación. No se sabe si el archivo fue abierto, descargado, reenviado o copiado (NO INDICADO). No se indica que el archivo estuviera protegido con contraseña o cifrado (NO INDICADO; se presume que no, inferencia).

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"): hubo una **comunicación o exposición no autorizada** de datos personales a un tercero que no tenía por qué recibirlos (falla del control de envío de información). Los datos identifican directamente a personas (nombre y DNI), así que se trata de una brecha confirmada, no de una sospecha.

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad ☐ Integridad ☐ Disponibilidad (el colegio conserva el archivo original; inferencia)
- **Categoría:** `FUG`: fuga o divulgación accidental (correo enviado al destinatario equivocado)
- **Entorno digital:** **Sí** (correo electrónico institucional) → notificación adicional al CNSD (art. 34.5): **Sí**
- **Prioridad:** **P2 Alta**: brecha confirmada con datos personales de menores y datos financieros de sus apoderados, y el plazo de 48 h ya está corriendo. No es P1 porque no hay ataque en curso ni publicación en Internet que se conozca.

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Nombres y apellidos, DNI | No | Alumnos de primaria y secundaria | **Sí** | 420 | Hecho (reportado) |
| Grado / sección | No | Alumnos | **Sí** | 420 | Hecho |
| Notas del bimestre (rendimiento académico) | No (dato académico), pero delicado en el contexto | Alumnos | **Sí** | 420 | Hecho |
| Nombre y celular del apoderado | No | Apoderados (padres/tutores) | No | Hasta 420 (puede ser menor si hay hermanos) | Estimado (inferencia) |
| Estado de pago de la pensión (al día / en deuda) y **monto adeudado** | **Duda** `[VERIFICAR]`: es un dato financiero; queda por confirmar si cabe en "ingresos económicos" (dato sensible según la Ley 29733) | Apoderados (y de forma indirecta el alumno) | No (apoderado) / vinculado a un menor | Hasta 420; el número de apoderados en deuda es NO INDICADO | Hecho la categoría; estimado el número |

## 6. Sistemas, activos y terceros involucrados
- Cuenta de correo institucional de la secretaria académica (proveedor/plataforma de correo NO INDICADA).
- Archivo `notas_y_pensiones_2026.xlsx` (origen: NO INDICADO; posible exportación del sistema académico o del sistema de pensiones, inferencia).
- **Tercero receptor no autorizado:** empresa de fotos de promoción (razón social y dirección de correo receptora NO INDICADAS). Puede ser encargado del colegio para otro tratamiento (fotos), pero **no** para estos datos.
- Destinatario previsto: contadora (no se indica si es interna o externa; si es externa, sería encargada del tratamiento).

## 7. Medidas ya adoptadas (según el reporte)
- Llamada telefónica a la empresa de fotos para pedir la eliminación. Respuesta verbal: "seguro lo borran". **No hay constancia escrita.**

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | Enviar hoy a la empresa de fotos una **solicitud escrita** (correo y, si es posible, carta) para que elimine el archivo de la bandeja de entrada, la papelera, las descargas y cualquier copia; para que confirme **por escrito** que no lo abrió, reenvió, copió ni usó (o diga en qué medida lo hizo), y para que firme un compromiso de confidencialidad | Contener | Dirección del colegio / Oficial de Datos Personales |
| 2 | **Conservar** el correo enviado con sus cabeceras completas (no borrarlo de "Enviados") y exportar el registro de seguimiento de mensajes de la plataforma de correo | Preservar evidencia | Responsable de TI |
| 3 | Si la plataforma lo permite (solo dentro del mismo dominio), intentar la recuperación del mensaje. Si el adjunto se compartió como enlace, revocar el enlace | Contener | Responsable de TI |
| 4 | Registrar por escrito la llamada ya hecha: hora, nombre y cargo de quien atendió y lo que se dijo | Preservar evidencia / informar | Secretaria académica |
| 5 | Informar al Oficial de Datos Personales y a la dirección **ahora mismo** para decidir la notificación antes del **02/10/2026 15:30** | Informar | Secretaria académica / Dirección |

## 9. Preguntas pendientes
1. Nombre y datos de contacto del **Oficial de Datos Personales** o del punto de contacto (art. 34.2 num. 2). NO INDICADO.
2. ¿Confirma la empresa de fotos **por escrito** la eliminación? ¿Abrió, descargó o reenvió el archivo?
3. ¿A qué dirección exacta se envió (correo corporativo o personal)? ¿Había más destinatarios (CC/CCO)?
4. ¿El archivo tenía contraseña o cifrado?
5. ¿Cuántos apoderados distintos hay y cuántos figuran "en deuda"?
6. ¿La contadora es personal interno o un proveedor externo (encargado)? ¿Necesitaba las notas para su trabajo? (minimización)
7. RUC del colegio y banco(s) de datos inscritos que resultaron afectados.

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
