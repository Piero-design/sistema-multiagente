# Presentación y demo

**Responsable: Integrante 4.** Cada integrante expone su parte.

## Estructura sugerida de diapositivas
1. Portada y equipo (4 integrantes)
2. Problema: cuando ocurre una brecha hay **48 horas** para notificar y el proceso es manual
3. Marco normativo: D.S. 016-2024-JUS, arts. 34 a 36 (Integrante 2)
4. Estándares: ciclo ISO/IEC 27035, controles ISO/IEC 27002, ISO/IEC 27701, NIST (Integrante 3)
5. De prompt a skill: antes y después
6. Los 4 skills, uno por fase del ciclo
7. El agente y su flujo (diagrama del `README.md`)
8. Severidad ENISA: un ejemplo calculado
9. Demo en vivo
10. Resultados de las pruebas (incluye el caso de control)
11. Limitaciones y trabajo futuro
12. Conclusiones

## Guion de demo (5 min)
1. Mostrar `examples/unsa/unsa-01-ransomware-registro-academico.md` (30 s).
2. Ejecutar `/gestionar-incidente examples/unsa/unsa-01-ransomware-registro-academico.md contexto: demo/unsa-ransomware` (2 min). Señalar que el agente cita logs (`archivo:línea`) y descubre la transferencia de 3,4 GB que el reporte no mencionaba.
3. Abrir `salidas/<ID>/00-informe.md`: hora límite, severidad y decisiones pendientes (1 min).
4. Abrir `03-notificacion-anpd.md` y señalar los 4 elementos del art. 34.2 (30 s).
5. Ejecutar el caso 4 (phishing bloqueado) y mostrar que **no** notifica (30 s).
6. Cierre: todo es borrador, la decisión es humana (30 s).

Tener una **grabación de respaldo** por si falla la demo en vivo.

## Preguntas que pueden hacer (todos deben poder responder)
- ¿Qué diferencia hay entre evento, incidente y brecha?
- ¿Desde cuándo corren las 48 horas?
- ¿Por qué hay que notificar aunque el incidente ya se haya resuelto? (art. 34.1)
- ¿Cómo se calcula la severidad y por qué no basta con ella para decidir?
- ¿Qué diferencia hay entre un skill y un agente?
- ¿Cómo evitan que la IA invente artículos o plazos?
- ¿Por qué el agente no envía las notificaciones?
