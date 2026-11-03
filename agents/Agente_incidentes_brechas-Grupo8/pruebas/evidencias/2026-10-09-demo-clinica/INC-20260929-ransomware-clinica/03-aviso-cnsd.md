# Aviso al Centro Nacional de Seguridad Digital (CNSD) — INC-20260929-ransomware-clinica

**Destinatario:** Centro Nacional de Seguridad Digital — Registro Nacional de Incidentes de Seguridad Digital (art. 34.5, D.S. 016-2024-JUS; D.U. N.° 007-2020)
**Canal:** `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`
**Tipo:** ☒ Inicial ☐ Complementario

## Organización y contacto
- Clínica San Gabriel S.A.C. (Arequipa), RUC `[COMPLETAR]`.
- Contacto: Dra. Lucía Paredes Quispe, Oficial de Datos Personales — odp@clinicasangabriel.example — 054-555-0101 / 999 000 101. Contacto técnico: Marco Ayala Condori, Jefe de TI — ti@clinicasangabriel.example — 999 000 102.

## Cronología
- 2026-09-28 22:41 correo con adjunto con macro entregado; 23:48 adjunto abierto en una estación de facturación.
- 2026-09-28 23:52 acceso remoto (RDP) a servidor de historias clínicas con credencial de administrador local reutilizada; 2026-09-29 00:03 creación de cuenta administradora `svc_backup2`.
- 2026-09-29 00:31–02:04 volcado de base de datos y archivo comprimido de resultados; 02:14–~02:55 salida de unos 3,4 GB hacia una IP externa.
- 2026-09-29 07:14–07:30 cifrado de dos servidores y del disco de respaldo; detección por el personal a las 07:15.
- Notificación: `[COMPLETAR fecha y hora]`.

## Descripción técnica
Ransomware (familia indicada por el antivirus como `Ransom.Lock.A`; extensión `.lck`) con intrusión previa y probable exfiltración (doble extorsión). Vector inicial: documento Office con macro que lanzó PowerShell codificado, detuvo la protección en tiempo real del antivirus y estableció conexión con infraestructura externa. Movimiento lateral por RDP con administrador local reutilizado. Persistencia mediante cuenta `svc_backup2` en el grupo de administradores. Se desactivó la rotación del log de auditoría. Impacto: indisponibilidad total del sistema de historias clínicas y de archivos; el respaldo también fue cifrado. Demanda: 3 BTC en 72 h, con amenaza de publicar la base de pacientes.

## Indicadores de compromiso (sin datos personales)
| Tipo | Valor | Fuente |
|---|---|---|
| IP (comando y control probable) | 198.51.100.77:443 | `antivirus.log:5`, `firewall.log:1-2` |
| IP (destino de 3,4 GB) | 203.0.113.9:443 | `firewall.log:3` |
| Archivo adjunto | `Factura_F001-48213.docm` | `correo-gateway.log:4` |
| Cuenta creada | `svc_backup2` | `auth-hce.log:5` |
| Detección | `Trojan.Downloader.Macro`; `Ransom.Lock.A` | `antivirus.log:3,7` |
| Extensión de archivos cifrados | `.lck` | reporte |
| Hash de archivos | NO INDICADO `[COMPLETAR tras la preservación]` | |

(Las direcciones del caso son de rangos de documentación y ficticias.)

## Datos y personas afectadas
Datos personales de salud (sensibles) de aprox. 18 000 pacientes, incluidos aprox. 3 100 menores, y datos de seguro, facturación y personal. Notificación paralela a la ANPD en `03-notificacion-anpd.md`.

## Medidas
Servidor desconectado de la red; atención en papel; aislamiento de equipos, bloqueo de IP, deshabilitación de cuenta y preservación de evidencia propuestos. Investigación forense en curso. Pendiente: confirmar alcance de la exfiltración y publicar actualización complementaria.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
