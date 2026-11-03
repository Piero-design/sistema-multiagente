# Aviso al Centro Nacional de Seguridad Digital (CNSD) — INC-20260930-correo-equivocado-colegio

**Destinatario:** Centro Nacional de Seguridad Digital, para el Registro Nacional de Incidentes de Seguridad Digital
**Fundamento:** art. 34.5 del D.S. N.° 016-2024-JUS; D.U. N.° 007-2020 (Marco de Confianza Digital)
**Motivo:** el incidente se desarrolló mediante el entorno digital (correo electrónico institucional). Este aviso se hace **además** de la notificación a la ANPD.
**Canal:** `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace y si un mismo formulario cubre a la ANPD y al CNSD]`
**Plazo de referencia:** junto con la notificación a la ANPD, antes de **2026-10-02, 15:30 (-05:00)** `[VERIFICAR plazo propio del CNSD]`

## 1. Organización
- Colegio Los Andes — RUC `[PENDIENTE]` — sector educación (privado `[VERIFICAR]`)
- Punto de contacto: `[PENDIENTE nombre, correo, teléfono del Oficial de Datos Personales]`

## 2. Datos técnicos del incidente
| Campo | Valor |
|---|---|
| Categoría | Fuga o divulgación accidental (correo a destinatario equivocado) |
| Dimensión afectada | Confidencialidad |
| Vector | Correo electrónico saliente desde una cuenta institucional legítima hacia un dominio externo no autorizado |
| Intención maliciosa | No (error humano) |
| Activo | Hoja de cálculo con datos de 420 alumnos menores de edad y de sus apoderados (identificación, DNI, notas, celular, situación y monto de deuda de pensión) |
| Ocurrencia | 2026-09-29, 17:05 |
| Detección | 2026-09-30, 15:30 |
| Estado | En contención: eliminación solicitada al receptor, confirmación escrita pendiente |
| Compromiso de sistemas | No hay indicios de compromiso de cuentas ni de malware |

## 3. Medidas
- Adoptadas: solicitud telefónica de eliminación al receptor.
- Propuestas: requerimiento escrito con confirmación de eliminación; preservación del correo con cabeceras y del registro del servidor de correo; controles de verificación de destinatarios externos y de protección de adjuntos (ver `04-respuesta-y-cierre.md`).

## 4. Información pendiente
- Confirmación escrita del receptor; si el archivo fue abierto o reenviado.
- Protección del archivo (contraseña): NO INDICADO.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
