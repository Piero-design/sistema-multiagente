# Instalación del agente ISO 27701 en Windows (PowerShell)

Este kit incorpora los workflows exportados por el equipo. Es una preparación para ejecutar n8n y Qdrant localmente. Los tres workflows aún requieren importación, credenciales propias y pruebas; no contienen el PDF completo de la norma.

## 1. Preparar Windows

- Usar una versión de Windows 10/11 compatible con Docker Desktop (preferentemente Windows 11 actualizado).
- Recomendado: 8 GB de RAM o más. Virtualización habilitada en el BIOS/UEFI (puede verse en Administrador de tareas > Rendimiento > CPU).
- Abrir **PowerShell como administrador**, ejecutar `wsl --version`. Si ya está instalado, `wsl --update`. Si no, `wsl --install` y reiniciar cuando lo pida.
- Instalar Docker Desktop desde https://docs.docker.com/desktop/setup/install/windows-install/ y seleccionar el motor de WSL 2 cuando corresponda.
- Abrir Docker Desktop y esperar a que termine el arranque.
- En PowerShell normal, verificar:

```powershell
docker --version
docker compose version
docker info
```

`docker info` debe mostrar información del servidor; un error de conexión significa que Docker Desktop aún no está listo.

## 2. Descomprimir este ZIP

Extraer la carpeta del kit en una ruta sin espacios, por ejemplo `C:\agente-iso27701`. En PowerShell, ir a la carpeta **que contiene el archivo `compose.yaml`**, por ejemplo:

```powershell
cd C:\agente-iso27701
Get-ChildItem
```

Se deben ver `compose.yaml`, `.env.example`, `LEEME.md` y la carpeta `workflows`. Windows suele ocultar archivos cuyo nombre comienza con punto; `Get-ChildItem -Force` los muestra.

## 3. Preparar la configuración y clave de Qdrant

En la misma carpeta ejecutar **PowerShell** (no `cmd`):

```powershell
Copy-Item .env.example .env
$clave = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
(Get-Content .env) -replace '^QDRANT_API_KEY=.*$', "QDRANT_API_KEY=$clave" | Set-Content -Encoding ASCII .env
```

Estas órdenes generan automáticamente una clave aleatoria larga en `.env`. No compartas el contenido de `.env` ni lo subas a repositorios.

Para validar el archivo, sin mostrar la clave, ejecuta:

```powershell
Test-Path .env
```

Debe devolver `True`.

## 4. Levantar los servicios

Con Docker Desktop en marcha, ejecuta:

```powershell
docker compose config --quiet
docker compose up -d
docker compose ps
```

La primera descarga puede tardar varios minutos, dependiendo de Internet. `docker compose ps` debería mostrar `n8n` y `qdrant` en estado `Up` (el nombre de contenedor exacto depende de la carpeta).

Abre http://localhost:5678 y crea la cuenta administradora local que te pida n8n. Usa contraseñas propias para la cuenta local.

**Aviso:** Qdrant queda accesible solo dentro de la red privada de Docker, a través de `http://qdrant:6333`. El chat no está publicado en Internet.

## 5. Importar workflows

En n8n, crea/importa los workflows con menú `...` > `Import from File` (las etiquetas concretas pueden cambiar según versión). Importar en este orden:

1. `workflows/Skill_Evaluacion_Riesgos_27701.json`
2. `workflows/RAG_ISO27701.json`
3. `workflows/Agente_Evaluacion_Riesgos.json`

En el nodo `obtener_skill_evaluacion` del Agente, vuelve a seleccionar el workflow **Skill** importado, porque el ID del entorno cloud original puede ser diferente en tu instalación. Guarda.

## 6. Credenciales Gemini

En https://aistudio.google.com/apikey crea una API key (sujeta a los términos y cuotas de Google). En n8n agrega una credencial **Google Gemini(PaLM) API** y asígnala a los nodos Gemini Chat Model y Gemini Embeddings de los workflows Agente y RAG. Comprueba que el modelo seleccionado en el nodo esté disponible con tu cuenta. No compartas la API key.

## 7. Prueba básica

En el workflow Agente, abre el chat de prueba y envía:

- `Hola, ¿cuál es tu función?`
- `Quiero evaluar riesgos de un proveedor de servicios. ¿Qué datos necesitas?`

El segundo mensaje sirve para comprobar que el Agente puede llamar a `obtener_skill_evaluacion`. La búsqueda RAG y la exactitud normativa **no se validarán hasta que carguemos el libro autorizado**.

**Importante:** los archivos JSON del equipo conservan `Simple Vector Store`. Qdrant ya está iniciado pero **todavía no se usa**; lo conectaremos después de validar la migración, para preservar los datos incluso al reiniciar. El PDF del libro no está incluido en este kit.

## 8. Si falla

En la misma carpeta del proyecto:

```powershell
docker compose ps
docker compose logs --tail=100 n8n
docker compose logs --tail=100 qdrant
```

- `docker no se reconoce`: Docker Desktop no está instalado o PowerShell se abrió antes de instalarlo; cierra y abre PowerShell.
- `Cannot connect to the Docker daemon`: inicia Docker Desktop y espera a que esté listo.
- `port 5678 is already allocated`: otro proceso ya usa el puerto 5678; verifica con `netstat -ano | findstr :5678` antes de modificar Compose.
- `http://localhost:5678` no abre: comprobar `docker compose ps` y los logs de n8n.
- No ejecutes `docker compose down -v` porque borraría los volúmenes (n8n y Qdrant).

Para detener sin perder datos: `docker compose stop`. Para reanudar: `docker compose start`.

## Notas de seguridad y alcance

- La interfaz de n8n se vincula a `127.0.0.1` para evitar exposición directa en la red local.
- El archivo `.env` guarda la clave Qdrant; mantenlo privado.
- Si se usa Gemini, los prompts y fragmentos enviados al servicio se procesarán fuera del equipo. Este modo requiere Internet y puede tener cuotas/costos. Localizar el modelo con Ollama es una mejora opcional posterior.
- Las pruebas de tus compañeros, documentadas en su informe, no sustituyen una verificación nueva en tu PC.
