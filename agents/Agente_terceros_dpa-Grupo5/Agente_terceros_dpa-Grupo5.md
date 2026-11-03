# Agente_terceros_dpa — Grupo 5

**Responsabilidad:** Gestionar la relación con terceros (proveedores, encargados) y los acuerdos de protección de datos (DPA).

Evalúa el nivel de cumplimiento de proveedores, revisa y valida los contratos DPA, y monitorea continuamente el desempeño de terceros en materia de privacidad.

**Implementación:** PIMS Privacy Guard, sobre n8n. En el código se llama «Agente 7» (numeración del proyecto original; no tiene relación con el Grupo 7). Ver [README.md](README.md) y, para integrarlo, [GUIA_INTEGRACION.md](GUIA_INTEGRACION.md).

## Skills
- `revisar_acuerdos_dpa/` → `pims-dpa-auditor/`: audita el contrato contra 26 controles de ISO/IEC 27701:2025 y la Ley 29733, con puntaje, dictamen y doble aprobación DPO → Legal.
- `evaluar_proveedores/` → el puntaje del proveedor por sección del Anexo A, y `pims-perfilador-organizacion/`, que lista los terceros de la organización y cuáles no tienen DPA evaluado.
- `monitorear_terceros/` → flujo de Renovaciones de n8n: alertas de vencimiento y renovación cada lunes.
