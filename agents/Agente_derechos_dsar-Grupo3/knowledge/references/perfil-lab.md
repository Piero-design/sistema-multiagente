# Perfiles LAB: demostración académica

`LAB-30` y `LAB-15-REVIEW` son políticas ficticias para probar el agente sin depender de una ley real. Úsalos cuando el profesor o la evaluación pidan una configuración neutral.

## Características

| Perfil | Plazo | Tipo de día | Revisión especializada |
|---|---|---|---|
| `LAB-30` | 30 días | Naturales | No |
| `LAB-15-REVIEW` | 15 días | Naturales | Sí: todo caso con identidad verificada pasa a `APPROVAL_REQUIRED` |

- Derechos admitidos: acceso, rectificación, supresión, portabilidad y oposición. El derecho de información no existe en estos perfiles.
- No citan artículos de ninguna ley. Si la pregunta es legal, responde que el perfil es ficticio y sugiere el perfil `PE-LEY29733`.
- El plazo se cuenta desde el día siguiente a la recepción, igual que en el perfil PE, para que los resultados sean comparables.

## Cómo quitar o cambiar una jurisdicción

Toda la lógica legal vive en el perfil (`config/perfiles-jurisdiccion.json`) y en su referencia. Para usar otra ley se agrega un perfil nuevo con `supported_rights`, `response_days_by_right`, `day_type`, `holidays` y `legal_basis`, más su archivo `perfil-*.md`. El motor no cambia.
