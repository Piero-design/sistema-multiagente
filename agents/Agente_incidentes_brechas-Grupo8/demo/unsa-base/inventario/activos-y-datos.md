# Inventario de activos y datos personales — UNSA (ESCENARIO SIMULADO)

> Estructura y sistemas según fuentes públicas (`FUENTES.md`). Las columnas marcadas **Simulado** (volúmenes internos, ubicación, cifrado, respaldos y controles) son inventadas para la prueba. Responsable del banco de datos: Universidad Nacional de San Agustín de Arequipa. Versión del documento de seguridad (simulada): 2025-09.

## Sistemas

| ID | Sistema (nombre público) | Responsable | Ubicación (simulado) | Cifrado (simulado) | Respaldo (simulado) |
|---|---|---|---|---|---|
| S-01 | **Sistema Académico (SISACAD)**: libretas, notas parciales, sistema docente. Servidores `SRV-SISACAD-APP` y `SRV-SISACAD-DB` | Oficina Universitaria de Informática y Sistemas (OUIS) | Centro de Datos | No | NAS `NAS-BKP-01` conectado permanentemente (semanal; último completo 2026-10-04) |
| S-02 | Carpeta de actas escaneadas (`SRV-ARCH`) | Oficina responsable del registro académico `[VERIFICAR denominación]` | Centro de Datos | No | Mismo NAS |
| S-03 | **Aulas Virtuales** (aulavirtual.unsa.edu.pe; pregrado por semestre y posgrado) | OUIS | Alojamiento por un proveedor externo (**hipotético**; no hay información pública sobre quién lo aloja) | Desconocido | Del proveedor (hipotético) |
| S-04 | **Portal de admisión** (admision.unsa.edu.pe) y resultados de admisión y CEPRUNSA | Dirección Universitaria de Admisión / OUIS | Servidor web `SRV-WEB-ADM` | No | Ninguno |
| S-05 | Fichas del **Apoyo Psicopedagógico** y del servicio social | Dirección de Bienestar Universitario | Laptops institucionales y carpeta local | No | Ninguno |
| S-06 | Planillas del personal y régimen CAS | Unidad de Recursos Humanos | Hojas de cálculo y sistema de planillas | No | Parcial |
| S-07 | **Correo institucional** (mail.unsa.edu.pe) | OUIS | Servicio del proveedor `[VERIFICAR]` | Sí | Proveedor |
| S-08 | **Matrícula en línea** (matricula.unsa.edu.pe) | OUIS | Servidor web `SRV-WEB-MAT` | No | Ninguno |
| S-09 | **Trámite Documentario** y pagos **UNSAPay** | OUIS | Servidores de la OUIS | No | Parcial |

## Bancos de datos personales

| Tratamiento | Titulares | Origen de la cifra | Datos | ¿Sensibles? | Sistema |
|---|---|---|---|---|---|
| Estudiantes y egresados | **más de 24 000 activos** y 61 000 históricos | Activos: **público**. Históricos: simulado | Nombres, DNI, fecha de nacimiento, domicilio, correo, teléfono, escuela profesional, notas, situación académica | Parcial (**menores de edad**: ~900 activos con 17 años o menos, simulado) | S-01, S-02 |
| Aulas Virtuales | **~25 000** usuarios (estudiantes y docentes) | Simulado | Nombres, DNI, correo, calificaciones, mensajes, actividad | No | S-03 |
| Postulantes a admisión | **~17 300 por proceso**; unos 45 000 registros de varios procesos | Por proceso: **público** (17 277 en 2026-II). Total: simulado | Nombres, DNI, correo, celular, colegio, puntaje, dirección y **tipo de discapacidad** (exoneración) | **Sí** (salud) y menores | S-04 |
| Ingresantes del proceso actual | 612 (grupo convocado a inducción) | Simulado; el total real es de hasta 2 450 vacantes (público) | Datos para el carné; condición (discapacidad, deportista) | Sí (salud) y ~40 menores | S-04 |
| Apoyo psicopedagógico y servicio social | **~4 200 fichas** (histórico); 150 del semestre | Simulado | Motivo de consulta (salud mental, violencia familiar), situación económica, notas de sesión | **Sí** (salud) y menores | S-05 |
| Personal docente y administrativo | **~1 400 docentes** (público) y 320 en régimen CAS (simulado) | Docentes: **público** | Nombres, DNI, cargo, cuenta bancaria, remuneración, descuentos | Parcial (financieros) | S-06 |

## Controles existentes (todo SIMULADO, con las carencias típicas)
- Autenticación del SISACAD: usuario y contraseña; sin MFA; **las cuentas de docentes jubilados no se dan de baja** de forma regular.
- Acceso remoto: VPN con usuario y contraseña; sin MFA ni bloqueo por intentos fallidos.
- Antivirus: consola local; las alertas llegan a `seguridad@unsa.example`, sin guardia de fin de semana.
- Registros de auditoría del SISACAD: se guardan 60 días (el art. 46.3 del reglamento exige mínimo 2 años).
- Última prueba de restauración del respaldo: nunca.
- Los archivos con datos personales se comparten por enlaces en la nube sin política de uso aprobada.
