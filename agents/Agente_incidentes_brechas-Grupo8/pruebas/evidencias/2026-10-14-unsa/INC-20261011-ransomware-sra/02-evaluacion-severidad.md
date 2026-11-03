# 02 · Evaluación de severidad — INC-20261011-ransomware-sra

> BORRADOR. Metodología ENISA (2013) de `knowledge/metodologia-severidad.md`. La severidad se mide sobre los titulares.

## 1. Puntuación SE = DPC × EI + CB

| Componente | Valor | Justificación |
|---|---|---|
| **DPC** | **2** | Base 1: nombres, DNI, domicilio, contacto y datos académicos (simples). Ajuste +1: unos 900 menores de edad y el conjunto DNI + domicilio + fecha de nacimiento + teléfono facilita suplantación y perfilado |
| **EI** | **1** | Identificación directa: nombre completo + DNI + correo. Sin cifrado en reposo (`activos-y-datos.md:9`) |
| CB confidencialidad | +0,5 | Exfiltración probable a una IP externa desconocida (`firewall.log:3`) con amenaza de publicar. Sin cifrado que proteja los datos |
| CB integridad | 0 | No hay evidencia de alteración de contenido, solo cifrado. Pendiente de verificar tras restaurar |
| CB disponibilidad | +0,5 | Indisponibilidad total: servidores y NAS cifrados. Sin copias offline ni snapshots. Restauración nunca probada |
| CB intención maliciosa | +0,5 | Ataque deliberado y extorsión |
| **CB total** | **1,5** | |

**SE = 2 × 1 + 1,5 = 3,5 → ALTA** (consecuencias significativas superables con serias dificultades).

### Sensibilidad del resultado
- Si las actas o la BD contienen datos sensibles (p. ej. discapacidad, salud o ingresos), DPC = 3 y **SE = 4,5 → Muy alta**.
- Si se descarta la exfiltración (CB conf. = 0), SE = 3,0, que sigue siendo Alta. El resultado no depende de esa duda.

## 2. Decisión legal (art. 34)

| Pregunta | Respuesta | Resultado |
|---|---|---|
| ¿Datos sensibles? | No confirmados en S-01/S-02 (verificar actas) | Posible; no es necesario para decidir |
| ¿Grandes volúmenes o gran número de personas? | **Sí**: hasta 89 000 titulares y más de 30 000 archivos cifrados | **Notificar a la ANPD (34.1)** |
| ¿Perjuicio evidente a otros derechos o libertades? | **Sí probable**: SE Alta, menores de edad, amenaza de publicar notas y datos, riesgo de suplantación | Notificar (34.1) **y comunicar a titulares (34.3)** |
| ¿Entorno digital? | Sí | **Notificar al CNSD (34.5)** |
| ¿Excepción del 34.4? | No aplica: el incidente no está superado | — |

**Conclusión: notificar a la ANPD, comunicar a los titulares y avisar al CNSD, todo con carácter urgente y con justificación de la demora.**

## 3. Plazos

| Obligación | Plazo | Estado a las 2026-10-13 09:00 |
|---|---|---|
| ANPD (34.1) | 48 h: 2026-10-13 06:40 (05:12 en lectura estricta) | **Vencido** (+2 h 20 min / +3 h 48 min). Enviar hoy con justificación |
| Titulares (34.3) | 48 h, sin dilación indebida | **Vencido**. Emitir lo antes posible |
| CNSD (34.5) | Junto con la ANPD (el plazo exacto no está en `knowledge/`) `[VERIFICAR]` | Pendiente |
| Documentar (35) | Siempre | En curso (este expediente) |

## 4. Factores agravantes de riesgo
- Doble extorsión con plazo propio (aprox. 2026-10-14 06:40).
- Los respaldos son inservibles, así que no se puede recuperar sin ceder a la extorsión salvo otra fuente `[VERIFICAR]`.
- Persistencia del atacante: cuenta `svc_mant`, VPN comprometida, contraseña de Administrador compartida.
- Evidencia en riesgo: logs del firewall purgados a 30 días, auditoría del SRA de solo 60 días (la mínima legal es 2 años, art. 46.3).
- Riesgo de que la lectura estricta del plazo sea la aplicada por la ANPD.

## 5. Posibles consecuencias para los titulares
Suplantación de identidad y fraude con DNI y domicilio; phishing dirigido a estudiantes; publicación de notas y situación académica (daño reputacional, acoso, especial riesgo para menores); pérdida de continuidad académica (notas, matrícula).
