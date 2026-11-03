# Aviso al Centro Nacional de Seguridad Digital (CNSD) — INC-20260929-laptop-robada-financiera

**Destinatario:** Centro Nacional de Seguridad Digital, para el Registro Nacional de Incidentes de Seguridad Digital
**Fundamento:** art. 34.5 del Reglamento de la Ley N.° 29733 (D.S. N.° 016-2024-JUS) y D.U. N.° 007-2020 (Marco de Confianza Digital)
**Canal:** `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace y si el mismo formulario cubre ANPD y CNSD]`
**Plazo recomendado:** el mismo que el de la ANPD, **2026-10-01 21:00**

> **Por qué se genera:** existe duda razonable sobre si el incidente "se desarrolla en y/o mediante el entorno digital". El hecho es un robo físico, pero los datos están en soporte digital y quedó expuesta una sesión de correo institucional en la nube, que permite un posible acceso no autorizado por medios digitales. Siguiendo la regla "ante la duda, notificar", se prepara este borrador. **Decisión PENDIENTE del ODP y de asesoría legal** `[VERIFICAR]`.

## 1. Entidad reportante
- Cooperativa Misti Ahorro, RUC [PENDIENTE]
- Contacto: Oficial de Datos Personales [PENDIENTE: nombre, correo, teléfono]. Responsable de seguridad de la información [PENDIENTE]

## 2. Cronología
- Ocurrencia y toma de conocimiento: 29/09/2026, aproximadamente a las 21:00
- Reporte interno al ODP: 30/09/2026 09:10
- Notificación paralela a la ANPD: [PENDIENTE: fecha y hora]

## 3. Descripción técnica
- **Categoría:** robo de dispositivo de usuario final (laptop institucional), con riesgo asociado de acceso no autorizado a una cuenta de correo en la nube.
- **Activos:** laptop con Windows (contraseña de inicio de sesión; cifrado de disco **no confirmado**); archivo de hoja de cálculo exportado del sistema de créditos; sesión del correo institucional abierta en el navegador.
- **Datos personales:** identificación, contacto, financieros y datos sensibles (ingresos económicos) de unos 1 500 socios. Posible contenido adicional del buzón: en investigación.
- **Indicadores de compromiso:** ninguno identificado hasta ahora. Revisión de registros de acceso al correo en curso [PENDIENTE: resultado].

## 4. Impacto
- Confidencialidad: posible exposición a terceros desconocidos.
- Integridad: sin indicios de alteración.
- Disponibilidad: pérdida del equipo. Los datos originales se conservan en los sistemas internos [VERIFICAR].
- Severidad estimada (metodología ENISA): **Muy alta** (SE = 5,0) mientras no se confirme el cifrado.

## 5. Medidas
- Adoptadas: denuncia policial.
- En curso / propuestas: cierre de sesiones y cambio de credenciales con MFA; revisión de registros de acceso; verificación de cifrado y bloqueo/borrado remoto; comunicación a los titulares; política de cifrado obligatorio y restricción de descargas a portátiles.

## 6. Pendiente para actualización
- Estado de cifrado, resultado de la revisión de accesos al correo, número exacto de afectados y número de denuncia.

---
*Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación.*
