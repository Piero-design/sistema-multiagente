# Organizaciones

Cada subcarpeta es **una organización** que usa el sistema. La skill `pims-dpa-auditor` es la misma para todas; lo que cambia es lo que hay aquí.

```
organizaciones/
├── _plantilla/               copiar para crear una organización nueva
│   ├── config_organizacion.json   política interna, cargos de aprobadores y jurisdicción
│   ├── documentos/                ROF, MOF, TUPA, organigrama, manuales… (originales)
│   └── contratos/                 contratos de proveedores a auditar
├── inversiones_altiplano/    organización ficticia de los contratos de prueba de la v1.1
└── unsa/                     caso de prueba del TIF (configuración provisional)
```

Cuando se genera el perfil, aparece `perfil_organizacion.md` junto a la configuración.

## Crear una organización

### Desde la página (recomendado)

1. En **Organización y perfil**, pulsa **Crear otra organización** e indica id, nombre, jurisdicción y los cargos que actúan como DPO y como Legal. n8n crea la carpeta con la configuración de `_plantilla/`.
2. Revisa con el DPO la política interna de `config_organizacion.json` (plazos, países aprobados, certificaciones). La página no la edita.
3. Sube los documentos institucionales y pulsa **Generar perfil**. El modelo configurado lo redacta y n8n valida su formato.
4. Revisa el perfil, sobre todo la sección 8, y pulsa **Validar perfil como DPO**.
5. Audita contratos eligiendo esa organización.

### A mano (sin n8n)

1. Copia `_plantilla/` con un id en minúsculas, sin tildes ni espacios (p. ej. `municipalidad_cayma`).
2. Edita `config_organizacion.json`:
   - `id_organizacion` y `organizacion`, el nombre completo;
   - `jurisdiccion`: una carpeta existente de `pims-dpa-auditor/jurisdicciones/` (hoy, `peru`);
   - `aprobadores_cargos`: cómo se llaman en esta organización el rol DPO y el rol Legal;
   - la política interna (plazos, países, certificaciones), revisada con el DPO.
3. Pon los documentos institucionales en `documentos/`.
4. Genera el perfil con la skill `pims-perfilador-organizacion` y guárdalo como `perfil_organizacion.md`.
5. Valida el formato: `python pims-perfilador-organizacion/scripts/validar_perfil.py organizaciones/<id>/perfil_organizacion.md`.
6. El DPO lo revisa y cambia `Estado` a `Validado por DPO (nombre, fecha)`.
7. Audita contratos indicando la organización, y calcula con:
   `python pims-dpa-auditor/scripts/calcular_resultado.py resultado.json --org organizaciones/<id>`

El perfil es **opcional**: sin él la auditoría funciona como en la v1.1, con más supuestos.

## Qué aporta cada pieza

| Pieza | Aporta | No puede |
|---|---|---|
| `config_organizacion.json` | Plazos y listas de la política interna, cargos de aprobadores, jurisdicción | Bajar exigencias de la ley (el script advierte si un plazo interno no deja margen para cumplir el legal) |
| `perfil_organizacion.md` | Proceso de origen de cada tercero, categorías de datos, nivel de riesgo PII, terceros sin contrato | Servir como evidencia de cumplimiento ni relajar la evaluación (regla 9, asimetría) |
