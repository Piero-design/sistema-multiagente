# Publicar el proyecto en GitHub y trabajar en equipo

## 1. Crear el repositorio

Crear un repositorio nuevo en GitHub, por ejemplo **`ISO-Studio-Auditoria`**, preferiblemente **privado** hasta revisar los archivos y acordar permisos del material. No seleccionar «Initialize with README», `.gitignore` ni licencia porque ya están aquí.

## 2. Primer push desde Windows

Con Git instalado y PowerShell ubicado en la carpeta raíz descargada:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "feat: ISO Studio 2.0 local con n8n, Qdrant, React y artefactos"
git remote add origin https://github.com/TU_USUARIO/ISO-Studio-Auditoria.git
git push -u origin main
```

Sustituir `TU_USUARIO` por el propietario real. Si Git pide identificación:

```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

Usar autenticación de GitHub a través del navegador o Git Credential Manager: **no** pegar tokens ni contraseñas en URLs de remotos. Si el repositorio ya existe y tiene commits, NO forzar (`--force`) el push; primero conciliar la historia o crear un repo vacío nuevo.

## 3. Instalación por los compañeros

```powershell
git clone https://github.com/TU_USUARIO/ISO-Studio-Auditoria.git
cd ISO-Studio-Auditoria
```

Luego seguir `docs/INSTALAR_WINDOWS.md`. Cada persona crea sus credenciales propias de Gemini y Qdrant, importa los workflows y carga sus propios documentos autorizados.

## 4. Ramas y cambios

```powershell
git switch -c feature/mejoras-interfaz
# editar código y probar
git add .
git commit -m "feat(ui): mejora interfaz del chat"
git push -u origin feature/mejoras-interfaz
```

Abrir un **Pull Request** hacia `main`, revisar, probar y hacer merge. Para actualizar con cambios nuevos:

```powershell
git switch main
git pull --ff-only origin main
```

No hacer force-push sobre ramas compartidas. No hacer commit de `.env`, `node_modules`, `dist`, `.local-artifacts`, credenciales, PDFs ISO con licencia, o backups Docker.

## 5. Compartir acceso

En la configuración del repositorio GitHub → **Collaborators** / **Manage access**, invitar a los integrantes del equipo como colaboradores. Si se comparte por privado cada compañero debe aceptar la invitación para clonar.
