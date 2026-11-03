# 01 · Ficha de triaje — INC-20261008-campus-virtual-proveedor

> BORRADOR para revisión del Oficial de Datos Personales (ODP) y del responsable de seguridad. ESCENARIO SIMULADO (TIF). No se afirma que nada haya sido notificado.

## 1. Reloj (primero)
| Dato | Valor |
|---|---|
| Hecho según el proveedor | 2026-10-08 (hora desconocida): "acceso no autorizado a un servidor compartido" |
| **Toma de conocimiento de la UNSA (lectura principal)** | **2026-10-11 17:55 (-05)**: el Coordinador del Campus Virtual recibe el correo de ProveedorEdu (reportado en `job1791983211947.md:9`) |
| Escalamiento al ODP (referencia) | 2026-10-11 18:40 (`job1791983211947.md:7`). No es la fecha más temprana, no se usa |
| **Hora límite de 48 h (art. 34.1)** | **2026-10-13 17:55 (-05)** |
| Hora actual (dada por el usuario) | 2026-10-13 09:00 (-05) |
| **Tiempo restante** | **8 h 55 min** |

**Lectura más estricta (referencia, `[VERIFICAR con asesoría legal/lineamientos ANPD]`):** si se contara desde el conocimiento del proveedor (8-oct), las 48 h ya habrían vencido hacia el 10-oct. El proveedor es encargado y debía avisar "de forma inmediata" (art. 36); avisó ~3 días después. Se recomienda preparar, dentro de la notificación, una explicación de la demora y guardar el correo del proveedor como prueba. La UNSA no se tomó la lectura temprana porque no tenía forma de saberlo.

Nota: el reloj corrió desde el 11-oct 17:55 sin avisar a nadie más; ya van ~39 h. Cualquier retraso adicional agrava el riesgo.

## 2. Clasificación
| Campo | Resultado |
|---|---|
| ¿Evento o incidente? | **Incidente** de seguridad (acceso no autorizado reportado por el encargado; copia de BD "podría haber sido descargada") |
| ¿Datos personales? | **Sí** (nombres, DNI, correo, calificaciones, mensajes, actividad) |
| Clasificación | **Brecha (incidente de seguridad de datos personales) probable**: art. III num. 16. Pendiente confirmar que hubo exfiltración. Ante la duda se trata como brecha |
| Categoría (taxonomía) | **PRV** (incidente en proveedor) + **INT** (acceso no autorizado) |
| Tipo | **Confidencialidad** (probable). Integridad y disponibilidad: sin indicios `[VERIFICAR]` |
| Prioridad | **P2 Alta** (reloj de 48 h corriendo); escalar a P1 si se confirman credenciales en claro o publicación |
| Rol de la UNSA | **Responsable** del banco de datos; ProveedorEdu S.A.C. es **encargado**. La obligación de notificar es de la UNSA (arts. 34 y 36). Respuesta a la pregunta del Coordinador: **sí, es responsabilidad de la UNSA y corresponde evaluar y, muy probablemente, notificar** |

## 3. Hechos en tres niveles
### Reportado (por el Coordinador / el proveedor)
- ProveedorEdu detectó el 8-oct un acceso no autorizado a un servidor compartido (`job1791983211947.md:9`).
- La copia de la base de varios clientes, incluida la de la UNSA, "podría haber sido descargada" (:9).
- No precisan qué datos ni cuántos; recomiendan cambiar contraseñas (:9).
- El Coordinador cambió su clave de administrador; no se avisó a nadie más (:13).

### Verificado (contexto `demo/unsa-base`)
- El Campus Virtual (S-03) está alojado en servidor compartido externo de ProveedorEdu S.A.C. (`inventario/activos-y-datos.md:11`).
- Cifrado en reposo: **"Desconocido"**; respaldo "del proveedor" (`activos-y-datos.md:11`).
- Banco de datos Campus Virtual: ~22 000 usuarios; nombres, DNI, correo, calificaciones, mensajes, actividad; clasificado "No sensible" (`activos-y-datos.md:23`). Coincide con el reporte.
- El documento de seguridad no define procedimiento ni responsable de notificación a la ANPD (`politicas/documento-seguridad-extracto.md:19`); el plan vigente no tiene roles ni plazos (`politicas/plan-respuesta-incidentes.md:3-5`).
- Contactos de ODP, OTI, Asesoría Legal y proveedor: `inventario/contactos.md:5-9`.
- **No hay logs en este contexto** (`README.md:5`): no se pudo verificar la fecha del acceso, la exfiltración ni qué se descargó.

### Supuesto
- Que la copia descargada incluye todo el banco de 22 000 usuarios (peor caso razonable).
- Que el almacenamiento de contraseñas es débil o desconocido (el Coordinador lo ignora).
- Que entre los usuarios hay menores de edad (el inventario cuenta ~900 estudiantes de 17 años o menos en el SRA, no específicamente en el Campus) `[VERIFICAR]`.
- Que los mensajes docente-estudiante pueden contener información sensible `[VERIFICAR]`.

## 4. Acciones inmediatas de contención (propuestas, requieren aprobación)
1. Pedir hoy por escrito a ProveedorEdu (soporte 24 h) la información de la sección 5.
2. Forzar cambio de contraseñas de **todos** los usuarios y admins del Campus; revocar sesiones y tokens/API keys; activar MFA para administradores si la plataforma lo permite.
3. Alertar de phishing: los datos (nombres, DNI, correo institucional) permiten suplantación.
4. Verificar si el Campus Virtual usa el mismo usuario/clave que otros sistemas (SRA, correo) y reforzar vigilancia.
5. Preservar evidencia: el correo original del proveedor con cabeceras, y cualquier informe forense que entregue (ISO/IEC 27037).

## 5. Preguntas para el proveedor (exigir respuesta escrita)
- Fecha y hora exactas del acceso y de su detección; ¿sigue el atacante dentro?
- ¿Qué datos de la UNSA se descargaron realmente? ¿Cuántos titulares? ¿Había contraseñas, y con qué hash/sal?
- ¿Cifrado en reposo de la BD y de las copias? ¿Claves comprometidas?
- ¿Por qué se avisó 3 días después? ¿Se notificó a otras autoridades?
- ¿Se publicó o hay indicios de venta/uso de los datos?
- Informe forense, lista de IoC y medidas de remediación.

## 6. Siguiente paso
Pasa al paso 2 (severidad). Resultado: ver `02-evaluacion-severidad.md`.
