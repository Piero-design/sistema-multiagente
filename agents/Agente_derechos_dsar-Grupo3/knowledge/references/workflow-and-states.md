# Flujo, estados y aprobacion humana

## Estados

| Estado | Significado |
|---|---|
| `RECEIVED` | Solicitud registrada. |
| `TRIAGED` | Derechos, perfil de jurisdiccion y plazos por derecho clasificados. |
| `IDENTITY_PENDING` | No se permite buscar PII hasta completar la verificacion. |
| `VERIFIED` | La verificacion externa fue confirmada. |
| `DISCOVERY` | Se localizaron fuentes y registros del titular. |
| `REVIEW` | El expediente y el borrador esperan revision humana ordinaria. |
| `APPROVAL_REQUIRED` | Existe una decision sensible o una accion que exige autorizacion. |
| `APPROVED` | La persona autorizada aprobo el plan. |
| `FULFILLED` | La accion fue ejecutada fuera del prototipo y existe evidencia. |
| `CLOSED` | El caso fue comunicado y cerrado. |
| `ON_HOLD` | El plazo o la actividad se encuentra suspendido conforme a una politica. |
| `REJECTED` | Se rechazo la solicitud con fundamento documentado. |
| `PARTIALLY_FULFILLED` | Solo una parte pudo atenderse y se explicaron los motivos. |
| `ESCALATED` | Requiere intervencion del DPO, responsable o asesoria competente. |
| `CANCELLED` | El titular retiro la solicitud o se aplico otra causa documentada. |

## Transiciones del prototipo

```text
RECEIVED -> TRIAGED
TRIAGED -> IDENTITY_PENDING
TRIAGED -> VERIFIED -> DISCOVERY
DISCOVERY -> REVIEW
DISCOVERY -> APPROVAL_REQUIRED
```

El motor termina en `IDENTITY_PENDING`, `REVIEW` o `APPROVAL_REQUIRED`. `ON_HOLD` (plazo suspendido), `APPROVED`, `REJECTED` y `CANCELLED` solo se alcanzan con una decision humana registrada; los demas estados representan integraciones futuras.

## Casos que requieren HITL

- supresion, rectificacion, restriccion u oposicion que modifique el tratamiento;
- rechazo total o parcial;
- datos sensibles o de categorias especiales;
- datos de terceros o secretos que deban redactarse;
- conflicto con retencion, contrato, investigacion o mandato aplicable;
- identidad dudosa, representacion, menores o controversia;
- solicitud combinada (varios derechos en una misma solicitud);
- ampliacion/suspension del plazo (prorroga, requerimiento de informacion adicional);
- transferencia directa a otra organizacion;
- cualquier comunicacion externa definitiva.

## Invariantes

1. Una identidad distinta de `verified` produce cero registros descubiertos.
2. Ninguna accion (`proposed_action` ni `proposed_actions`) contiene `executed: true` en esta fase.
3. El plazo procede del perfil configurado, no del conocimiento del modelo. Cada derecho tiene su plazo en `deadlines` y `deadline_at` es el mas cercano.
4. Cada registro entregable conserva `source_system` y `record_id`.
5. Los campos listados en `third_party_fields` no aparecen en la vista preparada para el titular.
6. Si cualquiera de los derechos solicitados es `rectification`, `erasure` u `objection`, `hitl.required` es verdadero.
