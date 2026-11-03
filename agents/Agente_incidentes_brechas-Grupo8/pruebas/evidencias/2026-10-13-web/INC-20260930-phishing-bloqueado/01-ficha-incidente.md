# Ficha de triaje — INC-20260930-phishing-bloqueado

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Caso ficticio. Sin carpeta de contexto: no hay evidencia verificable en logs, solo el reporte.

## Reloj
- Toma de conocimiento: 2026-09-30 11:45 (reportado).
- Referencia de 48 h: 2026-10-02 11:45. Hora actual: 2026-10-13 10:00 (-0500). La referencia pasó hace unos 12 días y 22 h.
- **No aplica plazo legal**, porque no hay incidente de datos personales (art. 34.1). El reloj de 48 h solo corre para incidentes de datos personales.

## Datos del reporte
| Campo | Valor | Nivel |
|---|---|---|
| Organización | Municipalidad Distrital de Cayma | Reportado |
| Reportante | Asistente de la Gerencia de Rentas | Reportado |
| Hecho | Correo de phishing que suplantaba al banco ("validar cuenta institucional") con enlace | Reportado |
| Clic del reportante | No | Reportado |
| Clics de otros usuarios | Ninguno. El proxy no muestra accesos al dominio | Reportado por soporte (12:10). **No verificado**: no hay log disponible |
| Alcance | 37 buzones recibieron el correo | Reportado |
| Contención | Dominio bloqueado y correo eliminado de los 37 buzones | Reportado |
| Datos personales afectados | Ninguno identificado | Supuesto |

## Clasificación
- Categoría: **FRA** (fraude e ingeniería social, phishing).
- Dimensión CID: ninguna afectada según lo reportado.
- **Resultado del triaje: EVENTO SIN INCIDENTE.** Fue un intento bloqueado: nadie interactuó con el enlace y no hay indicios de que se vulnerara un control (`taxonomia-incidentes.md` §3).
- Prioridad: **P4 Baja** (registro rutinario).
- Datos personales: no hay vulneración, así que no hay brecha según el art. III num. 16.
- Ley 29733: no hay notificación a la ANPD, comunicación a titulares ni aviso al CNSD. Esto es una recomendación, no una decisión final.

## Puntos débiles de la conclusión (verificar para cerrar con certeza)
1. "Nadie más hizo clic" se basa solo en el registro del proxy. Pudo haber accesos fuera del proxy: móvil con datos propios, equipo personal o red externa. Pida confirmar con el log del proxy/DNS/firewall y con el filtro de correo.
2. No se sabe si alguien respondió el correo ni si abrió adjuntos. Revisar el log de correo.
3. Ese correo pudo ser una de varias oleadas. Buscar el mismo remitente, asunto o dominio en otros buzones.
4. Se necesita la hora de recepción del correo, que no consta.
5. Los logs deben conservarse como evidencia (ISO/IEC 27037) `[VERIFICAR con knowledge/estandares-incidentes.md]`.

## Condición para reabrir
Si aparece un clic, credenciales ingresadas, una respuesta al correo o actividad anómala en cuentas, **reclasificar como incidente (INT/FRA)**. La toma de conocimiento sería el momento en que se detecte el hecho. Evalúe entonces si hay datos personales expuestos (Rentas maneja datos de contribuyentes `[VERIFICAR inventario]`) y recalcule las 48 h.
