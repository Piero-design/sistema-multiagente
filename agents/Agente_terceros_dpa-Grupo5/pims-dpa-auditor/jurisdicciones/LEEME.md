# Jurisdicciones

Cada subcarpeta describe la ley de protección de datos de **un país o región**. La organización elige la suya con el campo `"jurisdiccion"` de su `config_organizacion.json`, y la skill lee la carpeta correspondiente en el Paso 5.

```
jurisdicciones/
├── peru/          En uso (contenido de la v1.1)
│   ├── marco_legal.md           resumen operativo en 7 secciones fijas
│   └── parametros_legales.json  los mismos datos en forma estructurada
└── _plantilla/    Punto de partida para un país nuevo
```

## Agregar un país

1. Copia `_plantilla/` con el id del país, por ejemplo `colombia/`. El id va en minúsculas, sin tildes ni espacios.
2. Llena `marco_legal.md` **a partir del texto oficial** de la ley y su reglamento, citando artículos. Puede redactarlo una persona o una IA, pero siempre como borrador.
3. Llena `parametros_legales.json` con los mismos datos y pon `"estado": "Borrador"`.
4. Una persona con conocimiento legal de ese país lo revisa. Al aprobarlo, cambia el estado a `"Verificada"` y registra quién lo revisó.
5. En la organización correspondiente pon `"jurisdiccion": "colombia"`.

## Qué hace la skill según el estado

| Estado | Comportamiento |
|---|---|
| `Plantilla` | **No se puede usar.** El script se detiene con un error. |
| `Borrador` | Se usa, pero el script lo registra en la trazabilidad y el informe lo declara como limitación en la sección 11. |
| `En uso` / `Verificada` | Uso normal. |

## Por qué no se genera automáticamente

La jurisdicción es la base legal de **todas** las evaluaciones de ese país. Un plazo mal copiado (por ejemplo, 72 h donde la ley dice 48 h) arruinaría cada informe sin que nadie lo notara. Por eso siempre pasa por una revisión humana antes de usarse.

## Regla que no cambia

**Rige la ley de la organización (el Responsable)**. El país del proveedor solo importa para evaluar transferencias internacionales. Los marcos extranjeros son referencia informativa: nunca reemplazan un plazo de la jurisdicción configurada.
