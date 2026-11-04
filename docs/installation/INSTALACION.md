# Instalación (laptop, sin Ollama)

Requisitos: Docker Desktop (Linux containers), ~8 GB de RAM libres para Docker, acceso a Internet la primera vez (imágenes, dependencias, llamadas al modelo en la nube).

## 1. Configurar

Crear `.env` en la raíz (está en `.gitignore`; no se versiona):

```
LLM_MODE=cloud
LLM_API_KEY=<clave del proveedor>
```

Los demás valores tienen defaults en `docker-compose.yml` (Gemini por su endpoint compatible con OpenAI, `gemini-3.5-flash-lite`, `gemini-embedding-001`). Ver `.env.example` para todas las variables. `LLM_MODE=mock` funciona sin clave y sin Internet, con respuestas **simuladas** etiquetadas como tales.

## 2. Levantar

```bash
docker compose up --build -d
```

Abrir <http://localhost:8080>. Es el único puerto publicado; PostgreSQL, el gateway, Qdrant y los agentes quedan en la red interna. La primera construcción tarda (n8n se instala con npm en las imágenes de G2 y G5).

## 3. Norma ISO/IEC 27701 para el Grupo 2 (opcional, fuera del repositorio)

El PDF con licencia **no se copia al repo**. Es un escaneo sin texto, así que se hace OCR en un contenedor de apoyo:

```bash
NORM_PDF_PATH="C:/ruta/ISO 27701-2025.pdf" docker compose --profile tools run --rm ocr
MSYS_NO_PATHCONV=1 NORM_PDF_PATH="C:/ruta/ISO 27701-2025.pdf" docker compose --profile tools run --rm ocr python /opt/md_to_pdf.py
docker cp ocr_output/ISO27701-2025.ocr.pdf sistema-multiagente-agent-g2-1:/tmp/norma.pdf
docker compose exec agent-g2 python3 /opt/g2_ingest.py /tmp/norma.pdf
```

`ocr_output/` está en `.gitignore`. El texto es **derivado** (Tesseract spa+eng, 220 dpi): en la corrida de desarrollo la confianza media fue 93,5 % y las páginas 4, 59, 60, 61 y 71 quedaron por debajo del 85 %; no se contrastaron los números de cláusula contra las imágenes, así que no se afirma exactitud normativa. La ingesta respeta la cuota de embeddings del proveedor y tarda varios minutos.

## 4. Grupo 2 y su control de alcance

El agente permanece bloqueado hasta que alguien revise n8n y el RAG. Cuando lo haya hecho, poner `G2_SCOPE_N8N_REVIEWED=true` en `.env` y `docker compose up -d agent-g2`.

## 4b. Revisión humana

`/revision` pide iniciar sesión. Cuentas de demostración por defecto: `dpo` / `demo-dpo` y `legal` / `demo-legal`. Cámbialas en `.env` con `HUMAN_USERS` (formato `usuario:contraseña:ROL;...`, roles `DPO` y `Legal`) antes de mostrar la plataforma fuera de tu máquina.

## 5. Operación

- Estado: `/` y `/configuracion`. Pruebas: `pytest tests/integration -q` (con la plataforma arriba).
- Los datos persisten en volúmenes (`pgdata`, `g1data`, `g3data`, `g5*`, `g8*`, `g2n8n`, `qdrantdata`). `docker compose down -v` los borra.
- Seguridad: rotar la clave del proveedor tras las pruebas. Las cuentas de demostración de G1 (por ejemplo `admin`) son datos del propio grupo; no usar la plataforma en una red abierta.
