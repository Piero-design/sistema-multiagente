# Metodología de severidad de brechas de datos personales

Basada en **ENISA (2013)**, *Recommendations for a methodology of the assessment of severity of personal data breaches*, y combinada con los supuestos del **art. 34.1 del D.S. 016-2024-JUS**. La severidad se mide **sobre los titulares de los datos**, no sobre la organización.

## Fórmula

```
SE = DPC × EI + CB
```

- **DPC** (Data Processing Context): qué tan delicados son los datos en su contexto.
- **EI** (Ease of Identification): qué tan fácil es identificar a las personas a partir de los datos expuestos.
- **CB** (Circumstances of Breach): circunstancias de la brecha.

## 1. DPC — Contexto de los datos (1 a 4)

| Puntaje base | Tipo de datos | Ejemplos |
|---|---|---|
| 1 | Simples | Nombre, contacto, datos académicos o laborales básicos |
| 2 | De comportamiento | Ubicación, hábitos, historial de navegación o compras |
| 3 | Financieros | Cuentas bancarias, tarjetas, ingresos, deudas |
| 4 | Sensibles | Salud, biométricos, vida sexual, origen racial, convicciones, afiliación sindical, ingresos económicos (sensible en Perú, Ley 29733) |

**Ajuste por contexto (±1, dentro de 1–4):** sube si el contexto agrava el daño (datos de menores, víctimas, relación de dependencia, el conjunto permite perfilar) y baja si los datos ya eran públicos o son triviales en ese contexto. Justifica el ajuste en una línea.

## 2. EI — Facilidad de identificación

| Valor | Nivel | Criterio |
|---|---|---|
| 0,25 | Despreciable | Muy difícil identificar a la persona (datos seudonimizados sin clave, agregados) |
| 0,5 | Limitada | Posible con esfuerzo o información adicional |
| 0,75 | Significativa | Fácil con información accesible (nombre común + ciudad) |
| 1 | Máxima | Identificación directa (nombre completo + DNI, foto, correo personal) |

## 3. CB — Circunstancias (se suman)

| Factor | Valor | Cuándo |
|---|---|---|
| Pérdida de **confidencialidad** | 0 | Expuestos a destinatarios conocidos y confiables, sin evidencia de uso |
| | +0,25 | Expuestos a un número conocido de destinatarios no autorizados |
| | +0,5 | Expuestos a destinatarios desconocidos o publicados en Internet |
| Pérdida de **integridad** | 0 | Alterados pero recuperables sin daño |
| | +0,25 | Alterados y posiblemente usados, recuperables |
| | +0,5 | Alterados y usados, o no recuperables |
| Pérdida de **disponibilidad** | 0 | Recuperables sin dificultad (respaldo íntegro) |
| | +0,25 | Indisponibilidad temporal |
| | +0,5 | Indisponibilidad total o permanente |
| **Intención maliciosa** | +0,5 | Robo, ataque deliberado, extorsión (ransomware), uso indebido intencional por personal interno |

Si la confidencialidad está cifrada con un algoritmo robusto y la clave no fue comprometida, puede considerarse EI = 0,25 y CB de confidencialidad = 0 (justificarlo).

## 4. Niveles de severidad

| SE | Nivel | Significado para el titular |
|---|---|---|
| < 2 | **Baja** | Sin impacto o inconvenientes menores superables |
| 2 a < 3 | **Media** | Inconvenientes significativos superables con algo de esfuerzo |
| 3 a < 4 | **Alta** | Consecuencias significativas superables con serias dificultades |
| ≥ 4 | **Muy alta** | Consecuencias graves o irreversibles |

## 5. Del puntaje a la decisión (Perú)

La obligación legal **no depende solo del puntaje**: se activa si se cumple **cualquiera** de los supuestos del art. 34.1 (ver `marco-normativo-peru.md`).

| Pregunta | Si la respuesta es Sí |
|---|---|
| ¿Hay **datos sensibles** afectados? | Notificar a la ANPD (art. 34.1), aunque SE sea Media |
| ¿Grandes volúmenes o gran número de personas? | Notificar a la ANPD (art. 34.1) |
| ¿Perjuicio evidente a otros derechos o libertades? (SE Alta o Muy alta suele indicarlo) | Notificar a la ANPD (art. 34.1) **y** comunicar a los titulares (art. 34.3) |
| ¿Ocurrió en o mediante entorno digital? | Además, notificar al CNSD (art. 34.5) |
| ¿Ninguno de los anteriores y el incidente fue superado totalmente? | No se notifica, pero **se documenta** (art. 35). No se comunica al titular (art. 34.4) |
| ¿Hay duda razonable? | **Recomendar notificar** y dejar constancia de la duda |

Criterio de apoyo cuando no hay umbral oficial: SE ≥ 3 (Alta o Muy alta) se trata como "perjuicio evidente" probable y activa la comunicación al titular.

## 6. Ejemplo de puntuación justificada
> **Correo con lista de 1 200 alumnos enviado por error a un proveedor.** DPC = 1 (nombres, correos y notas) +1 por menores de edad = 2. EI = 1 (nombre completo y correo personal). CB = +0,25 (un destinatario conocido, no autorizado). Sin intención maliciosa. **SE = 2 × 1 + 0,25 = 2,25 → Media.** Art. 34.1: no hay datos sensibles; 1 200 personas `[evaluar si es "gran número"]` → ante la duda, recomendar notificar a la ANPD. Comunicación a titulares: no obligatoria si el proveedor confirma por escrito la eliminación (art. 34.4).
