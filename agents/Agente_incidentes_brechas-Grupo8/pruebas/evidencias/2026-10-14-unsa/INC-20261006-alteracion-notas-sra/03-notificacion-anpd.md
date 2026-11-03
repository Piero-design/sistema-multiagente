# 03 · Notificación a la ANPD — BORRADOR (art. 34.1 y 34.2)

> **BORRADOR NO ENVIADO.** ESCENARIO SIMULADO. Debe revisarlo y enviarlo el Oficial de Datos Personales **antes del 2026-10-14 11:20 (-05:00)**.
> Canal: formulario de reporte de incidentes `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace]`.
> Usa los mismos datos para el CNSD (ver `03-aviso-cnsd.md`).

**Responsable del banco de datos:** Universidad Nacional de San Agustín (simulado).
**Banco de datos afectado:** Estudiantes y egresados (Sistema de Registro Académico, S-01).
**Tipo de notificación:** inicial, a completar con información adicional [VERIFICAR si el formulario permite ampliarla].

## 1. Naturaleza del incidente (art. 34.2 num. 1)
- **Descripción:** entre el 06/10/2026 22:41 y el 07/10/2026 00:41 se usó una cuenta de docente jubilado en 2024, nunca dada de baja, para modificar **23 notas** de estudiantes de la escuela profesional de Ingeniería de Sistemas en el SRA. Las acciones se hicieron fuera del horario laboral, desde un equipo de la red interna asociado a la secretaría de esa escuela.
- **Tipo:** alteración ilícita de datos personales (integridad). La confidencialidad no puede descartarse porque el SRA solo audita modificaciones.
- **Fecha de toma de conocimiento:** 12/10/2026 11:20 (bloqueo de la cuenta tras revisar la auditoría) `[VERIFICAR fecha/hora del reclamo del estudiante, que podría ser anterior]`.
- **Datos afectados:** nombres, DNI, escuela, notas y situación académica.
- **Titulares afectados:** 23 confirmados. Alcance en revisión: se verifican otras escuelas y la posible consulta de datos. El banco completo tiene ~28 000 activos y ~61 000 históricos (incluye ~900 menores activos).
- **Datos sensibles:** no identificados hasta ahora [VERIFICAR].

## 2. Punto de contacto (art. 34.2 num. 2)
Dra. Mariela Quispe Huamaní, Oficial de Datos Personales — odp@unsa.example — 054-555-0301 / 999 000 301 (datos ficticios del contexto).

## 3. Posibles consecuencias (art. 34.2 num. 3)
- Registros académicos falsos: aprobaciones indebidas, efectos en grados y títulos.
- Perjuicio para estudiantes que no participaron (cuestionamiento de su rendimiento, sanciones indebidas) y daño a la fe pública de los registros.
- Posible acceso a datos de otros estudiantes (en investigación).
- Riesgo de que los hechos se repitan con otras cuentas inactivas o compartidas.

## 4. Medidas adoptadas o propuestas (art. 34.2 num. 4)
**Adoptadas (verificado):** bloqueo de la cuenta el 12/10/2026 11:20.
**En curso / propuestas (pendientes de confirmar su ejecución):**
- Preservar logs, el equipo implicado y las actas firmadas; contrastar notas del SRA con actas y con el respaldo del 04/10.
- Revisar modificaciones de todas las escuelas y bloquear cuentas inactivas y compartidas.
- Restaurar las notas alteradas a su valor válido, con aprobación académica.
- Activar MFA, un procedimiento de baja de cuentas, ampliar la auditoría a consultas y aumentar la retención a 2 años.
- Investigación disciplinaria con Asesoría Jurídica.
- Comunicación a los titulares afectados.

## 5. Justificación (si se supera el plazo)
Solo si se envía después del 14/10 11:20: indicar los motivos y adjuntar sustento (art. 34.1). `[Completar]`

## Revisión humana antes de enviar
- [ ] Confirmar la hora de toma de conocimiento.
- [ ] Verificar la cifra (23) y si hay más titulares.
- [ ] Verificar que las medidas escritas como "adoptadas" lo estén realmente.
- [ ] Aprobación del ODP y de la Alta Dirección.
