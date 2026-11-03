# Caso UNSA: contratos supuestos y evaluaciones de referencia (Etapa 4)

> **Los cinco contratos son ficticios.** Se redactaron para el TIF con el formato de contratos reales
> de una universidad pública peruana. No corresponden a contratos de la Universidad Nacional de San
> Agustín de Arequipa ni a empresas existentes, y no contienen datos personales reales.

## Qué hay aquí

| Carpeta / archivo | Contenido |
|---|---|
| `contratos/` | Los 5 contratos supuestos (también copiados en `organizaciones/unsa/contratos/`, para subirlos desde la página). |
| `referencia/ref_*.json` | Evaluación "ideal" de cada contrato, control por control, como debería entregarla el modelo. Incluye `_alternativas` en los controles discutibles. |
| `esperado/esperado_*.json` | La referencia después de pasar por `calcular_resultado.py` con la organización `unsa` y fecha 2026-10-13: puntaje, alertas de renovación y dictamen calculados por código. |
| `construir_referencia.py` | Genera `referencia/` y `esperado/`. Comprueba que cada cita exista literalmente en el contrato y tenga 20 palabras o menos. |
| `comparar_con_referencia.py` | Compara resultados del sistema con `esperado/` (concordancia, kappa, críticos, puntaje, dictamen, alertas). |
| `ejecutar_casos_unsa.py` | Audita los 5 contratos a través de n8n con el modelo configurado y llama al comparador. |
| `casos_unsa.json` | Los mismos casos en formato de evaluación de la skill (prompt + resultado esperado). |
| `corridas/` | Se crea al ejecutar; una carpeta por corrida y modelo. No se entrega en el zip. |

## Los cinco casos

Cada contrato se diseñó para probar algo distinto del criterio de la skill.

| # | Proveedor (ficticio) | Servicio | Riesgo PII | Puntaje | Dictamen | Qué prueba |
|---|---|---|---|---|---|---|
| 01 | Plataforma Aprende Andes S.A.C. | Aula virtual | Alto | 50 (medio) | No recomendable sin enmiendas | Uso de datos para entrenar IA de terceros, aviso en 72 h, alojamiento en EE. UU. El puntaje no es malo, pero las 3 alertas Altas mandan (regla A). |
| 02 | Laboratorio Clínico Misti S.A.C. | Exámenes médicos de ingreso | Alto | 46 | No recomendable sin enmiendas | Datos de salud (sensibles). Aviso en 48 h frente a las 24 h internas. |
| 03 | Recaudo Sur Pagos S.A. | Pasarela de pago de tasas | Alto | 99 | Recomendable con condiciones | Un buen contrato: solo alertas Medias (SOC 2 de más de 12 meses y preaviso de renovación hasta el 2026-11-30, calculado por código). |
| 04 | Seguridad Integral Characato S.A.C. | Videovigilancia con reconocimiento facial | Alto | 0 | No recomendable sin enmiendas | Biometría, fines propios, sin aviso ni eliminación, y contrato **vencido** el 2026-06-30 (alerta de renovación del script). |
| 05 | Ingeniería de Software Altoandino S.A.C. | Soporte del sistema académico | Medio | 31 | No recomendable sin enmiendas | Contrato estatal típico: solo dice "cumplirá la Ley 29733". Muestra que remitir a la ley no sustituye las cláusulas. |

**Controles discutibles** (donde dos auditores razonables podrían diferir; se aceptan como alternativa):
01: 3 · 02: 4 · 03: 1 · 04: 3 · 05: 4. Están en el campo `_alternativas` de cada control en `referencia/`.

## Cómo usarlo

**Para medir un modelo de punta a punta** (n8n en marcha, modelo elegido en Configuración):

```
python pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py
python pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py --repeticiones 3      # estabilidad
python pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py --casos 01,04
```

Deja los informes, los JSON y `comparacion.md` en `corridas/<fecha>_<modelo>/`. Para comparar modelos,
cambia el modelo en la página (Configuración) y vuelve a ejecutarlo.

**Para comparar resultados ya guardados** (por ejemplo, exportados desde la página o de `datos/registro/`):

```
python pims-dpa-auditor_pruebas/unsa/comparar_con_referencia.py datos/registro --salida comparacion.md
```

**Desde la página:** elige la organización *UNSA*, sube uno de los contratos de
`organizaciones/unsa/contratos/` y compara el resultado con la tabla de arriba.

### Cómo leer la comparación

- **Concordancia exacta** y **con alternativas**: porcentaje de los 26 controles con el mismo estado.
- **Kappa de Cohen**: acuerdo corregido por azar. Más de 0,8 es casi perfecto; entre 0,6 y 0,8, sustancial.
- **Críticos**: acuerdo en los 9 controles de peso 3. Es lo que más mueve el puntaje.
- **Dictamen** y **alertas Altas cubiertas**: lo que importa al DPO. Un modelo puede acertar 24 de 26
  controles y aun así cambiar el dictamen si falla un control crítico.

Con el modelo simulado (`n8n/pruebas/modelo_simulado.py`) la comparación da 100 %: eso comprueba el
circuito, no la calidad. Para medir calidad hay que usar un modelo real.

## Importante: revisar las referencias

Las evaluaciones de `referencia/` las redactó el asistente que construyó el sistema. **Son una propuesta,
no la verdad.** Antes de usarlas en el TIF como verdad de referencia, el grupo (idealmente con el docente
en el rol de DPO) debe revisar control por control y corregir lo que no comparta. Si se edita algo,
se cambia en `CASOS` dentro de `construir_referencia.py` y se ejecuta:

```
python pims-dpa-auditor_pruebas/unsa/construir_referencia.py
```

La fecha de referencia está fija en 2026-10-13 para que las alertas de renovación sean reproducibles.
Si se cambia, cambian las alertas del script y los puntajes de los casos 03 y 04.
