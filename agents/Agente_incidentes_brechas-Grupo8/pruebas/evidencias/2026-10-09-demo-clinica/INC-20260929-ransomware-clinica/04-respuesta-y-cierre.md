# Respuesta y cierre — INC-20260929-ransomware-clinica

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-*.md`, y evidencia del entorno en `demo/clinica-san-gabriel/`.
- Las acciones son recomendaciones para el equipo de TI; el agente no ejecuta nada. No se recomiendan acciones ofensivas ni el pago del rescate.

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Aislar de la red PC-FACT-01, PC-ADM-01…05 y el servidor aún conectado; mantenerlos **encendidos** (no apagar ni reiniciar) | Inmediata | Jefe de TI | No, si se conservan encendidos; apagarlos sí perdería memoria |
| C2 | Deshabilitar `svc_backup2`; cambiar la contraseña del Administrador local (reutilizada, `auth-hce.log:3`) y de `postgres` (fija en `config.py:4`); cerrar sesiones | Inmediata | Jefe de TI / SoftSalud | Sí: antes, exportar el estado de cuentas y logs |
| C3 | Bloquear en el firewall `198.51.100.77` y `203.0.113.9`; revisar la VPN de NetAndes y suspender accesos remotos hasta validarlos | Inmediata | Jefe de TI / NetAndes | No |
| C4 | Desmontar físicamente `BKP-01` **sin escribir en él** y guardarlo como evidencia | Inmediata | Jefe de TI | No, si se hace en solo lectura |
| C5 | Buscar y eliminar el correo `Factura_F001-48213.docm` y el aviso de dominio sospechoso (`correo-gateway.log:3-4`) en todos los buzones de M365 | Corto | Jefe de TI | Conservar copia con cabeceras |
| C6 | Cambiar credenciales de cuentas compartidas (`admision1`, `admision2`) y de cualquier usuario que haya iniciado sesión en PC-FACT-01 | Corto | Jefe de TI | No |
| C7 | Continuidad asistencial en papel: lista de pacientes críticos, alergias y tratamientos desde fuentes alternas | Inmediata | Gerencia / Dirección médica | No |
| C8 | Decidir con alta dirección y asesor legal (Mamani & Asociados, `contactos.md:10`) la postura frente al rescate; no pagar sin asesoría y sin que ello cambie la obligación de notificar | Corto | Gerencia | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| Logs del firewall (retención 30 días) | `firewall.log` / equipo | Exportar hoy, copia de solo lectura | SHA-256 por archivo | Jefe de TI |
| Logs de antivirus, pasarela de correo, auth HCE | Consolas y servidores | Exportar; priorizar antes de rotación | SHA-256 | Jefe de TI |
| Memoria y disco de PC-FACT-01, SRV-HCE, SRV-ARCH | Equipos encendidos | Captura de memoria, luego imagen forense (con proveedor especializado) | SHA-256 de la imagen | Responsable de seguridad / forense |
| Disco `BKP-01` | Sala técnica | Retirar y sellar; clonar | SHA-256 | Responsable de seguridad |
| Nota de rescate y capturas de pantalla | 6 PC | Fotografía y archivo; anotar hora | SHA-256 | Oficial de Datos Personales |
| Correo original con cabeceras y adjunto `.docm` | M365 | Exportar `.eml` y muestra en entorno aislado | SHA-256 | Jefe de TI |
| Constancias de decisiones y horas (reloj de 48 h) | Este expediente | Registro con fecha y firma | — | Oficial de Datos Personales |

**Registro de cadena de custodia:** para cada ítem anotar quién recolectó, fecha y hora, ubicación, método, hash y cada traspaso. Plantilla pendiente: `[COMPLETAR]`.
Advertencia: el log de auditoría de la HCE tuvo la rotación desactivada por el atacante (`auth-hce.log:9`) y la app solo registra nivel ERROR (`app/hce/config.py:8`), por lo que habrá vacíos de evidencia.

### 1.3 Erradicación
- Reconstruir SRV-HCE, SRV-ARCH y las 6 PC desde imágenes limpias; no limpiar en el sitio.
- Eliminar persistencia: cuenta `svc_backup2`, tareas programadas y servicios añadidos (por determinar en el análisis forense).
- Corregir la app HCE (sin autenticación, inyección SQL, `/exportar` sin control, `app.py:10-21`) antes de volver a ponerla en línea.
- Rotar contraseñas administrativas, de base de datos y de VPN.

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** no hay copia limpia conocida. Último respaldo bueno: 2026-09-08 (`respaldos.log:2`), en `BKP-01`, ahora cifrado (`respaldos.log:5`). Las ejecuciones del 15 y 22/09 se omitieron (`respaldos.log:3-4`). Consultar a SoftSalud por copias propias, revisar copias fuera de línea o en nube, y evaluar con especialistas si existe descifrador `[VERIFICAR]`. Reconstruir información clínica con registros en papel.
- **Verificación de integridad:** hash de las copias; restauración de prueba en entorno aislado (nunca se ha probado: `activos-y-datos.md:33`).
- **Criterio para volver a operación normal:** equipos reconstruidos y sin indicadores de compromiso, credenciales rotadas, MFA activo, respaldo aislado funcionando, monitoreo reforzado durante `[COMPLETAR]` días, aprobación del responsable de seguridad.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué se perdió el acceso a la HCE? | Ransomware cifró SRV-HCE, SRV-ARCH y `BKP-01` | Hecho (`antivirus.log:7-8`, `respaldos.log:5`) |
| 2. ¿Por qué el atacante llegó a los servidores? | Macro abierta en PC-FACT-01; RDP al servidor con admin local reutilizado; creó cuenta admin | Hecho (`correo-gateway.log:6`, `auth-hce.log:3,5`) |
| 3. ¿Por qué no se detuvo en el correo y en el equipo? | Sandbox desactivado, adjunto entregado sin análisis; el antivirus no pudo poner en cuarentena y fue detenido; la alerta fue solo por correo | Hecho (`correo-gateway.log:4-5`, `antivirus.log:4,6`, `activos-y-datos.md:31`) |
| 4. ¿Por qué nadie actuó sobre la alerta y la intrusión duró 8 horas? | Alertas "cuando hay tiempo"; sin monitoreo fuera de horario; sin plan de respuesta, roles ni responsable de notificar | Hecho (`documento-seguridad-extracto.md:19,18`, `plan-respuesta-incidentes.md:3-5`) |
| 5. ¿Por qué el daño fue total (sin respaldo, red plana, datos sin cifrar)? | Respaldo en disco conectado, restauración nunca probada, jobs omitidos, sin cifrado, sin MFA, app sin autenticación, contraseña fija, logs mínimos | Hecho (`documento-seguridad-extracto.md:7-8`, `respaldos.log:3-5`, `activos-y-datos.md:9-10,29`, `config.py:4,6,8`, `app.py:10`) |

- **Causa técnica:** sin MFA ni segmentación, admin local reutilizado, correo sin análisis de macros, respaldo sin aislar y sin cifrado en reposo.
- **Causa de proceso:** plan de respuesta sin roles ni plazos; nadie definido para notificar a la ANPD; revisión de alertas informal; respaldos manuales sin supervisión; logs 90 días frente a 2 años del art. 46.3.
- **Causa humana:** apertura del adjunto por falta de concienciación (inferencia: no hay evidencia de capacitación); operador ausente en los respaldos del 15 y 22/09.

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** el personal detectó y escaló rápido (07:15 a 08:40); se aisló un servidor; hay continuidad asistencial en papel; existe Oficial de Datos Personales con contacto.
- **Qué falló:** alerta de antivirus sin atender durante ~9 horas; respaldo inútil; falta de procedimiento y de responsable de notificación; falta de monitoreo y de retención de logs; confianza excesiva en credenciales compartidas.
- **Qué cambiaremos:** ver controles propuestos.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.13 Copias de respaldo | Regla 3-2-1 con una copia fuera de línea o inmutable; prueba de restauración trimestral; monitoreo de jobs omitidos; art. 48 | Respaldo cifrado y jobs omitidos | Alta | Jefe de TI |
| 8.5 Autenticación segura / 5.17 Información de autenticación | MFA para HCE, VPN, correo y administradores; contraseñas únicas; eliminar la contraseña fija de `config.py` | Credenciales y accesos | Alta | Jefe de TI / SoftSalud |
| 5.15 Control de acceso | Cuentas personales (fin de `admision1/2`), mínimo privilegio, sin admin local en facturación, revisión semestral (art. 46.1) | Movimiento lateral | Alta | Jefe de TI |
| 8.7 Protección contra malware / 8.1 Dispositivos de usuario final | EDR o antivirus gestionado con alertas 24x7, bloqueo de macros, sandbox de adjuntos, protección anti-manipulación | Macro y antivirus detenido | Alta | Jefe de TI |
| 8.15 / 8.16 Registro y monitoreo | Retención de logs de la HCE y firewall de 2 años (art. 46.3), registro de consultas y exportaciones, alertas fuera de horario | Detección tardía y falta de trazabilidad | Alta | Jefe de TI / SoftSalud |
| 5.24 Planificación y preparación | Plan de respuesta con roles, clasificación, plazo de 48 h, plantillas y lista de contactos; designar quién notifica; ensayo anual | Falta de proceso | Alta | Oficial de Datos Personales |
| 6.3 Concienciación y formación | Capacitación anti-phishing a admisión y facturación | Causa humana | Media | Oficial de Datos Personales |
| 8.24 Uso de criptografía | Cifrado en reposo de servidores y estaciones | Impacto de la exfiltración | Media | Jefe de TI |
| 8.12 Prevención de fuga de datos | Alerta por transferencias salientes grandes; restringir salida a Internet de los servidores | Exfiltración de 3,4 GB | Media | Jefe de TI |
| 8.22 Segregación de redes `[VERIFICAR, no está en knowledge/]` | Aislar servidores de las estaciones de usuario | Movimiento lateral | Alta | Jefe de TI |

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Ransomware con intrusión previa y probable exfiltración en la red de la clínica, ver `01-ficha-incidente.md` |
| Periodo del incidente | 2026-09-28 23:48 a 2026-09-29 07:30 (cifrado); acceso del atacante hasta 04:10 (`auth-hce.log:10`); en curso hasta contención completa |
| Datos y titulares afectados | Salud (sensibles), identificación, seguro, facturación y personal; aprox. 18 000 pacientes (3 100 menores) y 74 trabajadores |
| Efectos / consecuencias | Indisponibilidad total de la HCE y archivos, respaldo perdido, riesgo de publicación, atención en papel |
| Quién reportó y cuándo | Jefe de TI al Oficial de Datos Personales, 2026-09-29 08:40 |
| Notificación ANPD (fecha / no corresponde y por qué) | Corresponde (obligación probable); fecha de envío `[COMPLETAR]`; límite 2026-09-30 23:50 |
| Comunicación a titulares (fecha / no corresponde y por qué) | Corresponde (art. 34.3); fecha `[COMPLETAR]`; límite 2026-09-30 23:50 |
| Notificación CNSD (fecha / no corresponde) | Corresponde (art. 34.5); fecha `[COMPLETAR]` |
| Medidas adoptadas | Desconexión de red del servidor; papel; las demás, ver 1.1 (propuestas) |

## 6. Criterios de cierre
- [ ] Incidente contenido
- [ ] Causa erradicada
- [ ] Servicios y datos recuperados
- [ ] Notificaciones realizadas o descartadas con fundamento
- [ ] Acciones correctivas asignadas con fecha
- [ ] Registro del art. 35 completo

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
