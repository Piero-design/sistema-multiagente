# 03 · Notificación a la ANPD — BORRADOR (NO ENVIADO)

> Borrador para revisión del ODP. Debe presentarse **antes del 2026-10-14 15:50 (-05:00)**. Canal: formulario `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`. Un humano debe validar y enviar. Nada de lo siguiente se ha notificado aún.

**Tipo de reporte:** Preliminar (se ampliará cuando HostAndes entregue información).

## Datos del responsable
- Razón social: Academia Pre Cima E.I.R.L., Arequipa. RUC: `[COMPLETAR]`
- Inscripción del banco de datos en el RNPDP: `[COMPLETAR/VERIFICAR]`

## 1. Naturaleza del incidente (art. 34.2 num. 1)
- Acceso no autorizado a un servidor compartido del proveedor de alojamiento HostAndes (encargado del tratamiento), detectado por el proveedor el 2026-10-10. El proveedor informó a la Academia el 2026-10-12 a las 15:50 que una copia de la base de datos de varios clientes, incluida la nuestra, "podría haber sido descargada". La descarga no está confirmada.
- Tipo de brecha: pérdida de confidencialidad. No hay indicios de alteración ni indisponibilidad (por confirmar).
- Toma de conocimiento de la Academia: 2026-10-12 15:50.
- Tipos de datos: nombres, DNI, fecha de nacimiento, colegio, dirección, teléfono y correo de apoderados, estado de pagos. Credenciales de usuarios de la plataforma: cifrado desconocido. No hay datos de tarjetas ni datos sensibles (según lo reportado).
- Titulares afectados (aproximado): 2 400 alumnos, muchos menores de edad, y sus apoderados `[CONFIRMAR cifra de apoderados]`.

## 2. Punto de contacto (art. 34.2 num. 2)
- Oficial de Datos Personales: `[NOMBRE]`, `[CORREO]`, `[TELÉFONO]`

## 3. Posibles consecuencias (art. 34.2 num. 3)
Suplantación de identidad o fraude con DNI y fecha de nacimiento, phishing o estafas dirigidas a apoderados (pagos), contacto indebido a menores usando dirección y teléfono, y acceso a cuentas si las contraseñas no estaban protegidas. Severidad evaluada: ALTA (SE = 3,0).

## 4. Medidas adoptadas o propuestas (art. 34.2 num. 4)
Adoptadas: cambio de la clave de la administradora (12/10).
Propuestas: restablecer todas las credenciales y activar MFA; exigir a HostAndes informe técnico (alcance, vector, hora, datos, cifrado, contención); preservar evidencia; comunicar a los titulares; monitorear uso indebido; revisar el contrato de encargo y las medidas del proveedor.

## 5. Otras comunicaciones
- Comunicación a titulares (art. 34.3): en preparación, ver `03-comunicacion-titulares.md`.
- Aviso al CNSD (art. 34.5): ver `03-aviso-cnsd.md`.
- Si se presenta después de las 48 h, añadir la justificación de la demora: `[REDACTAR SI APLICA]`.
