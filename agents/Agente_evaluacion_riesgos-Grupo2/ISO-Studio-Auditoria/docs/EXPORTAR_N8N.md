# Obtener los 4 workflows **reales** probados en la PC principal

**Por qué es importante:** los JSON del repositorio son plantillas reconstruidas de la arquitectura probada. Los cambios que se realizaron mediante la interfaz n8n (modificación Qdrant, selección de workflows Skills, metadatos y ajustes finales) solo se reflejan con fidelidad exportando desde el n8n que ya funciona.

## Exportar manualmente (recomendado)

En la PC principal, abrir <http://localhost:5678> y realizar, para cada workflow:

1. Abrir el editor y verificar que está guardado/publicado si corresponde.
2. Menú `...` → **Download** o `Export` (según versión).
3. Guardar el JSON con su nombre en una carpeta local `exportaciones_n8n`.
4. Repetir para `Skill_Evaluacion_Riesgos_27701`, `Skill_Artefactos_ISO_Studio`, `RAG_ISO27701`, `Agente_Evaluacion_Riesgos`.
5. **Revisar los JSON para eliminar datos confidenciales.** n8n suele excluir valores de API keys guardados en Credentials, pero puede exportar **IDs/nombres de credenciales** y valores sensibles escritos directamente como parámetros. No subas JSON sin revisar.

## Comprobación previa al commit

- No incluir tokens, claves Gemini, Qdrant, cookies, contraseñas, encabezados de autorización, URLs externas privadas.
- Eliminar los campos `credentials` del nodo si se quiere una plantilla neutral para colaboradores. Al hacerlo, los compañeros deberán crear/seleccionar sus propias credenciales en n8n.
- Borrar `meta.instanceId`, `pinData`, historial de pruebas y datos personales de ejemplos cuando corresponda. Las referencias a IDs de subworkflows **deben volver a seleccionarse** en cada instalación.
- Mantener los parámetros de operación, colecciones `iso27701_2025` y las conexiones de nodos.
- Si contiene material de ISO con licencia, retirarlo; distribuir solo flujos/skills redactados por el equipo.

## Sustituir las plantillas

Una vez revisados, reemplazar los JSON respectivos en `n8n/workflows/` del repositorio local. Luego:

```powershell
git status
git diff -- n8n/workflows
git add n8n/workflows
git commit -m "chore(n8n): sincronizar workflows exportados y saneados"
git push
```

**No exportar credenciales desencriptadas** (`export:credentials --decrypted`) a Git ni compartir el archivo `infra/.env`. Para migrar las credenciales cada integrante creará las propias.

### Nota sobre respaldo completo

El repositorio Git guarda **código y configuración**; no es un respaldo automático de las cuentas, claves cifradas, datos de Qdrant ni historial de ejecución. Mantener los volúmenes Docker separados y respaldados fuera de Git si el equipo los necesita.
