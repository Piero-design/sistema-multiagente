# Ficha de incidente — INC-20260930-correo-equivocado-colegio

> **Caso ficticio de prueba (PR-10).** El reporte no trae datos personales reales de los afectados (solo categorías y cantidades); se trabaja únicamente con categorías y cantidades. El nombre del archivo se cita porque identifica el activo, no a personas.

- **Organización (responsable del tratamiento):** Colegio Los Andes (ficticio) — RUC: NO INDICADO
- **Reportado por:** Secretaria académica (personal del propio colegio) — ¿Es encargado del tratamiento? **No.** La obligación de notificar recae en el colegio como responsable (art. 34.1). La empresa de fotos es **destinataria no autorizada** de este archivo; su relación contractual con el colegio (¿encargada para otro tratamiento?) es NO INDICADA.
- **Canal de reporte:** Reporte escrito de la secretaria académica (destinatario interno del reporte: NO INDICADO)
- **Fecha/hora de esta ficha:** 2026-10-01 23:25 (-05:00), modo no interactivo

## 1. Línea de tiempo

| Hito | Fecha y hora (-05:00) | Fuente / certeza |
|---|---|---|
| Ocurrencia del incidente (envío del correo al destinatario equivocado) | 2026-09-29, 17:05 | Hecho (reporte) |
| **Toma de conocimiento** (inicia el plazo) | **2026-09-30, 15:30** | Hecho (reporte): la contadora avisa que no recibió el archivo y la secretaria advierte el error |
| Llamada a la empresa de fotos | 2026-09-30, entre 15:30 y 16:20 (inferencia) | Hora exacta NO INDICADA |
| Reporte al responsable | 2026-09-30, 16:20 | Hecho (reporte) |
| **Hora límite de notificación (48 h, art. 34.1)** | **2026-10-02, 15:30** | Calculada (lectura más temprana) |
| Tiempo transcurrido / restante al 2026-10-01 23:25 | Transcurrido 31 h 55 min — **restan 16 h 05 min** | Calculado |

**Base de cálculo del reloj** (criterio de `knowledge/marco-normativo-peru.md`, "¿Desde cuándo corren las 48 horas?"):
- **Lectura adoptada (más temprana):** 2026-09-30 15:30, primer momento en que una persona del colegio (la secretaria) supo con certeza razonable del incidente → límite **2026-10-02 15:30**.
- **Referencia (más tardía):** 2026-09-30 16:20, hora del reporte formal → límite 2026-10-02 16:20. No se usa para planificar.
- **Riesgo de lectura más estricta (no adoptada):** si se sostuviera que el colegio "conoció" el hecho al enviar el correo (2026-09-29 17:05), el plazo habría vencido el 2026-10-01 17:05 (hace 6 h 20 min). El reporte indica que el error no se advirtió hasta el día siguiente; conviene **conservar el sustento** (mensaje o testimonio de la contadora con hora) por si la ANPD cuestiona la fecha `[VERIFICAR con asesoría legal]`.

## 2. Descripción de lo ocurrido
El 2026-09-29 a las 17:05, la secretaria académica envió desde su cuenta de correo institucional el archivo `notas_y_pensiones_2026.xlsx` a la empresa que hace las fotos de promoción, en lugar de a la contadora. El archivo contiene datos de 420 alumnos de primaria y secundaria (identificación, DNI, grado, notas del bimestre) y de sus apoderados (nombre, celular, situación de pago de la pensión y monto adeudado). El error se advirtió el 2026-09-30 a las 15:30. La secretaria llamó a la empresa de fotos; quien contestó dijo que "seguro lo borran", **sin confirmación escrita**. No consta si el archivo tenía contraseña o cifrado (se presume que no, inferencia), ni si fue abierto, descargado o reenviado por el destinatario.

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☑ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"): hubo vulneración de la confidencialidad (el archivo salió del colegio hacia un tercero no autorizado) que produjo una **"comunicación o exposición no autorizada"** de datos personales de alumnos y apoderados. La afirmación verbal de que "seguro lo borran" no elimina la brecha: la exposición ya ocurrió.

## 4. Clasificación
- **Tipo:** ☑ Confidencialidad ☐ Integridad ☐ Disponibilidad (el colegio conserva el original)
- **Categoría:** **FUG** — Fuga o divulgación accidental (correo al destinatario equivocado)
- **Entorno digital:** **Sí** (correo electrónico institucional) → notificación adicional al CNSD (art. 34.5): **Sí, probable**
- **Prioridad:** **P2 Alta** — brecha confirmada con datos personales de menores y datos financieros; reloj de 48 h corriendo con menos de 17 h restantes. No es P1 porque no hay ataque en curso ni publicación en Internet conocida.

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Nombres y apellidos, DNI, grado | No | Alumnos de primaria y secundaria | **Sí** | 420 | Hecho |
| Notas del bimestre | No (datos académicos) | Alumnos | **Sí** | 420 | Hecho |
| Nombre y celular del apoderado | No | Apoderados | No | Hasta 420 (menos si hay hermanos) | Estimación |
| Situación de pago de la pensión (al día / en deuda) y monto adeudado | **Duda** — dato financiero (deuda); podría vincularse a "ingresos económicos", sensible en la Ley 29733 `[VERIFICAR]` | Apoderados (y, por asociación, alumnos) | Vinculado a menores | Hasta 420 familias; n.° en deuda NO INDICADO | Hecho (categoría) / NO INDICADO (cantidad) |

**Total estimado:** hasta ~840 titulares (420 alumnos, hecho; hasta 420 apoderados, estimación).

## 6. Sistemas, activos y terceros involucrados
- Cuenta de correo institucional de la secretaria académica (plataforma de correo NO INDICADA).
- Archivo `notas_y_pensiones_2026.xlsx` (una hoja por sección).
- Tercero receptor no autorizado: empresa de fotos de promoción (razón social, contacto y relación contractual NO INDICADOS).
- Destinataria prevista: contadora (¿interna o externa/encargada?: NO INDICADO).

## 7. Medidas ya adoptadas (según el reporte)
- Llamada telefónica a la empresa de fotos; respuesta verbal "seguro lo borran". **Sin constancia escrita** ni identificación de la persona que atendió.
- Reporte interno el 2026-09-30 a las 16:20.
- Ninguna otra medida consta. Lo hecho entre 2026-09-30 16:20 y ahora: NO INDICADO.

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | Enviar a la empresa de fotos un **requerimiento escrito** (correo formal de la dirección u Oficial de Datos Personales): no abrir, no reenviar ni usar; eliminar el correo y el adjunto de bandeja, papelera, descargas, equipos y respaldos; **confirmar por escrito** indicando quién lo recibió, si lo abrió o reenvió y la fecha de eliminación | Contener | Dirección / Oficial de Datos Personales |
| 2 | **Preservar evidencia** antes de cualquier limpieza: exportar el correo enviado con cabeceras completas (.eml), no borrarlo de "Enviados"; solicitar a TI el registro de seguimiento del mensaje del servidor de correo; dejar constancia escrita de la llamada (hora, interlocutor, lo dicho) y del aviso de la contadora con su hora | Preservar evidencia | Secretaria académica + TI |
| 3 | Escalar ya al Oficial de Datos Personales y a la dirección para **decidir la notificación a la ANPD, la comunicación a apoderados y el aviso al CNSD antes de 2026-10-02 15:30** | Informar | Secretaria / responsable de seguridad |
| 4 | Si la plataforma de correo permite revocar o retirar el mensaje, intentarlo dejando registro (rara vez funciona con dominios externos; no sustituye la acción 1) | Contener | TI |
| 5 | Remitir a la contadora solo lo que necesita (datos de pensiones, no notas), verificando el destinatario y protegiendo el archivo con contraseña enviada por canal separado | Contener / minimizar | Secretaria académica |

## 9. Preguntas pendientes (modo no interactivo: no se preguntan, quedan como PENDIENTE)
1. **PENDIENTE:** ¿Qué se hizo entre el reporte (2026-09-30 16:20) y ahora? ¿Ya hubo comunicación escrita con la empresa de fotos?
2. **PENDIENTE:** Confirmación escrita de eliminación y no reenvío por la empresa de fotos; ¿quién recibió el correo (buzón personal o compartido)?
3. **PENDIENTE:** ¿El archivo tenía contraseña o cifrado?
4. **PENDIENTE:** Número real de apoderados distintos y de familias marcadas "en deuda".
5. **PENDIENTE:** Nombre y contacto del Oficial de Datos Personales o punto de contacto (art. 34.2 num. 2); RUC y banco de datos inscrito.
6. **PENDIENTE:** Relación contractual con la empresa de fotos y con la contadora (¿encargados del tratamiento?).
7. **PENDIENTE (legal):** ¿El monto adeudado de pensión se califica como dato sensible ("ingresos económicos")? `[VERIFICAR]`

## 10. Siguiente paso
☐ Cerrar como evento ☑ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
