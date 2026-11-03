# Guía de uso del agente DSAR

Esta guía describe las pantallas y los pasos de la aplicación. Es documentación de uso, no normativa: explica dónde se hace cada cosa. El agente prepara expedientes y borradores; las decisiones las toma una persona.

## Registrar una solicitud

En **Inicio** se cargan los casos de demostración con «Cargar caso». Para una solicitud propia, abre **Nueva solicitud**, escribe el identificador sintético del titular, elige el perfil de jurisdicción, marca los derechos pedidos, indica la fecha de recepción (por defecto, hoy), marca la identidad solo si fue verificada por el canal autorizado y pulsa «Registrar y tramitar». El motor calcula el estado, los plazos y los registros; el asistente no registra solicitudes por ti.

## Revisar y decidir un expediente (aprobar o rechazar)

Desde el expediente, pulsa «Revisión y decisión». Abajo está el panel **Decisión humana**:

1. Escribe en «Persona que decide» el nombre de quien decide; el aprobador designado se muestra encima (por ejemplo, el Oficial de Datos Personales).
2. Elige **Aprobar** o **Rechazar** (no hay opción preseleccionada).
3. Escribe la justificación.
4. Marca la casilla de confirmación de que revisaste el expediente, los motivos de revisión humana y el borrador.
5. Pulsa «Registrar decisión».

Solo una persona puede registrar la decisión; el asistente no aprueba, rechaza ni cierra casos, aunque quien pregunte sea el DPO. Un expediente con la identidad pendiente (`IDENTITY_PENDING`) no se puede decidir hasta completar la verificación. Al aprobar se generan los handoffs a otros agentes (evidencia y, según el caso, terceros e inventario) y se muestra el resultado; ninguna acción se ejecuta: siguen siendo propuestas.

## Solicitar una prórroga

En «Revisión y decisión» despliega «Solicitar prórroga». Elige el derecho: el formulario muestra el plazo vigente, la prórroga máxima, el nuevo vencimiento, el tope legal y hasta cuándo debe comunicarse al titular. Escribe los días de prórroga (hasta el máximo), quién decide y el motivo, y pulsa «Registrar prórroga». Se puede una sola vez por derecho y por un plazo igual al legal como máximo (D.S. 016-2024-JUS, art. 71); no aplica al derecho de información.

## Redactar y exportar el borrador

En «Revisión y decisión», «Redactar con el asistente» genera el borrador con el modo elegido arriba («Respuestas»: guiado, Ollama, Gemini o Claude Code). El motor pone la estructura y los hechos; un modelo solo redacta la carta al titular. Puedes editarlo en «Editar Markdown», verlo en «Vista previa» y guardarlo con «Exportar expediente». Si ya editaste el borrador, pide confirmación antes de reemplazarlo.

## Usar el asistente (chat)

En **Asistente** puedes preguntar sin expediente (normativa, definiciones) o elegir uno en «Expediente de contexto» para preguntar por su estado, plazos, motivos de revisión, aprobador, controles, prórroga, campos retirados o sistemas. El asistente no muestra datos personales del titular, no aprueba ni ejecuta nada y rechaza lo que no trata de derechos de los titulares.

## Política de la organización

En **Organización** se ve y se edita la política (plazos internos más estrictos que la ley, aprobadores, campos confidenciales y sistemas a consultar) y el procedimiento interno. «Validar y guardar» pide confirmación: la API rechaza una política que alargue un plazo legal y la versión anterior queda en el historial. Se aplica a los expedientes que se creen desde ese momento y cuyo perfil coincide con el de la política.

## Auditoría

En **Auditoría** están la huella del skill, la consulta directa al RAG, la bitácora de llamadas a modelos (solo con el hash del prompt) y los handoffs, con el expediente al que pertenece cada uno.
