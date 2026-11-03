# UNSA — caso de prueba del TIF

**Estado: configuración provisional. Hay contratos supuestos; faltan los documentos institucionales y el perfil.**

| Carpeta / archivo | Estado |
|---|---|
| `config_organizacion.json` | Política interna por defecto de la v1.1 y **cargos de aprobadores supuestos** (Oficial de Datos Personales y Oficina de Asesoría Jurídica). Hay que confirmarlos con el ROF y el MOF. |
| `contratos/` | 5 contratos **ficticios** de proveedores de la UNSA, listos para auditar. Resultados esperados y cómo medir un modelo: `pims-dpa-auditor_pruebas/unsa/LEEME.md`. |
| `documentos/` | Vacía. Aquí van los documentos institucionales cuando se consigan. |
| `perfil_organizacion.md` | Aún no existe. Se genera desde la página con **Generar perfil**. |

Mientras no haya documentos, el sistema audita con la configuración sola: funciona igual, solo que sin el
contexto del perfil (procesos, áreas, terceros conocidos).

## Qué documentos conseguir

En orden de utilidad para el perfil. Con los tres primeros ya se obtiene un perfil útil.

| Documento | Para qué le sirve al sistema | Sección del perfil |
|---|---|---|
| **ROF** (Reglamento de Organización y Funciones) | Unidades y sus funciones: quién trata qué datos. | 2, 3 |
| **MOF** o manual de puestos / clasificador de cargos | Cargos reales del DPO o responsable de datos y del área legal → `aprobadores_cargos`. | 3 |
| **Mapa de procesos** o manual de procesos | Procesos (admisión, matrícula, bienestar, pagos, biblioteca) y los datos que usa cada uno. Sube el riesgo cuando un proceso trata datos sensibles. | 4, 5 |
| **TUPA** y **TUSNE** | Trámites y qué datos se piden a estudiantes y ciudadanos. | 5 |
| **Estatuto** | Naturaleza jurídica, órganos de gobierno. | 1, 2 |
| **Organigrama** | Confirma la estructura del ROF. Si es una imagen, convertirla a PDF con texto o describirla. | 2 |
| Políticas de **privacidad**, **seguridad de la información** o de **TI**; plan de gobierno digital | Plazos y exigencias internas que pueden endurecer la auditoría. | 7 |
| Plan anual de contrataciones o relación de contratos | Terceros que tratan datos → lista "Terceros sin DPA evaluado". | 6 |

## Dónde buscarlos

La Ley Universitaria (Ley 30220) obliga a las universidades públicas a publicar en su portal de
transparencia, entre otros, el estatuto, el TUPA y sus instrumentos de gestión.

1. **Página de la UNSA en gob.pe** — https://www.gob.pe/institucion/universidad-nacional-de-san-agustin
   Revisar *Informes y publicaciones* y *Normas legales* (resoluciones de Consejo Universitario y de
   Asamblea Universitaria: ahí se aprueban el ROF, el MOF y el estatuto).
2. **TUPA de la UNSA** (verificado, aprobado por RCU N.° 1171-2016 y modificado por RCU 673-2017 y 936-2017):
   https://cdn.www.gob.pe/uploads/document/file/5797555/5144213-09-tupa-rcu-0262-2020.pdf
   Comprobar en la página de gob.pe si hay una versión más reciente.
3. **Portal de Transparencia Estándar** de la UNSA y su portal institucional (*unsa.edu.pe*): sección de
   documentos de gestión.
4. **SEACE** (Sistema Electrónico de Contrataciones del Estado): contratos y bases de procesos de
   selección reales de la UNSA. Sirven como contratos de prueba **públicos**; antes de subirlos, quitar
   cualquier dato personal (firmas, DNI, domicilios de personas naturales).
5. Si un documento no está publicado: **solicitud de acceso a la información pública** (Ley 27806) o
   pedirlo al docente.

> **Cuidado con los buscadores:** muchas universidades nacionales publican en el mismo dominio de gob.pe.
> Durante la Etapa 4 un "ROF" encontrado por búsqueda resultó ser de la Universidad Nacional de Cañete,
> no de la UNSA. Comprueba siempre en la primera página del documento que el nombre de la universidad y la
> resolución que lo aprueba sean de la UNSA, y que sea la versión vigente.

## Pasos cuando lleguen los documentos

1. En la página, **Organización y perfil** → UNSA → sube los PDF o DOCX (o cópialos a `documentos/`).
2. Pulsa **Generar perfil** (jurisdicción `peru`). El modelo configurado lo redacta en el formato fijo,
   citando documento y página.
3. Revisa la sección 8 del perfil (contenido sospechoso) y que cada dato tenga su cita `[Dn, p. X]`.
4. Corrige `aprobadores_cargos` con los cargos reales de la sección 3 editando `aprobadores_cargos` en `config_organizacion.json`.
5. Que el DPO, o el docente en ese rol, **valide el perfil**. Hasta entonces cada auditoría lleva la advertencia "Perfil de la organización sin validar por el DPO" en la trazabilidad.
6. Vuelve a auditar los 5 contratos supuestos y compara con los resultados sin perfil: el perfil solo
   puede endurecer la evaluación (regla de asimetría), nunca suavizarla.
