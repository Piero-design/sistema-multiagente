# bd/ · El Agente 7 sobre la base de datos del PIMS Gestitel

Fases 2, 3, 4 y 7 del plan de migración v2.0 → v3.0, listas y probadas. Las fases 5 y 6 (conectar n8n y cambiar los flujos) todavía no están hechas.

| Archivo | Qué es |
|---|---|
| `gestitel_base_de_datos.sql` | Script del profesor: base en blanco (15 tablas en `public`, 58 en `demo`, sin usuarios). |
| `agente7_terceros_dpa.sql` | Extensión del grupo: 6 tablas, 5 vistas, 2 disparadores y **2 funciones de escritura**. Idempotente. |
| `roles_agente7.sql` | Usuarios autores (`agente7`, `dpo`, `legal`) y los roles `agente7` (n8n) y `agente7_lectura` (chat). |
| `migrar_registros.py` | Carga los expedientes ya calculados, sin llamar al modelo. Usa `psql` y no necesita librerías de Python. |
| `instalar_bd.ps1` | Hace todo lo anterior en orden. Pide las contraseñas y no las guarda en disco. |
| `pruebas/02_reglas.sql` | 10 pruebas de las reglas del motor. Corre dentro de una transacción que se revierte. |

## Instalar

PostgreSQL 17 ya instalado y corriendo (servicio `postgresql-x64-17`):

```powershell
powershell -ExecutionPolicy Bypass -File bd\instalar_bd.ps1
```

Pide la contraseña de `postgres` y dos contraseñas nuevas, una para `agente7` y otra para `agente7_lectura`. Al terminar muestra los conteos, el resultado de la migración y las pruebas de reglas.

## Lo que se verificó (PostgreSQL 17.7, servidor de prueba desechable)

| Comprobación | Resultado |
|---|---|
| Script del profesor | Carga sin errores: `public` 15, `demo` 58, `auth_user` vacío. |
| Extensión ejecutada dos veces | Sin errores; 11 objetos (6 tablas + 5 vistas). |
| Migración de 10 expedientes (2 de `datos/registro` + 8 de referencia) | 10/10 con el mismo puntaje que su JSON, 26 controles cada uno (260 filas) y 8 contratos. Ejecutada dos veces: la segunda no duplica nada. |
| Mapeo al Anexo A | 260/260 controles ligados a `core_annexacontrol`: los 18 A.2 directo y los 8 A.3 por `equivalent_controls`. |
| `pruebas/02_reglas.sql` | 10/10: puntaje 120, rol inválido, estado inválido, Legal antes que el DPO, auditoría duplicada, segunda decisión del DPO, `UPDATE` y `DELETE` de una aprobación se rechazan; DPO → `L` y Legal → `A` funcionan. |
| Permisos | `agente7_lectura` no puede insertar; `agente7` no puede tocar `core_asset`, borrar auditorías ni editar aprobaciones. |

## Correcciones al plan

Al probar el plan contra el JSON real del agente (`assets/esquema_salida.json`) y contra el script del profesor aparecieron estos puntos:

1. **La transacción de §6.2 no funciona en un nodo Postgres de n8n.** Con parámetros (`$1`, `$2`…) el nodo usa el protocolo extendido, que no admite varias sentencias (`BEGIN; INSERT…; COMMIT;`) en una consulta. **Solución:** la transacción vive en la función `agente7_guardar_auditoria(registro jsonb, informe_md text, autor_id int)`, y n8n hace una sola llamada:
   ```sql
   SELECT demo.agente7_guardar_auditoria($1::jsonb, $2, $3);
   ```
   La función es atómica y la usan igual n8n y la migración, así que la traducción a la base está en un solo lugar.
2. **El nodo «Preparar parámetros» de §6.3 deja de hacer falta.** Además, sus nombres no existen en el JSON real. La función ya usa los campos verdaderos:

   | Plan | JSON real del agente |
   |---|---|
   | `r.proveedor.nombre`, `.ruc`, `.pais` | `tercero.nombre`; no hay RUC ni país del proveedor (el tercero se identifica por nombre) |
   | `r.objeto`, `r.rol` | `tercero.servicio`, `tercero.rol` (no existe «Rol invertido») |
   | `c.id`, `c.critico`, `c.cita`, `c.clausula` | `control`, criticidad según la lista fija de 9 controles, `evidencia`, `clausula_dpa` |
   | `c.fuente`: Norma / Ley / Política | `fuente_requisito`: ISO 27701 / Ley aplicable / Ley 29733/Reglamento / Política interna / **Mixta** |
   | `severidad` B/M/A/C | además «Ninguna», que se guarda como `NULL` |
   | `r.contrato.codigo`, `.inicio`, `.fin`, `.preaviso_dias` | `contrato.id_contrato` (casi siempre `null`), `fecha_vigencia_inicio`, `fecha_vigencia_fin`, `preaviso_terminacion_dias` |
   | `r.puntaje`, `r.puntaje_base`, `r.puntaje_por_seccion` | `puntaje_proveedor.valor`, `.base`, `.por_dimension` (con nombres de sección: la función los guarda como `A.2.2`…`A.3`) |
   | `r.alertas_renovacion` | alertas con `tipo = 'Renovación'` dentro de `alertas` |
   | `r.id` | `_registro.id_registro` (`id_evaluacion` se repite entre corridas del mismo contrato) |
   | `r.modelo.*`, `r.trazabilidad.hash_contrato` | `_registro.proveedor`/`.modelo`, `contrato.hash_documento_sha256` |
3. **`requirement_source` no admitía «Mixta»**, que el agente usa en uno de cada cinco controles. Ahora el `CHECK` acepta `'M'`.
4. **Código del contrato:** como `id_contrato` casi siempre viene vacío, la función usa `H-` + los primeros 16 caracteres del SHA-256 del texto. Dos auditorías del mismo texto quedan en el mismo contrato; por ejemplo, NubeAndina migrado y NubeAndina auditado en n8n.
5. **Fase 7:** `datos/registro/` no tiene los 8 casos (está en `.gitignore` y solo tiene lo que se audita en cada equipo). La migración toma los 8 casos de `pims-dpa-auditor_pruebas/resultados/` y `unsa/esperado/`, y además lo que haya en `datos/registro/`.
6. **Versión de PostgreSQL:** el script del profesor lo generó `pg_dump 18.4` y usa `\restrict`, así que necesita **psql 17.6+ o 16.10+** (o 18). Un PostgreSQL 16 anterior a 16.10, que es lo que recomienda la fase 1, falla en la primera línea. `instalar_bd.ps1` comprueba la versión antes de empezar.
7. **Laboratorio clínico (UNSA 02):** `esperado_unsa_02_laboratorio_clinico.json` da **44**, pero README y PROYECTO dicen **46**. La migración guarda 44, que es lo que dice el JSON. Hay que revisar cuál es el valor correcto.
8. Detalles menores: la extensión crea 6 tablas, no 5 (§0); `GRANT SELECT ON ALL TABLES` solo cubre las tablas que ya existen, así que hay que repetirlo cuando otros grupos agreguen tablas.

## Fases 5 y 6: n8n escribe en la base

Con **n8n detenido**:

```powershell
python n8n\instalar_flujos.py --importar   # 14 flujos (incluye «PIMS · Base de datos»)
python n8n\configurar_bd.py                # pide la contraseña de agente7, crea la credencial y activa la base
n8n\iniciar_n8n.bat
```

`configurar_bd.py` comprueba que `agente7` entra a la base. Después crea en n8n la credencial **PIMS Postgres**, que n8n guarda cifrada con un id fijo, y pone `"activo": true` en `datos/config_bd.json`. Para volver a trabajar solo con archivos: `python n8n\configurar_bd.py --desactivar`.

| Flujo | Qué hace con la base |
|---|---|
| **PIMS · Base de datos** (nuevo subflujo) | Lee `datos/config_bd.json`. Si está activo, llama a la función que corresponde con los valores como parámetros. Nunca detiene al flujo que lo llama. |
| **Auditar contrato** | Después del cálculo: `agente7_guardar_auditoria(registro, informe, autor)`. El trabajo queda con `"bd": "guardado"`, o con `"bd": "error"` y una advertencia; los archivos se escriben siempre. |
| **Aprobaciones** | Después de guardar el JSON: `agente7_registrar_decision(...)`. La respuesta incluye `bd: {ok}` o el error del motor. |

Sin base configurada (o con `"activo": false`) todo funciona como en la v2.0. Los flujos se publican aunque la credencial no exista, así que quien no tenga PostgreSQL puede instalarlos igual.

**Probado con n8n 2.43.4 y un PostgreSQL 17.7 de prueba:**
- Una auditoría de UNSA 01 quedó en la base con 50 puntos, 26 controles, el informe y `agente7` como autor.
- La aprobación del DPO y el rechazo de Legal quedaron en `core_dpaapproval`, y el estado pasó a `R`.
- Con la base caída, la auditoría termina igual, con la advertencia «No se guardó en la base de datos: Connection refused».
- `n8n/pruebas/probar_flujos.py` dio 27/29 con la base activa. Las 2 fallas son anteriores a este cambio: la prueba supone que la UNSA no tiene perfil (ahora sí lo tiene), y necesita las organizaciones de prueba `altiplano_perfil` y `altiplano_docs`, que no están en el repositorio.

**Pendiente del plan:** Renovaciones, Consultas y Chat todavía leen de los archivos (§6.5, §6.6 y §9), y falta la pestaña «Cartera de proveedores».
