# Estándares internacionales para la gestión de incidentes y brechas

> Resumen de trabajo para los skills. Las normas ISO son de pago: la numeración de controles corresponde a las ediciones indicadas. **Responsable de validar contra el texto de cada norma: Investigación (ver `docs/reparto-equipo.md`).**

## 1. ISO/IEC 27035 — Gestión de incidentes de seguridad de la información
Es la **columna vertebral** del agente: cada skill implementa una o más fases.

| Parte | Título | Uso en el proyecto |
|---|---|---|
| ISO/IEC 27035-1:2023 | Principios y proceso | Define el ciclo de 5 fases (abajo) |
| ISO/IEC 27035-2:2023 | Guías para planificar y preparar la respuesta | Roles (equipo de respuesta, punto de contacto), política, plantillas de reporte |
| ISO/IEC 27035-3:2020 | Operaciones de respuesta a incidentes TIC | Detalle de contención, erradicación y recuperación |

### Fases del proceso (ISO/IEC 27035-1:2023) y skill que las cubre

| Fase | Qué se hace | Skill |
|---|---|---|
| 1. Planificar y preparar | Política, equipo, procedimientos, herramientas | Fuera del alcance del agente (insumo: documento de seguridad, art. 47 del reglamento) |
| 2. Detectar y reportar | Recibir el reporte de un **evento** y registrarlo | `brecha-triaje` |
| 3. Evaluar y decidir | ¿El evento es un **incidente**? ¿Afecta datos personales? Clasificar y priorizar | `brecha-triaje`, `brecha-evaluacion-severidad` |
| 4. Responder | Contener, erradicar, recuperar, comunicar, recolectar evidencia | `brecha-notificacion`, `brecha-respuesta-cierre` |
| 5. Aprender lecciones | Causa raíz, mejoras a controles y al proceso | `brecha-respuesta-cierre` |

Conceptos clave:
- **Evento de seguridad:** ocurrencia que indica una posible vulneración o falla de controles.
- **Incidente de seguridad:** uno o varios eventos con probabilidad significativa de comprometer operaciones o amenazar la seguridad de la información.
- **Brecha de datos personales:** incidente que compromete la confidencialidad, integridad o disponibilidad de **datos personales** (en Perú: "incidente de seguridad de datos personales", ver `marco-normativo-peru.md`).

## 2. ISO/IEC 27001:2022 e ISO/IEC 27002:2022 — Controles del Anexo A
Perú la adopta como **NTP-ISO/IEC 27001:2022**, citada en el art. 48.2 del reglamento de la Ley 29733.

| Control | Nombre | Skill |
|---|---|---|
| 5.24 | Planificación y preparación de la gestión de incidentes | (preparación) |
| 5.25 | Evaluación y decisión sobre eventos de seguridad | `brecha-triaje`, `brecha-evaluacion-severidad` |
| 5.26 | Respuesta a incidentes de seguridad | `brecha-respuesta-cierre`, `brecha-notificacion` |
| 5.27 | Aprendizaje de los incidentes | `brecha-respuesta-cierre` |
| 5.28 | Recolección de evidencias | `brecha-respuesta-cierre` |
| 5.29 | Seguridad durante una disrupción | `brecha-respuesta-cierre` (ransomware, indisponibilidad) |
| 5.34 | Privacidad y protección de datos personales | todos |
| 6.8 | Reporte de eventos de seguridad | `brecha-triaje` |
| 8.13 | Copias de respaldo | `brecha-respuesta-cierre` (recuperación) |
| 8.15 / 8.16 | Registro (logs) y monitoreo | `brecha-triaje`, `brecha-respuesta-cierre` (investigación) |

Controles preventivos que suelen proponerse como lección aprendida: 5.15 control de acceso, 5.17 información de autenticación, 6.3 concienciación y formación, 6.7 trabajo remoto, 7.9 seguridad de activos fuera de las instalaciones, 8.1 dispositivos de usuario final, 8.5 autenticación segura, 8.7 protección contra malware, 8.12 prevención de fuga de datos, 8.22 segregación de redes, 8.23 filtrado web, 8.24 uso de criptografía.

## 3. ISO/IEC 27701 — Extensión de privacidad (PIMS)
Extiende ISO/IEC 27001/27002 para datos personales (PII).

| Edición 2019 | Requisito | Skill |
|---|---|---|
| 6.13.1.1 | Responsabilidades y procedimientos: incluir la notificación de brechas de PII en la gestión de incidentes | `brecha-notificacion` |
| 6.13.1.5 | Respuesta a incidentes: determinar si un incidente es una **brecha de PII**, notificar a autoridad y titulares cuando corresponda y **registrar** cada brecha (descripción, periodo, consecuencias, quién reportó, a quién se notificó, medidas) | `brecha-triaje`, `brecha-notificacion`, `brecha-respuesta-cierre` |
| B.8.x (encargado) | El encargado informa al responsable sin demora | `brecha-triaje` (rol del reportante) |

> `[VERIFICAR]` La **ISO/IEC 27701:2025** se publicó como norma independiente y reorganizó su numeración. Indicar en el informe qué edición se cita.

## 4. NIST SP 800-61 Rev. 3 (abril 2025)
*Incident Response Recommendations and Considerations for Cybersecurity Risk Management.* Alinea la respuesta a incidentes con las funciones del **NIST Cybersecurity Framework 2.0**:

| Función CSF 2.0 | Relación con la respuesta | Skill |
|---|---|---|
| Govern (GV) / Identify (ID) / Protect (PR) | Preparación y mejora continua | lecciones aprendidas |
| Detect (DE) | Detección y análisis de eventos adversos | `brecha-triaje` |
| Respond (RS) | Gestión, análisis, mitigación, reporte y comunicación del incidente | `brecha-evaluacion-severidad`, `brecha-notificacion`, `brecha-respuesta-cierre` |
| Recover (RC) | Restauración de activos y comunicación de la recuperación | `brecha-respuesta-cierre` |

La Rev. 2 (2012) usaba 4 fases: preparación → detección y análisis → contención, erradicación y recuperación → actividad post-incidente. Se mantiene como modelo didáctico en el skill de respuesta.

## 5. ISO/IEC 27037:2012 — Evidencia digital
Directrices para **identificar, recolectar, adquirir y preservar** evidencia digital. Principios: relevancia, confiabilidad, suficiencia; mantener **cadena de custodia** (quién, qué, cuándo, dónde, cómo, hash). Lo usa `brecha-respuesta-cierre`.

## 6. Severidad de brechas de datos personales
- **ENISA (2013)**, *Recommendations for a methodology of the assessment of severity of personal data breaches*. Ver `metodologia-severidad.md`.
- **EDPB, Directrices 9/2022** sobre notificación de violaciones de datos personales y **Directrices 01/2021** con ejemplos de casos. Referencia comparada útil para justificar cuándo comunicar a los titulares.

## 7. Correspondencia rápida

| Paso del agente | ISO/IEC 27035-1 | ISO/IEC 27002:2022 | ISO/IEC 27701:2019 | NIST 800-61r3 | D.S. 016-2024-JUS |
|---|---|---|---|---|---|
| Triaje | Detectar y reportar / Evaluar y decidir | 6.8, 5.25 | 6.13.1.5 | DE | art. III num. 16, art. 36 |
| Severidad | Evaluar y decidir | 5.25 | 6.13.1.5 | RS (análisis) | art. 34.1 |
| Notificación | Responder | 5.26 | 6.13.1.1, 6.13.1.5 | RS (reporte y comunicación) | arts. 34.1–34.5 |
| Respuesta y cierre | Responder / Aprender lecciones | 5.26, 5.27, 5.28, 5.29 | 6.13.1.5 (registro) | RS, RC | art. 35 |
