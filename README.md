# Plataforma PIMS multiagente

Ocho agentes independientes (ISO/IEC 27701 / Ley 29733) integrados detrás de un orquestador, un gateway LLM compartido, PostgreSQL (Gestitel) y una web unificada. Siete están integrados; el Grupo 6 queda fuera de alcance en esta ronda.

```
navegador → frontend (nginx :8080) → backend (API + orquestador) → adaptadores → agentes G1..G8
                                         │                                     │
                                         ├─ PostgreSQL (Gestitel + orchestrator)
                                         └─ llm-gateway  ← todos los agentes (cloud | ollama | mock)
```

- Instalación: `docs/installation/INSTALACION.md` · Ollama en otra PC: `docs/installation/OLLAMA_OTRA_PC.md`
- Cambios a los agentes: `docs/integration/MODIFICACIONES_A_AGENTES.md` · Pruebas: `docs/integration/RESULTADOS_PRUEBAS.md`
- Arranque: `docker compose up --build -d` y abrir <http://localhost:8080>
