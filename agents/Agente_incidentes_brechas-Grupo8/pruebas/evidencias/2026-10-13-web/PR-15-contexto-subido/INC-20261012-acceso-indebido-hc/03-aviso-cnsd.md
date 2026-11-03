# 03 · Aviso al CNSD — BORRADOR (no enviado)

> Art. 34.5: el incidente se desarrolló mediante entorno digital (SIS-HC) → notificar además al Centro Nacional de Seguridad Digital, para el Registro Nacional de Incidentes de Seguridad Digital (D.U. 007-2020). Canal: `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR si el mismo formulario cubre ANPD y CNSD]`. **Pendiente de aprobación; no enviado.**

| Campo | Contenido |
|---|---|
| Organización | Clínica Santa Rosa S.A., Arequipa `[RUC]` |
| Referencia | INC-20261012-acceso-indebido-hc |
| Punto de contacto | Dr. Pablo Cornejo, odp@santarosa.example, 054-555-0200 |
| Fecha de toma de conocimiento | 2026-10-12 `[hora exacta]` |
| Periodo del incidente | 2026-10-01 a 2026-10-10 (último acceso en el log: 10/10 15:22) |
| Tipo | Acceso no autorizado / uso indebido interno (INS) — confidencialidad |
| Activo afectado | SIS-HC (historias clínicas) |
| Datos y titulares | Datos de salud (incl. psiquiatría), DNI, dirección; 47 titulares de 6 200 |
| Vector | Cuenta interna de admisión (`admision3`, cuenta compartida) desde IP interna 10.1.0.23 |
| Indicadores | 47 consultas `VIEW` a HC distintas; sin copia/exportación evidenciada |
| Impacto | Exposición no autorizada de datos sensibles; sin evidencia de difusión |
| Contención | Trabajadora suspendida; cuenta a bloquear `[confirmar]`; logs preservados `[confirmar]` |
| Estado | En investigación; notificación a ANPD en curso `[actualizar]` |
