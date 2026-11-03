# Respuesta y cierre — INC-20260929-ransomware-clinica

- **Estado:** ☒ En contención ☐ En recuperación ☐ Listo para cierre
- **Insumos:** `01-ficha-incidente.md`, `02-evaluacion-severidad.md`, `03-notificacion-anpd.md`, `03-comunicacion-titulares.md`, `03-aviso-cnsd.md`

> Todas las acciones técnicas son **recomendaciones** para el equipo de TI y los especialistas. El agente no ejecuta nada. No se recomienda pagar el rescate, negociar con el atacante ni ninguna acción ofensiva. Cualquier decisión sobre contactar al atacante corresponde a la alta dirección, con asesoría legal y especializada.

## 1. Plan de respuesta

### 1.1 Contención
| # | Acción | Plazo | Responsable sugerido | ¿Afecta evidencia? |
|---|---|---|---|---|
| C1 | Aislar de la red (cable y Wi-Fi) las 6 PC afectadas y la PC de facturación, **sin apagarlas** | Inmediata | Jefe de TI | No, si no se apagan. Apagarlas hace perder la memoria volátil |
| C2 | Desconectar físicamente el disco de respaldo del servidor; no montarlo en otro equipo de producción. Rotularlo y guardarlo bajo custodia | Inmediata | Jefe de TI | Mínimo; registrarlo en la cadena de custodia |
| C3 | Barrido del resto de la red (otras PC y servidores) en busca de archivos `.lck` o notas de rescate; aislar lo que aparezca | Inmediata | TI | No |
| C4 | Desde un equipo limpio: deshabilitar o restablecer la cuenta de la persona de facturación y las cuentas administrativas (dominio, servidor, sistema de historias clínicas, acceso remoto) | Inmediata | TI | Exportar antes los logs de autenticación |
| C5 | Bloquear el remitente y el dominio del correo "factura pendiente", buscar el mismo mensaje en otros buzones y ponerlo en cuarentena (conservando una copia como evidencia) | Inmediata | Administrador de correo | Conservar el correo original con cabeceras |
| C6 | Cortar los accesos remotos (VPN, escritorio remoto, accesos de proveedores) hasta revisarlos | Corto plazo | TI | Exportar antes los logs |
| C7 | Mantener y formalizar la contingencia en papel; definir cómo se registrará luego en el sistema (control 5.29) | Corto plazo | Dirección médica / admisión | No |
| C8 | Vigilar posibles publicaciones de los datos por fuentes legítimas (por ejemplo, aviso de autoridades o de un proveedor especializado), sin interactuar con el atacante | Corto plazo | Responsable de seguridad / proveedor externo | No |

### 1.2 Preservación de evidencia (ISO/IEC 27037; ISO/IEC 27002 5.28)
| Evidencia | Fuente | Método de preservación | Hash / integridad | Custodio |
|---|---|---|---|---|
| Memoria RAM | PC de facturación y las 6 PC afectadas (encendidas) | Captura de memoria con herramienta forense antes de apagar | SHA-256 de cada volcado | `[Responsable forense]` |
| Imagen de disco | PC de facturación, servidor de archivos, servidor de base de datos | Imagen bit a bit, con bloqueador de escritura cuando corresponda | SHA-256 del original y de la copia | `[ ]` |
| Disco de respaldo | Disco conectado al servidor | Imagen forense antes de cualquier intento de restauración | SHA-256 | `[ ]` |
| Correo "factura pendiente" y su adjunto | Servidor o buzón de correo | Exportar en formato original (.eml/.msg) con cabeceras completas | SHA-256 | `[ ]` |
| Alerta del antivirus (28/09 23:50) y su historial | Consola del antivirus | Exportación y captura con fecha | SHA-256 | `[ ]` |
| Logs de acceso a los datos (art. 46.3), del sistema operativo, del firewall, del proxy/DNS y de la VPN | Servidores y equipos de red | Exportar antes de que roten; guardar en un medio de solo lectura | SHA-256 | `[ ]` |
| Nota de rescate | Pantallas y archivos de nota | Foto con fecha y copia del archivo | SHA-256 | `[ ]` |
| Muestra de archivos cifrados `.lck` | Servidor | Copia en medio aislado | SHA-256 | `[ ]` |

**Registro de cadena de custodia:** por cada elemento, anotar quién lo recolectó, la fecha y hora, el equipo de origen, la ubicación de almacenamiento, el hash y cada traspaso (de quién a quién, cuándo y por qué). Primero se preserva y después se erradica.

### 1.3 Erradicación
- Identificar la variante de ransomware y los mecanismos de persistencia (tareas programadas, servicios, cuentas creadas) con el análisis forense.
- Reinstalar desde cero (no "limpiar") los equipos y servidores comprometidos, con imágenes de confianza.
- Restablecer todas las credenciales de la organización, empezando por las privilegiadas, y revocar sesiones y tokens.
- Cerrar el vector: filtrado de adjuntos en el correo, revisar por qué el antivirus alertó pero no bloqueó y aplicar los parches pendientes.
- Evaluar la denuncia ante la autoridad policial competente `[VERIFICAR unidad especializada]`.

### 1.4 Recuperación (ISO/IEC 27002 8.13; art. 48 del reglamento)
- **Fuente de restauración:** el respaldo completo de hace 3 semanas, si la imagen forense confirma que no está cifrado. Si está comprometido, buscar otras fuentes: el proveedor del sistema, copias en la nube o exportaciones parciales `[NO INDICADO]`.
- **Verificación de integridad:** antes de restaurar, revisar el respaldo en un entorno aislado (sin malware, sin archivos `.lck`, base consistente). Restaurar primero en un entorno de prueba.
- **Datos faltantes:** reconstruir las 3 semanas sin respaldo a partir de los registros en papel, laboratorio y facturación, y documentar qué no se pudo recuperar.
- **Criterio para volver a operación normal:** equipos reconstruidos, credenciales renovadas, MFA activo en los accesos administrativos y remotos, respaldo nuevo fuera de línea verificado y monitoreo reforzado de al menos `[definir días]` sin indicadores de compromiso.

## 2. Análisis de causa raíz (5 porqués)
| Por qué | Respuesta | Hecho / inferencia |
|---|---|---|
| 1. ¿Por qué no se pueden usar las historias clínicas? | Porque un ransomware cifró el servidor y la base de datos | Hecho |
| 2. ¿Por qué pudo ejecutarse el ransomware? | Porque en la PC de facturación se abrió un adjunto malicioso y el antivirus alertó pero no lo detuvo | Hecho (alerta) / inferencia (que no lo bloqueara) |
| 3. ¿Por qué se propagó de la PC al servidor? | Porque probablemente la red no está segmentada y había credenciales con privilegios suficientes | Inferencia |
| 4. ¿Por qué nadie reaccionó a la alerta de las 23:50? | Porque no hay monitoreo fuera del horario ni un procedimiento de escalamiento de alertas | Inferencia, apoyada en el hecho de que "nadie la revisó" |
| 5. ¿Por qué no se puede restaurar con seguridad? | Porque el único respaldo tiene 3 semanas y está conectado permanentemente al servidor, sin copia fuera de línea ni verificación | Hecho |

- **Causa técnica:** ejecución de malware desde un adjunto de correo; probable falta de segmentación y de bloqueo de adjuntos; respaldo en línea y desactualizado.
- **Causa de proceso:** no hay monitoreo ni escalamiento de alertas de seguridad; la política de respaldos no cumple la regla de una copia fuera de línea con verificación de integridad (art. 48.1).
- **Causa humana:** apertura de un correo de phishing ("factura pendiente"), lo que sugiere falta de concienciación. No se busca culpar a la persona sino reforzar los controles.

## 3. Lecciones aprendidas (ISO/IEC 27002 5.27)
- **Qué funcionó:** el antivirus detectó el adjunto; el Jefe de TI desconectó el servidor y avisó al Oficial de Datos Personales en unos 85 minutos; la contingencia en papel mantuvo la atención.
- **Qué falló:** nadie atendió la alerta; el malware se propagó al servidor; el respaldo no estaba aislado ni actualizado; no consta un procedimiento formal de respuesta a incidentes.
- **Qué cambiaremos:** monitoreo y escalamiento de alertas, respaldos fuera de línea verificados, segmentación, MFA, capacitación contra phishing y un procedimiento de gestión de incidentes que incluya el reloj de 48 h.

## 4. Controles propuestos
| Control ISO/IEC 27002:2022 | Medida concreta | Causa que ataca | Prioridad | Responsable sugerido |
|---|---|---|---|---|
| 8.13 Copias de respaldo | Copias diarias, con al menos una fuera de línea o inmutable; pruebas de restauración periódicas (art. 48.1) | Respaldo en línea y desactualizado | Alta | TI |
| 8.7 Protección contra malware | Configurar el antivirus para bloquear y poner en cuarentena (no solo alertar); filtrado de adjuntos en el correo | Ejecución del adjunto | Alta | TI |
| 8.15 / 8.16 Registro y monitoreo | Alertas críticas con escalamiento 24/7 (interno o tercerizado); logs de acceso a los datos conservados 2 años (art. 46.3) | Alerta no revisada | Alta | Responsable de seguridad |
| 5.24 Planificación de la gestión de incidentes | Procedimiento formal, roles, contactos de la ANPD y del CNSD y plantillas de notificación | Respuesta improvisada; riesgo con el plazo de 48 h | Alta | Oficial de Datos Personales / seguridad |
| 6.3 Concienciación y formación | Capacitación y simulacros de phishing para el personal administrativo | Apertura del correo | Media | RR. HH. / seguridad |
| 8.5 Autenticación segura | MFA en cuentas privilegiadas, correo y accesos remotos | Uso de credenciales para propagarse | Alta | TI |
| 5.15 Control de acceso | Mínimo privilegio y revisión semestral de privilegios (art. 46.1) | Privilegios excesivos (inferencia) | Media | TI |
| 8.24 Uso de criptografía | Cifrar la base de historias clínicas y los respaldos | Exposición si hay extracción | Media | TI |
| 5.29 Seguridad durante una disrupción | Plan de continuidad clínica con procedimiento en papel y reingreso de datos | Interrupción de la atención | Media | Dirección médica |

## 5. Registro del incidente (art. 35, D.S. 016-2024-JUS; ISO/IEC 27701 6.13.1.5)
| Campo | Valor |
|---|---|
| Descripción | Ransomware con amenaza de publicación que cifró el servidor de archivos, la base del sistema de historias clínicas y 6 PC. Vector probable: phishing |
| Periodo del incidente | Desde el 28/09/2026 23:50 (estimado) hasta: en curso |
| Datos y titulares afectados | ~18 000 pacientes; identificación, contacto, salud (sensibles) y seguro |
| Efectos / consecuencias | Indisponibilidad total del sistema clínico; posible exposición de datos de salud; severidad Muy alta (SE = 5,75) |
| Quién reportó y cuándo | Jefe de TI, al Oficial de Datos Personales, el 29/09/2026 a las 08:40 |
| Notificación ANPD (fecha / no corresponde y por qué) | **Corresponde.** Borrador listo; fecha de envío `[PENDIENTE]`. Hora límite: 01/10/2026 07:15 |
| Comunicación a titulares (fecha / no corresponde y por qué) | **Corresponde.** Borrador listo; fecha `[PENDIENTE]` |
| Notificación CNSD (fecha / no corresponde) | **Corresponde.** Borrador listo; fecha `[PENDIENTE]` |
| Medidas adoptadas | Desconexión del servidor y contingencia en papel. Las demás medidas están propuestas (ver sección 1) |

## 6. Criterios de cierre
- [ ] Incidente contenido (todos los equipos afectados aislados; sin actividad maliciosa)
- [ ] Causa erradicada (equipos reconstruidos, credenciales renovadas, vector cerrado)
- [ ] Servicios y datos recuperados (pérdidas documentadas)
- [ ] Notificaciones realizadas (ANPD, titulares y CNSD), más la notificación complementaria con el resultado sobre la exfiltración
- [ ] Acciones correctivas asignadas con fecha
- [ ] Registro del art. 35 completo

---
*Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales.*
