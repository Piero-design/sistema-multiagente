# Archivos de demostración

Todo es **simulado**: la estructura y los sistemas de la UNSA salen de fuentes públicas (ver `demo/unsa-base/FUENTES.md`), pero los incidentes, las cifras internas y las personas son inventados. Los contextos `demo/unsa-*` ya vienen cargados en la aplicación; aquí están los **reportes** para cargar desde archivo y un **contexto nuevo** para probar la subida.

## Demo rápida (3 pasos)
1. Abra **Analizar** y pulse *Cargar desde archivo*: elija `reportes/01-ransomware-registro-academico.md`.
2. En *Contexto* elija **Demo · unsa-ransomware**.
3. Pulse **Analizar incidente** (2 a 3 minutos).

## Qué contexto usar con cada reporte
| Reporte | Contexto | Qué se espera |
|---|---|---|
| `01-ransomware-registro-academico.md` | `unsa-ransomware` | Brecha P1; cita los logs de VPN, firewall y respaldos del SISACAD |
| `02-correo-masivo-ingresantes.md` | `unsa-base` | Fuga con menores y discapacidad |
| `03-laptop-robada-bienestar.md` | `unsa-base` | Salud mental, sin cifrado |
| `04-phishing-docentes-bloqueado.md` | `unsa-base` | **Control:** evento sin incidente, no notifica |
| `05-aviso-proveedor-aulas-virtuales.md` | `unsa-base` | Encargado del tratamiento |
| `06-portal-admision-inyeccion-sql.md` | `unsa-admision` | Extorsión y dato de discapacidad |
| `07-cambio-indebido-de-notas.md` | `unsa-notas` | Alteración de datos |
| `08-planilla-cas-en-enlace-publico.md` | `unsa-base` | Datos financieros expuestos |
| `09-ddos-matricula-sin-datos.md` | `unsa-base` | **Control:** sin brecha confirmada |
| `10-acceso-indebido-posgrado.txt` | **el que cargue usted** (abajo) | Uso indebido interno con datos de salud |

## Demo con un contexto nuevo (carga propia)
1. Abra **Contextos → Nuevo contexto**.
2. Nombre: `Escuela de Posgrado (simulada)`. Arrastre los 3 archivos de `contexto-nuevo/` y pulse *Guardar contexto*.
3. Abra el contexto para ver sus archivos (el log tiene números de línea, que el agente cita).
4. En **Analizar**, cargue `reportes/10-acceso-indebido-posgrado.txt`, elija ese contexto y analice.
5. Esperado: confirma con el log las 85 consultas, usa el contacto del Oficial de Datos Personales y los 1 450 titulares del inventario, y trata las constancias médicas como datos sensibles.

Los reportes también se pueden descargar desde la propia aplicación (Analizar → *Archivos de demostración*).
