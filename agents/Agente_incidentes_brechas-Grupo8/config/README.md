# Conectores del agente autónomo

El agente trabaja solo con lo que se declara aquí. Copie `conectores.ejemplo.json` a `conectores.json` (no se versiona) y ajústelo. Si `conectores.json` no existe se usa el ejemplo, que apunta a los datos de demostración.

**Todo acceso es de solo lectura.** Las contraseñas y tokens **nunca** van en este archivo: se indica el *nombre* de una variable de entorno (`*_env`) y el valor se define en `.env`. Las rutas locales deben estar dentro del proyecto; `config/`, `.ib-data/`, `.git/` y `.env` están vetados.

## `conocimiento` (base de conocimiento)
| tipo | campos | qué hace |
|---|---|---|
| `carpeta` | `ruta` | Indexa los `.md/.txt/.log/.json/.csv` de la carpeta y los busca por relevancia (BM25) |
| `http` | `url`, `param` (def. `q`), `auth_env` | GET `url?q=<consulta>` a un buscador interno (wiki, SharePoint, Confluence…) |

## `sistemas` (sistemas y subsistemas)
| tipo | campos | qué hace |
|---|---|---|
| `archivos` | `ruta` | El agente busca patrones o lee las últimas líneas de sus logs |
| `http` | `base_url`, `rutas_permitidas` (globs, p. ej. `["/events","/users/*"]`), `auth_env`, `auth_header` | GET solo a rutas permitidas, mismo origen, sin redirecciones |

## `buzones` (buzón de quejas)
| tipo | campos | qué hace |
|---|---|---|
| `webhook` | `ruta` | Recibe `POST /api/buzon/webhook/<id>` con cabecera `X-Webhook-Token` (= `BUZON_WEBHOOK_TOKEN`) y cuerpo `{asunto, remitente, texto}` |
| `carpeta` | `ruta` | Lee archivos `.md/.txt/.eml` que otro proceso deposite |
| `imap` | `host`, `puerto`, `usuario_env`, `clave_env`, `carpeta` | Lee los correos **no leídos** en modo solo lectura (no los marca) |
| `http` | `url`, `auth_env`, `campo_lista`, `campo_id`, `campo_asunto`, `campo_texto`, `campo_fecha` | GET a una API de quejas que devuelve una lista JSON |

## `autonomia`
`intervalo_seg` (sondeo), `max_por_hora` (tope de análisis automáticos), `desde_dias` (primer sondeo IMAP), `contexto_defecto` (carpeta de contexto que se pasa al agente).

Ejemplo IMAP + API de sistema:
```json
{ "buzones": [{ "id": "quejas-mail", "tipo": "imap", "host": "imap.unsa.example", "usuario_env": "QUEJAS_USER", "clave_env": "QUEJAS_PASS" }],
  "sistemas": [{ "id": "siem", "tipo": "http", "base_url": "https://siem.unsa.example/api", "rutas_permitidas": ["/events", "/assets/*"], "auth_env": "SIEM_TOKEN", "descripcion": "Eventos de seguridad" }] }
```
