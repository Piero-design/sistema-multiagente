# Ficha de incidente — INC-20260929-ransomware-clinica

> ID asignado con la fecha de ocurrencia/reporte (2026-09-29). La toma de conocimiento admite dos lecturas (ver sección 1); la fecha del ID es la de hoy.
> Los datos de la organización, personas e IP son ficticios (caso de demostración). No se copian datos personales de pacientes: solo categorías y cantidades.

- **Organización (responsable del tratamiento):** Clínica San Gabriel S.A.C. (Arequipa). RUC y código de inscripción del banco de datos: NO INDICADO.
- **Reportado por:** Jefe de TI (Marco Ayala Condori, `demo/clinica-san-gabriel/inventario/contactos.md:6`) al Oficial de Datos Personales — ¿Es encargado del tratamiento? **No** (es personal interno; no aplica el aviso inmediato del art. 36). Nota: SoftSalud S.A.C. (HCE) y NetAndes Perú (VPN) son proveedores; su condición de encargado y si tuvieron acceso a datos está `[VERIFICAR]`.
- **Canal de reporte:** correo del 2026-09-29 08:40 (`examples/entradas/caso-01-ransomware-clinica.md:7`).
- **Hora actual usada para el cálculo (dada por el usuario):** 2026-09-29 09:00 (-05:00).

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Correo con macro entregado a facturación (sandbox desactivado) | 2026-09-28 22:41 | Hecho — `logs/correo-gateway.log:4-5` |
| **Ocurrencia: apertura del adjunto y ejecución de PowerShell** | 2026-09-28 23:48 – 23:49 | Hecho — `correo-gateway.log:6`, `antivirus.log:2` |
| Alerta del antivirus enviada a TI (cuarentena falló) | 2026-09-28 23:50 | Hecho — `antivirus.log:3-4` |
| Acceso del intruso a SRV-HCE por RDP con admin local reutilizado | 2026-09-28 23:52 | Hecho — `auth-hce.log:3` |
| Creación de cuenta `svc_backup2` (administradores) | 2026-09-29 00:03 | Hecho — `auth-hce.log:5` |
| Volcado de la base y empaquetado de resultados de laboratorio | 00:31 – 02:04 | Hecho — `auth-hce.log:6-8` |
| **Salida de 3,4 GB a 203.0.113.9 (41 min)** | 2026-09-29 02:14 – ~02:55 | Hecho — `logs/firewall.log:3` |
| Fin de la sesión RDP del intruso | 2026-09-29 04:10 | Hecho — `auth-hce.log:10` |
| Cifrado de SRV-HCE (inicio estimado ~07:14) y SRV-ARCH | 07:20 y 07:24 | Hecho — `antivirus.log:7-8`; inicio por cálculo de 4 210 archivos en 6 min (inferencia) |
| **Toma de conocimiento — lectura A (estricta, más temprana)** | **2026-09-28 23:50** | Alerta recibida por TI y no atendida (`antivirus.log:4`; política "cuando hay tiempo": `politicas/documento-seguridad-extracto.md:19`) |
| Toma de conocimiento — lectura B (referencia) | 2026-09-29 07:15 | Admisión descubre el cifrado (`caso-01…md:9`) |
| Reporte al Oficial de Datos Personales | 2026-09-29 08:40 | Hecho — `caso-01…md:7` |
| **Hora límite de notificación (48 h, art. 34.1) — con lectura A** | **2026-09-30 23:50** | Calculada. Tiempo restante desde las 09:00 del 29/09: **38 h 50 min** |
| Hora límite con lectura B (solo referencia) | 2026-10-01 07:15 | Calculada. Restan 46 h 15 min |
| Plazo del rescate (72 h) | ~2026-10-02 07:15 | Inferencia: se asume que la nota apareció a las 07:15 |

Criterio: una alerta sin revisar no es por sí sola toma de conocimiento, pero la organización debió atenderla; se usa la lectura más temprana `[VERIFICAR con lineamientos ANPD o asesoría legal]`.

## 2. Descripción de lo ocurrido
Un correo de "factura pendiente" con macro (adjunto `.docm`) llegó sin análisis a facturación y fue abierto a las 23:48 del 28/09 en PC-FACT-01. El antivirus alertó a las 23:50, falló la cuarentena y su protección en tiempo real fue detenida por PowerShell. El atacante usó el administrador local reutilizado para entrar por RDP a SRV-HCE (23:52), creó una cuenta administradora, generó un volcado de la base (3,4 GB) y un archivo comprimido de resultados de laboratorio (3,4 GB), desactivó la rotación del log de auditoría y salió 3,4 GB hacia una IP externa. A las 07:14–07:24 cifró SRV-HCE y SRV-ARCH, incluido el disco de respaldo. Exige 3 BTC en 72 h y amenaza con publicar "la base de pacientes". La clínica atiende en papel.
Es un ataque con **doble extorsión**: el reporte lo trata solo como cifrado y dice "no sabemos si sacaron datos"; los logs indican **exfiltración probable** (inferencia fuerte, no confirmada en contenido).

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, "Evaluar y decidir"): hay vulneración de la seguridad (ransomware e intrusión) que ocasiona **pérdida de acceso/destrucción** de datos personales de salud y probable **exposición no autorizada** (salida de 3,4 GB, amenaza de publicación).

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad (probable) ☒ Integridad (datos cifrados, sin copia limpia) ☒ Disponibilidad (confirmada)
- **Categoría:** MAL — Código malicioso (ransomware con doble extorsión); con componente INT (intrusión, cuenta creada, movimiento lateral).
- **Entorno digital:** Sí → notificación adicional al CNSD (art. 34.5): **Sí**
- **Prioridad:** **P1 Crítica** — ransomware, datos sensibles amenazados con publicación, ataque posiblemente aún con acceso (cuenta `svc_backup2`, PC-FACT-01 en red).

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Historia clínica: identificación, contacto, diagnósticos, evolución, recetas (S-01) | **Sí** (salud) | Pacientes | Sí | 18 000 | Reporte + inventario (`activos-y-datos.md:21`) |
| Resultados de laboratorio e imágenes (S-02) | **Sí** (salud) | Pacientes (misma población) | Sí | ~18 000 | Inventario (`:22`); no estaba en el reporte |
| Datos de seguro (aseguradora, póliza) | No (identificación/financiero) | Pacientes asegurados | Posible | ~6 500 | Inventario (`:23`) |
| Facturación (nombre, DNI/RUC, dirección, montos) | No | Pacientes/clientes | Posible | ~12 000 | Inventario (`:24`); puede solaparse con los anteriores; terceros `[VERIFICAR]` |
| Personal (planillas, contratos, certificados médicos) | Parcial (salud) | Trabajadores | No | 74 | Inventario (`:25`); exfiltración no demostrada |
| Subconjunto de menores | **Sí** | Menores de edad | Sí | ~3 100 de los 18 000 | Inventario (`:26`) |

Distinción: **hecho** = cifrado de ambos servidores y volumen del inventario; **inferencia** = que lo exfiltrado incluya HCE y resultados; **NO INDICADO** = contenido real del archivo que salió.

## 6. Sistemas, activos y terceros involucrados
- S-01 SRV-HCE (sin cifrado en reposo) y S-02 SRV-ARCH (carpeta abierta a todo el dominio) — `inventario/activos-y-datos.md:9-10`.
- Disco de respaldo `BKP-01`, cifrado también (`logs/respaldos.log:5`).
- PC-FACT-01 (admin local, origen del acceso) y PC-ADM-01…05 (`activos-y-datos.md:11-12`); las 6 PC con el mensaje de rescate coinciden en número con estas (inferencia).
- IP de comando y control `198.51.100.77` (`antivirus.log:5`, `firewall.log:1-2`) e IP de destino `203.0.113.9` (`firewall.log:3`); cuenta `svc_backup2`.
- Terceros: SoftSalud S.A.C. (HCE), NetAndes Perú (VPN), Microsoft 365 (correo).

## 7. Medidas ya adoptadas (según el reporte)
- Cable de red del servidor desconectado (`caso-01…md:16`); no indica cuál de los dos servidores.
- Las PC siguen encendidas y en red (`:16`); atención en papel (`:19`).

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | Aislar de la red (sin apagar) PC-FACT-01, las otras 5 PC afectadas y el segundo servidor; no formatear ni reiniciar | Contener / preservar evidencia | Jefe de TI |
| 2 | Deshabilitar `svc_backup2`, cambiar la clave del Administrador local y de `postgres`; bloquear `198.51.100.77` y `203.0.113.9` en el firewall | Contener | Jefe de TI con SoftSalud/NetAndes |
| 3 | Exportar ya los logs del firewall (retención 30 días), antivirus, correo y HCE; conservar `BKP-01` sin montarlo ni escribir en él | Preservar evidencia | Jefe de TI |
| 4 | Activar al Oficial de Datos Personales, Gerencia y asesor legal; designar quién aprueba y envía la notificación a la ANPD antes del 30/09 23:50 | Informar | Oficial de Datos Personales |
| 5 | No negociar ni pagar sin decisión de la alta dirección con asesoría legal; activar continuidad asistencial en papel | Informar / continuidad | Gerencia |

## 9. Preguntas pendientes
1. ¿Qué servidor se desconectó y a qué hora exacta? ¿Quién más estuvo en contacto con los equipos?
2. ¿Qué contiene exactamente la nota de rescate (sitio, plazo, prueba de datos)? Conservar captura.
3. ¿Hay alguna copia de datos fuera de `BKP-01` (SoftSalud, nube, medios fuera de línea)?
4. ¿La nota de rescate o el atacante aportó muestras de datos que confirmen la exfiltración?
5. RUC y código de inscripción del banco de datos; ¿SoftSalud o NetAndes tuvieron acceso a los datos?

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
