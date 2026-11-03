<template>
  <aside class="status-panel">
    <div class="panel-header">
      <h3>Panel de Cumplimiento</h3>
      <p>ISO 27701:2025 & Ley 29733</p>
    </div>

    <!-- Mi Cumplimiento -->
    <div class="metric-card">
      <div class="metric-title">Mi Cumplimiento de Formación</div>
      <div class="metric-value-box">
        <span class="metric-number">{{ data?.cumplimiento_pct ?? 100 }}%</span>
      </div>
      <div class="progress-bar-container">
        <div
          class="progress-bar-fill"
          :style="{ width: `${data?.cumplimiento_pct ?? 100}%` }"
        ></div>
      </div>
    </div>

    <!-- Resumen de Estados -->
    <div class="status-list">
      <div class="status-item">
        <span>Formaciones Pendientes:</span>
        <span class="badge-count badge-pending">{{ data?.formaciones_pendientes ?? 0 }}</span>
      </div>

      <div class="status-item">
        <span>Formaciones Vencidas:</span>
        <span class="badge-count badge-expired">{{ data?.formaciones_vencidas ?? 0 }}</span>
      </div>

      <div class="status-item">
        <span>NDAs Pendientes de Firma:</span>
        <span class="badge-count badge-pending">{{ data?.ndas_pendientes ?? 0 }}</span>
      </div>

      <div class="status-item">
        <span>Certificados Vigentes:</span>
        <span class="badge-count badge-completed">{{ data?.certificados_vigentes ?? 0 }}</span>
      </div>
    </div>

    <!-- Métricas Especiales de Administrador -->
    <div class="admin-section" v-if="data?.admin_metrics && Object.keys(data.admin_metrics).length > 0">
      <h4>Métricas Globales (Admin)</h4>
      <div class="status-list">
        <div class="status-item">
          <span>Total Usuarios UNSA:</span>
          <span class="badge-count badge-completed">{{ data.admin_metrics.total_usuarios }}</span>
        </div>
        <div class="status-item">
          <span>Correos Enviados Hoy:</span>
          <span class="badge-count badge-pending">{{ data.admin_metrics.correos_enviados_hoy }}</span>
        </div>
        <div class="status-item">
          <span>Cursos Activos PIMS:</span>
          <span class="badge-count badge-completed">{{ data.admin_metrics.formaciones_activas }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
});
</script>
