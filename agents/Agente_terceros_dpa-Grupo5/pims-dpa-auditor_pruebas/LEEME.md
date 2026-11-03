# Archivos de prueba — pims-dpa-auditor v2.0

Contratos ficticios, resultados de referencia y pruebas automáticas. Los contratos y documentos fueron redactados por el grupo y no contienen datos personales reales.

## Pruebas automáticas (sin modelo de IA)

```
python pims-dpa-auditor_pruebas/ejecutar_pruebas.py
```

28 pruebas sobre la parte determinista: regresión exacta contra la v1.1 (el desglose por sección del Anexo A se verifica aparte), jurisdicciones, coherencia de política, perfil, validador de perfiles y compatibilidad. Deben salir **27/27 correctas**.

## Todas las pruebas del proyecto

| Prueba | Necesita | Resultado esperado |
|---|---|---|
| `python pims-dpa-auditor_pruebas/ejecutar_pruebas.py` | Solo Python | 28/28 |
| `python n8n/pruebas/equivalencia_py_js.py` y `equivalencia_perfil.py` | Python y Node | IDÉNTICOS |
| `python n8n/pruebas/probar_flujos.py --raiz <copia>` | n8n y el modelo simulado | 30/30 |
| `python web/pruebas/probar_pagina.py --raiz <copia>` | n8n y Playwright | 10/10 |
| `python pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py` | n8n y un modelo | Con el simulado, 120/120; con un modelo real, mide su calidad |

Detalle de las de n8n en `n8n/INSTALACION_N8N.md` §6 y de la página en `web/LEEME.md`.

## contratos/
| Archivo | Caso | Propósito |
|---|---|---|
| dpa_nubeandina.md | NubeAndina (centro de contacto) | Contrato deficiente con fallas críticas sembradas |
| dpa_andescloud_bueno.md | AndesCloud (hosting) | Contrato conforme, para verificar que la escala discrimina |
| dpa_ambiguo_inyeccion.md | DigiServ (addendum) | Cláusulas vagas y un intento de inyección de instrucciones |

## resultados/ (referencia del TIF, fecha 2026-10-01)
| Archivo | Puntaje | Dictamen |
|---|---|---|
| resultado_NubeAndina.json | 22 (riesgo alto) | No recomendable sin enmiendas |
| resultado_AndesCloud.json | 100 (riesgo bajo) | Recomendable |
| resultado_DigiServ.json | 0 (riesgo alto) | No recomendable sin enmiendas |
| informe_DPA_NubeAndina.md | Informe completo de 11 secciones | |

`ejecuciones_2026-10-07/` guarda las ejecuciones en Claude Code con la v1.1 (ver `MCP_SETUP.md` §8).

## unsa/ (Etapa 4)

Cinco contratos ficticios de proveedores de la UNSA, sus evaluaciones de referencia, los resultados esperados y un comparador para medir modelos (concordancia, kappa, dictamen). Ver `unsa/LEEME.md`.

## organizaciones_prueba/ (v2.0)
| Archivo | Propósito |
|---|---|
| altiplano_con_perfil/documentos/ | Dos documentos institucionales ficticios (ROF y manual de procesos). El manual contiene **a propósito** una nota dirigida a un evaluador |
| altiplano_con_perfil/perfil_organizacion.md | Perfil de referencia: lo que debería producir el perfilador con esos documentos. La nota queda en la sección 8 y no como hecho |
| altiplano_con_perfil/config_organizacion.json | Configuración de esa organización (cargos reales de sus aprobadores) |
| perfil_contaminado.md | El mismo perfil, pero como si el perfilador hubiera obedecido la nota ("homologado, no requiere DPA"). `validar_perfil.py` debe rechazarlo y el cálculo no debe cambiar |

## casos_de_prueba.json
9 casos con su comportamiento esperado: los 1 a 5 vienen de la v1.1 y los 6 a 9 son nuevos (perfil, asimetría y perfilador). Estos casos se ejecutan **con el modelo**: adjuntar el archivo indicado, y la organización si corresponde, y comparar con `expected_output`.

## Recalcular un resultado a mano

Desde la raíz del proyecto:

```
python pims-dpa-auditor/scripts/calcular_resultado.py pims-dpa-auditor_pruebas/resultados/resultado_NubeAndina.json --org organizaciones/inversiones_altiplano --fecha-ref 2026-10-01 --salida prueba.json
```

Usa `--salida` para no sobrescribir el resultado de referencia.
