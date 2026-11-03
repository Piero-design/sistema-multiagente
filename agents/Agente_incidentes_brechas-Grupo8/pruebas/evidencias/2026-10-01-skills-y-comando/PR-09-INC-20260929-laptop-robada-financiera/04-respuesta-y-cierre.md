# Respuesta y cierre — INC-20260929-laptop-robada-financiera

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`
- **Marco:** ISO/IEC 27035-1:2023 (Responder / Aprender lecciones), ISO/IEC 27035-3:2020, ISO/IEC 27002:2022 (5.26, 5.27, 5.28), ISO/IEC 27037:2012, NIST SP 800-61r3 (RS, RC), art. 35 del D.S. 016-2024-JUS

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Exportar los registros de acceso del correo del analista desde el 29/09 ~21:00 (inicios de sesión, IP, dispositivos, reglas del buzón, reenvíos, enviados) | Inmediata (**antes** de C2) | Seguridad | No, la preserva. Hacerlo antes de que los registros roten |
| C2 | Cerrar todas las sesiones y revocar los tokens de la cuenta de correo; cambiar la contraseña; activar MFA | Inmediata | TI | Sí, cambia el estado de la cuenta. Por eso C1 va primero |
| C3 | Rotar todas las credenciales que pudieran estar guardadas en el equipo o el navegador (sistema de créditos, VPN, Wi-Fi corporativa, certificados). Dar de baja el equipo en el dominio/MDM | Inmediata | TI | Bajo. Registrar fecha y hora de cada revocación |
| C4 | Consultar en la consola (AD/Entra/MDM) el estado de BitLocker y la custodia de la clave de recuperación; capturar pantalla del último contacto del equipo | Inmediata | TI | No, es evidencia clave |
| C5 | Si hay MDM: bloqueo y borrado remoto del equipo, una vez registrado su estado (C4) | Corto plazo (hoy) | TI, con aprobación del responsable de seguridad | Sí, se pierde el contenido del equipo. Es aceptable porque el equipo no está en poder de la organización; documentar la decisión |
| C6 | Revisar si hubo correos enviados desde la cuenta a socios después del robo (posible *phishing* interno) y, si los hay, alertar a los destinatarios | Corto plazo | Seguridad / Atención al socio | No |
| C7 | Alertar al área de atención al socio y de cobranzas sobre posibles llamadas fraudulentas; preparar un guion de respuesta | Corto plazo | Atención al socio | No |
| C8 | Suspender temporalmente la descarga de bases de clientes a portátiles hasta aprobar la política (L1) | Corto plazo | Gerencia / TI | No |
| C9 | Hacer seguimiento a la denuncia policial y avisar a la policía si el equipo aparece | Largo plazo | Legal | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| Registros de acceso del correo (29/09 21:00 en adelante) | Consola del proveedor de correo | Exportación nativa (CSV/JSON) a almacenamiento de solo lectura | SHA-256 del archivo exportado | Responsable de seguridad |
| Estado de BitLocker y del equipo en la consola de gestión | AD / Entra / MDM | Captura de pantalla con fecha y hora + exportación del reporte | SHA-256 | TI |
| Registros de exportación del sistema de créditos (art. 46.3): qué archivo, cuándo y qué campos | Sistema de créditos | Exportación del log | SHA-256 | TI / Riesgos |
| Copia de la denuncia policial | Trabajador / comisaría | Escaneo en PDF | SHA-256 | Legal |
| Mensaje de WhatsApp del trabajador al jefe y reenvío al ODP (fija la línea de tiempo) | Teléfono del jefe | Captura con fecha y hora visibles + exportación del chat | SHA-256 | ODP |
| Registro de inventario del equipo (serie, usuario asignado, configuración) | Inventario de TI | Copia | SHA-256 | TI |
| Declaración escrita del trabajador (hora, lugar, qué contenía la laptop, otros archivos) | Trabajador | Documento firmado | — | ODP / RR. HH. |

**Registro de cadena de custodia:** por cada elemento, anotar quién lo recolectó, la fecha y hora, la ubicación de origen, el hash, el lugar de almacenamiento y cada traspaso (quién lo entrega, quién lo recibe, cuándo y para qué). [PENDIENTE: abrir el formato de cadena de custodia]

### 1.3 Erradicación
- La "causa" inmediata es la pérdida del control del equipo. Se erradica con la revocación de todas las credenciales y sesiones vinculadas (C2, C3) y, si existe, con el borrado remoto (C5).
- Si C1 o C6 detectan accesos indebidos al correo: revisar y eliminar reglas de reenvío maliciosas, identificar los datos accedidos y ampliar el alcance de la brecha (notificación complementaria).

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** los datos originales están en el sistema de créditos (inferencia, [VERIFICAR]). Los archivos de trabajo del analista se recuperan del almacenamiento institucional o de las copias de respaldo, si existen [NO INDICADO].
- **Verificación de integridad:** confirmar que la cartera en el sistema coincide con el último estado conocido y que no hay archivos que solo existían en la laptop.
- **Criterio para volver a operación normal:** el analista recibe un equipo nuevo con cifrado de disco verificado, MFA activo y acceso a la cartera por medios que no requieran descargar bases completas; además, 30 días de monitoreo reforzado de la cuenta de correo y de reclamos de socios por fraude.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué se expusieron los datos de ~1 500 socios? | Porque robaron una laptop que tenía un Excel con la cartera completa | Hecho |
| 2. ¿Por qué la laptop tenía la cartera completa? | Porque el analista la descargó para trabajar desde casa | Hecho |
| 3. ¿Por qué pudo descargarla y llevarla fuera de la oficina? | Porque no hay una política escrita ni un control técnico que limite la exportación de bases de clientes a portátiles | Hecho (no hay política) / inferencia (no hay control técnico) |
| 4. ¿Por qué el robo implica exposición y no solo la pérdida de un equipo? | Porque no está garantizado el cifrado del disco ("algunas sí, otras no") y la sesión del correo estaba abierta | Hecho |
| 5. ¿Por qué el cifrado no es uniforme? | Porque no existe una línea base de configuración obligatoria para dispositivos de usuario final ni se verifica su cumplimiento | Inferencia |

- **Causa técnica:** equipo portátil sin cifrado de disco garantizado; sesión de correo persistente sin expiración; sin capacidad confirmada de borrado remoto.
- **Causa de proceso:** no hay política de uso de dispositivos portátiles ni de exportación o minimización de datos (art. 46.4: impedir copias no autorizadas); no hay un procedimiento formal de reporte de incidentes fuera de horario (el reporte usó WhatsApp y tardó ~12 h en llegar al ODP).
- **Causa humana:** el analista descargó la cartera completa (incluidos datos sensibles innecesarios para la gestión diaria, inferencia) y la transportó en transporte público. No se le atribuye mala fe.

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** el trabajador denunció el robo y avisó a su jefatura; la jefatura recopiló rápidamente información útil (campos del archivo, cantidad aproximada, estado de la sesión de correo).
- **Qué falló:** no había control sobre la descarga de datos, el cifrado no era uniforme, el reporte llegó tarde al ODP (~12 h) por un canal no institucional, y no se sabía con certeza el estado de seguridad del equipo.
- **Qué cambiaremos:** cifrado obligatorio y verificado en todos los portátiles, política de no descargar bases completas (acceso remoto controlado), un canal 24/7 de reporte de incidentes y capacitación.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.24 Uso de criptografía | Cifrado de disco completo obligatorio en el 100 % de los portátiles, con la clave custodiada centralmente y un reporte de cumplimiento mensual | Exposición del contenido de equipos perdidos | Alta | TI |
| 8.1 Dispositivos de usuario final | Línea base de configuración, gestión mediante MDM con bloqueo y borrado remoto, y expiración de sesiones del navegador | Pérdida de control del equipo | Alta | TI |
| 8.12 Prevención de fuga de datos | Restringir y registrar la exportación masiva de cartera desde el sistema de créditos; bloquear la copia de bases completas a portátiles | Descarga de la cartera completa | Alta | TI / Riesgos |
| 5.15 Control de acceso | Acceso a la cartera solo por el sistema o por escritorio remoto, sin descargas; mínimo privilegio (ocultar ingresos si no se necesitan) | Minimización de datos | Media | Riesgos / TI |
| 8.5 Autenticación segura | MFA en correo y sistemas, con reautenticación periódica | Uso de sesiones abiertas por terceros | Alta | TI |
| 6.8 Reporte de eventos de seguridad | Canal institucional 24/7 (teléfono o correo) para reportar incidentes directamente a Seguridad y al ODP | Demora y canal no institucional | Alta | Seguridad / ODP |
| 6.3 Concienciación y formación | Capacitación sobre manejo de datos fuera de la oficina y reporte inmediato | Causa humana | Media | RR. HH. / ODP |
| 5.24 Planificación de la gestión de incidentes | Procedimiento escrito de incidentes con el reloj de 48 h y plantillas | Respuesta tardía | Media | Seguridad / ODP |

Relación con el reglamento: art. 46.4 (impedir copias no autorizadas), art. 48.1 (equipos seguros fuera de las instalaciones) y art. 47 (actualizar el documento de seguridad).

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Robo de una laptop institucional con un Excel de la cartera de créditos y la sesión del correo institucional abierta. Cifrado no confirmado |
| Periodo del incidente | Desde el 29/09/2026 ~21:00. Sigue abierto mientras el equipo no se recupere ni se confirme la revocación de accesos |
| Datos y titulares afectados | ~1 500 socios: nombre, DNI, dirección, teléfono, monto del crédito, cuotas atrasadas e ingresos mensuales declarados (sensible). Buzón de correo: en investigación |
| Efectos / consecuencias | Riesgo alto de fraude dirigido y riesgo medio de suplantación, extorsión y daño reputacional. Severidad ENISA SE = 5,0 (Muy alta) |
| Quién reportó y cuándo | Analista de créditos a su jefe por WhatsApp (hora NO INDICADA); jefe al ODP el 30/09/2026 09:10 |
| Notificación ANPD (fecha / no corresponde y por qué) | **PENDIENTE de aprobación y envío.** Obligación probable por datos sensibles (art. 34.1). Límite: 01/10/2026 21:00 |
| Comunicación a titulares (fecha / no corresponde y por qué) | **PENDIENTE de aprobación y envío.** Corresponde según el art. 34.3; el art. 34.4 no aplica |
| Notificación CNSD (fecha / no corresponde) | **PENDIENTE de decisión** (recomendado notificar, art. 34.5, ante la duda sobre el entorno digital) |
| Medidas adoptadas | Denuncia policial. Las demás medidas (C1–C9) están propuestas; registrar la fecha de ejecución de cada una |

## 6. Criterios de cierre
- [ ] Incidente contenido (sesiones y credenciales revocadas; borrado remoto ejecutado o descartado con fundamento)
- [ ] Causa erradicada (sin accesos indebidos activos al correo)
- [ ] Servicios y datos recuperados (equipo de reemplazo seguro; datos verificados en el sistema)
- [ ] Notificaciones realizadas o descartadas con fundamento (ANPD, titulares, CNSD, y complementaria si corresponde)
- [ ] Acciones correctivas asignadas con fecha (controles de la sección 4)
- [ ] Registro del art. 35 completo con las fechas reales

**Estado actual: NO apto para cierre.**

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
