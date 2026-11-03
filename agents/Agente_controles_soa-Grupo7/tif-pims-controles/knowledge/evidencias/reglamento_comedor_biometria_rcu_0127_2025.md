# EVIDENCIA DE AUDITORÍA: REGLAMENTO DEL SERVICIO DE COMEDOR UNIVERSITARIO (DUDE)

- **Código de Documento:** EVID-UNSA-COM-02
- **Resolución Oficial:** Resolución de Consejo Universitario RCU N.° 0127-2025 (Versión 03)
- **Fecha de Aprobación:** 10 de marzo de 2025 (Deroga RCU N.° 0240-2024 y RCU N.° 0441-2023)
- **Control ISO/IEC 27701 Asociado:** A.1.2.6 (Evaluación de Impacto en la Privacidad - DPIA)
- **Área Responsable:** Dirección Universitaria de Desarrollo Estudiantil (DUDE) - Comedor Universitario
- **Estado de Auditoría:** Parcialmente Implementado (Requiere Formalización del Informe DPIA Final)

---

## 1. Contexto del Servicio y Tratamiento de Datos Sensibles
El Reglamento establece el marco operacional para la selección, asignación de raciones y control diario de asistencia alimentaria a los estudiantes agustinos en condición de vulnerabilidad socioeconómica:
1. **Ficha Socioeconómica:** Evaluación de ingresos económicos del hogar, estado de salud familiar y vivienda.
2. **Registro Biométrico (Huella Dactilar):** Control de acceso en las puertas de los comedores de Área Sociales, Ingenierías y Biomédicas para evitar la doble adjudicación o suplantación de tickets.

## 2. Relevancia para la Evaluación de Impacto de Privacidad (DPIA - Control A.1.2.6)
* **Categoría de Datos:** Tratamiento masivo de datos biométricos (huellas) de personas en situación de vulnerabilidad social.
* **Riesgo Identificado (R-UNSA-02):** Posible filtración o mal uso de plantillas biométricas almacenadas en terminales de marcación locales sin cifrado extremo a extremo.
* **Salvaguardas Exigidas por el PIMS:**
  * Uso de plantillas criptográficas de un solo sentido (hash biométrico no reversible a la imagen de la huella).
  * Retención temporal: Cancelación del registro biométrico al término del semestre lectivo o egreso del beneficiario.
  * Elaboración preceptiva del informe DPIA antes del inicio del año académico 2026.
