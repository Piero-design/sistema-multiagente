# 03 · Notificación a la ANPD (art. 34.1 y 34.2) — BORRADOR

> **BORRADOR. No enviado.** Debe revisarlo y aprobarlo el ODP y el responsable de seguridad. Canal: formulario `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia]`.
> **Enviar antes de: 2026-10-13 17:55 (-05).** Hora actual: 09:00 (restan 8 h 55 min).

**Tipo de notificación:** inicial / parcial (se ampliará cuando el proveedor entregue información).
**Responsable del tratamiento:** Universidad Nacional de San Agustín (UNSA) — simulado.
**Encargado del tratamiento:** ProveedorEdu S.A.C. (hosting del Campus Virtual).

## 1. Naturaleza del incidente (art. 34.2 num. 1)
El 2026-10-11 a las 17:55 la UNSA fue informada por su encargado, ProveedorEdu S.A.C., de que el 2026-10-08 detectó un acceso no autorizado a un servidor compartido donde se aloja el Campus Virtual de la UNSA, y de que la copia de la base de datos de varios clientes, incluida la nuestra, "podría haber sido descargada". A la fecha **no está confirmado** si hubo descarga ni qué datos se llevaron; el proveedor no ha precisado el alcance. Se notifica de manera preventiva y se tratará como brecha de confidencialidad hasta descartarla.

- Tipo: confidencialidad (probable). Categoría: acceso no autorizado en un encargado.
- Entorno digital: sí.
- Fecha del hecho: 2026-10-08 (según el proveedor, hora desconocida). Toma de conocimiento de la UNSA: 2026-10-11 17:55.

**Tipos de datos:** nombres, DNI, correo institucional, escuela profesional, calificaciones, mensajes entre docentes y estudiantes, actividad en las aulas. Posible exposición de credenciales (forma de almacenamiento desconocida). No se han identificado datos sensibles; los mensajes están pendientes de revisar.
**Titulares afectados (aprox.):** hasta **22 000** (estudiantes y docentes); posible presencia de menores de edad `[VERIFICAR]`.

## 2. Punto de contacto (art. 34.2 num. 2)
Dra. Mariela Quispe Huamaní, Oficial de Datos Personales · odp@unsa.example · 054-555-0301 / 999 000 301 (`contactos.md:5`).

## 3. Posibles consecuencias (art. 34.2 num. 3)
- Suplantación de identidad y fraude usando nombre + DNI.
- Phishing dirigido a estudiantes y docentes (correo institucional).
- Acceso indebido a cuentas si las contraseñas están expuestas o se reutilizan en otros servicios.
- Divulgación de calificaciones y mensajes privados; daño reputacional y emocional, en especial a menores.

## 4. Medidas adoptadas o propuestas (art. 34.2 num. 4)
Adoptadas: cambio de clave del administrador del Campus (11-oct).
Propuestas (indicar fecha prevista al aprobar): [ ] restablecimiento obligatorio de contraseñas y cierre de sesiones; [ ] MFA para administradores; [ ] requerimiento formal de informe forense al proveedor; [ ] comunicación a titulares con recomendaciones; [ ] monitoreo de inicios de sesión anómalos; [ ] revisión contractual del encargo (art. 36); [ ] aviso al CNSD.

## 5. Justificación de la demora (art. 34.1) — incluir solo si se envía después de las 48 h
El hecho ocurrió el 2026-10-08; el encargado comunicó el 2026-10-11 a las 17:55, cerca de tres días después, pese al deber de aviso inmediato (art. 36). La UNSA no tuvo conocimiento antes. Se adjunta el correo del proveedor como sustento. `[ODP: decidir si se menciona aunque se envíe dentro del plazo]`

## 6. Información pendiente que se ampliará
Fecha y hora exactas del acceso, datos efectivamente descargados, cantidad real de titulares, estado de cifrado y de las contraseñas, y confirmación de que el atacante fue expulsado.

## Adjuntos sugeridos
Correo del proveedor (con cabeceras); `01-ficha-incidente.md`; `02-evaluacion-severidad.md`.
