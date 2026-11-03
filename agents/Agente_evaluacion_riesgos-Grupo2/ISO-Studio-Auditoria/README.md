# ISO Studio — Agente de Auditoría de Sistemas (local)

Aplicación académica desarrollada para el curso de Auditoría de Sistemas. Se ejecuta localmente en Windows con **n8n + Google Gemini + Qdrant + React/Vite + Node.js/Express**. Es compatible con otros sistemas con Docker, Node.js y ajustes de rutas.

> **Estado comprobado por el equipo:** chat de Gemini desde React, invocación del Skill de riesgos en n8n, ingesta/búsqueda de un PDF ficticio con Qdrant, visualización de diagramas Mermaid y exportación a PDF/DOCX. **Pendiente:** carga y validación rigurosa del documento ISO/IEC 27701:2025 definitivo. Los JSON incluidos en este repositorio son **plantillas reconstruidas** a partir de los flujos recibidos; si se necesita reproducir exactamente la última ejecución, usar los JSON exportados del n8n local del equipo (consulta `docs/EXPORTAR_N8N.md`).

## Requisitos

- Windows 10/11 con virtualización activada y WSL 2.
- Docker Desktop en **Linux containers** (reservar aproximadamente 8 GB de RAM para Docker cuando sea posible).
- Node.js **22 LTS o posterior** y npm.
- Cuenta de Google AI Studio con clave API de Gemini y cuota disponible.
- Un navegador moderno. Git es opcional si se descarga ZIP.

> n8n, Qdrant, React y el generador de documentos pueden ejecutarse localmente. Gemini **es externo**; requiere red y está sujeto a cuotas. No subas información confidencial sin evaluar la privacidad de la API.

## Inicio rápido — compañeros en Windows

En dos ventanas de PowerShell:

**Terminal A: Docker**

```powershell
cd 'C:\ruta\a\ISO_Studio_Equipo_GitHub'
Copy-Item '.\infra\.env.example' '.\infra\.env'
$clave = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
(Get-Content '.\infra\.env') -replace '^QDRANT_API_KEY=.*$', "QDRANT_API_KEY=$clave" | Set-Content -Encoding ascii '.\infra\.env'
docker compose -f '.\infra\compose.yaml' up -d
docker compose -f '.\infra\compose.yaml' ps
```

Abre <http://localhost:5678>, crea el usuario local de n8n y configura los **4 workflows** y **credenciales propias** siguiendo **[Instalación completa](docs/INSTALAR_WINDOWS.md)**. Recuerda: una instalación nueva no contiene la base vectorial ni la cuenta n8n de otra máquina.

**Terminal B: frontend, después de configurar y publicar n8n**

```powershell
cd 'C:\ruta\a\ISO_Studio_Equipo_GitHub\frontend'
npm install
Copy-Item '.env.example' '.env'
notepad .env
npm run dev
```

En `frontend/.env` coloca la **URL de producción del Chat Trigger local**, por ejemplo `N8N_CHAT_URL=http://127.0.0.1:5678/webhook/ID-REAL/chat`. El ID se obtiene en **When chat message received**; no copies el ejemplo. Abre <http://127.0.0.1:5173>.

## Componentes

| Carpeta | Contenido |
|---|---|
| `frontend/` | React, Mermaid, estilos, backend Express y exportación PDF/DOCX |
| `infra/` | Docker Compose para n8n y Qdrant, ejemplo de `.env` |
| `n8n/workflows/` | Cuatro plantillas importables sin credenciales: agente, RAG y dos Skills |
| `docs/` | Instalación detallada, arquitectura, exportación real, diagnóstico y seguridad |
| `examples/` | PDF ficticio FARO para probar RAG sin incluir el texto de ISO |
| `scripts/` | Comprobación de servicios en PowerShell |

## Casos de uso verificados

1. Preguntar al agente sobre evaluación de riesgos ISO (el Skill prepara metodología; la veracidad normativa depende del documento indexado).
2. Crear diagramas Mermaid en el chat y exportarlos en SVG/PNG.
3. Crear un informe a partir de Markdown y exportarlo a DOCX o PDF desde React.
4. Recuperar el identificador `FARO-7429` y la revisión de incidentes del PDF ficticio de prueba desde Qdrant.

## Pruebas técnicas

```powershell
cd frontend
npm install
npm run test:parsers
npm run test:exports
npm run build
```

Estas comprobaciones no sustituyen la validación end-to-end de n8n/Qdrant/Gemini en el equipo. Ver [casos de prueba](docs/PRUEBAS.md).

## Seguridad y licencias

- **Nunca subas** `.env`, claves de Gemini, API Keys, credenciales exportadas, la base de datos n8n/Qdrant, documentos con datos privados ni archivos normativos licenciados.
- Los workflows exportados deben revisarse antes de un commit: pueden incluir tokens en parámetros aunque las credenciales se almacenen por separado.
- Docker solo publica n8n en `127.0.0.1:5678`; Qdrant no publica puertos. Express/Vite también escuchan en localhost.
- No incluye ISO/IEC 27701:2025 ni el informe académico original. Añádelos solo si cuentas con permisos y es necesario en un repositorio privado.
- Los archivos generados se almacenan temporalmente en `.local-artifacts` y no se versionan.
- No existe autenticación multiusuario; no exponas esta instalación directamente a Internet.

Consulta [SEGURIDAD](docs/SEGURIDAD.md) y [ARQUITECTURA](docs/ARQUITECTURA.md).

## Equipo y colaboración

Usar ramas `feature/<tema>` para mejoras y pull requests hacia `main`. Para actualizar workflows, exportar desde n8n, depurar secretos y registrar qué cambió. Evitar commits de archivos binarios generados. Ver [GIT_COLABORACION](docs/GIT_COLABORACION.md).
