// Real capabilities per agent (mirrors the adapters). `demo` values are labeled as demonstration data in the UI.
// Human decisions (G3 verify/decide, G5 DPO/Legal approval, G8 action approval) are intentionally NOT offered here.
const sid = () => 'plataforma-' + Math.random().toString(16).slice(2, 12);

export const AGENTS = {
  formacion: {
    route: '/agentes/formacion', title: 'Formación y concientización', group: 1,
    about: 'Asistente de formación ISO/IEC 27701: capacitaciones, evaluaciones e indicadores de concientización. Usa su propia base SQLite y base de conocimiento.',
    actions: [{
      id: 'chat', label: 'Consultar al asistente', long: false,
      fields: [{ name: 'mensaje', label: 'Pregunta', type: 'textarea', demo: '¿Qué capacitaciones de protección de datos debería completar el personal administrativo?' }],
      build: (v) => ({ mensaje: v.mensaje }),
    }],
  },
  riesgos: {
    route: '/agentes/riesgos', title: 'Evaluación de riesgos', group: 2,
    about: 'Agente de riesgos de privacidad (React + Express + n8n + Qdrant). Responde con el procedimiento de evaluación y consulta la norma ISO/IEC 27701 indexada.',
    actions: [{
      id: 'chat', label: 'Consultar al agente', long: true,
      fields: [{ name: 'message', label: 'Consulta', type: 'textarea', demo: 'Evalúa los riesgos de privacidad de un sistema de matrícula en línea que almacena DNI y correos de estudiantes.' }],
      build: (v) => ({ message: v.message, sessionId: sid() }),
    }],
  },
  dsar: {
    route: '/agentes/dsar', title: 'Derechos de titulares (DSAR)', group: 3,
    about: 'Calcula plazos legales (Ley 29733), consulta la norma con citas, gestiona expedientes y muestra los controles y cláusulas ISO/IEC 27701 de cada caso. La verificación de identidad y la aprobación son decisiones humanas y no se ofrecen aquí.',
    actions: [
      { id: 'dsar_calcular_plazos', label: 'Calcular plazos', fields: [
        { name: 'request_types', label: 'Derechos solicitados', type: 'multi', options: ['information', 'access', 'portability', 'rectification', 'erasure', 'objection'], demo: ['access', 'erasure'] },
        { name: 'received_at', label: 'Fecha de recepción', type: 'date', demo: new Date().toISOString().slice(0, 10) }],
        build: (v) => ({ request_types: v.request_types, received_at: v.received_at, policy_id: 'PE-LEY29733' }) },
      { id: 'dsar_consultar_norma', label: 'Consultar la norma', fields: [
        { name: 'pregunta', label: 'Pregunta', type: 'text', demo: '¿Qué plazo hay para atender un derecho de acceso?' }],
        build: (v) => ({ pregunta: v.pregunta, top_k: 4 }) },
      { id: 'dsar_listar', label: 'Listar expedientes', fields: [], build: () => ({}) },
      { id: 'dsar_handoffs', label: 'Ver handoffs', fields: [], build: () => ({}) },
      // The identity always starts as pending: only the DPO verifies it in /revision.
      { id: 'dsar_crear_caso', label: 'Crear caso', fields: [
        { name: 'principal_id', label: 'Identificador del titular', type: 'text', demo: 'person-001' },
        { name: 'request_types', label: 'Derechos solicitados', type: 'multi', options: ['information', 'access', 'portability', 'rectification', 'erasure', 'objection'], demo: ['erasure'] },
        { name: 'received_at', label: 'Fecha de recepción', type: 'date', demo: new Date().toISOString().slice(0, 10) }],
        build: (v) => ({ principal_id: v.principal_id, request_types: v.request_types, received_at: v.received_at, policy_id: 'PE-LEY29733', identity_status: 'pending' }) },
      { id: 'dsar_estado', label: 'Ver estado de un caso', fields: [
        { name: 'case_id', label: 'Identificador del caso', type: 'text', demo: '' }],
        build: (v) => ({ case_id: v.case_id.trim() }) },
      { id: 'dsar_controles', label: 'Controles y cláusulas ISO de un caso', fields: [
        { name: 'case_id', label: 'Identificador del caso', type: 'text', demo: '' }],
        build: (v) => ({ case_id: v.case_id.trim() }) },
      { id: 'dsar_asistente', label: 'Preguntar al asistente', long: true, fields: [
        { name: 'pregunta', label: 'Pregunta', type: 'textarea', demo: '¿Qué plazo hay para atender un derecho de supresión?' },
        { name: 'case_id', label: 'Identificador del caso (opcional)', type: 'text', demo: '' },
        { name: 'modo', label: 'Modo', type: 'select', options: ['guided', 'gateway'], demo: 'guided' }],
        build: (v) => ({ pregunta: v.pregunta, case_id: v.case_id.trim() || null, modo: v.modo }) },
      { id: 'dsar_borrador', label: 'Ver borrador (caso aprobado)', fields: [
        { name: 'case_id', label: 'Identificador del caso', type: 'text', demo: '' }],
        build: (v) => ({ case_id: v.case_id.trim() }) },
    ],
  },
  auditoria: {
    route: '/agentes/auditoria', title: 'Evidencia y auditoría', group: 4,
    about: 'Evalúa una evidencia contra los controles de ISO/IEC 27701 y propone un dictamen. Es una propuesta: la valida un auditor humano.',
    actions: [
      { id: 'auditar', label: 'Evaluar evidencia', long: true, fields: [
        { name: 'nombre_archivo', label: 'Nombre de la evidencia', type: 'text', demo: 'politica_privacidad.txt' },
        { name: 'contenido', label: 'Contenido (texto)', type: 'textarea', demo: 'Política de privacidad v1.0. No define plazos de conservación ni procedimiento de notificación de brechas.' }],
        build: (v) => v },
      { id: 'hash', label: 'Calcular SHA-256', fields: [{ name: 'contenido', label: 'Texto', type: 'textarea', demo: 'texto de ejemplo' }], build: (v) => v },
    ],
  },
  terceros: {
    route: '/agentes/terceros', title: 'Terceros y DPA', group: 5,
    about: 'Audita contratos de encargo de tratamiento (DPA). El número lo calcula el código, no el modelo. Las aprobaciones DPO y Legal son humanas y se hacen en la interfaz original del grupo.',
    actions: [
      { id: 'auditar', label: 'Auditar contrato', long: true, fields: [
        { name: 'organizacion', label: 'Organización', type: 'text', demo: 'unsa' },
        { name: 'contrato_texto', label: 'Texto del contrato', type: 'textarea', demo: 'CONTRATO DE ENCARGO DE TRATAMIENTO. El encargado tratará datos personales de estudiantes según instrucciones del responsable. No se define plazo de notificación de brechas ni subencargados.' }],
        build: (v) => v },
      { id: 'organizaciones', label: 'Organizaciones y terceros sin DPA', fields: [], build: () => ({}) },
      { id: 'registro', label: 'Expedientes de una organización', fields: [{ name: 'organizacion', label: 'Organización', type: 'text', demo: 'unsa' }], build: (v) => v },
    ],
  },
  controles: {
    route: '/agentes/controles', title: 'Controles y SoA', group: 7,
    about: 'Genera la Declaración de Aplicabilidad (SoA) y verifica controles del Anexo A de ISO/IEC 27701 con reglas deterministas más un análisis ejecutivo del modelo.',
    actions: [
      { id: 'catalogo', label: 'Ver catálogo de controles', fields: [], build: () => ({}) },
      { id: 'ejecutar', label: 'Generar SoA', long: true, fields: [
        { name: 'organizacion', label: 'Organización', type: 'text', demo: 'UNSA' },
        { name: 'rol', label: 'Rol en el tratamiento', type: 'select', options: ['responsable', 'encargado', 'ambos'], demo: 'responsable' }],
        build: (v) => ({ operacion: 'generar_soa', perfil: { rol: v.rol, organizacion: v.organizacion }, riesgos: [], evidencias: [] }) },
    ],
  },
  incidentes: {
    route: '/agentes/incidentes', title: 'Incidentes y brechas', group: 8,
    about: 'Clasifica el evento, evalúa severidad (ENISA), controla el plazo de 48 h y redacta borradores. Todo sale como borrador: nada se notifica sin aprobación humana.',
    actions: [{
      id: 'analizar', label: 'Analizar reporte', long: true,
      fields: [{ name: 'reporte', label: 'Reporte del incidente', type: 'textarea', demo: 'Un funcionario envió por error una hoja de cálculo con DNI y notas de 300 estudiantes a una lista externa de correo de la universidad.' }],
      build: (v) => ({ reporte: v.reporte }),
    }],
  },
};

export const ORDER = [
  ['/', 'Panel general'], ['/agentes/formacion', 'G1 · Formación'], ['/agentes/riesgos', 'G2 · Riesgos'],
  ['/agentes/dsar', 'G3 · DSAR'], ['/agentes/auditoria', 'G4 · Auditoría'], ['/agentes/terceros', 'G5 · Terceros'],
  ['/agentes/inventario', 'G6 · Inventario'], ['/agentes/controles', 'G7 · Controles'], ['/agentes/incidentes', 'G8 · Incidentes'],
  ['/revision', 'Revisión humana'], ['/actividad', 'Actividad'], ['/configuracion', 'Configuración'],
];
export const ID_BY_ROUTE = { formacion: 'formacion', riesgos: 'riesgos', dsar: 'dsar', auditoria: 'auditoria', terceros: 'terceros', inventario: 'inventario', controles: 'controles', incidentes: 'incidentes' };
