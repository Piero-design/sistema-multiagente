# Tarea T3: redactar la respuesta al titular

Produce un **borrador** de respuesta. La estructura la fija la plantilla; el modelo solo redacta la prosa de cada sección.

## Requisitos previos

- Existe un expediente validado (tarea T1).
- El estado no es `IDENTITY_PENDING`. Si lo es, el único borrador posible es la solicitud de verificación de identidad.

## Lista de control

```
Redacción:
- [ ] 1. Generar la base con render_response (no escribir desde cero); la carta va en su sección
- [ ] 2. Completar la prosa por derecho, con el contenido mínimo de la tabla
- [ ] 3. Verificar que no aparece ningún campo de redacted_fields
- [ ] 4. Verificar que toda acción figura como propuesta, no como hecho
- [ ] 5. Incluir plazos con su base legal desde el expediente
- [ ] 6. Marcar el documento como BORRADOR pendiente de aprobación
```

## Contenido mínimo por derecho

| Derecho | Debe incluir |
|---|---|
| Información | Finalidades, destinatarios, conservación, cómo ejercer derechos |
| Acceso | Categorías de datos, finalidades, base legal, destinatarios, origen, conservación, copia revisada de los datos |
| Portabilidad | Formato estructurado y legible por máquina; si procede, opción de transmisión directa |
| Rectificación | Campo, corrección propuesta y destinatarios a informar (A.1.3.8) |
| Supresión o cancelación | Datos a suprimir, datos que se conservan y por qué (art. 84), bloqueo durante la evaluación (art. 82.3) |
| Oposición | Finalidad objetada, efecto propuesto y destinatarios a informar |

## Denegación total o parcial

Requiere HITL. En el perfil PE, el borrador debe motivar la denegación e indicar que el titular puede reclamar ante la Autoridad Nacional de Protección de Datos Personales o acudir al hábeas data (art. 73).

## Formato de salida del modelo

En T3 no uses las cuatro partes (Hechos, Propuesta, Pendiente, Fuentes): el sistema las genera con `render_response` e inserta tu texto en la sección **Carta al titular** de la plantilla. Devuelve **solo la carta**, en Markdown simple:

1. Primera línea: `**Asunto:** Respuesta a su solicitud de <derecho> — Referencia <case_id>`.
2. Saludo con marcador: `Estimado/a [nombre del titular]:`.
3. Párrafos breves: recepción, estado de la solicitud en lenguaje llano, plazo del expediente y lo que falta.
4. Despedida y `[Nombre y cargo del responsable]`.

Reglas:

- Sin encabezados `#`, sin citas en bloque (`>`), sin tablas, sin listas de fuentes ni notas internas.
- Lo que no conste en los hechos (nombre, campo, valor corregido, categorías) va entre corchetes, p. ej. `[campo a rectificar]`; no lo inventes.
- Cita autoridades y artículos solo si el perfil del caso es `PE-LEY29733`. Con perfiles `LAB-*` no menciones leyes ni autoridades reales.
- Si el estado es `APPROVAL_REQUIRED` o `REVIEW`, la carta dice que la solicitud está en revisión; nunca que algo se corrigió, eliminó o envió.

## Estilo

Usa lenguaje claro y directo, en segunda persona, sin jerga técnica (ISO/IEC 27701, B.1.3.4: información clara y accesible). No menciones el modelo, el RAG ni los estados internos en el texto para el titular.
