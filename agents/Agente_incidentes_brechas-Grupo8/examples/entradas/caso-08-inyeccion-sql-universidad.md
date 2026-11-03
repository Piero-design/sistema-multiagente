# Reporte de incidente — Instituto Superior Tecnológico Chachani (CASO FICTICIO)

> Caso inventado para pruebas. Organización, personas y datos son ficticios.

**De:** Jefe de Sistemas del instituto
**Fecha del correo:** 2026-10-11, 08:10

El sábado en la noche alguien publicó en un foro una muestra de 200 filas de nuestro portal de postulantes y amenaza con publicar "todo" si no respondemos. Las filas tienen nombre, DNI, correo, teléfono, colegio de procedencia y notas del examen. Los logs del servidor web muestran muchas peticiones con `UNION SELECT` al formulario de consulta de resultados desde el viernes 21:00, hasta el sábado 03:00. La tabla de postulantes tiene **aprox. 14 000 registros** de 3 años, incluidos menores de 17. Ya pusimos el portal en mantenimiento. No sabemos cuántos registros salieron.
