# Ficha de incidente — INC-20260929-ransomware-clinica

> Caso ficticio de prueba (`examples/entradas/caso-01-ransomware-clinica.md`). La entrada no trae datos personales reales de pacientes: se trabaja solo con categorías y cantidades.

- **Organización (responsable del tratamiento):** Clínica San Gabriel S.A.C. (Arequipa). RUC: NO INDICADO
- **Reportado por:** Jefe de TI (área interna de la clínica). ¿Es encargado del tratamiento? **No.** Es personal del propio responsable, así que la obligación de notificar (art. 34) recae directamente en la clínica. El art. 36 no aplica.
- **Canal de reporte:** correo electrónico al Oficial de Datos Personales, 2026-09-29 08:40

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Alerta del antivirus por un adjunto de un correo de "factura pendiente" abierto en la PC de facturación | 2026-09-28 23:50 | Hecho (reporte). Nadie la revisó |
| Ocurrencia del cifrado | Entre 2026-09-28 23:50 y 2026-09-29 07:15 | **Estimado** (inferencia: la alerta sería el vector inicial; el cifrado se encontró a las 07:15) |
| Posible extracción de datos previa al cifrado | NO INDICADO | Desconocido ("no sabemos si sacaron datos") |
| **Toma de conocimiento** (inicia el plazo) | **2026-09-29 07:15** | Hecho: el personal de admisión encuentra el sistema inaccesible y la nota de rescate |
| Reporte al Oficial de Datos Personales | 2026-09-29 08:40 | Hecho (fecha del correo) |
| **Hora límite de notificación (48 h, art. 34.1)** | **2026-10-01 07:15** | Calculada: 07:15 del 29/09 + 48 h |
| Plazo del atacante (72 h) | Hacia el 2026-10-02 07:15 si se cuenta desde que se vio la nota | Inferencia: no se sabe cuándo apareció la nota |

> **Alerta sobre el reloj.** Este expediente se elabora el 2026-10-01 y el agente no tiene la hora actual. La hora límite es **hoy, 2026-10-01, a las 07:15**. Si ya pasó, el plazo está **VENCIDO** y la notificación tiene que explicar los motivos de la demora (art. 34.1).
> **Criterio conservador `[VERIFICAR con asesoría legal]`:** si se considera que la clínica "tomó conocimiento" con la alerta del antivirus (2026-09-28 23:50), el plazo habría vencido el **2026-09-30 23:50**. La alerta avisaba de un archivo malicioso, no de una vulneración de datos ya ocurrida, por eso se usa 07:15 como hora principal. Aun así, el hecho de que nadie revisara la alerta debe constar en el expediente.

## 2. Descripción de lo ocurrido
El 2026-09-29 a las 07:15, el personal de admisión no pudo abrir el sistema de historias clínicas. Seis computadoras mostraban una nota de rescate: los archivos fueron cifrados y el atacante pide 3 BTC en 72 h, con la amenaza de publicar "la base de pacientes" en un sitio web. El servidor de archivos y la base de datos de historias clínicas tienen la extensión `.lck`. La base contiene unos 18 000 pacientes. La noche anterior (23:50) el antivirus alertó sobre un adjunto de un correo de "factura pendiente" abierto en la PC de facturación, y nadie revisó la alerta. Se desconoce si hubo extracción de datos. El único respaldo completo tiene 3 semanas y está en un disco conectado permanentemente al servidor (no se sabe si se cifró). Por eso la atención de pacientes sigue en papel.
(Inferencia) El patrón coincide con un ransomware de **doble extorsión**: cifrado y amenaza de filtración, con acceso inicial por phishing.

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"): hubo una vulneración de la seguridad por código malicioso que **alteró** y dejó **inaccesibles** (pérdida de disponibilidad) los datos personales de los pacientes. Además, la amenaza de publicarlos indica una **posible comunicación o exposición no autorizada**. Se trata como confirmada hasta que se demuestre lo contrario, porque ante la duda se presume brecha.

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad (probable, no confirmada) ☒ Integridad (archivos cifrados por un tercero) ☒ Disponibilidad (confirmada)
- **Categoría:** `MAL`, código malicioso (ransomware). Vector probable `FRA` (phishing con adjunto), como inferencia.
- **Entorno digital:** Sí → notificación adicional al CNSD (art. 34.5): **Sí**
- **Prioridad:** **P1 Crítica**. Es ransomware, con datos sensibles (salud) y amenaza de publicación en Internet, y además afecta la atención de pacientes.

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Identificación: nombres, DNI, fecha de nacimiento | No | Pacientes | NO INDICADO (inferencia: es probable que haya pacientes menores) | ~18 000 | Cantidad estimada por TI ("alrededor de") |
| Contacto: teléfono, dirección | No | Pacientes | Ídem | ~18 000 | Ídem |
| Salud: diagnósticos, resultados de laboratorio | **Sí** (datos de salud, Ley 29733) | Pacientes | Ídem | ~18 000 | Ídem |
| Datos del seguro | Probable vínculo con la salud y la situación económica `[VERIFICAR contenido exacto]` | Pacientes (y quizá titulares de pólizas) | Ídem | ~18 000 | Ídem |
| Contenido del servidor de archivos | NO INDICADO (podría incluir datos de personal o de proveedores) | NO INDICADO | NO INDICADO | NO INDICADO | Por inventariar |

## 6. Sistemas, activos y terceros involucrados
- Servidor de base de datos del sistema de historias clínicas (cifrado).
- Servidor de archivos (cifrado).
- 6 PC con nota de rescate, entre ellas probablemente la PC de facturación (paciente cero, inferencia).
- Disco de respaldo conectado permanentemente al servidor (estado desconocido).
- Correo electrónico institucional (vector del phishing) y consola del antivirus.
- Terceros: proveedor del sistema de historias clínicas, aseguradoras y laboratorio, todos NO INDICADO.

## 7. Medidas ya adoptadas (según el reporte)
- El Jefe de TI desconectó el cable de red del servidor.
- Las PC afectadas siguen encendidas (bien para la evidencia en memoria; el reporte no dice si siguen en red).
- La atención de pacientes continúa en papel (contingencia).

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | Desconectar de la red (cable y Wi-Fi) las 6 PC y cualquier otro equipo con `.lck` o nota de rescate. **No apagarlas ni formatearlas** hasta capturar la memoria | Contener / preservar evidencia | Jefe de TI |
| 2 | Desconectar físicamente el disco de respaldo del servidor sin formatearlo ni abrirlo en un equipo de producción; rotularlo y custodiarlo | Contener (salvar el respaldo si aún está íntegro) / preservar evidencia | Jefe de TI |
| 3 | Restablecer, desde un equipo limpio, las contraseñas de las cuentas privilegiadas y de la usuaria o usuario de facturación; bloquear el remitente y el dominio del correo "factura pendiente" y buscarlo en los demás buzones | Contener | TI / administrador de correo |
| 4 | Exportar y conservar los logs del antivirus, del correo, del servidor, del sistema de historias clínicas y del firewall antes de que roten (art. 46.3) | Preservar evidencia / determinar si hubo extracción | TI |
| 5 | Convocar ya a la alta dirección, al Oficial de Datos Personales y a asesoría legal para aprobar la notificación a la ANPD y al CNSD, con la hora límite **2026-10-01 07:15**. No pagar el rescate ni contactar al atacante sin decisión de la alta dirección y asesoría especializada | Informar / decidir | Oficial de Datos Personales |

## 9. Preguntas pendientes
1. **Hora actual frente a la hora límite (2026-10-01 07:15):** ¿ya se notificó o venció el plazo? (pendiente crítica)
2. ¿Hubo extracción de datos? Revisar el tráfico saliente, los logs del firewall y del proxy, y si el atacante publicó una muestra.
3. ¿El disco de respaldo está cifrado o íntegro? ¿Hay otras copias (nube, cintas, el proveedor del sistema)?
4. Número exacto de titulares, si hay menores de edad y qué contiene el servidor de archivos.
5. Nombre y contacto del Oficial de Datos Personales; RUC; código de inscripción del banco de datos.
6. ¿El sistema de historias clínicas lo opera un proveedor (encargado)? ¿Hay acceso remoto de terceros?
7. ¿Cuándo apareció exactamente la nota de rescate? Sirve para fijar el plazo de 72 h del atacante.

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
