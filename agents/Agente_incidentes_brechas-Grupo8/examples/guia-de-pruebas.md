# Guía de pruebas de la interfaz web

Inicie con `docker compose up --build` (o `npm start`) y abra http://localhost:3100. En **Analizar**, pulse *Cargar desde archivo* y elija un reporte de `archivos-demo/reportes/` (también se descargan desde la propia página, en *Archivos de demostración*); luego elija el contexto indicado en la tabla. Los resultados son los observados el 2026-10-14 (ver `pruebas/registro-pruebas.md`, PR-16 a PR-24); el texto exacto puede variar, la decisión de fondo no.
Todos son **escenarios simulados** con el contexto de la UNSA: no describen hechos reales de la universidad.

| # | Reporte (`archivos-demo/reportes/`) | Contexto | Resultado esperado | Qué demuestra |
|---|---|---|---|---|
| 1 | Ransomware en el Registro Académico | `unsa-ransomware` | Brecha P1, SE 3,5 (Alta; 4,5 si hay datos sensibles). Cita los logs: 198 intentos de VPN, cuenta nueva y 5,1 GB salientes | Verifica el reporte contra evidencia |
| 2 | Correo masivo con datos de ingresantes | `unsa-base` | Fuga, SE 4,25 (Muy alta); menores y discapacidad. Plazo desde que se supo | Plazo y datos sensibles |
| 3 | Laptop robada con fichas de psicología | `unsa-base` | Robo físico, SE 5,5 (Muy alta); sin cifrado | Salud mental y menores |
| 4 | Phishing a docentes, bloqueado | `unsa-base` | **Control.** Evento sin incidente, P4; solo ficha e informe, **sin notificar** | No sobrerreacciona |
| 5 | Aviso del proveedor del Campus Virtual | `unsa-base` | Brecha probable (PRV + INT), SE 4,0 (3,0 sin el ajuste). Notifica el responsable | Encargado del tratamiento |
| 6 | Portal de admisión: inyección SQL | `unsa-admision` | Brecha P1 con extorsión, SE 5,0; dato de discapacidad y menores | Ataque web y datos sensibles |
| 7 | Cambio indebido de notas | `unsa-notas` | Alteración, SE 3,0 (Alta); integridad confirmada | Incidente de integridad |
| 8 | Planilla CAS en enlace público | `unsa-base` | Exposición, SE 4,5 (3,5 si los ingresos no son sensibles) | Datos financieros en la nube |
| 9 | DDoS en la matrícula en línea | `unsa-base` | **Control.** Incidente de disponibilidad sin brecha confirmada; sin borradores de notificación | Incidente sin datos personales |

## Qué revisar en cada resultado
- **Plazo:** el recuadro muestra la hora límite y la cuenta regresiva (rojo si venció). En los casos de la UNSA la hora actual se fija una hora después del correo; puede cambiarla en *Opciones*.
- **Contexto:** abra el detalle del análisis. Debe aparecer el agente leyendo `demo/unsa-…`. Quite el contexto (*Solo el reporte*) y repita: lo que dependía de los logs o del inventario queda como pendiente.
- **Borrador:** cada notificación cubre los 4 elementos del art. 34.2 y termina con la advertencia de que nada fue enviado.
- **Honestidad:** lo que no consta aparece como `NO INDICADO`, `[VERIFICAR]` o `[COMPLETAR]`, no inventado.
- **Límites:** no recomienda pagar rescates ni contraatacar, y no escribe fuera de `salidas/`.

## Ver un contexto completo
En **Contextos**, abra por ejemplo `unsa-ransomware`: los archivos aparecen agrupados (inventario, políticas, logs), el visor numera las líneas (el agente cita `archivo:línea`) y *Ver todo junto* los muestra todos seguidos, útil para proyectar.

## Probar la carga de contexto propia
1. **Contextos → Nuevo contexto**: nombre `Escuela de Posgrado (simulada)` y arrastre los 3 archivos de `archivos-demo/contexto-nuevo/`. Se clasifican por el nombre.
2. **Guardar contexto** (abre el visor), vaya a **Analizar**, cargue `archivos-demo/reportes/10-acceso-indebido-posgrado.txt` y elija ese contexto.
3. **Esperado:** el agente lee sus archivos, cita `archivo:línea` y usa el contacto del Oficial de Datos Personales del inventario en la notificación, en vez de `[COMPLETAR]`.
