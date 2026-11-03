# Marco legal Perú — Ley N.° 29733 y Reglamento (D.S. 016-2024-JUS)

> Resumen operativo para auditoría de encargados. El nuevo Reglamento se publicó el 30/11/2024 y entró en vigor a fines de marzo de 2025, reemplazando al D.S. 003-2013-JUS. Cuando el informe cite un artículo concreto, indica "verificar numeración en texto oficial" si no se ha confirmado.

## 1. Relación responsable–encargado
- El encargo de tratamiento debe constar en un contrato o instrumento que delimite el tratamiento por cuenta del responsable.
- El encargado no puede tratar los datos para fines propios; si lo hace, asume responsabilidad como responsable.
- Deber de confidencialidad del encargado y su personal, también después de terminada la relación.

## 2. Incidentes de seguridad (punto crítico de contraste)
- El **encargado** debe informar **de inmediato** al responsable cuando detecta un incidente.
- El **responsable** debe notificar a la Autoridad Nacional de Protección de Datos Personales (ANPD) **dentro de las 48 horas** desde que toma conocimiento, aun si el incidente se resolvió internamente.
- Si el incidente afecta derechos de los titulares, el responsable debe comunicárselo también dentro de **48 horas**, en lenguaje claro.
- Si el incidente ocurre en entorno digital, se informa además al Centro Nacional de Seguridad Digital.
- El incidente debe documentarse (hechos, efectos, medidas).

**Consecuencia para el DPA:** un plazo de aviso del encargado de 48 h o más deja al responsable sin margen para cumplir. El máximo aceptable lo fija `assets/config_organizacion.json` (por defecto 24 h). Plazos de 72 h copiados de contratos RGPD → 🔴 No cumple frente a la política interna.

## 3. Flujo transfronterizo
- La Ley 29733 (art. 15) condiciona el flujo transfronterizo a que el país receptor ofrezca niveles de protección adecuados o, en su defecto, a que el emisor garantice que el tratamiento se ajuste a la ley (p. ej. cláusulas contractuales), salvo excepciones legales.
- Para el DPA: exigir lista de países, garantías contractuales y aviso de cambios. El Reglamento regula el flujo transfronterizo; confirma requisitos formales vigentes ante la ANPD antes de un uso formal.

## 4. Seguridad
- El Reglamento exige medidas de seguridad documentadas (documento de seguridad) y toma como referencia normas técnicas como la NTP-ISO/IEC 27001.
- Para el DPA: el encargado debe comprometer medidas técnicas y organizativas concretas (anexo de seguridad), no genéricas.

## 5. Oficial de Datos Personales
- El Reglamento obliga a responsables **y encargados** a designar un Oficial de Datos Personales en ciertos supuestos (sector público, grandes volúmenes, datos sensibles, entre otros), con plazos de adecuación escalonados según tamaño de empresa.
- Para el DPA: pedir datos de contacto del oficial o del punto de contacto de privacidad del encargado.

## 6. Derechos de los titulares
- Derechos ARCO y portabilidad (incorporada por el nuevo Reglamento). El encargado debe asistir al responsable en plazos compatibles con los legales.

## 7. Otros marcos (decisión de diseño v1.1)
El alcance normativo es la Ley 29733 y su Reglamento. El RGPD (y el Anexo D de ISO 27701, de carácter informativo) se usa **solo como referencia**: si el contrato lo declara aplicable, menciónalo en la sección 5 del informe, pero no modifica el semáforo ni los plazos. Nunca sustituyas un plazo peruano por uno del RGPD (p. ej. 72 h).
