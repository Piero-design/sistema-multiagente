# G4: planificación, evaluación y consolidación

Rama `agente4`. La interfaz común de `/agentes/auditoria` ofrece:

- **M1 · Planificar**: rol responsable/encargado/ambos y alcance. El endpoint nativo `POST /api/planificar` construye un checklist inicial del catálogo real del grupo (44/33/52 ítems). No utiliza un LLM. El alcance queda registrado; el auditor debe ajustar el checklist a ese alcance y los riesgos. Los códigos CL/RT/EN/SG son internos, no numeración ISO oficial.
- **M2 · Evaluar evidencia**: mantiene el endpoint existente, restaura seis casos sintéticos originales y admite archivos de texto hasta 1 MB. No extrae texto de PDF ni imágenes. Guarda en el resultado el nombre de la evidencia y estado pendiente de revisión. Identifica contingencia sin LLM conservando esa distinción en M3. La etiqueta del caso de política no asegura que sea una política actualizada.
- **M3 · Consolidar**: seleccionar evaluaciones M2 finalizadas desde el historial o pegar sus UUID. El backend recupera los dictámenes persistidos, rechaza ejecuciones de otros agentes, fallidas, inexistentes o que no sean M2, elimina duplicados y agrupa por severidad propuesta. No recibe dictámenes inventados por el navegador. Genera matriz e informe descargable Markdown conservando ID, nombre, hash, dictamen y etiquetas de simulación/contingencia. El orquestador persiste también la consolidación. Se cuentan evaluaciones, no controles únicos; no se calcula un porcentaje de cumplimiento ni se genera la SoA de G7.

## Prueba en Codespaces

```bash
git fetch origin
git switch agente4
docker compose up --build -d agent-g4 backend frontend
```

1. Abrir el puerto 8080 y G4.
2. M1: elegir rol y alcance; verificar que los ítems correspondan al rol.
3. M2: seleccionar contrato, ejecutar, revisar dictamen/hash/etiqueta de proveedor.
4. Ejecutar otra evidencia y abrir M3; marcar ambas evaluaciones del historial.
5. Consolidar y descargar el informe. Debe incluir las dos evidencias con sus ID y hash, sin porcentaje fijo ni aprobación inventada.
6. Verificar que los módulos de otros grupos y el flujo G3→G4 con acción `auditar` siguen disponibles.

## Límites

La validación humana se muestra como **pendiente**, no se registra una aprobación. Se reutiliza la severidad propuesta por el M2 actual (extraída de texto): no se presenta como certificación. Los nombres de evaluaciones históricas anteriores a esta rama pueden no estar registrados; en ese caso se indica el faltante y se conserva su ID. Las fuentes normativas del catálogo deben verificarse con los textos oficiales.

Pruebas unitarias: `python -m pytest tests/unit/test_g4_modes.py -q`. Las pruebas no sustituyen una ejecución completa de Docker con proveedor real.
