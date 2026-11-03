# datos/ — lo que escriben los flujos de n8n

| Carpeta / archivo | Contenido |
|---|---|
| `config_modelo.json` | Modelo de IA en uso (proveedor, modelo, URL, API key). Se cambia desde la página o con `POST /webhook/pims/config`. **Contiene la API key: no lo compartas.** |
| `registro/<id>.json` y `.md` | Registro de DPAs: resultado calculado e informe de 12 secciones de cada auditoría, con su historial de aprobación. |
| `registro/<id>.contrato.txt` | Texto del contrato evaluado; lo usa el chat para citarlo. |
| `chats/exp_<id>.json`, `chats/org_<id>.json` | Conversaciones del chat de cada expediente u organización (quién preguntó, cuándo y con qué modelo). |
| `trabajos/<T…>.json` | Avance de cada auditoría o perfil en curso (lo consulta la página). Se pueden borrar los antiguos. |
| `fallidos/<T…>.md` | Respuesta cruda del modelo cuando una auditoría falló, para revisarla. |
| `tmp/` | Archivos temporales (contratos subidos, prompts para Claude Code). Se pueden borrar. |
| `alertas_renovacion.json` | Resultado del control semanal de renovaciones (cada lunes a las 07:52). |
