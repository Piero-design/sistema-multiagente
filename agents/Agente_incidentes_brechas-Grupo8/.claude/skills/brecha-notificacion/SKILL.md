---
name: brecha-notificacion
description: Redacta los borradores de notificación de una brecha de datos personales a la Autoridad Nacional de Protección de Datos Personales (ANPD), la comunicación a los titulares afectados en lenguaje claro y el aviso al Centro Nacional de Seguridad Digital, con el contenido mínimo del art. 34 del Reglamento de la Ley 29733 y control de plazos de 48 horas. Úsalo cuando se pida "notificar la brecha", "redactar el aviso a los afectados" o cuando la evaluación de severidad indique que hay que notificar.
---

# Skill: Notificación de brechas

Implementa la comunicación de la fase **Responder** de ISO/IEC 27035-1:2023, el control **5.26** de ISO/IEC 27002:2022 y los requisitos **6.13.1.1** y **6.13.1.5** de ISO/IEC 27701:2019 (notificación de brechas de PII), aplicando los **arts. 34.1 a 34.5 del D.S. 016-2024-JUS**.

## Cuándo se activa
- "Redacta la notificación a la ANPD", "prepara el correo para los afectados".
- `salidas/<ID>/02-evaluacion-severidad.md` concluye que hay que notificar o comunicar.

## Entradas
`01-ficha-incidente.md` y `02-evaluacion-severidad.md` de la carpeta del incidente. Si no existen, pide los datos mínimos del art. 34.2 antes de redactar.

## Pasos
1. **Confirmar destinatarios** según la evaluación: ANPD, titulares, CNSD. Genera solo los borradores que correspondan y explica por qué se omiten los demás.
2. **Notificación a la ANPD** con `plantilla-notificacion-anpd.md`. Debe contener, como mínimo (art. 34.2):
   1. naturaleza del incidente, tipos de datos y número aproximado de titulares;
   2. nombre y contacto del Oficial de Datos Personales u otro punto de contacto;
   3. posibles consecuencias;
   4. medidas adoptadas o propuestas para remediar y mitigar.
   Si se notifica después de 48 h, incluye la sección de **motivos de la demora**. Si falta información, usa la notificación **inicial** y anuncia una **complementaria**.
3. **Comunicación a los titulares** con `plantilla-comunicacion-titulares.md`: lenguaje sencillo y claro (art. 34.3), qué pasó, qué datos, qué hizo la organización, **qué puede hacer la persona** (cambiar contraseña, vigilar movimientos bancarios, desconfiar de llamadas que pidan datos) y a quién contactar. Sin tecnicismos, sin culpar al titular, sin minimizar.
4. **Aviso al CNSD** (si hubo entorno digital): mismo contenido técnico que a la ANPD, indicando que es para el Registro Nacional de Incidentes de Seguridad Digital (art. 34.5, D.U. 007-2020).
5. **Verificación de contenido.** Tabla final: cada elemento del art. 34.2 → ¿incluido? → sección.
6. **Entregar** en `salidas/<ID>/03-notificacion-anpd.md`, `03-comunicacion-titulares.md` y, si aplica, `03-aviso-cnsd.md`.

## Reglas
- Son **borradores**: el agente nunca envía nada.
- No incluyas datos personales de los afectados en los borradores; usa categorías y cantidades.
- No prometas resultados ("sus datos están a salvo") sin evidencia; no admitas responsabilidad legal: describe hechos.
- Lo desconocido se escribe como "en investigación" y se lista como pendiente para la notificación complementaria.
- El canal oficial va como referencia `[VERIFICAR vigencia]` (ver `knowledge/marco-normativo-peru.md`).
- Cierra cada borrador con: *"Borrador para revisión del Oficial de Datos Personales. No enviar sin aprobación."*
