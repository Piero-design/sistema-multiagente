# 02 · Evaluación de severidad — INC-20261009-sqli-admision

> BORRADOR para revisión del ODP. Metodología: ENISA 2013 (`knowledge/metodologia-severidad.md`) + art. 34.1 del D.S. 016-2024-JUS.

## 1. Puntuación SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **4** | Base 4: dato de salud (tipo de discapacidad) = sensible. Ajuste +1 por menores y por perfilado (identidad+dirección+salud+colegio) → topado en 4 |
| EI | **1** | Nombre completo + DNI + correo + celular + dirección: identificación directa |
| CB confidencialidad | **+0,5** | Datos publicados en canal público (muestra) y amenaza de publicar el resto: destinatarios desconocidos |
| CB integridad | 0 | Solo `SELECT` observado; [VERIFICAR] ausencia de escrituras |
| CB disponibilidad | 0 | Datos no destruidos. La indisponibilidad del portal es por contención, no pérdida de datos. Sin respaldo: riesgo si hubiera alteración |
| CB intención maliciosa | **+0,5** | Ataque deliberado y extorsión |
| **CB total** | **1,0** | |

**SE = 4 × 1 + 1,0 = 5,0 → MUY ALTA** (consecuencias graves o potencialmente irreversibles: discriminación por discapacidad, suplantación, acoso a menores, phishing dirigido).

## 2. Regla de decisión (art. 34 D.S. 016-2024-JUS)
| Pregunta | Respuesta | Resultado |
|---|---|---|
| ¿Datos sensibles? | Sí (discapacidad) | Notificar a la ANPD (34.1) |
| ¿Grandes volúmenes / gran número? | Sí (~18 000 titulares, 3 procesos) [no hay umbral oficial; ante la duda, notificar] | Notificar (34.1) |
| ¿Perjuicio evidente a otros derechos? | Sí probable (SE ≥ 3; discapacidad y menores; publicación y extorsión) | Notificar y **comunicar a titulares** (34.1, 34.3) |
| ¿Entorno digital? | Sí (inyección SQL vía web) | **Notificar al CNSD** (34.5) |
| ¿Excepción 34.4? | No: el incidente no fue superado totalmente (datos ya fuera de control) | No aplica |

## 3. Conclusión
- **Notificar a la ANPD: SÍ, urgente y fuera de plazo** (justificar la demora, art. 34.1).
- **Comunicar a titulares: SÍ** (34.3), con atención a menores (a través de padres/representantes) [VERIFICAR mecanismo legal].
- **Notificar al CNSD: SÍ** (34.5).
- **Documentar (art. 35): SÍ**.
- Infracción posible por no notificar a tiempo: grave (art. 133 num. 12). Rango de multa [VERIFICAR].

## 4. Factores que agravan / incertidumbres
- Alcance real posiblemente ~60 veces mayor que la muestra reportada (300 vs ~18 000).
- Posible incumplimiento previo de medidas de seguridad: sin cifrado, sin respaldo, sin alerta (art. 46, 48.1); logs a conservar (46.3).
- Si se publica la base completa, la severidad no disminuye; la muestra ya es irreversible.
