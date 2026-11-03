# Marco normativo peruano sobre incidentes de seguridad de datos personales

> Fuente principal: **Reglamento de la Ley N.° 29733**, aprobado por **D.S. N.° 016-2024-JUS** (El Peruano, 30/11/2024). Entró en vigencia a los 120 días calendario de su publicación (**30/03/2025**, Primera Disposición Complementaria Final). Reemplaza al D.S. N.° 003-2013-JUS.
> Los textos entre comillas son citas literales del reglamento. Lo marcado `[VERIFICAR]` debe confirmarse antes de citarlo en el informe.

## 1. Definición

**Incidente de seguridad de datos personales** (Título Preliminar, art. III, num. 16):
> "Es toda vulneración de la seguridad que ocasione la destrucción, pérdida, alteración ilícita de los datos personales o la comunicación o exposición no autorizada a dichos datos."

Consecuencia práctica: no todo **evento** de seguridad es un incidente de datos personales. Para serlo debe existir una vulneración **y** afectar datos personales (destrucción, pérdida, alteración ilícita, comunicación o exposición no autorizada).

## 2. Obligaciones (arts. 34 a 36)

| Obligación | Quién | Cuándo | Artículo |
|---|---|---|---|
| **Notificar a la ANPD** | Titular del banco de datos / responsable del tratamiento | Si se cumple **alguno** de los supuestos del art. 34.1 (abajo). Máximo **48 horas** desde que se tomó conocimiento | 34.1 |
| Justificar la demora | Responsable | Si se notifica después de las 48 h: motivos y/o sustento probatorio | 34.1 |
| Notificar aunque ya se resolvió | Responsable | "Esta obligación permanece aun cuando el responsable [...] considere que tal incidente haya sido subsanado o resuelto internamente" | 34.1 |
| **Comunicar a los titulares** | Responsable | Si el incidente "afecte al titular de los mismos en otros de sus derechos". Dentro de **48 horas**, sin dilación indebida, en lenguaje sencillo y claro, con las medidas adoptadas | 34.3 |
| Excepción a comunicar al titular | — | Si no produjo esa afectación **y** fue superado totalmente por las medidas adoptadas | 34.4 |
| **Notificar al Centro Nacional de Seguridad Digital (CNSD)** | Responsable | Si el incidente se desarrolla en y/o mediante el **entorno digital**, además de la ANPD, para el Registro Nacional de Incidentes de Seguridad Digital (D.U. N.° 007-2020) | 34.5 |
| **Documentar todo incidente** | Responsable | Siempre, se notifique o no: hechos, efectos y medidas adoptadas | 35 |
| **Avisar al responsable** | Encargado del tratamiento | De forma **inmediata** al tomar conocimiento | 36 |

### Supuestos que obligan a notificar a la ANPD (art. 34.1)
Basta **uno**:
1. Exposición de **grandes volúmenes** de datos, "en cantidad o tipo de datos".
2. Puede afectar a un **gran número de personas**.
3. Se trata de **datos sensibles**.
4. Se produce un **perjuicio evidente a otros derechos o libertades** del titular.

> El reglamento no fija un umbral numérico para "grandes volúmenes" ni "gran número". La ANPD debe emitir lineamientos (art. 34.7 y Segunda Disposición Complementaria Final) `[VERIFICAR si ya se publicaron]`. Mientras tanto, el agente usa la metodología de `metodologia-severidad.md` como criterio de apoyo y, **ante la duda, recomienda notificar**.

### ¿Desde cuándo corren las 48 horas?
El art. 34.1 dice "posteriores a haber tomado conocimiento o constancia de ello", pero no precisa **quién** debe conocerlo. Criterio prudente del proyecto `[VERIFICAR con lineamientos ANPD o asesoría legal]`:
- Cuenta el primer momento en que **cualquier persona de la organización** (no solo el Oficial de Datos Personales) supo con certeza razonable que hubo un incidente. Ej.: el trabajador al que le robaron la laptop, no el reenvío posterior a su jefe.
- Una **alerta sin revisar** (ej. un antivirus) no es por sí sola toma de conocimiento, pero se registra; si la organización debió atenderla, anótalo como riesgo de una lectura más estricta.
- Si hay dos lecturas posibles, se calcula la hora límite con la **más temprana** y se deja la otra como referencia.

### Contenido mínimo de la notificación a la ANPD (art. 34.2)
1. Naturaleza del incidente; cuando sea posible, tipos de datos y número aproximado de titulares afectados.
2. Nombre y datos de contacto del Oficial de Datos Personales u otro punto de contacto.
3. Posibles consecuencias del incidente.
4. Medidas adoptadas o propuestas para remediar la vulneración y mitigar sus efectos negativos.

### Canal
Formulario de reporte de incidentes: `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia del enlace antes de la demo]`.

## 3. Medidas de seguridad relacionadas (prevención y evidencia)

| Artículo | Exigencia útil para la gestión de incidentes |
|---|---|
| 46.1 | Control de acceso: altas/bajas, autenticación, privilegios revisados como mínimo semestralmente |
| 46.3 | **Registros (logs) de interacción** con los datos: cuentas, inicio/cierre de sesión, visualización, modificación, eliminación, importación y exportación. Conservación **mínima de 2 años**. Insumo clave para investigar un incidente |
| 46.4 | Impedir copias no autorizadas; mensajería, correo o redes no institucionales deben estar aprobadas formalmente |
| 47 | **Documento de seguridad** aprobado y con fecha cierta (incluye inventario de datos y sistemas) |
| 48.1 | Áreas seguras, equipos seguros dentro y fuera de las instalaciones, **copias de respaldo** con verificación de integridad |
| 48.2 | Puede tomar como referencia la **NTP-ISO/IEC 27001:2022** |
| 40.2 | La evaluación de impacto puede referirse a **NTP-ISO/IEC 27005** y **NTP-ISO 31000** |

## 4. Oficial de Datos Personales (arts. 37 a 39)
Debe designarse en entidades públicas y en los demás supuestos del art. 37.1 (con cronograma progresivo para privados según ventas anuales). Es el **punto de contacto** que exige el art. 34.2 num. 2 y quien valida todos los borradores del agente.

## 5. Sanción por no notificar
- **Infracción grave** (art. 133, num. 12): "No comunicar a la Autoridad Nacional de Protección de Datos Personales un incidente de seguridad de datos personales cuando así corresponda conforme a lo previsto en el artículo 34".
- Las multas se gradúan según el art. 39 de la Ley 29733 y los arts. 123 y 124 del reglamento `[VERIFICAR rango en UIT para infracciones graves en el art. 39 de la Ley]`.

## 6. Normas conexas
| Norma | Relación |
|---|---|
| Ley N.° 29733, art. 9 (principio de seguridad) | Base legal de las medidas de seguridad `[VERIFICAR artículo]` |
| D.U. N.° 007-2020, Marco de Confianza Digital | Registro Nacional de Incidentes de Seguridad Digital y CNSD (art. 34.5) |
| D.Leg. N.° 1412 y D.S. N.° 029-2021-PCM (Gobierno Digital) | Oficial de datos en entidades públicas; equipos de respuesta a incidentes en el Estado `[VERIFICAR]` |

## 7. Referencia comparada (no obligatoria en Perú)
**RGPD (UE) 2016/679**, arts. 33 y 34: notificación a la autoridad en 72 h y comunicación a los interesados si hay alto riesgo. Útil para el marco teórico: Perú adopta un plazo **más corto (48 h)**.
