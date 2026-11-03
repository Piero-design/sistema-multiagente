# Respuesta y cierre — INC-20260929-laptop-robada-cooperativa

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md` (carpeta `pruebas/evidencias/2026-10-01-agente/INC-20260929-laptop-robada-cooperativa/`)
- **Fecha del borrador:** 2026-10-01
- **Marco:** ISO/IEC 27035-1:2023 (fases Responder y Aprender lecciones), ISO/IEC 27035-3:2020, ISO/IEC 27002:2022 (5.26, 5.27, 5.28), ISO/IEC 27037:2012, NIST SP 800-61 Rev. 3 (RS, RC), ISO/IEC 27701:2019 (6.13.1.5), D.S. 016-2024-JUS (arts. 34, 35, 46, 48).
- **Convención:** **(hecho)** = consta en los insumos; **(inferencia)** = deducción del agente; **NO INDICADO** = no consta.

> **Por qué el estado es "En contención" y no "Listo para cierre":** el pedido es un informe post-incidente, pero los insumos no registran que se haya ejecutado ninguna medida técnica (cierre de sesiones, cambio de credenciales, bloqueo o borrado remoto), ni el resultado de la verificación de BitLocker y de la revisión del correo (01, sección 7; 03-notificación, secciones F e I). Las lecciones aprendidas y los controles propuestos se entregan ya, pero el **cierre formal** queda condicionado a los criterios de la sección 6.

---

## 1. Plan de respuesta

### 1.1 Contención

Categoría **FIS** (robo físico) con riesgo secundario **INT** (acceso al correo por la sesión abierta). Orden recomendado: **primero preservar (1.2), luego contener**; las acciones C2–C5 solo después de E1–E3.

| # | Acción | Plazo (inmediata / corto / largo) | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Obtener la **constancia de la denuncia policial** y una declaración escrita y firmada del analista (hora y lugar del robo, estado del equipo: apagado / suspendido / bloqueado, archivos y credenciales en la laptop) | Inmediata | Jefe del área + Oficial de Datos Personales | **No** (genera evidencia; ver E5) |
| C2 | **Cerrar todas las sesiones** activas de la cuenta de correo del analista y **cambiar su contraseña**; activar MFA | Inmediata | TI / administrador de correo | **Sí, parcialmente.** Cierra el estado "vivo" de la sesión. Exportar antes los registros de inicio de sesión y actividad (E1) y fotografiar o exportar las reglas del buzón (E2) |
| C3 | Revisar y **eliminar reglas de reenvío o filtros** no autorizados y delegaciones en el buzón | Inmediata | TI / administrador de correo | **Sí.** Eliminar una regla maliciosa borra un indicador de compromiso: exportarla primero (E2) |
| C4 | Cambiar las credenciales de **todo servicio guardado en el navegador** (sistema de créditos, VPN, otros) y revocar tokens / sesiones de esos servicios | Inmediata | TI | **Sí, parcialmente.** Exportar antes los logs de acceso del sistema de créditos y VPN (E3) |
| C5 | Desde la consola de gestión (AD / Intune / MDM; NO INDICADO cuál existe): **registrar** estado de BitLocker, custodia de la clave de recuperación y última conexión; luego **bloquear** el equipo y ordenar el **borrado remoto**; deshabilitar el objeto equipo en el dominio y su certificado / perfil VPN | Inmediata (tras E4) | TI, con aprobación del responsable de seguridad | **Sí.** El borrado remoto destruye el contenido del disco y cualquier rastro del uso posterior al robo. Se acepta porque el equipo no está en poder de la cooperativa y el riesgo para los titulares prevalece, pero **solo después** de capturar el estado en la consola (E4) y con la decisión documentada |
| C6 | Si se confirma uso del correo después del robo: enviar alerta a los destinatarios afectados y bloquear remitentes / dominios de suplantación | Corto | TI + Comunicaciones | No (conservar copia de los correos enviados por el atacante con cabeceras, E1) |
| C7 | Suspender temporalmente la **exportación de carteras a Excel** y la descarga de bases de clientes a portátiles hasta aprobar una política (sección 4) | Corto | Gerencia de créditos + responsable de seguridad | No |
| C8 | Habilitar un **guion y registro de consultas** en atención y cobranzas para detectar llamadas fraudulentas a socios que usen los datos robados | Corto (antes de la comunicación a titulares) | Atención al socio + Oficial de Datos Personales | No (los reportes de socios se conservan como evidencia de impacto) |
| C9 | Inventariar el estado de cifrado de **todas** las portátiles y cifrar las que no lo tengan | Largo (iniciar ya) | TI | No |

No se recomienda ninguna acción ofensiva (rastreo activo con intrusión, "hack back", contacto con el ladrón). La geolocalización del equipo, si la consola la ofrece, se entrega a la Policía y no se usa para recuperarlo por cuenta propia.

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)

El equipo no está disponible, por lo que no hay imagen forense de disco posible. La evidencia está en los **servicios en la nube y en la consola de gestión**, y puede perderse por rotación de registros (art. 46.3 exige conservarlos mínimo 2 años, pero la retención por defecto del proveedor de correo puede ser menor: NO INDICADO).

| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| E1. Registros de inicio de sesión y actividad de la cuenta de correo (IP, dispositivo, fecha y hora) desde el 29/09/2026 00:00 hasta la fecha; correos enviados, leídos o eliminados después de las 21:00 del 29/09 | Consola del proveedor de correo (NO INDICADO) | Exportación completa (CSV / JSON y .eml con cabeceras) **antes** de C2; copia en almacenamiento de solo lectura | SHA-256 de cada archivo exportado, anotado en el registro de custodia | Responsable de seguridad |
| E2. Reglas del buzón, reenvíos, delegaciones y aplicaciones autorizadas | Consola de correo | Exportación y captura de pantalla con fecha visible **antes** de C3 | SHA-256 | Responsable de seguridad |
| E3. Logs del sistema de créditos: exportación del Excel (quién, cuándo, qué consulta / cuántos registros) y accesos posteriores al robo; logs de VPN | Sistema de créditos y VPN (art. 46.3) | Exportación a solo lectura | SHA-256 | TI / responsable de seguridad |
| E4. Estado del equipo en la consola: BitLocker (activo / inactivo), ubicación de la clave de recuperación, última sincronización, n.° de serie y n.° de activo, comando de bloqueo / borrado y su confirmación | AD / Intune / MDM (NO INDICADO) | Capturas de pantalla con fecha y hora + exportación del informe del dispositivo **antes** de C5 | SHA-256 de las capturas | Soporte / TI |
| E5. Constancia de la denuncia policial y declaración firmada del analista | Comisaría; analista | Original en custodia física; copia escaneada en PDF | SHA-256 del PDF | Oficial de Datos Personales |
| E6. Copia del Excel (o la consulta que lo regenera) para fijar el número exacto de titulares y campos expuestos | Sistema de créditos | Regenerar la exportación en un entorno controlado; guardar cifrada con acceso restringido | SHA-256 | Oficial de Datos Personales |
| E7. Mensajes de WhatsApp analista → jefe → ODP (sustentan la hora de toma de conocimiento y, si aplica, los motivos de la demora del art. 34.1) | Teléfonos del analista y del jefe | Captura con fecha y hora visibles y exportación del chat | SHA-256 | Oficial de Datos Personales |
| E8. Constancias de envío de la notificación a la ANPD, del aviso al CNSD y de la comunicación a titulares | Formulario / correo / proveedor de SMS | PDF o acuse con fecha y hora | SHA-256 | Oficial de Datos Personales |

**Registro de cadena de custodia** (llenar por cada ítem E1–E8):

| Ítem | Recolectado por | Fecha y hora | Ubicación de almacenamiento | Hash SHA-256 | Traspasos (de → a, fecha, motivo) |
|---|---|---|---|---|---|
| E1 | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |
| … | | | | | |

### 1.3 Erradicación
En un robo físico no hay malware que eliminar; la "causa" a erradicar son las **vías de acceso** que el equipo robado conserva:
- Invalidar toda credencial, token, certificado o sesión asociada al equipo y al usuario (C2, C4, C5).
- Confirmar el borrado remoto (acuse en la consola) o, si el equipo nunca vuelve a conectarse, dejarlo dado de baja en el inventario y en el dominio.
- Si E1 muestra actividad del atacante: revisar los buzones de los destinatarios de esos correos y eliminar los mensajes fraudulentos (tras preservarlos).
- Eliminar las copias del Excel que existan en otros equipos o en el correo del analista (adjuntos enviados a sí mismo) que no tengan justificación (inferencia: práctica habitual; `[VERIFICAR]`).

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** los datos originales siguen en el sistema de créditos (inferencia de 01 y 02, `[VERIFICAR]`); no se requiere restaurar datos. Se entrega al analista un **equipo nuevo, cifrado y gestionado**, sin copia local de la cartera.
- **Verificación de integridad:** comparar los registros de la cartera del analista en el sistema de créditos con los logs (E3) para descartar modificaciones posteriores al robo con sus credenciales.
- **Monitoreo reforzado (mínimo 90 días, inferencia de plazo razonable):** alertas de inicio de sesión anómalo en la cuenta del analista y del sistema de créditos; registro de reportes de socios sobre llamadas o mensajes sospechosos (C8).
- **Criterio para volver a operación normal:** (1) credenciales rotadas y MFA activo; (2) equipo robado bloqueado / borrado o dado de baja; (3) E1–E3 revisados sin actividad maliciosa, o con la actividad maliciosa contenida; (4) analista operando con equipo cifrado y sin bases locales.

---

## 2. Análisis de causa raíz (5 porqués)

Problema: datos de ~1 500 socios, incluidos datos sensibles (ingresos), quedaron en poder de un tercero no autorizado.

| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué los datos quedaron expuestos? | Porque se robó una laptop que contenía un Excel con la cartera y una sesión de correo abierta | Hecho |
| 2. ¿Por qué el robo del equipo expone los datos? | Porque no hay certeza de que el disco estuviera cifrado y el navegador mantenía la sesión del correo; la contraseña de Windows sola no protege el disco | Hecho (cifrado desconocido, sesión abierta) / inferencia técnica |
| 3. ¿Por qué no se sabe si estaba cifrado? | Porque el cifrado no es obligatorio ni se controla de forma centralizada: soporte responde "algunas sí, otras no" | Hecho (respuesta de soporte) / inferencia (ausencia de control central) |
| 4. ¿Por qué había una cartera completa con ingresos en un portátil? | Porque no existe política escrita que regule descargar bases de clientes a equipos portátiles y el sistema permite exportar sin restricción | Hecho (no hay política) / inferencia (exportación sin control técnico) |
| 5. ¿Por qué no existe esa política ni el control? | Porque la gestión de dispositivos y de datos fuera de las instalaciones no está cubierta en el documento de seguridad (art. 47) ni en un inventario de activos y datos | Inferencia (documento de seguridad NO INDICADO) |

- **Causa técnica:** portátil institucional sin cifrado de disco garantizado (BitLocker no aplicado ni verificado centralmente) y sesión de correo persistente en el navegador, sin MFA ni caducidad corta de sesión confirmada; ausencia de controles técnicos que impidan o registren la exportación masiva de la cartera a Excel (DLP). *Mientras no se confirme el estado de BitLocker, la falta de cifrado es inferencia.*
- **Causa de proceso:** no existe política de uso de dispositivos portátiles ni de manejo de datos fuera de las instalaciones (prohibición o autorización de descargas, minimización, cifrado obligatorio); no hay inventario del estado de cifrado; el canal de reporte de incidentes es informal (WhatsApp analista → jefe → ODP) y el ODP recibió el aviso ~12 h después, consumiendo una cuarta parte del plazo de 48 h.
- **Causa humana:** el analista descargó y transportó una base completa con datos sensibles y dejó la sesión del correo abierta; el robo en sí es un acto delictivo de un tercero, no una falta del trabajador. Se trata de una práctica tolerada por la falta de reglas y de capacitación, no de una conducta aislada (inferencia).

---

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)

- **Qué funcionó:**
  - El analista reportó el robo y presentó denuncia policial con rapidez (hecho).
  - El jefe escaló al Oficial de Datos Personales a la mañana siguiente (hecho).
  - El triaje fijó un reloj conservador (vence 01/10/2026 21:00) y la cooperativa contó con borradores de notificación a la ANPD, CNSD y titulares dentro del plazo (hecho, según 03-*).
- **Qué falló:**
  - Nadie pudo responder si la laptop estaba cifrada: la severidad varía de **Baja (1,5) a Muy alta (5,0)** según ese único dato (02).
  - No consta ninguna medida técnica de contención tras el reporte (01, sección 7): la sesión de correo pudo seguir activa durante horas.
  - Reporte por canal informal y con demora de ~12 h hasta el ODP; la hora del aviso al jefe no está registrada.
  - Se expusieron más datos de los necesarios: la cartera completa con ingresos para el trabajo de campo de un analista (falta de minimización).
  - Faltan datos básicos para notificar (RUC, contacto del ODP, código del banco de datos), lo que indica que el procedimiento de respuesta no estaba preparado (fase 1 de ISO/IEC 27035).
- **Qué cambiaremos:**
  - Cifrado obligatorio y verificado de todas las portátiles, con gestión remota (bloqueo / borrado).
  - Prohibir descargas locales de bases de socios; acceso a la cartera solo en línea, con permisos mínimos y registro de exportaciones.
  - MFA y caducidad de sesiones en el correo y el sistema de créditos.
  - Canal formal de reporte 24/7 con registro de hora y procedimiento de respuesta con datos de notificación pre-cargados.
  - Capacitación del personal de campo en protección de equipos y reporte inmediato.

---

## 4. Controles propuestos

| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| **8.24** Uso de criptografía | Cifrado de disco completo (BitLocker con TPM + PIN) obligatorio en todas las portátiles; claves de recuperación custodiadas centralmente | Técnica: disco posiblemente sin cifrar | Alta (inmediata) | TI |
| **8.1** Dispositivos de usuario final | Gestión centralizada (MDM / Intune) con política de cumplimiento: cifrado, bloqueo automático de pantalla, borrado remoto, inventario del estado de cifrado; prohibir el uso de equipos no conformes | Técnica / proceso: no se sabe el estado de los equipos ni se pudo bloquear | Alta | TI |
| **8.12** Prevención de fuga de datos | Restringir y registrar la exportación masiva de la cartera desde el sistema de créditos; DLP para impedir copias de bases de socios en discos locales o USB | Técnica / proceso: cartera completa descargada a Excel | Alta | TI + Gerencia de créditos |
| **5.15** Control de acceso | Acceso a la cartera solo en línea y por rol, con mínimo privilegio; revisión semestral de privilegios (art. 46.1) | Proceso: acceso y exportación sin restricción | Media | Gerencia de créditos + TI |
| **8.5** Autenticación segura | MFA obligatorio en correo, sistema de créditos y VPN; caducidad corta de sesión y reautenticación en dispositivos | Técnica: sesión de correo abierta usable por el ladrón | Alta (inmediata) | TI |
| **5.17** Información de autenticación | Prohibir el guardado de contraseñas en el navegador; usar gestor corporativo | Técnica: credenciales posiblemente guardadas en el navegador | Media | TI |
| **5.34** Privacidad y protección de datos personales (con art. 46.4 del reglamento) | Política de minimización: los analistas solo llevan los datos estrictamente necesarios para la visita (sin ingresos declarados, salvo justificación) | Proceso: exposición de datos sensibles innecesarios | Alta | Oficial de Datos Personales |
| **6.7** Trabajo remoto | Política escrita de trabajo de campo y fuera de las instalaciones: dónde se puede acceder a datos, custodia física del equipo en transporte público | Proceso: no hay política sobre equipos portátiles | Media | Responsable de seguridad + RR. HH. |
| **7.9** Seguridad de activos fuera de las instalaciones (con art. 48.1 del reglamento) | Incluir en el documento de seguridad (art. 47) las reglas de protección de equipos fuera de la oficina e inventario de activos asignados | Proceso: ausencia de control documentado | Media | Responsable de seguridad |
| **6.3** Concienciación y formación | Capacitación anual y al ingreso del personal de campo: bloqueo de equipo, no descargar bases, cerrar sesiones, reportar de inmediato | Humana: práctica tolerada de descarga y sesión abierta | Media | RR. HH. + Oficial de Datos Personales |
| **6.8** Reporte de eventos de seguridad | Canal formal 24/7 (correo o número dedicado, formulario) con registro automático de hora; el jefe reenvía de inmediato al ODP | Proceso: reporte informal y ~12 h de demora | Alta | Responsable de seguridad |
| **5.24** Planificación y preparación de la gestión de incidentes | Procedimiento de respuesta con plantillas pre-llenadas (RUC, ODP, códigos de bancos de datos, canal ANPD / CNSD) y responsables definidos | Proceso: datos básicos de notificación faltantes | Media | Oficial de Datos Personales |
| **8.15 / 8.16** Registro y monitoreo | Retención de logs de correo y sistema de créditos mínimo 2 años (art. 46.3) y alertas de inicio de sesión anómalo | Técnica: riesgo de perder evidencia por rotación; detección tardía | Media | TI |
| **5.28** Recolección de evidencias | Procedimiento documentado de preservación (exportar logs y capturar consola antes de contener) y formato de cadena de custodia | Proceso: no consta que se haya preservado nada | Media | Responsable de seguridad |

---

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)

| Campo | Valor |
|---|---|
| Descripción | Robo de una laptop institucional asignada a un analista de créditos, en un bus. Contenía un Excel con la cartera de clientes del analista; el navegador tenía abierta la sesión del correo institucional. Cifrado de disco desconocido. Categoría FIS con riesgo secundario INT. Brecha de datos personales (art. III num. 16). Prioridad P1 |
| Periodo del incidente | Inicio: 29/09/2026 ~21:00. Fin: **abierto** (equipo no recuperado; exposición potencial continúa hasta confirmar bloqueo / borrado y ausencia de accesos) |
| Datos y titulares afectados | ~1 500 socios con crédito (cifra por confirmar): nombre, DNI, dirección, teléfono, monto del crédito, cuotas atrasadas y **ingresos mensuales declarados (dato sensible)**. Posible contenido del correo institucional: NO INDICADO |
| Efectos / consecuencias | Severidad ENISA **5,0 Muy alta** (escenario base sin cifrado) o 1,5 Baja si se confirma cifrado y clave no comprometida. Riesgos: fraude por suplantación de la cooperativa, extorsión a socios morosos, suplantación de identidad, phishing desde el correo real, afectación a la vida privada. Daños efectivos: NO INDICADO a la fecha |
| Quién reportó y cuándo | Analista de créditos (personal propio) → jefe por WhatsApp (hora NO INDICADA) → Oficial de Datos Personales el 30/09/2026 09:10. Toma de conocimiento adoptada: 29/09/2026 ~21:00 (criterio conservador) |
| Notificación ANPD (fecha / no corresponde y por qué) | **Corresponde** (art. 34.1: datos sensibles y perjuicio evidente). Borrador inicial preparado; límite 01/10/2026 21:00. Fecha y hora de envío: `[COMPLETAR]`. Notificación complementaria pendiente (cifrado, revisión del correo, n.° exacto) |
| Comunicación a titulares (fecha / no corresponde y por qué) | **Corresponde** (art. 34.3; la excepción del 34.4 no aplica porque el incidente no está superado). Borrador preparado (SMS + carta / correo); límite 01/10/2026 21:00. Fecha de envío: `[COMPLETAR]` |
| Notificación CNSD (fecha / no corresponde) | **Recomendada** ante la duda sobre "entorno digital" (art. 34.5) `[VERIFICAR criterio]`. Borrador preparado. Fecha de envío: `[COMPLETAR]` |
| Medidas adoptadas | Adoptadas (hecho): denuncia policial; reporte al ODP; borradores de notificación. Propuestas / sin confirmar: C1–C9 (sección 1.1) y controles de la sección 4 `[COMPLETAR estado y fecha de cada una]` |

---

## 6. Criterios de cierre

- [ ] **Incidente contenido** — pendiente: no consta cierre de sesiones, cambio de credenciales ni bloqueo / borrado remoto (C2–C5).
- [ ] **Causa erradicada** — pendiente: vías de acceso del equipo robado sin invalidar confirmadamente; revisión de E1–E3 no realizada.
- [ ] **Servicios y datos recuperados** — pendiente: confirmar que el original de la cartera sigue íntegro en el sistema de créditos y entregar equipo cifrado al analista.
- [ ] **Notificaciones realizadas o descartadas con fundamento** — borradores listos; falta registrar fecha y hora de envío a ANPD, titulares y CNSD, y enviar la notificación complementaria a la ANPD.
- [ ] **Acciones correctivas asignadas con fecha** — controles de la sección 4 propuestos con responsable sugerido; faltan responsable nominal y fecha comprometida.
- [ ] **Registro del art. 35 completo** — faltan fechas de notificación, estado de las medidas y fin del periodo del incidente.

**Información pendiente para cerrar:** estado de BitLocker y del equipo al momento del robo; resultado de la revisión de accesos al correo y al sistema de créditos; n.° exacto de titulares y de socios con cuotas atrasadas; constancia de la denuncia; RUC, contacto del ODP y código del banco de datos; hora del aviso al jefe.

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
