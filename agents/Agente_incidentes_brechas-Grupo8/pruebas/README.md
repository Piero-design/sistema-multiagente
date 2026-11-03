# Pruebas de los skills y del agente

**Responsable: Integrante 4** (con apoyo de Ryan para interpretar los fallos).

## Cómo probar
1. Abre Claude Code en la raíz del repositorio.
2. Ejecuta un caso, por ejemplo: `/gestionar-incidente examples/unsa/unsa-01-ransomware-registro-academico.md contexto: demo/unsa-ransomware`.
3. Revisa la carpeta generada en `salidas/<ID>/`.
4. Compárala con el resultado esperado en `docs/06-proyecto-agentico.md` y con la lista de verificación de abajo.
5. Anota todo en `registro-pruebas.md`; guarda capturas y una copia de las salidas en `evidencias/<fecha>-<caso>/` (la carpeta `salidas/` no se versiona).

## Mínimo requerido
- Los 4 casos de `examples/entradas/` con el agente completo.
- Cada skill invocado por separado al menos una vez (frase natural, sin nombrar el skill).
- 1 caso con información incompleta (ej. sin hora de conocimiento) para ver si el agente pregunta.

## Lista de verificación por prueba
- [ ] Se activó el skill o agente esperado.
- [ ] Clasificó bien: evento / incidente / brecha.
- [ ] Calculó la hora límite desde la **toma de conocimiento**.
- [ ] La severidad muestra la operación y justifica cada factor.
- [ ] La decisión de notificar revisa los 4 supuestos del art. 34.1.
- [ ] La notificación a la ANPD cubre los 4 elementos del art. 34.2.
- [ ] La comunicación a los titulares está en lenguaje claro y dice qué puede hacer la persona.
- [ ] La contención no destruye evidencia.
- [ ] No inventa plazos, artículos ni controles.
- [ ] Cierra con la advertencia de borrador para revisión humana.

## Reglas
- Usar solo datos ficticios.
- Un fallo que se repite se reporta como *issue* para que Ryan lo corrija.
