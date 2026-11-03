<template>
  <div class="gform-modal-overlay" v-if="chatStore.showGoogleFormModal" @click.self="cerrar">
    <div class="gform-modal-card">
      <!-- Barra superior icónica Google Forms Morado -->
      <div class="gform-top-accent"></div>

      <!-- Cabecera del Modal -->
      <div class="gform-header-bar">
        <div class="gform-brand-row">
          <div class="gform-logo-box">
            <span class="gform-icon">📝</span>
            <span class="gform-brand-text">Google Forms <span class="gform-sub-brand">· PIMS UNSA Formación</span></span>
          </div>
          <span class="gform-live-badge">Modo Previsualización Interactiva</span>
        </div>
        <button class="gform-btn-close" @click="cerrar" title="Cerrar modal">✕</button>
      </div>

      <!-- Cuerpo del Formulario estilo Google Forms -->
      <div class="gform-body-scroll">
        <!-- Tarjeta Principal: Título y Contexto Institucional -->
        <div class="gform-section-card gform-title-card">
          <div class="gform-card-accent"></div>
          <h2 class="gform-title">{{ formInfo.titulo || 'Diagnóstico de Conciencia en Privacidad ISO/IEC 27701:2025' }}</h2>
          <p class="gform-desc">
            {{ formInfo.descripcion || 'Formulario oficial de diagnóstico y toma de conciencia en tratamiento de datos personales conforme al Control A.3.17 de ISO 27701 y la Ley Peruana N° 29733. Sus respuestas serán auditadas como evidencia formativa.' }}
          </p>

          <div class="gform-meta-tags">
            <span class="gform-tag tag-purple">🏛️ Padrón Oficial UNSA</span>
            <span class="gform-tag tag-blue">🛡️ ISO/IEC 27701 (Control A.3.17)</span>
            <span class="gform-tag tag-green">⚖️ Ley N° 29733</span>
          </div>

          <div class="gform-destinatarios-box" v-if="formInfo.destinatarios?.length">
            <span class="gform-recipients-label">Destinatarios Convocados ({{ formInfo.destinatarios.length }}):</span>
            <div class="gform-chips-wrap">
              <span
                v-for="(dest, idx) in formInfo.destinatarios.slice(0, 8)"
                :key="idx"
                class="gform-user-chip"
              >
                👤 {{ dest }}
              </span>
              <span v-if="formInfo.destinatarios.length > 8" class="gform-user-chip-more">
                +{{ formInfo.destinatarios.length - 8 }} más
              </span>
            </div>
          </div>
        </div>

        <!-- Preguntas estilo Google Forms -->
        <div
          v-for="(preg, pIdx) in preguntasList"
          :key="preg.id || pIdx"
          class="gform-section-card gform-question-card"
        >
          <div class="gform-q-header">
            <span class="gform-q-num">{{ pIdx + 1 }}.</span>
            <div class="gform-q-content">
              <span class="gform-q-text">{{ preg.pregunta }}</span>
              <span class="gform-q-badge" v-if="preg.control_iso">
                {{ preg.control_iso }}
              </span>
            </div>
          </div>

          <!-- Caso: Opción Múltiple -->
          <div v-if="preg.tipo === 'opcion_multiple' || preg.opciones" class="gform-options-group">
            <label
              v-for="(opc, oIdx) in (preg.opciones || [])"
              :key="oIdx"
              class="gform-option-row"
            >
              <input
                type="radio"
                :name="'pregunta_' + pIdx"
                :value="opc"
                v-model="respuestas[pIdx]"
                class="gform-radio"
              />
              <span class="gform-option-label">{{ opc }}</span>
            </label>
          </div>

          <!-- Caso: Escala Lineal (1 a 5) -->
          <div v-else-if="preg.tipo === 'escala'" class="gform-scale-wrap">
            <div class="gform-scale-labels">
              <span class="gform-scale-ext">{{ preg.etiqueta_min || '1: Mínimo' }}</span>
              <span class="gform-scale-ext">{{ preg.etiqueta_max || '5: Máximo' }}</span>
            </div>
            <div class="gform-scale-row">
              <label v-for="num in [1, 2, 3, 4, 5]" :key="num" class="gform-scale-col">
                <span class="gform-scale-num">{{ num }}</span>
                <input
                  type="radio"
                  :name="'escala_' + pIdx"
                  :value="num"
                  v-model="respuestas[pIdx]"
                  class="gform-radio"
                />
              </label>
            </div>
          </div>

          <!-- Caso: Texto Breve -->
          <div v-else class="gform-text-input-wrap">
            <input
              type="text"
              class="gform-text-input"
              placeholder="Tu respuesta..."
              v-model="respuestas[pIdx]"
            />
          </div>
        </div>
      </div>

      <!-- Footer de Acciones con Botón de Envío Human-In-The-Loop -->
      <footer class="gform-footer">
        <div class="gform-footer-left">
          <span class="gform-footer-hint">
            💡 Al enviar, el sistema notificará por correo institucional a todos los destinatarios con el enlace oficial.
          </span>
        </div>
        <div class="gform-footer-btns">
          <button class="gform-btn-cancel" @click="cerrar">
            Cerrar Vista Previa
          </button>
          <button
            class="gform-btn-submit"
            @click="enviarAprobacion"
            :disabled="enviando"
          >
            <span v-if="enviando">⏳ Despachando...</span>
            <span v-else>🚀 Enviar Formulario a Destinatarios</span>
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useChatStore } from '../stores/chat';

const chatStore = useChatStore();
const enviando = ref(false);
const respuestas = ref({});

const formInfo = computed(() => {
  return chatStore.googleFormData || chatStore.pendingApproval?.preview || {};
});

const preguntasList = computed(() => {
  const q = formInfo.value.preguntas;
  if (Array.isArray(q) && q.length > 0) return q;
  return [
    {
      id: 'p1',
      tipo: 'opcion_multiple',
      pregunta: '¿Cuál es el plazo legal según el D.S. 016-2024-JUS para notificar una brecha de seguridad a la Autoridad de Protección de Datos?',
      opciones: ['24 horas', '48 horas', '72 horas', '5 días hábiles'],
      control_iso: 'A.3.11'
    },
    {
      id: 'p2',
      tipo: 'opcion_multiple',
      pregunta: 'Bajo la norma ISO/IEC 27701:2025 y la Ley 29733, ¿qué derechos comprende la sigla ARCO?',
      opciones: [
        'Acceso, Rectificación, Cancelación y Oposición',
        'Autorización, Registro, Control y Operación',
        'Almacenamiento, Respaldo, Cifrado y Organización'
      ],
      control_iso: 'A.3.17'
    },
    {
      id: 'p3',
      tipo: 'escala',
      pregunta: '¿Qué tan capacitado se siente para detectar ataques de phishing dirigidos a su correo institucional @unsa.edu.pe?',
      escala_min: '1: Muy vulnerable',
      escala_max: '5: Totalmente capacitado',
      control_iso: 'A.3.17'
    }
  ];
});

function cerrar() {
  chatStore.closeGoogleFormModal();
}

async function enviarAprobacion() {
  enviando.value = true;
  try {
    if (chatStore.pendingApproval) {
      // Confirma la acción Human-in-the-Loop pendiente
      await chatStore.respondApproval(true);
    }
    cerrar();
  } catch (err) {
    alert(`Error al despachar el formulario: ${err.message}`);
  } finally {
    enviando.value = false;
  }
}
</script>
