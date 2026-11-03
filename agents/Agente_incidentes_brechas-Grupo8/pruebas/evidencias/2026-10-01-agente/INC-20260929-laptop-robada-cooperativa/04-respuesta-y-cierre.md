# Respuesta y cierre — INC-20260929-laptop-robada-cooperativa

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`
- **Información técnica de investigación:** NO INDICADO (no hay logs ni hallazgos todavía)

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Exportar los registros de inicio de sesión y de actividad del correo del analista (y de la exportación del Excel en el sistema de créditos) **antes** de cambiar nada | Inmediata (primero) | TI / seguridad | No: es la preservación previa |
| C2 | Cerrar todas las sesiones de la cuenta de correo, cambiar la contraseña, exigir MFA; revisar reglas de reenvío, correos enviados y eliminados después del 29/09 21:00 | Inmediata | Administrador de correo | Sí: el cierre de sesiones borra el estado vivo, por eso C1 va antes |
| C3 | Cambiar las credenciales de todo servicio que el navegador pudiera tener guardado (sistema de créditos, VPN, otros) y revocar los certificados o tokens del equipo | Inmediata | TI | Bajo (registrar qué se revocó y a qué hora) |
| C4 | Consultar en la consola de gestión el estado de BitLocker y la última conexión del equipo; capturar pantalla | Inmediata | Soporte | No |
| C5 | Bloqueo y borrado remoto del equipo (si hay MDM/Intune), solo después de C4 | Inmediata, tras C4 | TI, con aprobación del responsable de seguridad | Sí: se pierde el equipo como fuente de evidencia. Aceptable porque no se tiene en posesión, pero hay que dejarlo registrado |
| C6 | Dar de baja o bloquear el equipo en el dominio y en el inventario como "robado" | Corto | TI | No |
| C7 | Alertar al personal de atención y cobranzas sobre posibles llamadas fraudulentas a socios, con un guion | Corto (antes de comunicar a socios) | Jefe de créditos + ODP | No |
| C8 | Prohibir temporalmente las descargas de bases de clientes a portátiles y revisar quién tiene copias locales | Largo / corto | Gerencia + seguridad | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| Logs de inicio de sesión y auditoría del correo (desde 29/09 hasta hoy) | Consola del proveedor de correo | Exportación a archivo y copia en almacenamiento de solo lectura | SHA-256 del archivo exportado | Responsable de seguridad |
| Log de exportación/descarga del Excel (art. 46.3) | Sistema de créditos | Exportación y copia de solo lectura | SHA-256 | Responsable de seguridad |
| Estado de BitLocker y última conexión del equipo | Consola AD/Intune/MDM | Captura de pantalla con fecha y hora + exportación del informe | SHA-256 | Soporte → seguridad |
| Constancia de la denuncia policial | Analista / comisaría | Copia escaneada y original archivado | SHA-256 del escaneo | ODP |
| Mensaje de WhatsApp original y reenvío al ODP | Teléfonos del analista y del jefe | Capturas con fecha y hora visibles; exportación del chat | SHA-256 | ODP |
| Declaración escrita del analista | Analista | Documento firmado y fechado | — | ODP |
| Registro de acciones de contención (C1–C8) con horas | Equipo de TI | Bitácora del incidente | — | Responsable de seguridad |

**Registro de cadena de custodia:** por cada evidencia anotar quién la recolectó, fecha y hora, ubicación de almacenamiento, hash y cada traspaso (de quién a quién, cuándo y para qué).

### 1.3 Erradicación
- Invalidar toda credencial o sesión que pudiera usarse desde el equipo robado (C2, C3).
- Eliminar el acceso del equipo a la red y a los servicios (C5, C6).
- Revisar si el atacante creó reglas de reenvío, aplicaciones autorizadas (OAuth) o dispositivos registrados en la cuenta de correo, y eliminarlos.

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** los datos originales están en el sistema de créditos (inferencia, `[VERIFICAR]`). Entregar al analista un equipo nuevo, con cifrado verificado y sin copias locales de la cartera.
- **Verificación de integridad:** confirmar que no hubo cambios en el sistema de créditos ni en el buzón usando las credenciales del analista (revisión de logs, C1).
- **Criterio para volver a operación normal:** credenciales rotadas, MFA activo, sin actividad anómala por al menos `[definir: p. ej. 30 días]` de monitoreo reforzado del correo y de reclamos de socios por contactos fraudulentos.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué se expusieron datos de socios? | Porque se robó una laptop que tenía una copia local de la cartera | Hecho |
| 2. ¿Por qué había una copia local? | Porque el analista la descargó para trabajar desde casa | Hecho |
| 3. ¿Por qué pudo descargarla y sacarla de la oficina? | Porque no hay política ni control técnico que lo impida (art. 46.4) | Hecho (no hay política escrita); control técnico: inferencia |
| 4. ¿Por qué la copia robada podría ser legible? | Porque no se garantiza el cifrado de las portátiles ("algunas sí, otras no") | Hecho |
| 5. ¿Por qué no se sabe qué equipos están cifrados? | Porque no hay un estándar de configuración ni un inventario de seguridad de los dispositivos de usuario final | Inferencia |

- **Causa técnica:** cifrado de disco no garantizado; sesión de correo persistente en el navegador; posible ausencia de MDM con borrado remoto (inferencia).
- **Causa de proceso:** no hay política de trabajo remoto ni de manejo de bases de clientes fuera de la oficina; el reporte de incidentes llega por un canal informal (WhatsApp) y con 12 h de retraso hasta el ODP.
- **Causa humana:** el trabajador llevó datos sensibles en un soporte portátil sin controles, probablemente por necesidad operativa y sin formación sobre el riesgo (inferencia). No se atribuye culpa individual: la causa principal es organizacional.

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** el trabajador avisó en pocas horas y presentó la denuncia; el jefe escaló al ODP.
- **Qué falló:** no hay inventario de cifrado, no hay política de descargas, no hay canal formal de reporte de incidentes, y el reloj de 48 h empezó a correr antes de que el ODP se enterara.
- **Qué cambiaremos:** acceso remoto al sistema de créditos sin copias locales; cifrado obligatorio y verificado; canal único de reporte de incidentes, disponible las 24 horas, con instrucción de avisar directamente al ODP o a seguridad.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.24 Uso de criptografía | BitLocker obligatorio en el 100 % de las portátiles, con claves de recuperación custodiadas centralmente y verificación mensual | Cifrado no garantizado | Alta | TI |
| 8.1 Dispositivos de usuario final | Gestión centralizada (MDM) con bloqueo y borrado remoto, bloqueo automático de pantalla e inventario | Sin control remoto ni inventario | Alta | TI |
| 8.12 Prevención de fuga de datos | Bloquear o alertar las exportaciones masivas del sistema de créditos y las copias a dispositivos locales (art. 46.4) | Descarga de la cartera | Alta | Seguridad + TI |
| 5.15 Control de acceso | Acceso a la cartera solo vía sistema o escritorio remoto, por mínimo privilegio; revisión semestral (art. 46.1) | Copias locales innecesarias | Media | Dueño del proceso de créditos |
| 8.5 Autenticación segura / 5.17 Información de autenticación | MFA en el correo y en el sistema de créditos; sesiones con caducidad; no guardar contraseñas en el navegador | Sesión de correo abierta | Alta | TI |
| 6.3 Concienciación y formación | Capacitación sobre manejo de datos sensibles fuera de la oficina y sobre cómo reportar incidentes de inmediato | Factor humano y canal informal | Media | RR. HH. + ODP |
| 6.8 Reporte de eventos de seguridad | Canal único de reporte de incidentes, disponible las 24 horas, con aviso automático al ODP | 12 h de retraso hasta el ODP | Alta | Seguridad |
| 8.15 / 8.16 Registro y monitoreo | Asegurar los logs de exportación y acceso con conservación mínima de 2 años (art. 46.3) | Investigación limitada | Media | TI |

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Robo de una laptop institucional con un Excel de la cartera de créditos y una sesión de correo institucional abierta. Cifrado no confirmado |
| Periodo del incidente | Desde el 29/09/2026 ~21:00; exposición vigente mientras el equipo no se recupere o no se confirme el cifrado |
| Datos y titulares afectados | ~1 500 socios: nombre, DNI, dirección, teléfono, monto del crédito, cuotas atrasadas, **ingresos mensuales declarados (sensible)**; posibles datos del buzón (en investigación) |
| Efectos / consecuencias | Riesgo alto de fraude por suplantación de la cooperativa; riesgo medio de extorsión y de suplantación de identidad. SE = 5,0 (Muy alta) |
| Quién reportó y cuándo | Analista de créditos → jefe (hora NO INDICADA) → ODP el 30/09/2026 a las 09:10 |
| Notificación ANPD | **Pendiente de aprobación.** Borrador listo; límite: 01/10/2026 21:00 |
| Comunicación a titulares | **Pendiente de aprobación.** Borrador listo; corresponde (no aplica la excepción del art. 34.4) |
| Notificación CNSD | **Pendiente de aprobación.** Recomendada ante la duda sobre el entorno digital |
| Medidas adoptadas | Denuncia policial (según el trabajador). Las demás medidas (C1–C8) están propuestas, sin confirmación de ejecución |

## 6. Criterios de cierre
- [ ] Incidente contenido (sesiones revocadas, equipo bloqueado o borrado, credenciales rotadas)
- [ ] Causa erradicada (sin accesos anómalos; reglas o apps maliciosas eliminadas)
- [ ] Servicios y datos recuperados (equipo de reemplazo cifrado; integridad del sistema de créditos verificada)
- [ ] Notificaciones realizadas o descartadas con fundamento (ANPD, titulares, CNSD, complementaria)
- [ ] Acciones correctivas asignadas con fecha (tabla de la sección 4)
- [ ] Registro del art. 35 completo (fechas reales de notificación y medidas)

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
