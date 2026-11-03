# Guía de Diseño y Sistema Visual — PIMS UNSA (Agente #8)

> **Modo de Superficie:** `Operate` & `Read`  
> **Identidad de Marca:** Académica Agustina, rigurosa, moderna y de alta confiabilidad institucional.  
> **Estándar:** Implementado bajo especificaciones de diseño *Impeccable* (sin anti-patrones AI, contraste WCAG AA/AAA).

---

## 1. Tipografía Elegante

| Rol | Familia Tipográfica | Pesos | Uso |
| :--- | :--- | :--- | :--- |
| **Display / Títulos** | `Playfair Display`, serif | 600, 700 | Título del agente, encabezados principales, identidad institucional |
| **Cuerpo e Interfaz** | `Outfit`, sans-serif | 400, 500, 600 | Textos de chat, botones, formularios, metadatos, tablas |
| **Código y Cifrado** | `JetBrains Mono`, monospace | 400, 500 | Hashes SHA-256, IDs de matrícula, códigos de cursos, JWT |

---

## 2. Paleta de Colores Institucional

* **Granate Institucional UNSA (`--primary`):** `#8b1524` (Hover: `#700f1c`, Light: `#fdf2f4`)
* **Azul Pizarra Profundo (`--secondary`):** `#0f172a` (Superficie oscura premium con tinte zafiro)
* **Fondo Principal (`--bg-main`):** `#f8fafc` (Limpio, descansado a la vista)
* **Tarjetas y Burbujas:** `#ffffff` con borde sutil `#e2e8f0` y sombra multidimensional suave.
* **Acentos de Estado:**
  - Éxito / Vigente: `#059669` (Esmeralda)
  - Alerta / Pendiente: `#d97706` (Ámbar)
  - Crítico / Vencido: `#dc2626` (Rubí)

---

## 3. Directivas de Artesanía Visual (Anti-Patterns Eliminados)

1. **Sin Side-Tabs Artificiales:** Se eliminan los bordes gruesos unilaterales (`border-left: 3px solid`), reemplazándolos por tarjetas con bordes perimetrales refinados y micro-indicadores circulares.
2. **Jerarquía Visual Clara:** Diferenciación inmediata entre los mensajes del usuario (cápsula granate elegante) y las respuestas del asistente (tarjeta estructurada con markdown tipográfico impecable).
3. **Contraste A11y Cumplido:** Ratios de contraste superiores a 4.5:1 en todos los textos secundarios para máxima legibilidad según WCAG AA.
4. **Micro-interacciones Fluidas:** Transiciones suaves de 0.2s en botones, chips de sugerencia rápida con elevación y efecto de foco translúcido.
