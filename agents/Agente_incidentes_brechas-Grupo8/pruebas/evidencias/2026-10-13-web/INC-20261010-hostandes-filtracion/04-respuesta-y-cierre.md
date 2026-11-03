# 04 · Plan de respuesta y cierre — INC-20261010-hostandes-filtracion

> BORRADOR. No se ejecutó nada. Sin recomendaciones ofensivas. En caso de extorsión, no se recomienda pagar rescates.

## 1. Contención y erradicación (ISO 27035 / 27002 5.26)
| # | Acción | Responsable | Plazo sugerido |
|---|---|---|---|
| 1 | Restablecer todas las credenciales (admin, personal, apoderados) y sesiones; activar MFA; rotar claves de BD/API/SMTP | Seguridad / TI | Hoy |
| 2 | Pedir a HostAndes por escrito: hora y vector de la intrusión, bases y tablas afectadas, confirmación de descarga, cifrado y hash de contraseñas, logs de acceso, IoC, medidas de contención, contacto técnico y fecha de su aviso a la ANPD | ODP | Hoy |
| 3 | Revisar los logs propios de la aplicación (art. 46.3, retención ≥ 2 años) en busca de accesos anómalos, exportaciones o inicios de sesión sospechosos desde el 10/10 | Seguridad | 24 h |
| 4 | Vigilar abuso: correos o llamadas de phishing a apoderados, pagos fraudulentos | Administración | Continuo |
| 5 | Evaluar migrar o aislar la plataforma si HostAndes no demuestra contención | Dirección | 72 h |

## 2. Evidencia (ISO 27037, control 5.28)
Conservar el correo original de HostAndes con cabeceras, bitácora de acciones con hora y responsable, capturas del cambio de claves, copias de los logs con hash y cadena de custodia, y la correspondencia posterior con el proveedor.

## 3. Recuperación
Disponibilidad no afectada según lo reportado. Confirmar integridad de la BD comparando contra el respaldo (control 8.13) `[VERIFICAR existencia de respaldo]`.

## 4. Comunicaciones (ver archivos 03)
ANPD y CNSD antes de la hora límite; titulares dentro del mismo plazo del art. 34.3. Registrar fecha, hora y constancia de cada envío (ISO 27701 6.13.1.5).

## 5. Causa raíz preliminar y lecciones (ISO 27002 5.27)
- Causa inmediata: intrusión en infraestructura compartida del proveedor. Causa contributiva por confirmar.
- Brechas de control probables `[VERIFICAR]`: contrato de encargo sin cláusula de notificación inmediata (art. 36) ni SLA de incidentes; sin evidencia de cifrado de BD y contraseñas (8.24); sin MFA (8.5); sin revisión de proveedores (5.19–5.22 `[VERIFICAR, no están en knowledge/]`); posible falta de documento de seguridad (art. 47) y de procedimiento de incidentes.
- Mejoras: cláusulas contractuales y auditoría al encargado; cifrado en reposo; MFA; minimización y retención de datos; procedimiento interno de incidentes con responsable designado y plantillas; simulacro.

## 6. Criterios de cierre
- [ ] Notificación ANPD y aviso CNSD enviados y con constancia.
- [ ] Titulares comunicados.
- [ ] Informe técnico de HostAndes recibido y contrastado.
- [ ] Credenciales rotadas y MFA activo.
- [ ] Causa raíz confirmada, acciones correctivas con responsable y fecha.
- [ ] Registro del incidente completo (art. 35): hechos, efectos y medidas.
- [ ] Revisión de contrato con HostAndes y decisión sobre su continuidad.
