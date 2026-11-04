import { api } from '../services/api.js';
import { h, badge, fmtTime, alertBox, spinner } from '../components/ui.js';
import { table } from './dashboard.js';

// ---- Helper de descarga de Word oficial (.docx) ----
async function downloadWordSoA(data) {
  try {
    const res = await fetch('/api/agents/controles/exportar-docx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {})
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errText.slice(0, 200)}`);
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 2000);
  } catch (err) {
    alert('Error al descargar documento Word: ' + err.message);
  }
}

// Estilos de badge para estados
function badgeEstado(st) {
  const s = (st || '').toLowerCase();
  if (s.includes('implementado') && !s.includes('no') && !s.includes('parcial')) {
    return h('span', { style: 'background:#dff5ec; color:#12805c; padding:3px 9px; border-radius:99px; font-weight:600; font-size:12px; white-space:nowrap;' }, 'Implementado');
  }
  if (s.includes('parcial')) {
    return h('span', { style: 'background:#fdf0d5; color:#9a5b00; padding:3px 9px; border-radius:99px; font-weight:600; font-size:12px; white-space:nowrap;' }, 'Parcial');
  }
  if (s.includes('no aplica') || s.includes('excluido')) {
    return h('span', { style: 'background:#e9ebf2; color:#555d70; padding:3px 9px; border-radius:99px; font-weight:600; font-size:12px; white-space:nowrap;' }, 'No Aplica');
  }
  return h('span', { style: 'background:#fde4e2; color:#b3261e; padding:3px 9px; border-radius:99px; font-weight:600; font-size:12px; white-space:nowrap;' }, 'Brecha (No Imp.)');
}

function badgeDictamen(dic) {
  const d = (dic || '').toUpperCase();
  if (d.includes('ACEPTADO')) {
    return h('span', { style: 'background:#dff5ec; color:#12805c; padding:4px 10px; border-radius:6px; font-weight:700; font-size:11px; display:inline-block;' }, '[ACEPTADO - TOLERANCIA INSTITUCIONAL]');
  }
  return h('span', { style: 'background:#fde4e2; color:#b3261e; padding:4px 10px; border-radius:6px; font-weight:700; font-size:11px; display:inline-block;' }, '[NO ACEPTABLE - ACCIÓN REQUERIDA]');
}

export async function controlesPage(root) {
  let detail = { status: 'operativo', id: 'controles' };
  try {
    const list = await api.agents();
    const found = list.find((a) => a.group === 7 || a.id === 'controles');
    if (found) detail = found;
  } catch { /* continuar con valor por defecto */ }

  // Encabezado
  root.append(
    h('div', { class: 'row', style: 'justify-content:space-between; margin-bottom:4px;' },
      h('h1', {}, 'G7 · Controles y Declaración de Aplicabilidad (SoA)'),
      badge(detail.status)
    ),
    h('p', { class: 'sub', style: 'margin-bottom:12px;' },
      'Orquestador Normativo Institucional · ISO/IEC 27701:2025 & Ley N° 29733 (UNSA EPIS)'
    ),
    alertBox('info', 'El Agente de Controles actúa como Orquestador Normativo y Juez Supremo: evalúa los riesgos institucionales (G2), las evidencias certificadas de Secretaría General y DUTIC (G4), los contratos con proveedores de Asesoría Legal (G5), los procedimientos ARCO de la Oficialía de Datos (G3) y los protocolos de incidentes del CSIRT-UNSA (G8) para emitir la Declaración de Aplicabilidad oficial.')
  );

  // Estado reactivo de la vista
  let activeTab = 'inputs';
  let cachedSoa = null;
  let cachedCatalogo = null;
  let rolSeleccionado = 'responsable';
  let orgSeleccionada = 'Universidad Nacional de San Agustín de Arequipa (UNSA)';
  let tableFilter = 'todos';
  let tableSearch = '';

  const navTabs = h('div', { class: 'tabs', style: 'margin-bottom:16px;' });
  const contentArea = h('div', { class: 'controles-content' });
  const histBox = h('div', { class: 'card', style: 'margin-top:20px;' });

  const renderTabs = () => {
    navTabs.replaceChildren(
      h('button', { class: activeTab === 'inputs' ? 'on' : '', onclick: () => switchTab('inputs') }, '1. Entradas del Sistema (Inputs)'),
      h('button', { class: activeTab === 'soa' ? 'on' : '', onclick: () => switchTab('soa') }, '2. Dashboard Ejecutivo & SoA Oficial (DOCX)'),
      h('button', { class: activeTab === 'rag' ? 'on' : '', onclick: () => switchTab('rag') }, '3. Base Normativa & RAG (Chat FAISS)'),
      h('button', { class: activeTab === 'catalogo' ? 'on' : '', onclick: () => switchTab('catalogo') }, '4. Catálogo Maestro (142 Controles)')
    );
  };

  const switchTab = (tab) => {
    activeTab = tab;
    renderTabs();
    if (tab === 'inputs') renderTabInputs();
    else if (tab === 'soa') renderTabSoA();
    else if (tab === 'rag') renderTabRAG();
    else if (tab === 'catalogo') renderTabCatalogo();
  };

  // =========================================================================
  // PESTAÑA 1: ENTRADAS DEL SISTEMA (INPUTS)
  // =========================================================================
  function renderTabInputs() {
    const formBox = h('div', { class: 'card' });

    // Selector de rol
    const roleSelector = h('div', { style: 'margin: 14px 0;' },
      h('label', { style: 'font-weight:700; margin-bottom:6px;' }, 'Rol Institucional de la UNSA (según Inventario de Tratamientos G6):'),
      h('div', { class: 'grid g3', style: 'display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px; margin-top:8px;' },
        h('label', { class: 'card', style: `cursor:pointer; border:2px solid ${rolSeleccionado === 'responsable' ? 'var(--brand)' : 'var(--line)'};` },
          h('input', { type: 'radio', name: 'g7_rol', value: 'responsable', checked: rolSeleccionado === 'responsable', onchange: () => { rolSeleccionado = 'responsable'; renderTabInputs(); } }),
          h('strong', { style: 'margin-left:6px;' }, 'Responsable (PII Controller)'),
          h('p', { class: 'small mute', style: 'margin:4px 0 0;' }, 'La UNSA define fines y medios en SISUNSA y Comedor. Aplican controles A.1 y A.3 (ISO 27701). Se excluye A.2.')
        ),
        h('label', { class: 'card', style: `cursor:pointer; border:2px solid ${rolSeleccionado === 'encargado' ? 'var(--brand)' : 'var(--line)'};` },
          h('input', { type: 'radio', name: 'g7_rol', value: 'encargado', checked: rolSeleccionado === 'encargado', onchange: () => { rolSeleccionado = 'encargado'; renderTabInputs(); } }),
          h('strong', { style: 'margin-left:6px;' }, 'Encargado (PII Processor)'),
          h('p', { class: 'small mute', style: 'margin:4px 0 0;' }, 'Tratamiento por encargo de terceros externos. Aplican controles A.2 y A.3. Se excluye A.1.')
        ),
        h('label', { class: 'card', style: `cursor:pointer; border:2px solid ${rolSeleccionado === 'ambos' ? 'var(--brand)' : 'var(--line)'};` },
          h('input', { type: 'radio', name: 'g7_rol', value: 'ambos', checked: rolSeleccionado === 'ambos', onchange: () => { rolSeleccionado = 'ambos'; renderTabInputs(); } }),
          h('strong', { style: 'margin-left:6px;' }, 'Ambos Roles Simultáneos'),
          h('p', { class: 'small mute', style: 'margin:4px 0 0;' }, 'Evaluación exhaustiva de los 142 controles normativos (A.1, A.2 y A.3).')
        )
      )
    );

    // Tablas estructuradas de entradas institucionales
    const activosData = [
      {
        sistema: 'SISUNSA',
        area: 'DUTIC / Dirección de Registro Académico',
        datos: 'Nombres, DNI, calificaciones, récord de matrícula, filiación estudiantil',
        sensibilidad: 'PII Ordinaria / Académica',
        finalidad: 'Gestión académica oficial y registro de grados y títulos (Ley N° 30220)'
      },
      {
        sistema: 'Comedor Universitario',
        area: 'Dirección Universitaria de Bienestar',
        datos: 'Huellas dactilares biométricas, código de alumno, evaluación socioeconómica',
        sensibilidad: 'DATO SENSIBLE (Biométrico)',
        finalidad: 'Control de acceso al beneficio alimentario universitario (Ley N° 29733, Art. 13)'
      },
      {
        sistema: 'Portal de Admisión UNSA',
        area: 'Dirección Universitaria de Admisión',
        datos: 'DNI, fotografía biométrica, antecedentes escolares, menores de edad',
        sensibilidad: 'PII Menores de Edad',
        finalidad: 'Inscripción, evaluación y selección en concursos de admisión'
      },
      {
        sistema: 'Google Workspace UNSA',
        area: 'DUTIC / Redes y Comunicaciones',
        datos: 'Correos institucionales (@unsa.edu.pe), mensajería, documentos en la nube',
        sensibilidad: 'PII / Comunicaciones',
        finalidad: 'Plataforma de colaboración académica, investigación y gestión docente'
      },
      {
        sistema: 'Repositorio Institucional de Tesis',
        area: 'Vicerrectorado de Investigación (VRI)',
        datos: 'Metadatos de graduandos, código ORCID, producción científica y patentes',
        sensibilidad: 'PII Pública / Autores',
        finalidad: 'Divulgación científica y depósito nacional legal (RENATI / SUNEDU)'
      }
    ];

    const riesgosData = [
      {
        codigo: 'RSK-UNSA-01',
        activo: 'SISUNSA',
        amenaza: 'Inyección SQL y fuga masiva de actas por falta de sanitización web',
        impacto: 'ALTO',
        score: '4.2',
        controles: ['A.8.20', 'A.8.24', 'A.1.2.6']
      },
      {
        codigo: 'RSK-UNSA-02',
        activo: 'Comedor Universitario',
        amenaza: 'Tratamiento de huellas biométricas sin DPIA formal ni consentimiento explícito',
        impacto: 'CRÍTICO',
        score: '4.8',
        controles: ['A.1.2.6 (DPIA)', 'A.1.2.2']
      },
      {
        codigo: 'RSK-UNSA-03',
        activo: 'Portal de Admisión',
        amenaza: 'Ataques DDoS durante el cierre de inscripciones con caída del servicio',
        impacto: 'ALTO',
        score: '3.9',
        controles: ['A.8.6', 'A.8.20']
      },
      {
        codigo: 'RSK-UNSA-04',
        activo: 'Google Workspace UNSA',
        amenaza: 'Campañas de phishing y suplantación de identidad para captura de credenciales',
        impacto: 'MEDIO',
        score: '2.8',
        controles: ['A.5.15', 'A.3.17']
      },
      {
        codigo: 'RSK-UNSA-05',
        activo: 'Repositorio de Tesis',
        amenaza: 'Exfiltración de borradores de patentes o investigaciones previas a publicación',
        impacto: 'MEDIO',
        score: '2.4',
        controles: ['A.5.15', 'A.8.3']
      }
    ];

    const evidenciasData = [
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'RCU-2024-089',
        documento: 'Resolución de Consejo Universitario: Política General de Seguridad de la Información',
        jerarquia: 'Resolución Vigente',
        controles: 'A.5.1, A.5.2',
        estado: 'implementado'
      },
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'RCU-0127-2020',
        documento: 'Reglamento General de Matrícula y Derechos y Deberes Académicos de Estudiantes',
        jerarquia: 'Resolución Vigente',
        controles: 'A.1.2.2',
        estado: 'implementado'
      },
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'DIR-OTIC-004-UNSA',
        documento: 'Directiva de Gestión de Cuentas de Acceso y Uso Aceptable de Red Institucional',
        jerarquia: 'Directiva Vigente',
        controles: 'A.5.15, A.5.18',
        estado: 'implementado'
      },
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'Borrador-DPIA-Comedor-2025.docx',
        documento: 'Evaluación de Impacto de Privacidad para Sistema Biométrico del Comedor',
        jerarquia: 'Borrador Técnico',
        controles: 'A.1.2.6',
        estado: 'parcial'
      },
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'POL-SEG-BACKUP-v1.1.pdf',
        documento: 'Procedimiento de Respaldo, Custodia y Restauración de Bases de Datos',
        jerarquia: 'Directiva Vigente',
        controles: 'A.8.13',
        estado: 'implementado'
      },
      {
        area: 'Secretaría General / DUTIC [G4]',
        codigo: 'MAN-DES-SISUNSA-v2.pdf',
        documento: 'Manual de Ciclo de Vida de Desarrollo Seguro de Software (DUTIC)',
        jerarquia: 'Manual Técnico',
        controles: 'A.8.25, A.8.28',
        estado: 'implementado'
      },
      {
        area: 'Asesoría Legal / Contratos [G5]',
        codigo: 'DPA-Google-Workspace-2024.pdf',
        documento: 'Acuerdo de Tratamiento de Datos (DPA) formal con Google Cloud EMEA',
        jerarquia: 'Contrato Firmado',
        controles: 'A.1.2.7, A.5.19',
        estado: 'implementado'
      },
      {
        area: 'Asesoría Legal / Contratos [G5]',
        codigo: 'Contrato-AWS-Cloud-UNSA.pdf',
        documento: 'Adenda de Privacidad, Confidencialidad y Acuerdos de Nivel de Servicio (SLA)',
        jerarquia: 'Contrato Firmado',
        controles: 'A.5.20, A.5.22',
        estado: 'implementado'
      },
      {
        area: 'Oficialía de Protección de Datos [G3]',
        codigo: 'TUPA-PROC-ARCO-UNSA.pdf',
        documento: 'Procedimiento Oficial TUPA para Solicitudes de Derechos ARCO (odp@unsa.edu.pe)',
        jerarquia: 'Procedimiento Vigente',
        controles: 'A.1.3.7, A.1.3.9',
        estado: 'implementado'
      },
      {
        area: 'Oficialía de Protección de Datos [G3]',
        codigo: 'Formulario-ARCO-Web-v1.0.pdf',
        documento: 'Formulario Digital Único para Ejercicio de Derechos de Acceso, Rectificación y Supresión',
        jerarquia: 'Formulario Oficial',
        controles: 'A.1.3.1',
        estado: 'implementado'
      },
      {
        area: 'Seguridad / CSIRT-UNSA [G8]',
        codigo: 'Protocolo-CSIRT-UNSA-v0.2.docx',
        documento: 'Procedimiento Operativo de Respuesta a Incidentes de Privacidad y Notificación 48h a la ANPD',
        jerarquia: 'Borrador Técnico',
        controles: 'A.3.12',
        estado: 'parcial'
      },
      {
        area: 'Seguridad / CSIRT-UNSA [G8]',
        codigo: 'BITACORA-CSIRT-2024-Q3.xlsx',
        documento: 'Registro de Monitoreo de Eventos de Seguridad y Detección de Anomalías de Red',
        jerarquia: 'Registro Operativo',
        controles: 'A.8.16',
        estado: 'implementado'
      },
      {
        area: 'Desarrollo Docente / RRHH [G1]',
        codigo: 'Plan-Capacitacion-Privacidad-2024.pdf',
        documento: 'Plan Anual de Formación y Concientización en Protección de Datos Personales',
        jerarquia: 'Plan Aprobado',
        controles: 'A.3.17, A.6.3',
        estado: 'implementado'
      },
      {
        area: 'Desarrollo Docente / RRHH [G1]',
        codigo: 'Registro-Asistencia-Taller.pdf',
        documento: 'Actas de Concurrencia y Evaluación de Talleres de Inducción de Ley N° 29733',
        jerarquia: 'Evidencia Ejecutada',
        controles: 'A.6.3',
        estado: 'implementado'
      }
    ];

    // Card Input 1: Activos
    const cardActivos = h('div', { class: 'card', style: 'margin-top:16px; overflow-x:auto;' },
      h('h3', { style: 'font-size:15px; margin:0 0 4px;' }, 'Input 01: Mapeo de Activos Críticos & Tratamientos (Grupo 6 - Inventario)'),
      h('p', { class: 'small mute', style: 'margin:0 0 10px;' }, 'Inventario institucional de sistemas que tratan datos personales (PII) bajo la responsabilidad de la UNSA:'),
      h('table', { style: 'width:100%; border-collapse:collapse; font-size:12px;' },
        h('thead', {},
          h('tr', {},
            h('th', { style: 'width:160px;' }, 'Sistema / Activo'),
            h('th', { style: 'width:210px;' }, 'Área Custodia'),
            h('th', { style: 'min-width:240px;' }, 'Datos Personales Tratados'),
            h('th', { style: 'width:180px;' }, 'Clasificación'),
            h('th', { style: 'min-width:220px;' }, 'Finalidad Institucional & Base Legal')
          )
        ),
        h('tbody', {},
          activosData.map(a => h('tr', {},
            h('td', { style: 'font-weight:700;' }, a.sistema),
            h('td', { class: 'small mute' }, a.area),
            h('td', {}, a.datos),
            h('td', {},
              a.sensibilidad.includes('SENSIBLE')
                ? h('span', { style: 'background:#fde4e2; color:#b3261e; padding:2px 8px; border-radius:4px; font-weight:700; font-size:11px;' }, a.sensibilidad)
                : h('span', { style: 'background:#e9ebf2; color:#3b5998; padding:2px 8px; border-radius:4px; font-weight:600; font-size:11px;' }, a.sensibilidad)
            ),
            h('td', { class: 'small' }, a.finalidad)
          ))
        )
      )
    );

    // Card Input 2: Riesgos
    const cardRiesgos = h('div', { class: 'card', style: 'margin-top:16px; overflow-x:auto;' },
      h('h3', { style: 'font-size:15px; margin:0 0 4px;' }, 'Input 02: Matriz de Riesgos Operativos & DPIA (Grupo 2 - ISO 27005 / ISO 29134)'),
      h('p', { class: 'small mute', style: 'margin:0 0 10px;' }, 'Apreciación de amenazas y vulnerabilidades que sustentan la justificación de controles (Cláusula 6.1.3 d):'),
      h('table', { style: 'width:100%; border-collapse:collapse; font-size:12px;' },
        h('thead', {},
          h('tr', {},
            h('th', { style: 'width:100px;' }, 'Código'),
            h('th', { style: 'width:160px;' }, 'Activo Afectado'),
            h('th', { style: 'min-width:260px;' }, 'Amenaza & Vulnerabilidad Identificada'),
            h('th', { style: 'width:120px; text-align:center;' }, 'Impacto Residual'),
            h('th', { style: 'min-width:180px;' }, 'Controles Mitigadores ISO 27701')
          )
        ),
        h('tbody', {},
          riesgosData.map(r => {
            const badgeStyle = r.impacto === 'CRÍTICO'
              ? 'background:#fde4e2; color:#b3261e;'
              : (r.impacto === 'ALTO' ? 'background:#fdf0d5; color:#9a5b00;' : 'background:#e9ebf2; color:#3b5998;');
            return h('tr', {},
              h('td', { style: 'font-weight:700;' }, r.codigo),
              h('td', { style: 'font-weight:600;' }, r.activo),
              h('td', {}, r.amenaza),
              h('td', { style: 'text-align:center;' },
                h('span', { style: `${badgeStyle} padding:3px 8px; border-radius:4px; font-weight:700; font-size:11px;` }, `${r.impacto} (${r.score})`)
              ),
              h('td', {}, r.controles.map(c => h('span', { class: 'badge', style: 'margin:1px 3px; font-size:10px;' }, c)))
            );
          })
        )
      )
    );

    // Card Input 3: Evidencias por Área
    const cardEvidencias = h('div', { class: 'card', style: 'margin-top:16px; overflow-x:auto;' },
      h('h3', { style: 'font-size:15px; margin:0 0 4px;' }, 'Input 03: Repositorio Probatorio por Área Universitaria (Grupos 4, 5, 3, 8 y 1)'),
      h('p', { class: 'small mute', style: 'margin:0 0 10px;' }, 'Documentos probatorios auditados bajo jerarquía probatoria (ISO 19011 y Cláusula 7.5 de ISO 27001):'),
      h('table', { style: 'width:100%; border-collapse:collapse; font-size:12px;' },
        h('thead', {},
          h('tr', {},
            h('th', { style: 'width:200px;' }, 'Área Emisora / Grupo'),
            h('th', { style: 'width:190px;' }, 'Código / Archivo'),
            h('th', { style: 'min-width:240px;' }, 'Documento Probatorio Auditado'),
            h('th', { style: 'width:140px;' }, 'Jerarquía Probatoria'),
            h('th', { style: 'width:110px;' }, 'Controles'),
            h('th', { style: 'width:110px;' }, 'Estado')
          )
        ),
        h('tbody', {},
          evidenciasData.map(e => h('tr', {},
            h('td', { style: 'font-weight:600; font-size:11px;' }, e.area),
            h('td', { style: 'font-family:monospace; font-size:11px; font-weight:600;' }, e.codigo),
            h('td', {}, e.documento),
            h('td', { class: 'small mute' }, e.jerarquia),
            h('td', { style: 'font-weight:600; font-size:11px; color:var(--brand);' }, e.controles),
            h('td', {}, badgeEstado(e.estado))
          ))
        )
      )
    );

    const btnEjecutar = h('button', {
      type: 'button',
      style: 'font-size:15px; padding:12px 24px; margin-top:20px; font-weight:700; width:100%; display:flex; align-items:center; justify-content:center; gap:8px;',
      onclick: async () => {
        btnEjecutar.disabled = true;
        btnEjecutar.replaceChildren(spinner('Ejecutando auditoría determinista de 142 controles...'));
        try {
          const runRes = await api.run('controles', 'ejecutar', {
            operacion: 'generar_soa',
            perfil: { rol: rolSeleccionado, organizacion: orgSeleccionada },
            riesgos: [],
            evidencias: []
          });
          const rawOut = runRes.result?.output ?? runRes.result;
          cachedSoa = rawOut?.datos ?? rawOut;
          switchTab('soa');
          history();
        } catch (err) {
          alert('Error al generar SoA: ' + err.message);
        } finally {
          btnEjecutar.disabled = false;
          btnEjecutar.replaceChildren(document.createTextNode('Ejecutar Auditoría y Generar SoA Oficial'));
        }
      }
    }, 'Ejecutar Auditoría y Generar SoA Oficial');

    formBox.replaceChildren(
      h('h2', {}, 'Configuración de Auditoría Institucional'),
      h('div', { class: 'row' },
        h('div', { style: 'flex:1;' },
          h('label', {}, 'Entidad Universitaria Auditada:'),
          h('input', { type: 'text', value: orgSeleccionada, oninput: (e) => { orgSeleccionada = e.target.value; } })
        )
      ),
      roleSelector,
      cardActivos,
      cardRiesgos,
      cardEvidencias,
      btnEjecutar
    );

    contentArea.replaceChildren(formBox);
  }

  // =========================================================================
  // PESTAÑA 2: DASHBOARD EJECUTIVO & TABLAS OFICIALES (FORMATO DOCX)
  // =========================================================================
  async function renderTabSoA() {
    if (!cachedSoa) {
      contentArea.replaceChildren(
        h('div', { class: 'card', style: 'text-align:center; padding:40px 20px;' },
          h('h2', {}, 'La Declaración de Aplicabilidad (SoA) aún no ha sido generada'),
          h('p', { class: 'mute' }, 'Presione el botón para ejecutar la auditoría determinista sobre los 142 controles y riesgos institucionales:'),
          h('button', {
            style: 'margin-top:14px; font-size:15px; padding:10px 22px;',
            onclick: async (e) => {
              e.target.disabled = true;
              e.target.replaceChildren(spinner('Generando SoA...'));
              try {
                const res = await api.run('controles', 'ejecutar', {
                  operacion: 'generar_soa',
                  perfil: { rol: rolSeleccionado, organizacion: orgSeleccionada },
                  riesgos: [],
                  evidencias: []
                });
                const rawOut = res.result?.output ?? res.result;
                cachedSoa = rawOut?.datos ?? rawOut;
                renderTabSoA();
                history();
              } catch (err) {
                alert('Error: ' + err.message);
                e.target.disabled = false;
                e.target.textContent = 'Generar SoA Ahora';
              }
            }
          }, 'Generar SoA Ahora')
        )
      );
      return;
    }

    const datos = cachedSoa;
    const resumen = datos.resumen || {};
    const soaList = (datos.soa_canonico && datos.soa_canonico.length) ? datos.soa_canonico : (datos.soa || []);
    const riesgosList = datos.riesgos_residuales || [];
    const kpis = datos.kpis || {};

    const totalEvaluados = resumen.controles_evaluados || soaList.length || 142;
    const aplicables = resumen.aplican || soaList.filter(c => c.aplica).length;
    const implementados = resumen.implementados || soaList.filter(c => (c.estado || '').includes('implementado') && !(c.estado || '').includes('no') && !(c.estado || '').includes('parcial')).length;
    const parciales = resumen.parciales || soaList.filter(c => (c.estado || '').includes('parcial')).length;
    const brechas = resumen.no_implementados || soaList.filter(c => c.aplica && (c.estado || '').includes('no')).length;
    const compliance = kpis.compliance_pct != null
      ? kpis.compliance_pct
      : (kpis.compliance_global?.value != null ? Math.round(kpis.compliance_global.value) : Math.round((implementados / (aplicables || 1)) * 100));
    const cmmiPromedio = kpis.cmmi_average != null
      ? kpis.cmmi_average
      : (kpis.maturity_global?.value != null ? kpis.maturity_global.value : 0.2);

    // 1. Dashboard Superior de KPIs
    const dashboardCards = h('div', { class: 'kpis', style: 'display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:12px; margin-bottom:16px;' },
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Total Evaluados'), h('div', { class: 'kpi' }, String(totalEvaluados))),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Controles Aplicables'), h('div', { class: 'kpi', style: 'color:var(--brand);' }, String(aplicables))),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Implementados'), h('div', { class: 'kpi', style: 'color:var(--ok);' }, String(implementados))),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Parciales'), h('div', { class: 'kpi', style: 'color:var(--warn);' }, String(parciales))),
      h('div', { class: 'card' }, h('div', { class: 'small mute' }, 'Brechas Críticas'), h('div', { class: 'kpi', style: 'color:var(--bad);' }, String(brechas))),
      h('div', { class: 'card' },
        h('div', { class: 'small mute' }, 'Madurez CMMI'),
        h('div', { class: 'kpi', style: 'font-size:18px;' }, `Nivel ${cmmiPromedio} / 5`),
        h('div', { style: 'background:var(--line); border-radius:4px; height:6px; margin-top:6px; overflow:hidden;' },
          h('div', { style: `background:var(--ok); height:100%; width:${Math.min(100, Math.max(8, compliance))}%;` })
        )
      )
    );

    // 2. Barra de Acciones y Filtros
    const btnDescargarWord = h('button', {
      type: 'button',
      style: 'background:#1d6f42; color:#fff; font-weight:700; display:flex; align-items:center; gap:6px; padding:9px 18px;',
      onclick: () => downloadWordSoA(datos)
    }, 'Descargar Declaración SoA Oficial (.docx)');

    const searchInput = h('input', {
      type: 'text',
      placeholder: 'Buscar control por código o nombre...',
      value: tableSearch,
      style: 'max-width:280px; padding:7px 10px;',
      oninput: (e) => {
        tableSearch = e.target.value.toLowerCase();
        renderFilteredTable();
      }
    });

    const filterBtns = h('div', { class: 'row', style: 'gap:6px;' },
      h('button', { class: tableFilter === 'todos' ? 'on' : 'ghost', onclick: () => { tableFilter = 'todos'; renderTabSoA(); } }, `Todos (${aplicables})`),
      h('button', { class: tableFilter === 'brechas' ? 'on' : 'ghost', onclick: () => { tableFilter = 'brechas'; renderTabSoA(); } }, `🔴 Brechas (${brechas})`),
      h('button', { class: tableFilter === 'implementados' ? 'on' : 'ghost', onclick: () => { tableFilter = 'implementados'; renderTabSoA(); } }, `🟢 Implementados (${implementados})`),
      h('button', { class: tableFilter === 'parciales' ? 'on' : 'ghost', onclick: () => { tableFilter = 'parciales'; renderTabSoA(); } }, `🟡 Parciales (${parciales})`),
      h('button', { class: tableFilter === 'excluidos' ? 'on' : 'ghost', onclick: () => { tableFilter = 'excluidos'; renderTabSoA(); } }, `⚪ Excluidos`)
    );

    const actionToolbar = h('div', { class: 'card', style: 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:14px;' },
      btnDescargarWord,
      h('div', { class: 'row', style: 'gap:10px;' }, filterBtns, searchInput)
    );

    // 3. Tabla 2 Oficial (SoA)
    const tableContainer = h('div', { class: 'card', style: 'overflow-x:auto; margin-bottom:20px;' });

    function renderFilteredTable() {
      let filtered = soaList.filter((row) => {
        const est = (row.estado || '').toLowerCase();
        const apl = Boolean(row.aplica);
        if (tableFilter === 'brechas') {
          if (!apl || !est.includes('no')) return false;
        } else if (tableFilter === 'implementados') {
          if (!apl || !est.includes('implementado') || est.includes('no') || est.includes('parcial')) return false;
        } else if (tableFilter === 'parciales') {
          if (!apl || !est.includes('parcial')) return false;
        } else if (tableFilter === 'excluidos') {
          if (apl) return false;
        } else {
          // 'todos': muestra los aplicables por defecto
          if (!apl) return false;
        }

        if (tableSearch) {
          const matchCode = (row.control || '').toLowerCase().includes(tableSearch);
          const matchName = (row.nombre || '').toLowerCase().includes(tableSearch);
          const matchJust = (row.justificacion || '').toLowerCase().includes(tableSearch);
          return matchCode || matchName || matchJust;
        }
        return true;
      });

      const rowsDom = filtered.map((c) => {
        const evidenciasStr = (c.evidencias && c.evidencias.length) ? c.evidencias.join('; ') : 'Sin evidencia registrada';
        const cmmiLabel = c.cmmi ? `Nivel ${c.cmmi.current_level} (${c.cmmi.label})` : (c.nivel_etiqueta || 'Nivel 0');

        return h('tr', {},
          h('td', { style: 'font-weight:700; white-space:nowrap;' }, c.control || '—'),
          h('td', { style: 'font-weight:600;' }, c.nombre || '—'),
          h('td', { style: 'text-align:center;' }, c.aplica ? h('span', { style: 'color:var(--ok); font-weight:700;' }, 'SÍ') : h('span', { style: 'color:var(--mute);' }, 'NO')),
          h('td', { style: 'font-size:12px; line-height:1.4;' }, c.justificacion || '—'),
          h('td', {}, badgeEstado(c.estado)),
          h('td', { style: 'font-size:12px; white-space:nowrap;' }, cmmiLabel),
          h('td', { style: 'font-size:12px; line-height:1.4; color:var(--ink);' }, evidenciasStr),
          h('td', { style: 'font-size:12px; line-height:1.4;' },
            h('div', { style: 'font-weight:600; color:var(--brand); margin-bottom:2px;' }, c.responsable || 'DUTIC / OPD'),
            h('div', { class: 'small mute' }, c.improvement_action || c.metodo || '—')
          )
        );
      });

      tableContainer.replaceChildren(
        h('h2', { style: 'margin-bottom:6px;' }, 'Tabla 2 Oficial: Declaración de Aplicabilidad (SoA ISO/IEC 27701:2025)'),
        h('p', { class: 'small mute', style: 'margin-bottom:12px;' }, `Mostrando ${filtered.length} controles filtrados según el rol institucional: ${rolSeleccionado}`),
        h('table', { style: 'width:100%; border-collapse:collapse; font-size:13px;' },
          h('thead', {},
            h('tr', {},
              h('th', { style: 'width:80px;' }, 'Control'),
              h('th', { style: 'width:180px;' }, 'Nombre del Control'),
              h('th', { style: 'width:55px; text-align:center;' }, 'Aplica'),
              h('th', { style: 'min-width:200px;' }, 'Justificación & Riesgos'),
              h('th', { style: 'width:130px;' }, 'Estado'),
              h('th', { style: 'width:110px;' }, 'Madurez CMMI'),
              h('th', { style: 'min-width:180px;' }, 'Evidencia / Área'),
              h('th', { style: 'min-width:180px;' }, 'Acción de Mejora / Responsable')
            )
          ),
          h('tbody', {}, rowsDom.length ? rowsDom : h('tr', {}, h('td', { colspan: '8', style: 'text-align:center; padding:20px;' }, 'No se encontraron controles con el filtro actual.')))
        )
      );
    }

    renderFilteredTable();

    // 4. Tabla 3 Oficial (Riesgos Residuales de la UNSA)
    const riesgosCard = h('div', { class: 'card', style: 'margin-bottom:20px; overflow-x:auto;' },
      h('h2', { style: 'margin-bottom:4px;' }, 'Tabla 3 Oficial: Evaluación y Tratamiento de Riesgos Residuales (UNSA)'),
      h('p', { class: 'small mute', style: 'margin-bottom:12px;' }, 'Apreciación de riesgos sobre los activos críticos institucionales y criterio de aceptación formal:'),
      h('table', { style: 'width:100%; border-collapse:collapse; font-size:13px;' },
        h('thead', {},
          h('tr', {},
            h('th', { style: 'width:110px;' }, 'Código'),
            h('th', { style: 'width:200px;' }, 'Activo Institucional'),
            h('th', { style: 'min-width:240px;' }, 'Amenaza / Vulnerabilidad'),
            h('th', { style: 'width:100px; text-align:center;' }, 'Riesgo Residual'),
            h('th', { style: 'width:240px;' }, 'Criterio de Aceptación (Dictamen)'),
            h('th', { style: 'min-width:160px;' }, 'Controles Vinculados')
          )
        ),
        h('tbody', {},
          riesgosList.map((r) => {
            const residualScore = r.residual_score || r.riesgo_residual || 2.0;
            const dictamenLabel = residualScore <= 3.0 ? '[ACEPTADO - TOLERANCIA INSTITUCIONAL]' : '[NO ACEPTABLE - ACCIÓN REQUERIDA]';
            const ctrlBadge = (r.controles || []).map(cc => h('span', { class: 'badge', style: 'margin:2px; font-size:11px;' }, cc));

            return h('tr', {},
              h('td', { style: 'font-weight:700;' }, r.risk_code || r.id || 'RSK-UNSA'),
              h('td', { style: 'font-weight:600;' }, r.activo || '—'),
              h('td', { style: 'font-size:12px; line-height:1.4;' },
                h('div', { style: 'font-weight:600; color:var(--bad);' }, r.amenaza || '—'),
                h('div', { class: 'mute' }, r.vulnerabilidad || r.descripcion || '—')
              ),
              h('td', { style: 'text-align:center; font-weight:700; font-size:14px;' }, String(residualScore)),
              h('td', {}, badgeDictamen(dictamenLabel)),
              h('td', {}, ctrlBadge.length ? ctrlBadge : '—')
            );
          })
        )
      )
    );

    // 5. Banner de Gobernanza Human-in-the-Loop y JSON Técnico
    const humanGovernanceCard = h('div', { class: 'alert warn', style: 'margin-bottom:16px;' },
      h('strong', {}, 'Cláusula de Gobernanza y Supervisión Humana (Human-in-the-Loop): '),
      'La presente Declaración de Aplicabilidad es un dictamen técnico determinista emitido por el Agente G7. De conformidad con la Cláusula 6.1.3 de ISO/IEC 27701:2025 y la Ley N° 29733, la validez legal y certificación institucional definitiva requiere la validación y firma digital del Oficial de Protección de Datos (DPO) de la UNSA y del Director de OTIC.'
    );

    const jsonDetails = h('details', { class: 'card', style: 'margin-top:14px;' },
      h('summary', { style: 'cursor:pointer; font-weight:600;' }, 'Ver Payload JSON Completo (Auditoría Técnica)'),
      h('pre', { style: 'max-height:300px; overflow:auto; margin-top:10px;' }, JSON.stringify(datos, null, 2))
    );

    contentArea.replaceChildren(
      dashboardCards,
      actionToolbar,
      tableContainer,
      riesgosCard,
      humanGovernanceCard,
      jsonDetails
    );
  }

  // =========================================================================
  // PESTAÑA 3: BASE NORMATIVA & RAG SEMÁNTICO (CHAT FAISS)
  // =========================================================================
  function renderTabRAG() {
    const ragBox = h('div', { class: 'card' });

    const txtQuery = h('textarea', {
      placeholder: 'Escriba una consulta normativa o procedimiento institucional de la UNSA...',
      style: 'min-height:90px; margin-bottom:10px;',
      value: '¿Cómo se tramita el ejercicio de derechos ARCO de los estudiantes en la UNSA según la normativa institucional?'
    });

    const outResults = h('div', { style: 'margin-top:16px;' });

    const chipsPreguntas = [
      '¿Cómo se tramita el ejercicio de derechos ARCO de estudiantes en la UNSA?',
      '¿Qué controles aplican a los datos biométricos del comedor universitario?',
      '¿Cuáles son las obligaciones ante un incidente de seguridad y plazos ante la ANPD?',
      '¿Qué requisitos exige la Ley 29733 para contratar encargados de tratamiento (Google, AWS)?'
    ];

    const chipsContainer = h('div', { class: 'row', style: 'gap:6px; margin-bottom:12px;' },
      chipsPreguntas.map((q) => h('button', {
        class: 'ghost small',
        type: 'button',
        style: 'font-size:12px; padding:4px 9px;',
        onclick: () => { txtQuery.value = q; ejecutarConsulta(); }
      }, q))
    );

    async function ejecutarConsulta() {
      const q = txtQuery.value.trim();
      if (!q) return;
      btnBuscar.disabled = true;
      outResults.replaceChildren(h('div', { class: 'card' }, spinner('Buscando en FAISS y sintetizando respuesta con IA...')));

      try {
        const res = await api.run('controles', 'ejecutar', {
          operacion: 'consultar',
          solicitud: q
        });
        const raw = res.result?.output ?? res.result;
        const respTexto = raw?.respuesta || raw?.output || 'Sin respuesta';
        const hits = raw?.datos?.hits || [];

        const hitsDom = hits.map((hItem) => {
          const scorePct = Math.round((hItem.score || 0.8) * 100);
          return h('div', { class: 'card', style: 'margin-top:8px; border-left:4px solid var(--brand);' },
            h('div', { class: 'row', style: 'justify-content:space-between; margin-bottom:4px;' },
              h('strong', { style: 'font-size:13px; color:var(--brand);' }, hItem.meta || 'Directiva UNSA'),
              h('span', { class: 'badge b-operativo' }, `Afinidad: ${scorePct}%`)
            ),
            h('p', { class: 'small', style: 'margin:0; line-height:1.5;' }, hItem.texto || '')
          );
        });

        outResults.replaceChildren(
          h('div', { class: 'card', style: 'background:var(--panel); border:1px solid var(--brand); margin-bottom:14px;' },
            h('h3', { style: 'margin:0 0 8px; color:var(--brand);' }, 'Dictamen del Agente de Controles'),
            h('div', { class: 'md', style: 'line-height:1.6; font-size:14px;' }, respTexto)
          ),
          h('h3', { style: 'font-size:15px; margin:16px 0 6px;' }, `Fuentes Recuperadas por Búsqueda Vectorial FAISS (${hits.length} fragmentos)`),
          ...hitsDom
        );
      } catch (err) {
        outResults.replaceChildren(alertBox('bad', 'Error en consulta RAG: ' + err.message));
      } finally {
        btnBuscar.disabled = false;
      }
    }

    const btnBuscar = h('button', {
      type: 'button',
      style: 'padding:10px 20px; font-weight:700;',
      onclick: ejecutarConsulta
    }, 'Consultar Agente (Búsqueda Vectorial FAISS)');

    ragBox.replaceChildren(
      h('h2', {}, 'Búsqueda Semántica Vectorial (RAG con FAISS & directivas UNSA)'),
      h('p', { class: 'small mute', style: 'margin-bottom:10px;' },
        'Realice consultas en lenguaje natural. El agente busca en el índice vectorial FAISS sobre las directivas institucionales (DIR-OTIC-004-UNSA, TUPA, Política de Privacidad) y sintetiza la fundamentación jurídica:'
      ),
      chipsContainer,
      txtQuery,
      btnBuscar,
      outResults
    );

    contentArea.replaceChildren(ragBox);
  }

  // =========================================================================
  // PESTAÑA 4: CATÁLOGO MAESTRO (142 CONTROLES)
  // =========================================================================
  async function renderTabCatalogo() {
    contentArea.replaceChildren(h('div', { class: 'card' }, spinner('Cargando catálogo maestro de 142 controles...')));

    if (!cachedCatalogo) {
      try {
        const catRes = await api.run('controles', 'catalogo', {});
        const out = catRes.result?.output ?? catRes.result;
        cachedCatalogo = Array.isArray(out) ? out : (out.controles || []);
      } catch (err) {
        contentArea.replaceChildren(alertBox('bad', 'No se pudo cargar el catálogo: ' + err.message));
        return;
      }
    }

    const list = cachedCatalogo || [];
    let catFilter = 'todos';
    let catSearch = '';

    const catContainer = h('div');

    function drawCatalogo() {
      const filtered = list.filter((c) => {
        if (catFilter !== 'todos') {
          if ((c.grupo || '').toLowerCase() !== catFilter.toLowerCase()) return false;
        }
        if (catSearch) {
          const m1 = (c.id || '').toLowerCase().includes(catSearch);
          const m2 = (c.nombre || '').toLowerCase().includes(catSearch);
          const m3 = (c.descripcion || '').toLowerCase().includes(catSearch);
          return m1 || m2 || m3;
        }
        return true;
      });

      const rowsDom = filtered.map((c) => h('tr', {},
        h('td', { style: 'font-weight:700;' }, c.id || '—'),
        h('td', { style: 'font-weight:600;' }, c.nombre || '—'),
        h('td', { class: 'small mute' }, c.grupo_nombre || c.grupo || '—'),
        h('td', { style: 'text-align:center;' }, c.rol_normativo === 'A' ? 'Ambos' : (c.rol_normativo === 'C' ? 'Responsable' : 'Encargado')),
        h('td', { style: 'font-size:12px;' }, c.ley_29733_aplica ? (c.ley_29733_articulos || ['Sí']).join(', ') : '—'),
        h('td', { style: 'font-size:12px; color:var(--brand);' }, c.agente_responsable || 'DUTIC')
      ));

      catContainer.replaceChildren(
        h('div', { class: 'card', style: 'margin-bottom:14px;' },
          h('h2', {}, `Catálogo Maestro de Controles (${list.length} Controles ISO/IEC 27001:2022 & 27701:2025)`),
          h('div', { class: 'row', style: 'gap:10px; margin-top:10px;' },
            h('input', {
              type: 'text',
              placeholder: 'Filtrar por código, nombre o descripción...',
              value: catSearch,
              style: 'max-width:300px;',
              oninput: (e) => { catSearch = e.target.value.toLowerCase(); drawCatalogo(); }
            }),
            h('select', {
              style: 'max-width:220px;',
              onchange: (e) => { catFilter = e.target.value; drawCatalogo(); }
            },
              h('option', { value: 'todos' }, 'Todos los Dominios'),
              h('option', { value: 'A.5' }, 'A.5 Organizacionales (37)'),
              h('option', { value: 'A.6' }, 'A.6 Personas (8)'),
              h('option', { value: 'A.7' }, 'A.7 Físicos (14)'),
              h('option', { value: 'A.8' }, 'A.8 Tecnológicos (34)'),
              h('option', { value: 'A.1' }, 'A.1 Responsables (23)'),
              h('option', { value: 'A.2' }, 'A.2 Encargados (26)')
            )
          )
        ),
        h('div', { class: 'card', style: 'overflow-x:auto;' },
          h('table', { style: 'width:100%; border-collapse:collapse; font-size:13px;' },
            h('thead', {},
              h('tr', {},
                h('th', { style: 'width:90px;' }, 'Control'),
                h('th', { style: 'width:240px;' }, 'Nombre'),
                h('th', { style: 'width:180px;' }, 'Dominio'),
                h('th', { style: 'width:110px; text-align:center;' }, 'Rol Normativo'),
                h('th', { style: 'width:120px;' }, 'Ley N° 29733'),
                h('th', { style: 'min-width:160px;' }, 'Responsable')
              )
            ),
            h('tbody', {}, rowsDom)
          )
        )
      );
    }

    drawCatalogo();
    contentArea.replaceChildren(catContainer);
  }

  // Historial de ejecuciones en PostgreSQL
  async function history() {
    try {
      const rows = await api.executions(detail.id);
      histBox.replaceChildren(
        h('h2', {}, 'Historial de Ejecuciones de G7 (Persistido en PostgreSQL)'),
        rows.length
          ? table(['Hora', 'Acción', 'Estado', 'Modo', 'Error'],
              rows.map((r) => [fmtTime(r.created_at), r.action, r.status, r.llm_mode + (r.simulated ? ' (simulado)' : ''), r.error || '']))
          : h('span', { class: 'mute' }, 'Sin ejecuciones todavía.')
      );
    } catch {
      histBox.replaceChildren(h('span', { class: 'mute' }, 'No se pudo cargar el historial.'));
    }
  }

  // Render inicial
  renderTabs();
  renderTabInputs();
  history();

  root.append(navTabs, contentArea, histBox);
}
