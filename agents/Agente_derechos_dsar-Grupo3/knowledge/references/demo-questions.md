# Consultas de demostración sobre derechos DSAR

## Qué es una solicitud DSAR

Una solicitud DSAR permite que una persona ejerza derechos sobre sus datos personales. Este agente prepara expedientes de información, acceso, rectificación, supresión o cancelación, portabilidad y oposición, también combinados en una misma solicitud. El acceso permite conocer y solicitar una copia de la información; la rectificación propone corregir información; la supresión pide evaluar su eliminación; la portabilidad propone una copia estructurada; la oposición pide revisar una finalidad de tratamiento. Las condiciones concretas requieren una política aprobada y revisión competente.

## Identidad y bloqueo del descubrimiento

La identidad debe verificarse por un canal autorizado antes de descubrir registros de una persona. Una identidad pendiente produce IDENTITY_PENDING y cero registros localizados. El asistente no verifica documentos: consulta el estado externo. La casilla de la interfaz representa ese estado solo para la simulación. Recuperar referencias procedimentales del RAG no es descubrir datos personales.

## Revisión humana y siguiente paso del expediente

La supresión, rectificación y oposición pueden modificar o restringir el tratamiento y requieren revisión humana. También requieren revisión los datos sensibles, datos de terceros, restricciones de conservación o políticas que exigen evaluación especializada. En IDENTITY_PENDING se completa la identidad por el canal autorizado. En APPROVAL_REQUIRED se revisan los motivos pendientes. En REVIEW se revisa el borrador. Registrar una revisión simulada no ejecuta el derecho ni envía la respuesta.

## Plazos, perfiles de jurisdicción y política académica

El plazo de cada derecho se calcula desde el día siguiente a la recepción con el perfil seleccionado. El perfil PE-LEY29733 usa días hábiles del Reglamento D.S. 016-2024-JUS: información 8 días, acceso y portabilidad 20 días, rectificación, cancelación y oposición 10 días; excluye sábados, domingos y feriados nacionales. LAB-30 usa 30 días naturales y LAB-15-REVIEW 15 días con revisión especializada; son configuraciones ficticias. ISO/IEC 27701 no fija un plazo universal: exige definirlo. La fecha exacta se obtiene del expediente, no del modelo de lenguaje.

## Fuentes, RAG y skill

El skill define identidad, activación, pasos y límites del asistente. El RAG divide las referencias en fragmentos y recupera los más relevantes con una búsqueda híbrida: BM25 (raíces de palabras, sinónimos del dominio y títulos de sección) combinada con embeddings multilingües que capturan el significado, de modo que una pregunta con otras palabras puede encontrar el fragmento correcto. La respuesta muestra el archivo, sección y SHA-256. Si el modelo de embeddings no está disponible, se usa solo BM25 y el motivo queda registrado; aun así una paráfrasis sin palabras en común puede no recuperarse. Ollama utiliza las instrucciones del skill y el contexto recuperado para explicar o redactar; el motor DSAR conserva el control sobre los estados y las acciones propuestas.

## Borrador y ausencia de registros

Una respuesta preparada sigue siendo un borrador para revisión. Si la identidad está pendiente, informa que no se inició la búsqueda. Si no se encuentran registros, describe ese resultado sin inventar información ni afirmar que no existe dato alguno fuera de las fuentes consultadas. El borrador distingue acción propuesta de acción ejecutada. No se envían correos ni se eliminan datos desde la demostración.
