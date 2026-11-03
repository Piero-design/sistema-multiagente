# Perfil PE-LEY29733: Perú

Marco: Ley N.° 29733, Ley de Protección de Datos Personales, y su Reglamento aprobado por D.S. N.° 016-2024-JUS (publicado el 30-11-2024, vigente desde el 30-03-2025). Autoridad: Autoridad Nacional de Protección de Datos Personales (ANPD), del Ministerio de Justicia y Derechos Humanos.

Resumen académico de los artículos aplicables. No sustituye el texto oficial ni la asesoría legal.

## Derechos admitidos y su código en el motor

| Derecho (Perú) | Código | Ley 29733 |
|---|---|---|
| Información | `information` | art. 18 |
| Acceso | `access` | art. 19 |
| Portabilidad (manifestación del acceso) | `portability` | Reglamento, art. 76 |
| Actualización, inclusión y rectificación | `rectification` | art. 20 |
| Cancelación o supresión | `erasure` | art. 20 |
| Oposición | `objection` | art. 22 |

El tratamiento objetivo (decisiones automatizadas, art. 23 de la Ley) no lo tramita el motor: se deriva al DPO como HITL con el control A.1.3.11.

## Plazos de respuesta (días hábiles)

Se cuentan desde el día siguiente a la presentación de la solicitud (Reglamento, art. 69).

| Derecho | Plazo | Base |
|---|---|---|
| Información | 8 días hábiles | art. 69.1 |
| Acceso | 20 días hábiles | art. 69.2 |
| Portabilidad | 20 días hábiles | art. 76.1 + art. 69.2 (se aplica el plazo del acceso) |
| Rectificación, cancelación, oposición | 10 días hábiles | art. 69.3 |

## Prórroga, requerimientos y subsanación

- **Prórroga (art. 71):** una sola vez, por un plazo igual como máximo, si las circunstancias lo justifican. Debe comunicarse dentro del plazo que se amplía. No aplica al derecho de información.
- **Información adicional (art. 70):** el responsable puede requerirla dentro de 7 días; el titular tiene 10 días para atenderla. El plazo de respuesta se suspende mientras tanto.
- **Solicitud incompleta (art. 66.2):** observación en 5 días desde el día siguiente a la recepción; el titular tiene hasta 5 días para subsanar. Si no lo hace, la solicitud se tiene por no presentada.
- **Recepción por el encargado (art. 66.4):** debe trasladarla al responsable en 3 días.

El motor calcula la prórroga, la suspensión del art. 70 y la subsanación del art. 66.2, pero solo las aplica una persona.

## Requisitos de la solicitud (art. 64)

Identidad del titular y, si lo hay, de su representante con su acreditación; petición concreta; domicilio o dirección electrónica para notificaciones; fecha y firma; documentos que sustenten la petición, si corresponden.

## Gratuidad (art. 67)

En el sector privado el ejercicio de los derechos es gratuito, salvo normas especiales, y no puede generar ingresos adicionales al responsable.

## Portabilidad (art. 76)

- Procede cuando el tratamiento se basa en el consentimiento o en un contrato, o se realiza por medios automatizados.
- Entrega en formato estructurado, de uso común y legible por máquina.
- Transmisión directa a otro responsable cuando sea técnicamente posible y no imponga una carga excesiva; quien alegue imposibilidad técnica debe poder demostrarla ante la Autoridad.
- Los datos derivados o inferidos son portables solo si el responsable lo determina.

## Rectificación (arts. 79-81)

Corrige datos inexactos, erróneos o falsos; actualiza datos modificados; incluye datos faltantes con interés fundado. La solicitud debe indicar qué dato corregir y aportar el sustento.

## Cancelación o supresión (arts. 82-85)

- Procede cuando los datos ya no son necesarios, venció su plazo, se revocó el consentimiento o el tratamiento incumple la Ley (art. 82.1).
- Mientras se evalúa, los datos se **bloquean**: cesa su tratamiento (art. 82.3).
- Se documenta el cumplimiento y se indica a quién se transfirieron los datos suprimidos (art. 83). Esto se deriva al Agente de Terceros (A.1.3.8).
- No procede cuando deben conservarse por razones históricas, estadísticas, científicas o contractuales, entre otras (art. 84).
- Si se deniega, se usan medios de disociación o anonimización cuando sea posible (art. 85).

## Oposición (art. 86)

El titular puede oponerse en cualquier momento al tratamiento, en especial cuando no consintió la recopilación. Requiere HITL porque restringe el tratamiento.

## Denegación y tutela (art. 73; Ley, art. 24)

Toda denegación total o parcial debe motivarse e indicar que el titular puede reclamar ante la Autoridad (Dirección de Protección de Datos Personales) o acudir al Poder Judicial mediante hábeas data.

## Oficial de Datos Personales

El Reglamento crea la figura del Oficial de Datos Personales, que puede ser el canal de atención de solicitudes. En este skill cumple el papel de aprobador HITL junto al DPO.
