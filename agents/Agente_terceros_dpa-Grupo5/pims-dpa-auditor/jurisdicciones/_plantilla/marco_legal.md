# Marco legal [PAÍS] — [Ley principal] y [Reglamento]

| Campo | Valor |
|---|---|
| Jurisdicción | `[id_carpeta]` (minúsculas, sin tildes ni espacios; p. ej. `colombia`, `ue_rgpd`) |
| Versión | 0.1 |
| Estado | **Borrador — pendiente de verificación legal** |
| Parámetros estructurados | `parametros_legales.json` (misma carpeta) |
| Redactado por / revisado por | [nombre o "IA (borrador)"] / [persona con conocimiento legal del país] |

> **Cómo llenar esta plantilla.** Copia la carpeta `_plantilla/` con el nombre de la jurisdicción. Llena cada sección **solo con lo que diga el texto oficial** de la ley y su reglamento, citando el artículo entre paréntesis. Si un dato no se pudo confirmar, escribe "Pendiente de verificar". Mantén los mismos 7 títulos: la skill los busca por número. Mientras el estado sea "Borrador", los informes lo declaran como limitación.
>
> Las cifras que aparezcan aquí (plazos, autoridad, derechos) deben coincidir con `parametros_legales.json`.

## 1. Relación responsable–encargado
- ¿Exige la ley un contrato o instrumento escrito para el encargo? ¿Qué contenido mínimo? (art. …)
- ¿Qué ocurre si el encargado trata datos para fines propios? (art. …)
- Deber de confidencialidad del encargado y su personal. (art. …)

## 2. Incidentes de seguridad (punto crítico de contraste)
- Plazo y forma en que el **encargado** debe avisar al responsable. (art. …)
- Plazo en que el **responsable** debe notificar a la autoridad: **[N] horas**. (art. …)
- Si debe comunicarse a los titulares y en qué plazo. (art. …)
- Otras entidades a notificar (CSIRT nacional, regulador sectorial…). (art. …)

**Consecuencia para el DPA:** el plazo de aviso del encargado debe dejar margen al responsable para cumplir el plazo legal. El máximo aceptable lo fija la política interna de cada organización (`plazo_max_aviso_incidente_horas`), que debe ser **menor** que el plazo de notificación a la autoridad.

## 3. Flujo transfronterizo
- Condiciones para transferir datos fuera del país (adecuación, garantías, autorización previa…). (art. …)
- ¿Existe lista oficial de países adecuados? ¿Dónde se publica?
- Para el DPA: exigir lista de países, garantías contractuales y aviso de cambios.

## 4. Seguridad
- Medidas exigidas (documento de seguridad, normas técnicas de referencia…). (art. …)
- Para el DPA: el encargado debe comprometer medidas concretas (anexo de seguridad), no genéricas.

## 5. Oficial / delegado de protección de datos
- ¿Existe la figura? ¿Es obligatoria para responsables y/o encargados? ¿En qué supuestos? (art. …)
- Para el DPA: pedir datos de contacto del oficial o punto de contacto de privacidad del encargado.

## 6. Derechos de los titulares
- Derechos reconocidos y plazos legales de respuesta. (art. …)
- El encargado debe asistir al responsable en plazos compatibles con los legales.

## 7. Otros marcos
Indica qué marcos extranjeros se usan **solo como referencia informativa** (no cambian el semáforo ni los plazos). Regla general: nunca sustituyas un plazo de esta jurisdicción por uno de otro marco.
