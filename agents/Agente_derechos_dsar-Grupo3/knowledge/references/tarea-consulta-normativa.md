# Tarea T2: consultar la norma o la ley

Responde preguntas sobre lo que exigen ISO/IEC 27701:2025 o la ley del perfil activo, siempre con una fuente recuperada.

## Lista de control

```
Consulta normativa:
- [ ] 1. Identificar el marco: ISO/IEC 27701, la ley del perfil, o ambos
- [ ] 2. Recuperar fragmentos con el RAG (top 3)
- [ ] 3. Responder solo con lo que dicen los fragmentos recuperados
- [ ] 4. Citar cada afirmación con [chunk_id] y el control o artículo
- [ ] 5. Si no hay fragmento que lo respalde, decirlo y no responder de memoria
```

## Comando

```bash
python -m dsar.rag.retrieve --query "PREGUNTA EN PALABRAS CLAVE" --top-k 3 --json
```

Usa como consulta palabras clave del derecho y del concepto (por ejemplo `portabilidad formato estructurado plazo`), no la pregunta literal del usuario.

## Cómo responder

- Distingue entre la **norma** (qué debe tener la organización) y la **ley** (qué derecho tiene el titular y en qué plazo). ISO/IEC 27701 pide definir plazos y procedimientos; la ley fija los días.
- Usa "debe" solo cuando la fuente lo exige. Si la fuente dice "puede" o "conviene", mantén ese matiz.
- Si la pregunta pide una opinión legal sobre un caso real ("¿puedo negarme a borrar…?"), entrega lo que dice la fuente y marca la decisión como **pendiente de revisión por el DPO o asesoría legal**.
- No copies párrafos largos de la norma ISO: resume y cita el control.

## Ejemplo

Pregunta: "¿En qué formato se entrega la portabilidad?"

> La copia debe entregarse en un formato estructurado, de uso común y legible por máquina [perfil-pe-ley29733-07] (D.S. 016-2024-JUS, art. 76.1; ISO/IEC 27701:2025, A.1.3.9 [iso-control-map-02]). Cuando es técnicamente posible, puede transmitirse directamente a otro responsable (art. 76.2); esa transmisión la decide una persona.
