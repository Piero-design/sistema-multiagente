# Seguridad y privacidad

## Nunca versionar ni compartir

- Archivo real `infra/.env` que contiene la API Key de Qdrant.
- Archivo real `frontend/.env` de cada equipo si en él se configuran endpoints internos o secretos adicionales.
- API Key de Gemini; tokens, encabezados de autorización o credenciales de n8n.
- Archivo de credenciales desencriptadas de n8n, su base de datos y el directorio `.n8n`.
- Volúmenes Docker de Qdrant/n8n, historiales de chat, informes privados o datos personales.
- Norma ISO/IEC 27701 o textos de pago sin autorización de distribución.

## Seguridad de red

n8n se expone únicamente en `127.0.0.1:5678`; Express en `127.0.0.1:4317`; Vite en `127.0.0.1:5173`; Qdrant no publica puertos al host. Este diseño es para desarrollo local y **no** para exponer en Internet sin autenticación, HTTPS, control de CORS, rate limit, auditoría y separación de usuarios.

Gemini se consulta por API externa: la información seleccionada se envía a un servicio de terceros. No usar datos personales reales o sensibles en pruebas sin autorización.

## Revisión de commits

```powershell
git status --short
git diff --cached --name-only
git grep -ni -E 'AIza|sk-[A-Za-z0-9]|ghp_|QDRANT_API_KEY=.{30}|Bearer ' -- . ':!docs/*'
```

El último comando es orientativo y puede producir falsos positivos: revisar manualmente TODOS los cambios de configuración. `gitignore` impide commits accidentales de archivos sin seguimiento, **pero no elimina secretos ya versionados**. Si se publica alguna clave, revocarla/rotarla en el proveedor y eliminarla del historial si es necesario.
