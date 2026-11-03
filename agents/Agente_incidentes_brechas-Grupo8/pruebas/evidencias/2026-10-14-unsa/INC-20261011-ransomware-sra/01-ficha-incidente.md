# 01 · Ficha de triaje — INC-20261011-ransomware-sra

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. ESCENARIO SIMULADO (académico).
> Entrada: reporte del Jefe de la OTI (correo 2026-10-11 08:00). Contexto: `demo/unsa-ransomware`.

## 1. Reloj (lo primero)

| Concepto | Valor |
|---|---|
| Hora actual (dada por el usuario) | 2026-10-13 09:00 (-05:00) |
| Toma de conocimiento (lectura base) | **2026-10-11 06:40**: el personal de guardia ve la nota de rescate y los servidores caídos (reportado, correo OTI línea 9) |
| **Hora límite 48 h (lectura base)** | **2026-10-13 06:40** |
| Lectura más estricta (referencia) | 2026-10-11 05:12: alerta antivirus de ransomware enviada a `seguridad@unsa.example` (`antivirus.log:4`). Límite: 2026-10-13 05:12 |
| **Estado** | **PLAZO VENCIDO.** Pasaron 50 h 20 min desde las 06:40. Se excedió por **2 h 20 min** (3 h 48 min con la lectura estricta) |
| Consecuencia | Notificar **de inmediato** con justificación de la demora y sustento probatorio (art. 34.1). La alerta no es por sí sola toma de conocimiento, pero nadie la revisó por falta de guardia de fin de semana (`activos-y-datos.md:32`). Puede dar pie a la lectura estricta `[VERIFICAR con Asesoría Legal]` |
| Plazo de la extorsión (reportado) | 72 h desde la nota → aprox. **2026-10-14 06:40**. Quedan unas 21 h 40 min `[supuesto: la nota se vio a las 06:40]` |

Nota: el entorno indicó 2026-10-14 como fecha del día. Se usó 2026-10-13 09:00 por instrucción expresa del usuario. Con el 14 el atraso sería mayor.

## 2. Clasificación

| Campo | Resultado |
|---|---|
| ¿Evento o incidente? | **Incidente de seguridad confirmado** (cifrado de servidores y respaldo, acceso no autorizado) |
| ¿Datos personales? | **Sí. Brecha de datos personales** (art. III num. 16: destrucción/pérdida y exposición no autorizada probable) |
| Tipo de brecha | **Disponibilidad** (total: servidores y respaldo cifrados) + **Confidencialidad** (exfiltración probable) |
| Categoría | **MAL** (ransomware con doble extorsión), con **INT** como vector (VPN con credenciales comprometidas) |
| Prioridad | **P1 Crítica** (ransomware, amenaza de publicación) |
| Rol de la UNSA | Responsable del banco de datos (obligación de notificar propia; no es encargado) |

## 3. Hechos en tres niveles

### Verificado (contexto)
| Hecho | Fuente |
|---|---|
| Fuerza bruta a la VPN desde 203.0.113.50: 198 intentos fallidos desde las 20:50 del 10-10, incluido `mquispe.admin` | `vpn.log:1-4` |
| Acceso VPN exitoso con `jperez.docente` a las 21:14:08, y alerta de "inicio de sesión inusual" a la bandeja de seguridad | `vpn.log:5-6` |
| La VPN no bloquea por intentos fallidos | `vpn.log:7` |
| Sesión RDP como `Administrador` (contraseña local compartida) hacia SRV-SRA-APP desde 10.9.0.14, a las 21:30 | `sra-auth.log:1` |
| Se crea la cuenta `svc_mant` con grupo Administradores, a las 22:05 | `sra-auth.log:2` |
| `pg_dump sra_prod` de 5,1 GB (23:40-00:05) y exportación de actas `actas.7z` de 5,1 GB (00:09) | `sra-auth.log:3-5` |
| **5,1 GB salen a 198.51.100.200:443 durante 52 min desde las 00:12:30**, y 2,0 MB a las 21:40 | `firewall.log:2-3` |
| Se desactiva la rotación del log de auditoría a las 00:50 | `sra-auth.log:6` |
| Se desactiva la protección en tiempo real a las 04:48-04:49 | `antivirus.log:2-3` |
| BD cifrada 05:10; 3 980 archivos `.lck` en 5 min (SRV-SRA-DB); 27 400 en SRV-ARCH | `sra-auth.log:8`, `antivirus.log:4-5` |
| **El NAS de respaldos se montó en SRV-SRA-DB y el 100 % de sus archivos está cifrado.** Sin snapshots ni copias offline | `respaldos.log:3-4` |
| El último respaldo bueno (2026-10-04) es el que se cifró. Nunca se probó la restauración | `respaldos.log:2`, `activos-y-datos.md:34` |
| Sin cifrado en reposo en S-01 y S-02, sin MFA, sin guardia de fin de semana, auditoría de 60 días (el art. 46.3 exige 2 años) | `activos-y-datos.md:9-10, 31-33` |
| 28 000 titulares activos y 61 000 históricos; unos 900 menores de edad | `activos-y-datos.md:22` |
| No hay procedimiento de notificación a la ANPD ni responsable definido | `documento-seguridad-extracto.md:19` |
| Los logs del firewall de más de 30 días se purgaron a las 06:00 del 10-11 (evidencia en riesgo) | `firewall.log:5` |

### Reportado (sin contrastar)
- La guardia vio la caída y la nota a las 06:40; la extorsión pide pago en 72 h y amenaza con publicar notas y datos.
- La OTI desconectó el servidor de la red. Las demás máquinas siguen encendidas.
- Mañana (lunes 2026-10-12) empezaba la matrícula. Ese día ya pasó, así que **el impacto en la matrícula debe verificarse**.

### Contradicciones y correcciones al reporte
- El reporte dice "no sabemos si sacaron información". El contexto lo contradice en parte: hay una exportación de 5,1 GB seguida de 5,1 GB salientes a una IP externa. **La exfiltración es probable**, aunque no se confirma el contenido.
- El reporte dice "no sabemos si el NAS se cifró". **Sí se cifró** (`respaldos.log:3`).
- El reporte solo menciona el servidor del SRA. El atacante tuvo cuenta de administrador con persistencia (`svc_mant`) y acceso VPN, por lo que **otros equipos pueden estar comprometidos**.
- Inconsistencia a investigar: la sesión RDP se cerró a las 04:40, pero a las 04:48 un PowerShell "lanzado por sesión RDP" desactivó el antivirus (`sra-auth.log:7` frente a `antivirus.log:2`). Esto sugiere otra sesión o persistencia vía `svc_mant`.

### Supuesto
- El contenido saliente es la BD y/o las actas. Los dos paquetes miden 5,1 GB y solo un envío de 5,1 GB consta `[VERIFICAR]`.
- No se verificó afectación de S-03 a S-08 (Campus, admisión, bienestar, planillas, matrícula en línea). Admisión y bienestar contienen datos de salud, así que hay que confirmarlo cuanto antes.

## 4. Línea de tiempo (2026, hora local)

| Fecha y hora | Evento | Fuente |
|---|---|---|
| 10-10 20:50 | Inicia fuerza bruta a la VPN | `vpn.log:1` |
| 10-10 21:14 | Login VPN exitoso y alerta sin revisar | `vpn.log:5-6` |
| 10-10 21:30 | RDP como Administrador al SRA | `sra-auth.log:1` |
| 10-10 22:05 | Se crea `svc_mant` (administrador) | `sra-auth.log:2` |
| 10-10 23:40 a 10-11 00:09 | Volcado de BD y exportación de actas | `sra-auth.log:3-5` |
| 10-11 00:12 | 5,1 GB salen a 198.51.100.200 | `firewall.log:3` |
| 10-11 00:50 | Se desactiva la rotación del log de auditoría | `sra-auth.log:6` |
| 10-11 04:48 | Se desactiva el antivirus | `antivirus.log:2` |
| 10-11 05:10-05:15 | Cifrado de BD y actas | `sra-auth.log:8`, `antivirus.log:4-5` |
| 10-11 05:12 | Alerta de ransomware a la bandeja de seguridad (sin revisar) | `antivirus.log:4` |
| 10-11 05:30 | Cifrado del NAS de respaldos | `respaldos.log:3` |
| **10-11 06:40** | **Toma de conocimiento (guardia)** | reportado |
| 10-11 08:00 | Correo del Jefe OTI al Oficial de Datos Personales | reporte |
| **10-13 06:40** | **Vence el plazo de 48 h** | cálculo |
| 10-13 09:00 | Hora actual: plazo excedido | dato del usuario |

## 5. Alcance preliminar

| Dato | Cantidad | Fuente |
|---|---|---|
| Estudiantes y egresados | 28 000 activos y 61 000 históricos (hasta 89 000 titulares, puede haber solapamiento) | `activos-y-datos.md:22` |
| Menores de edad | unos 900 activos | `activos-y-datos.md:22` |
| Tipos de dato | nombres, DNI, fecha de nacimiento, domicilio, correo, teléfono, escuela, notas, situación académica; actas escaneadas | inventario y reporte |
| Datos sensibles confirmados | Ninguno confirmado en S-01/S-02. Las actas escaneadas pueden contener otros datos `[VERIFICAR]` | — |

Los afectados se manejan por categorías y cantidades. El reporte no trae datos personales reales de titulares.

## 6. Pregunta pendiente

Ninguna impide avanzar. La hora actual fue indicada.
