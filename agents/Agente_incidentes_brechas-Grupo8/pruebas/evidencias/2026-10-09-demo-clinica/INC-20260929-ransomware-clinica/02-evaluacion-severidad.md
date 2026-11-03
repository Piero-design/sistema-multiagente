# Evaluación de severidad — INC-20260929-ransomware-clinica

- **Insumo:** `salidas/INC-20260929-ransomware-clinica/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB — ver `knowledge/metodologia-severidad.md`

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 4 | Dato más delicado: salud (diagnósticos, laboratorio), sensible según la Ley 29733 (`activos-y-datos.md:21-22`) |
| Ajuste de contexto | +1 (tope) | ~3 100 menores y el conjunto permite perfilar (identidad + salud + seguro); el máximo de la escala es 4 |
| **DPC final** | **4** | Base 4 más ajuste = 5, limitado a 4 (rango 1–4) |
| **EI** | **1** | Nombre completo y DNI en la misma base: identificación directa; sin cifrado en reposo (`activos-y-datos.md:9-10`) |
| CB — confidencialidad | +0,5 | 3,4 GB salieron a una IP externa desconocida (`firewall.log:3`) y hay amenaza de publicación en Internet. Exfiltración probable, no confirmada en contenido |
| CB — integridad | +0,5 | Datos cifrados y sin copia limpia recuperable: `BKP-01` también cifrado (`respaldos.log:5`); además se creó una cuenta administradora (`auth-hce.log:5`) |
| CB — disponibilidad | +0,5 | Indisponibilidad total de HCE y laboratorio; no hay respaldo íntegro (último bueno 2026-09-08, en el mismo disco cifrado) |
| CB — intención maliciosa | +0,5 | Ataque deliberado con extorsión |
| **CB total** | **2,0** | |

**SE = 4 × 1 + 2,0 = 6,0 → Severidad Muy alta**

Sensibilidad: aun con confidencialidad = 0 (si se descartara la exfiltración) e integridad = 0,25, SE = 4 + 1,75 = 5,75: sigue siendo Muy alta. La conclusión no depende de los supuestos más inciertos.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Exposición pública de diagnósticos y resultados; estigma y discriminación | Alta | Amenaza de publicación y exfiltración probable (`firewall.log:3`) |
| Extorsión directa a pacientes | Media | Se dispone de teléfono, dirección y diagnóstico |
| Suplantación de identidad y fraude | Alta | DNI, fecha de nacimiento, dirección, teléfono en la misma base |
| Estafas telefónicas ("llamada de la clínica o de la aseguradora") y fraude con seguros | Alta | Datos de póliza de ~6 500 titulares |
| Afectación a ~3 100 menores (perfilamiento, riesgo duradero) | Alta | Menores en la base; datos de salud no se pueden "cambiar" |
| Pérdida de acceso a su historia clínica y riesgo para la continuidad de la atención | Alta | HCE inaccesible; solo papel; alergias, tratamientos y citas no disponibles |
| Daño reputacional/emocional | Alta | Naturaleza de los datos |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Sí** | Salud (HCE y laboratorio) |
| | Grandes volúmenes (cantidad o tipo) | **Sí** (probable) | Base completa de la HCE, 3,4 GB; tipo sensible. Sin umbral oficial `[VERIFICAR lineamientos ANPD]` |
| | Gran número de personas | **Sí** (probable) | ~18 000 titulares. Sin umbral oficial `[VERIFICAR lineamientos ANPD]` |
| | Perjuicio evidente a derechos o libertades | **Sí** | SE Muy alta; riesgo de publicación de datos de salud y suplantación |
| **Resultado ANPD** | | **Notificar** (obligación probable) | Basta un supuesto; aquí concurren cuatro |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí** | SE ≥ 3 y exfiltración probable. La excepción del art. 34.4 no aplica: el incidente no está superado |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Sí** | Intrusión y ransomware en sistemas informáticos |
| Documentar (art. 35) | Siempre | **Sí** | Registro en `04-respuesta-y-cierre.md` |

Comunicación a titulares: el art. 34.3 pide 48 h y lenguaje sencillo. Con ~18 000 personas, el canal masivo (SMS, correo, aviso en web y en recepción) lo define la clínica `[VERIFICAR lineamientos ANPD]`.

## 4. Plazos
- **Toma de conocimiento (lectura más temprana):** 2026-09-28 23:50 (alerta del antivirus a TI, `antivirus.log:4`).
- **Hora límite (48 h):** **2026-09-30 23:50** — Tiempo restante desde 2026-09-29 09:00: **38 h 50 min**. Lectura B (referencia): 2026-10-01 07:15 (46 h 15 min).
- Si se superara la hora límite, la notificación debe incluir los motivos de la demora (art. 34.1). Recomendación: enviar una notificación **inicial** antes del plazo y una **complementaria** después.

## 5. Nota aparte: impacto para la organización
- Riesgo de infracción grave por no notificar cuando corresponde (art. 133 num. 12). El rango de multa está `[VERIFICAR]`.
- El documento de seguridad admite que no está definido quién notifica (`documento-seguridad-extracto.md:18`): riesgo de que el plazo se pierda por falta de responsable.
- Continuidad asistencial, reputación, ausencia de seguro cibernético (`contactos.md:11`) y presión de la extorsión (3 BTC, 72 h). El pago no se recomienda; es decisión de la alta dirección con asesoría legal y no cambia la obligación de notificar.
- Las debilidades de control (sin MFA, registros 90 días frente a los 2 años del art. 46.3, respaldo sin aislar) pueden ser relevantes ante una fiscalización.

## 6. Supuestos e información pendiente
- Que lo exfiltrado incluya la HCE y los resultados de laboratorio (inferencia por tamaños 3,4 GB en `auth-hce.log:7-8` y `firewall.log:3`; solo una transferencia de 3,4 GB es visible, así que puede ser uno de los dos paquetes) `[VERIFICAR]`.
- Número real de titulares con datos en lo exfiltrado; el log de la app no registra consultas ni exportaciones (`app/hce/config.py:8`), por lo que no se puede acotar y se trata a los 18 000 como expuestos.
- Si hay otras salidas de datos anteriores a la retención del firewall (30 días).

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
