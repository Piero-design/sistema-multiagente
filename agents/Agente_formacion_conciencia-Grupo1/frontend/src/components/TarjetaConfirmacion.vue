<template>
  <div class="confirmation-card" v-if="action">
    <div class="confirmation-header">
      <span>⚠️</span>
      <span>Aprobación Requerida para Acción del Sistema (Human-in-the-Loop)</span>
    </div>

    <div class="confirmation-preview">
      <div class="preview-field">
        <strong>Tipo de Acción:</strong> {{ formatTipo(action.tipo) }}
      </div>

      <!-- CASO GOOGLE FORMS -->
      <div v-if="action.tipo === 'formulario_capacitacion'" class="preview-form-box">
        <div class="form-preview-header">
          <span class="form-preview-badge">📝 Google Forms · PIMS UNSA</span>
          <button class="btn-open-form-modal" type="button" @click="chatStore.openGoogleFormModal(action.preview)">
            👁️ Ver Formulario Tipo Google Forms
          </button>
        </div>
        <div class="preview-field" style="margin-top: 8px;">
          <strong>Título del Formulario:</strong> {{ action.preview?.titulo }}
        </div>
        <div class="preview-field">
          <strong>Preguntas Configuradas:</strong> {{ action.preview?.preguntas_count || 3 }} reactivos (Opción múltiple y escala)
        </div>
        <div class="preview-field">
          <strong>Destinatarios Convocados ({{ action.preview?.total || 0 }}):</strong>
          <span>{{ formatDestinatarios(action.preview?.destinatarios) }}</span>
        </div>
      </div>

      <!-- CASO CALENDARIO / RECORDATORIO -->
      <div v-else-if="action.tipo === 'agendar_calendario'" class="preview-calendar-box">
        <div class="calendar-preview-header">
          <span class="cal-preview-badge">📅 Google Calendar · Recordatorio</span>
          <a :href="action.preview?.enlace_reunion" target="_blank" class="cal-meet-link">
            📹 Enlace Google Meet
          </a>
        </div>
        <div class="preview-field" style="margin-top: 8px;">
          <strong>Evento:</strong> {{ action.preview?.titulo }}
        </div>
        <div class="preview-field">
          <strong>Fecha y Hora:</strong> {{ formatFecha(action.preview?.fecha_inicio) }} ({{ action.preview?.duracion || '60 min' }})
        </div>
        <div class="preview-field">
          <strong>Ubicación:</strong> {{ action.preview?.ubicacion }}
        </div>
        <div class="preview-field">
          <strong>Recordatorio Automático:</strong> 🔔 {{ action.preview?.recordatorio || '15 minutos antes' }}
        </div>
        <div class="preview-field">
          <strong>Asistentes Convocados ({{ action.preview?.total || 0 }}):</strong>
          <span>{{ formatDestinatarios(action.preview?.asistentes) }}</span>
        </div>
      </div>

      <!-- CASO GENERAL CORREO / MATRÍCULA -->
      <template v-else>
        <div class="preview-field" v-if="action.preview?.total">
          <strong>Destinatarios ({{ action.preview.total }}):</strong>
          <span>{{ formatDestinatarios(action.preview.destinatarios) }}</span>
        </div>

        <div class="preview-field" v-if="action.preview?.asunto">
          <strong>Asunto:</strong> {{ action.preview.asunto }}
        </div>

        <div class="preview-field" v-if="action.preview?.cuerpo">
          <strong>Cuerpo del Mensaje:</strong>
          <p style="white-space: pre-line; margin-top: 4px; color: #4b5563;">{{ action.preview.cuerpo }}</p>
        </div>

        <div class="preview-field" v-if="action.preview?.curso">
          <strong>Curso / Formación:</strong> {{ action.preview.curso }}
        </div>

        <div class="preview-field" v-if="action.preview?.accion">
          <strong>Operación:</strong> {{ action.preview.accion }}
        </div>
      </template>
    </div>

    <div class="confirmation-actions">
      <button class="btn-cancel" :disabled="loading" @click="$emit('cancel')">
        ✕ Cancelar
      </button>
      <button class="btn-confirm" :disabled="loading" @click="$emit('confirm')">
        ✓ Confirmar y Ejecutar
      </button>
    </div>
  </div>
</template>

<script setup>
import { useChatStore } from '../stores/chat';

const chatStore = useChatStore();

defineProps({
  action: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['confirm', 'cancel']);

function formatTipo(tipo) {
  if (tipo === 'correo_masivo') return 'Envío Masivo de Correos Institucionales';
  if (tipo === 'inscripcion_masiva') return 'Matrícula Masiva en LMS Moodle UNSA';
  if (tipo === 'formulario_capacitacion') return 'Envío de Formulario Tipo Google Forms (Evaluación ISO 27701)';
  if (tipo === 'agendar_calendario') return 'Programación de Recordatorio en Google Calendar';
  return tipo || 'Acción de Escritura';
}

function formatDestinatarios(dests) {
  if (!dests) return 'Ninguno';
  if (Array.isArray(dests)) {
    return dests.slice(0, 5).join(', ') + (dests.length > 5 ? ` y ${dests.length - 5} más...` : '');
  }
  return String(dests);
}

function formatFecha(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('es-PE', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return isoStr;
  }
}
</script>
