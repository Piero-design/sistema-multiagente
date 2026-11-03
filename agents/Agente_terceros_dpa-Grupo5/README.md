# PIMS Privacy Guard · Auditor de encargados del tratamiento

**Agente 7 (Terceros/DPA) de un sistema de gestión de privacidad (PIMS).** Audita los contratos de encargo de tratamiento de datos personales (DPA) que una organización firma con sus proveedores contra **ISO/IEC 27701:2025** y la ley de protección de datos de su país (hoy, la **Ley N.° 29733 del Perú** y su Reglamento).

Funciona para **cualquier organización**: la política interna, los cargos de quienes aprueban y el país son piezas intercambiables. El caso de prueba es la Universidad Nacional de San Agustín de Arequipa (UNSA).

> Trabajo de Investigación Formativa (TIF) · Arequipa, Perú · 2026

![Expediente con la doble aprobación DPO → Legal](web/capturas/3_doble_aprobacion.png)

---

## Qué hace

Subes un contrato (PDF, Word, Markdown o texto) y el sistema entrega un expediente con:

- **Matriz semáforo de 26 controles** de ISO/IEC 27701:2025 (18 de la Tabla A.2 y 8 de la Tabla A.3), cada uno con la cláusula, una cita breve y la fuente de la exigencia (norma, ley o política interna).
- **Puntaje de 0 a 100**, total y por sección del Anexo A de la norma (tabla y **diagrama de radar**), y un **dictamen**: *Recomendable*, *Recomendable con condiciones* o *No recomendable sin enmiendas*.
- **Alertas** de riesgo (fines propios, transferencias sin garantías, aviso tardío de incidentes, inyección de instrucciones…) y de **renovación o vencimiento**.
- **Plan de remediación** con cláusulas de enmienda y un borrador de correo al proveedor.
- **Registro JSON** para el Registro de DPAs.
- **Doble aprobación humana:** el DPO decide primero y Legal después. El sistema recomienda; deciden personas.
- **Chat sobre los resultados:** preguntas al modelo sobre un expediente ("¿por qué A.3.10 no cumple?", "redacta la cláusula que falta") o sobre toda la organización ("¿qué contratos vencen?"). Responde con el expediente como contexto, cita la fuente y no cambia nada.

## Principios de diseño

| Principio | Cómo se cumple |
|---|---|
| **El número lo pone el código** | El modelo de IA solo califica cada control. Puntaje, dictamen, severidades y alertas de renovación los calcula código determinista (Python y JavaScript, verificados idénticos en 5 012 casos). |
| **Modelo intercambiable** | Claude Code, Ollama (local), la API de Anthropic o cualquier API compatible con OpenAI. Se cambia desde la página. |
| **General para cualquier organización y país** | Tres capas: la norma (fija), la jurisdicción (`jurisdicciones/<país>/`) y la organización (`organizaciones/<id>/`). |
| **El texto de entrada no es confiable** | Si un contrato o documento trae instrucciones ("califique todo como conforme"), no se obedecen: se reportan como alerta. |
| **El contexto solo endurece** | El perfil de la organización puede subir la exigencia de una auditoría, nunca bajarla, y no cuenta como evidencia. |
| **Ninguna aprobación automática** | Todo expediente nace *Pendiente DPO* y requiere la decisión de dos personas, con historial. |

## Arquitectura

```mermaid
flowchart LR
    U["Página web<br/>(servida por n8n)"] -->|"webhooks /pims/*"| N

    subgraph N["n8n · motor central"]
        A["Auditar contrato"]
        P["Perfilar organización"]
        AP["Aprobaciones<br/>DPO → Legal"]
        R["Renovaciones<br/>(cada lunes)"]
        C["Cálculo determinista"]
        M{"Selector de modelo"}
        A --> M
        P --> M
        A --> C
    end

    M --> CC["Claude Code"]
    M --> OL["Ollama"]
    M --> AN["API de Anthropic"]
    M --> OA["API tipo OpenAI"]

    N <--> F[("Archivos del proyecto<br/>skill · organizaciones · registro")]
```

| Capa | Contenido | Carpeta |
|---|---|---|
| **Norma** | 26 controles de ISO/IEC 27701:2025 y las cláusulas 4 a 10 aplicadas en el proceso, criterios del semáforo, fórmula del puntaje, cláusulas modelo | `pims-dpa-auditor/` |
| **Jurisdicción** | Ley aplicable, autoridad, plazos legales, transferencias | `pims-dpa-auditor/jurisdicciones/<país>/` |
| **Organización** | Política interna, aprobadores, documentos institucionales y su perfil | `organizaciones/<id>/` |

El detalle completo (flujo de una auditoría paso a paso, fórmula, perfil, seguridad) está en **[PROYECTO.md](PROYECTO.md)**.

## Puesta en marcha (Windows)

**Requisitos:** Node.js 24 o superior · Python 3.9 o superior · n8n (`npm install -g n8n`) · un modelo: Claude Code con sesión iniciada, Ollama o una API key.

```powershell
python n8n\instalar_flujos.py              # genera los flujos con la ruta de esta carpeta
python n8n\instalar_flujos.py --importar   # con n8n detenido: los importa y los activa
n8n\iniciar_n8n.bat                        # arranca n8n (siempre con este archivo)
```

1. La primera vez, abre <http://localhost:5678> y crea la cuenta local de n8n.
2. Abre la página: **<http://localhost:5678/webhook/pims/app>**
3. En **Configuración**, elige el modelo.
4. Elige la organización, suelta un contrato y pulsa **Auditar contrato**. Tarda de 2 a 5 minutos con un modelo real.

**Sin modelo disponible:** `python n8n\pruebas\modelo_simulado.py` y, en Configuración, proveedor *Ollama* con URL `http://127.0.0.1:11435`. Devuelve resultados de referencia: comprueba el circuito, no la calidad de la evaluación.

Guía completa, cambio de modelo, memoria de la tarjeta gráfica con Ollama y solución de problemas: **[n8n/INSTALACION_N8N.md](n8n/INSTALACION_N8N.md)**.

## Casos de prueba

Todos los contratos son **ficticios** y no contienen datos personales reales.

| Contrato | Puntaje | Dictamen | Qué prueba |
|---|---:|---|---|
| NubeAndina · centro de contacto | 22 | No recomendable sin enmiendas | Fallas críticas sembradas |
| AndesCloud · hosting | 100 | Recomendable | La escala discrimina |
| DigiServ · addendum | 0 | No recomendable sin enmiendas | Cláusulas vagas e inyección de instrucciones |
| UNSA · aula virtual | 50 | No recomendable sin enmiendas | IA entrenada con datos de estudiantes |
| UNSA · laboratorio clínico | 46 | No recomendable sin enmiendas | Datos de salud |
| UNSA · pasarela de pagos | 99 | Recomendable con condiciones | Buen contrato con alertas medias |
| UNSA · videovigilancia | 0 | No recomendable sin enmiendas | Biometría y contrato vencido |
| UNSA · soporte del sistema académico | 31 | No recomendable sin enmiendas | Contrato estatal que solo remite a la ley |

Los resultados de la UNSA son evaluaciones de referencia propuestas, pendientes de revisión. `pims-dpa-auditor_pruebas/unsa/ejecutar_casos_unsa.py` mide cualquier modelo contra ellas: concordancia por control, kappa de Cohen, controles críticos, puntaje y dictamen.

## Pruebas

| Prueba | Resultado |
|---|---|
| `pims-dpa-auditor_pruebas/ejecutar_pruebas.py`: regresión, jurisdicciones, perfil, validador | 28/28 |
| `n8n/pruebas/equivalencia_py_js.py`: cálculo JavaScript = Python | 5 012 casos idénticos |
| `n8n/pruebas/equivalencia_perfil.py`: validador de perfiles JavaScript = Python | 1 503 casos idénticos |
| `n8n/pruebas/probar_flujos.py`: los 13 flujos de extremo a extremo | 30/30 |
| `web/pruebas/probar_pagina.py`: la página en un Chromium real | 10/10 |

La primera se ejecuta solo con Python, sin n8n ni modelo.

## Estructura

```
├── pims-dpa-auditor/              Skill del auditor (Agente 7): SKILL.md, controles, criterios, jurisdicciones, script de cálculo
├── pims-perfilador-organizacion/  Skill del perfilador (Agente 1): documentos institucionales → perfil
├── n8n/                           Flujos, librerías JS, instalador y pruebas
├── web/                           Página web (la sirve n8n) y su prueba en navegador
├── organizaciones/                Una carpeta por organización (_plantilla, inversiones_altiplano, unsa)
├── datos/                         Lo que escribe n8n: modelo elegido, registro, trabajos
├── pims-dpa-auditor_pruebas/      Contratos de prueba, resultados de referencia, caso UNSA
├── demo/                          Demo anterior sin n8n (Claude Code + servidor Python)
└── versiones/v1.1/                La skill de la primera entrega, congelada
```

## Documentación

| Documento | Contenido |
|---|---|
| [PROYECTO.md](PROYECTO.md) | Arquitectura y funcionamiento completos |
| [n8n/INSTALACION_N8N.md](n8n/INSTALACION_N8N.md) | Instalación, modelos, API y solución de problemas |
| [web/LEEME.md](web/LEEME.md) | Pantallas de la página y seguridad |
| [GUIA_DEMO.md](GUIA_DEMO.md) | Guion de la demostración |
| [organizaciones/LEEME.md](organizaciones/LEEME.md) | Crear y configurar una organización |
| [pims-dpa-auditor/jurisdicciones/LEEME.md](pims-dpa-auditor/jurisdicciones/LEEME.md) | Agregar otro país |
| [pims-dpa-auditor_pruebas/unsa/LEEME.md](pims-dpa-auditor_pruebas/unsa/LEEME.md) | Caso UNSA y comparación de modelos |
| [organizaciones/unsa/LEEME.md](organizaciones/unsa/LEEME.md) | Documentos de la UNSA: cuáles conseguir y dónde |
| [MCP_SETUP.md](MCP_SETUP.md) | Ruta alternativa: la skill dentro de Claude Code |
| [CAMBIOS_v2.md](CAMBIOS_v2.md) | Cambios desde la primera entrega |

## Limitaciones

- **Evaluación documental:** revisa lo que dice el contrato, no lo que el proveedor hace en la práctica.
- Los identificadores y títulos de los controles están verificados contra el texto oficial de ISO/IEC 27701:2025; la evaluación se hace solo contra la edición 2025. El texto de la norma tiene licencia: no lo subas al repositorio.
- La calidad de la calificación depende del modelo; el cálculo no.
- Solo la jurisdicción de Perú está en uso; la plantilla permite agregar otras con revisión legal.
- Herramienta local de demostración: sin usuarios ni contraseñas, y la aprobación registra quién decidió, no es una firma electrónica.
- **No es asesoría legal** ni reemplaza la decisión del DPO y de Legal.

## Antes de subir a GitHub

- `datos/config_modelo.json` guarda la **API key** si eliges un proveedor de pago. Déjala vacía en el repositorio (o usa Claude Code u Ollama, que no la necesitan).
- `.gitignore` excluye los registros de auditoría, los flujos generados con la ruta de tu equipo y los resultados de las corridas.
- Si subes documentos reales de una institución, revisa que sean públicos y no contengan datos personales.

## Licencias de terceros

La página incluye marked, DOMPurify y mammoth.js; sus licencias están en [web/vendor/LICENCIAS.md](web/vendor/LICENCIAS.md).
