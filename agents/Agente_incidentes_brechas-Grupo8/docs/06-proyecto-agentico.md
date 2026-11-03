# Etapa 6 — Proyecto agéntico

**Objetivo:** integrar todo en una solución funcional. **Resultado: proyecto agéntico.**

## Solución integrada

| Capa | Componentes |
|---|---|
| Conocimiento | `knowledge/` (D.S. 016-2024-JUS, ISO/IEC 27035/27002/27701, NIST SP 800-61r3, ENISA) |
| Skills | `brecha-triaje`, `brecha-evaluacion-severidad`, `brecha-notificacion`, `brecha-respuesta-cierre` |
| Agente | `agente-incidentes-brechas` |
| Automatización | Comando `/gestionar-incidente` |
| Casos de prueba | `examples/entradas/` (4 casos) |
| Resultados | `salidas/<ID>/` |

## Escenarios de demostración y resultado esperado

### Caso 1 — Ransomware en una clínica (caso retirado del repositorio; su evidencia sigue en `pruebas/evidencias/`)
- Triaje: **brecha** de disponibilidad + probable confidencialidad (amenaza de publicación), categoría MAL, **P1**, entorno digital.
- Severidad: DPC 4 (salud) · EI 1 · CB alta con intención maliciosa → **Muy alta**.
- Notificación: **ANPD** (datos sensibles, gran número), **titulares** (perjuicio evidente) y **CNSD** (entorno digital). Hora límite 48 h desde el 29/09 a las 07:15.
- Respuesta: aislar sin apagar, preservar memoria y disco, proteger el respaldo (estaba conectado), no recomendar el pago, señalar la alerta del antivirus no atendida como causa de proceso.

### Caso 2 — Excel enviado a un tercero equivocado (`caso-02-correo-equivocado-colegio.md`)
- Triaje: **brecha** de confidencialidad, FUG, datos de **menores** y deudas. Conocimiento: 30/09 a las 15:30 (no el envío del 29/09).
- Severidad: DPC 3 (deuda de pensión = dato financiero) +1 (menores) = 4 · EI 1 · CB 0,25 → **SE 4,25, Muy alta**. Sin el ajuste por menores: 3,25, Alta.
- Notificación: evaluar "gran número" (420) y los datos de deuda; ante la duda, **notificar a la ANPD**. Comunicar a los apoderados: no hay confirmación escrita de la eliminación, así que no aplica el art. 34.4.
- Lecciones: control 8.12 (prevención de fuga de datos), verificación del destinatario.

### Caso 3 — Laptop robada sin cifrado confirmado (`caso-03-laptop-robada-financiera.md`)
- Triaje: brecha probable, FIS; el cifrado es `NO INDICADO`, por lo que se trata como no cifrada hasta confirmar.
- Severidad: ingresos (dato **sensible** en Perú) → notificación a la ANPD obligatoria.
- Respuesta: cerrar la sesión de correo remotamente, bloqueo y borrado remoto, revisar BitLocker en todo el parque. Controles 8.1, 8.24 y política de descarga de bases.

### Caso 4 — Phishing bloqueado (`caso-04-phishing-bloqueado.md`) — **caso de control**
- Triaje: **evento sin incidente**. No hubo clics ni vulneración. Se registra y se cierra.
- No pasa a severidad ni a notificación. Valida que el agente **no sobrerreacciona**.

## Criterios de éxito

| Criterio | Cómo se verifica |
|---|---|
| El agente enruta bien | Caso 4 se cierra en el triaje; casos 1 a 3 llegan a la notificación |
| Calcula bien la hora límite | Caso 2: desde la toma de conocimiento, no desde el envío |
| Notificaciones con el contenido mínimo del art. 34.2 | Tabla de verificación del skill de notificación |
| Severidad reproducible | Dos integrantes recalculan SE con la justificación y obtienen el mismo nivel |
| No hay plazos ni artículos inventados | Revisión contra `knowledge/marco-normativo-peru.md` |
| No recomienda acciones que destruyan evidencia | Caso 1: no sugiere apagar ni formatear antes de preservar |

## Limitaciones
- La ANPD aún no fija umbrales para "gran volumen" ni "gran número" `[VERIFICAR lineamientos]`: el agente aplica el criterio prudente.
- Las normas ISO son de pago: la numeración se tomó de las ediciones citadas y debe validarse.
- Analiza solo lo que dice el reporte; no investiga sistemas reales ni accede a logs.
- No sustituye al Oficial de Datos Personales, al equipo de TI ni a la asesoría legal.

## Trabajo futuro
- Integración con el buzón de reportes y el sistema de tickets.
- Alertas automáticas de vencimiento del plazo.
- Skill de simulacros (ejercicios *tabletop*) basados en ISO/IEC 27035-2.
