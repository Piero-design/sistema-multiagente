# Ficha de incidente — INC-20260930-phishing-bloqueado

> Caso ficticio de prueba (caso de control). El reporte no contiene datos personales reales de terceros; se trabaja solo con categorías y cantidades.

- **Organización (responsable del tratamiento):** Municipalidad Distrital de Cayma (ficticia)
- **Reportado por:** Asistente de la Gerencia de Rentas (personal interno) — ¿Es encargado del tratamiento? **No**
- **Canal de reporte:** Reenvío del correo sospechoso a soporte (mesa de ayuda)

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Recepción del correo de phishing en los buzones | NO INDICADO (anterior a 2026-09-30 11:45) | NO INDICADO |
| Marcado como sospechoso por el filtro de correo | NO INDICADO (anterior a la revisión de soporte) | Hecho (según soporte), hora no indicada |
| **Toma de conocimiento** por la organización | 2026-09-30 11:45 (reporte de la asistente a soporte) | Hecho. Inferencia: el filtro pudo marcarlo antes, pero eso no se considera toma de conocimiento de un incidente |
| Respuesta y contención de soporte | 2026-09-30 12:10 | Hecho |
| **Hora límite de notificación (48 h, art. 34.1)** | **No aplica.** Solo como referencia: 2026-10-02 11:45 | Calculada. El plazo de 48 h solo corre si hay un incidente de seguridad de datos personales (ver sección 3) |

## 2. Descripción de lo ocurrido
- **Hecho:** Una asistente de la Gerencia de Rentas recibió un correo que suplantaba a un banco y pedía "validar la cuenta institucional" mediante un enlace. No hizo clic y lo reenvió a soporte, como indica la capacitación recibida.
- **Hecho:** Según soporte, el filtro de correo ya había marcado el mensaje como sospechoso. El registro del proxy no muestra accesos al dominio del enlace, por lo que **nadie hizo clic**.
- **Hecho:** Soporte bloqueó el dominio y eliminó el correo de los **37 buzones** que lo recibieron.
- **Inferencia:** El filtro marcó el mensaje pero no lo puso en cuarentena, porque llegó a 37 buzones. Es una oportunidad de mejora, no una vulneración.
- **Inferencia:** El proxy solo cubre el tráfico que pasa por la red institucional. No se sabe si alguien abrió el correo desde un dispositivo móvil o una red externa, ni si alguien **respondió** al correo con credenciales en lugar de hacer clic (ver preguntas pendientes).

## 3. Decisión de triaje
- **Resultado:** ☒ **Evento sin incidente** ☐ Incidente de seguridad (sin datos personales) ☐ Incidente de seguridad de datos personales (brecha)
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"; `knowledge/taxonomia-incidentes.md`, sección 3):
  - Primera pregunta del árbol: *¿hay indicios de que se vulneró un control de seguridad?* **No** con la información disponible. Es un intento de phishing reportado, no usado y bloqueado. La taxonomía lo da como ejemplo de evento sin incidente ("correo de phishing reportado y no abierto").
  - No hubo destrucción, pérdida, alteración ilícita ni comunicación o exposición no autorizada de datos personales. Por eso **no se configura** un incidente de seguridad de datos personales (art. III num. 16) y **no se activan** las obligaciones de los arts. 34 a 36.
  - Esta conclusión no se basa en lo que opina el reportante. Se apoya en una evidencia técnica (registro del proxy) contrastada con la definición legal. **Condición:** si la verificación pendiente (dispositivos fuera del proxy o respuestas al correo) muestra que alguien entregó credenciales, el caso debe **reabrirse** como incidente (categoría INT/FRA). En ese momento se evaluará si afectó datos personales y el plazo de 48 h empezará a contar desde esa nueva toma de conocimiento.

## 4. Clasificación
- **Tipo:** ☐ Confidencialidad ☐ Integridad ☐ Disponibilidad (ninguna dimensión afectada)
- **Categoría:** FRA — Fraude e ingeniería social (intento de phishing; no tuvo éxito)
- **Entorno digital:** Sí (correo electrónico) → notificación adicional al CNSD (art. 34.5): **No**, porque no hay incidente de seguridad de datos personales
- **Prioridad:** **P4 Baja** — evento sin impacto, contenido por soporte el mismo día; corresponde a un registro rutinario

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Ninguna afectada | — | — | — | 0 | Hecho (proxy sin accesos al dominio). Pendiente de verificar fuera del proxy |
| (Contexto) Direcciones de correo institucional de 37 destinatarios, ya conocidas por el atacante | No | Personal municipal | No | 37 | Hecho. No es exposición causada por la organización: el atacante ya tenía las direcciones |

## 6. Sistemas, activos y terceros involucrados
- Servicio de correo institucional y su filtro antiphishing
- Proxy web institucional (fuente de evidencia)
- 37 buzones institucionales
- Dominio malicioso externo (ya bloqueado)
- Tercero suplantado: un banco (sin nombre en el reporte)

## 7. Medidas ya adoptadas (según el reporte)
- La destinataria no hizo clic y reportó el correo (control 6.8 de ISO/IEC 27002 funcionando).
- El filtro marcó el correo como sospechoso.
- Soporte revisó el registro del proxy: no hubo accesos al dominio.
- Se bloqueó el dominio.
- Se eliminó el correo de los 37 buzones.

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo (contener / preservar evidencia / informar) | Responsable sugerido |
|---|---|---|---|
| 1 | Guardar una copia del correo original **con cabeceras** y los indicadores (dominio, URL, remitente, IP de origen) antes de que roten los registros | Preservar evidencia | Soporte / TI |
| 2 | Exportar y conservar el extracto del registro del proxy y del registro de entrega del correo (incluye la lista de 37 buzones) | Preservar evidencia | Soporte / TI |
| 3 | Revisar la bandeja de enviados de los 37 buzones (o las trazas del servidor) por si hubo respuestas al remitente, y los inicios de sesión anómalos de esas cuentas | Confirmar que no hubo compromiso | TI |
| 4 | Verificar si hubo accesos al dominio desde dispositivos móviles o redes que no pasan por el proxy (DNS, MDM) `[VERIFICAR alcance]` | Confirmar que no hubo compromiso | TI |
| 5 | Enviar un aviso breve al personal: "se recibió este phishing; si hiciste clic o respondiste, avisa a soporte". Reconocer el buen reporte de la asistente | Informar / concienciación | Responsable de seguridad |

## 9. Preguntas pendientes
1. ¿A qué hora llegó el correo a los buzones y a qué hora lo marcó el filtro? (para completar la línea de tiempo)
2. ¿Alguno de los 37 destinatarios **respondió** al correo o abrió el enlace desde un dispositivo o red fuera del proxy?
3. ¿Por qué el filtro marcó el correo pero lo entregó igual (etiqueta vs. cuarentena)? ¿Es la configuración prevista?
4. ¿Hay inicios de sesión anómalos en las cuentas de los 37 destinatarios después de recibir el correo?

## 10. Siguiente paso
☒ Cerrar como evento (con las verificaciones de la sección 8, puntos 3 y 4, como condición de cierre) ☐ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
