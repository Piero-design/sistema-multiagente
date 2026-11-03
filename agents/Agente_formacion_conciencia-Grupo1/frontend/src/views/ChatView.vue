<template>
  <div class="chat-layout">
    <!-- Barra Lateral Izquierda -->
    <Sidebar />

    <!-- Área Principal de Chat -->
    <main class="chat-main">
      <header class="chat-header">
        <div class="header-top-row">
          <div class="header-title-box">
            <h2>Agente de Formación y Conciencia</h2>
          </div>
          <div class="header-badges">
            <span class="badge-pims">ISO 27701 (Control A.3.17)</span>
            <span class="badge-tag">Ley 29733</span>
            <span class="badge-tag">{{ authStore.user?.facultad || 'UNSA' }}</span>
          </div>
        </div>

        <!-- Barra de Navegación Superior -->
        <nav class="app-navbar" aria-label="Navegación del Sistema">
          <button
            class="nav-tab-btn"
            :class="{ active: chatStore.activeTab === 'chat' }"
            @click="chatStore.setActiveTab('chat')"
          >
            💬 Copiloto
          </button>
          <button
            class="nav-tab-btn"
            :class="{ active: chatStore.activeTab === 'brechas' }"
            @click="chatStore.setActiveTab('brechas')"
          >
            📊 Matriz de Brechas (Skill Gap)
          </button>
          <button
            class="nav-tab-btn"
            :class="{ active: chatStore.activeTab === 'heatmap' }"
            @click="chatStore.setActiveTab('heatmap')"
          >
            🔥 Mapa de Calor de Riesgos PII
          </button>
          <button
            class="nav-tab-btn"
            :class="{ active: chatStore.activeTab === 'radar' }"
            @click="chatStore.setActiveTab('radar')"
          >
            🕸️ Radar de Cobertura
          </button>
        </nav>
      </header>

      <!-- VISTA 1: CHAT PRINCIPAL -->
      <section v-show="chatStore.activeTab === 'chat'" class="tab-content-section chat-section">
        <!-- Contenedor de Mensajes con Scroll -->
        <div class="chat-messages" ref="messagesContainer">
          <ChatMessage
            v-for="msg in chatStore.mensajes"
            :key="msg.id"
            :message="msg"
          />

          <!-- Tarjeta de Confirmación de Acción (Human-in-the-Loop) -->
          <TarjetaConfirmacion
            v-if="chatStore.pendingApproval"
            :action="chatStore.pendingApproval"
            :loading="chatStore.isStreaming"
            @confirm="handleConfirmApproval"
            @cancel="handleCancelApproval"
          />

          <!-- Indicador de tipeo / streaming -->
          <div v-if="chatStore.isStreaming" class="typing-indicator">
            <span>🛡️ Agente formulando respuesta</span>
            <span class="typing-dots">...</span>
          </div>
        </div>

        <!-- Barra de Sugerencias y Acciones Rápidas -->
        <div class="quick-actions-bar" v-if="!chatStore.isStreaming">
          <button
            v-for="accion in sugerenciasAcciones"
            :key="accion"
            class="quick-action-btn"
            @click="ejecutarSugerencia(accion)"
          >
            💡 {{ accion }}
          </button>
        </div>

        <!-- Barra Inferior de Entrada de Mensaje -->
        <footer class="chat-input-area">
          <form class="input-container" @submit.prevent="handleSendMessage">
            <textarea
              v-model="inputMessage"
              class="chat-textarea"
              placeholder="Consulta sobre cursos de privacidad, capacitaciones, Ley 29733 o solicita una acción formativa..."
              rows="1"
              :disabled="chatStore.isStreaming"
              @keydown.enter.exact.prevent="handleSendMessage"
              @input="autoResize"
              ref="textareaRef"
            ></textarea>
            <button
              type="submit"
              class="btn-send"
              :disabled="chatStore.isStreaming || !inputMessage.trim()"
              title="Enviar mensaje"
            >
              ➤
            </button>
          </form>
        </footer>
      </section>

      <!-- VISTA 2: MATRIZ DE BRECHAS DE COMPETENCIA (SKILL GAP ANALYSIS ISO 27701) -->
      <section v-show="chatStore.activeTab === 'brechas'" class="tab-content-section analytics-section">
        <div class="analytics-header">
          <div class="analytics-title-group">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <span class="analytics-badge">Control A.3.17 & Cláusula 7.2 ISO/IEC 27701:2025</span>
              <span class="analytics-badge" style="background-color: #f1f5f9; color: #334155;">Ley N° 29733 Art. 38</span>
            </div>
            <h3>Matriz de Brechas de Competencia por Rol (Skill Gap Analysis)</h3>
            <p class="analytics-subtitle">
              Evaluación cuantitativa y cualitativa de suficiencia competencial en protección de datos personales y PII,
              contrastando requisitos normativos frente al estado demostrable de la comunidad universitaria.
            </p>
          </div>
        </div>

        <!-- 1. KPIs EJECUTIVOS DE LA MATRIZ -->
        <div class="brechas-kpi-grid">
          <div class="brechas-kpi-card">
            <span class="brechas-kpi-label">Roles Auditados</span>
            <span class="brechas-kpi-value">{{ chatStore.matrizBrechas?.kpis?.total_roles_evaluados || 4 }} Estamentos</span>
            <span class="brechas-kpi-hint">{{ chatStore.matrizBrechas?.kpis?.total_usuarios_evaluados || 16 }} usuarios evaluados</span>
          </div>

          <div class="brechas-kpi-card" :class="kpiGapClass">
            <span class="brechas-kpi-label">Brecha Promedio (Skill Gap)</span>
            <span class="brechas-kpi-value">{{ chatStore.matrizBrechas?.kpis?.gap_promedio_pct ?? '--' }}%</span>
            <span class="brechas-kpi-hint">
              Meta institucional: &lt; 15% (Suficiencia &gt; 85%)
            </span>
          </div>

          <div class="brechas-kpi-card" :class="kpiCumplimientoClass">
            <span class="brechas-kpi-label">Cumplimiento Global PIMS</span>
            <span class="brechas-kpi-value">{{ chatStore.matrizBrechas?.kpis?.cumplimiento_global_pct ?? '--' }}%</span>
            <span class="brechas-kpi-hint">Exigencias: {{ chatStore.matrizBrechas?.kpis?.total_exigencias_formativas || 58 }} cursos-persona</span>
          </div>

          <div class="brechas-kpi-card critical-kpi">
            <span class="brechas-kpi-label">Gaps Críticos</span>
            <span class="brechas-kpi-value" style="color: #dc2626;">{{ chatStore.matrizBrechas?.kpis?.brechas_criticas_conteo ?? 0 }} Roles</span>
            <span class="brechas-kpi-hint">{{ chatStore.matrizBrechas?.kpis?.total_cursos_vencidos || 0 }} cursos vencidos</span>
          </div>
        </div>

        <!-- 2. TARJETA DE DICTAMEN OFICIAL DEL COPILOTO IA (AGENTE #8) -->
        <div class="brechas-dictamen-card">
          <div class="dictamen-header">
            <div class="dictamen-title-wrap">
              <span class="dictamen-icon">🛡️</span>
              <div>
                <h4>Dictamen del Copiloto PIMS UNSA (Agente #8)</h4>
                <div class="dictamen-meta">
                  <span class="dictamen-code" v-if="chatStore.matrizBrechas?.evidencia_documentada_id">
                    ID Evidencia: {{ chatStore.matrizBrechas.evidencia_documentada_id }}
                  </span>
                  <span class="dictamen-date" v-if="chatStore.matrizBrechas?.fecha_diagnostico">
                    Auditado: {{ formatFecha(chatStore.matrizBrechas.fecha_diagnostico) }}
                  </span>
                  <span
                    class="severity-pill"
                    :class="'severity-' + (chatStore.matrizBrechas?.diagnostico_ia?.nivel_exposicion_riesgo?.toLowerCase() || 'critico')"
                  >
                    Exposición: {{ chatStore.matrizBrechas?.diagnostico_ia?.nivel_exposicion_riesgo || 'ALTO' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="dictamen-btn-group">
              <button
                class="btn-ia-refresh"
                :disabled="chatStore.iaDiagnosing"
                @click="forzarDiagnosticoIA"
                title="Ejecuta una nueva evaluación en vivo con el LLM y guarda evidencia documental"
              >
                <span v-if="chatStore.iaDiagnosing" class="spin-icon">⏳</span>
                <span v-else>✨</span>
                {{ chatStore.iaDiagnosing ? 'Generando Dictamen IA...' : 'Actualizar Diagnóstico con IA' }}
              </button>
              <button
                class="btn-copiloto-chat"
                @click="consultarCopilotoPor('Analiza en detalle las brechas de competencia identificadas y sugiere la estrategia de mitigación inmediata.')"
              >
                💬 Debatir en Chat
              </button>
            </div>
          </div>

          <div class="dictamen-body">
            <p class="dictamen-lead">
              {{ chatStore.matrizBrechas?.diagnostico_ia?.dictamen_ejecutivo || 'Cargando dictamen institucional del Oficial de Protección de Datos...' }}
            </p>

            <div v-if="chatStore.matrizBrechas?.diagnostico_ia?.hallazgos_clave?.length" class="hallazgos-box">
              <h5 class="hallazgos-title">🚨 Hallazgos Críticos de Cumplimiento (Cláusula 7.2)</h5>
              <ul class="hallazgos-list">
                <li v-for="(hallazgo, hIdx) in chatStore.matrizBrechas.diagnostico_ia.hallazgos_clave" :key="hIdx">
                  {{ hallazgo }}
                </li>
              </ul>
            </div>

            <div v-if="chatStore.matrizBrechas?.diagnostico_ia?.plan_cierre_brechas?.length" class="dictamen-plan-box">
              <h5 class="plan-title">📋 Plan de Cierre de Brechas (Medidas Correctivas Cláusula 7.2)</h5>
              <div class="plan-grid">
                <div
                  v-for="(item, pIdx) in chatStore.matrizBrechas.diagnostico_ia.plan_cierre_brechas"
                  :key="pIdx"
                  class="plan-item-card"
                >
                  <div class="plan-item-top">
                    <span class="plan-step-num">Paso {{ item.paso || (pIdx + 1) }}</span>
                    <span class="plan-priority-badge" :class="'priority-' + (item.prioridad?.toLowerCase() || 'alta')">
                      {{ item.prioridad }}
                    </span>
                  </div>
                  <div class="plan-action-text">{{ item.accion }}</div>
                  <div class="plan-meta-row">
                    <span><strong>Objetivo:</strong> {{ item.estamento_objetivo }}</span>
                    <span><strong>Control:</strong> {{ item.control_iso }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="dictamen-footer">
            <span class="dictamen-norma-quote">
              "Appropriate documented information shall be available as evidence of competence." — ISO/IEC 27701:2025 Cláusula 7.2
            </span>
          </div>
        </div>

        <!-- 3. FILTROS POR ESTAMENTO Y TABLA MATRICIAL -->
        <div class="brechas-card">
          <div class="brechas-card-header">
            <div class="brechas-card-title-group">
              <h4>Mapeo de Competencias vs. Requisitos por Estamento</h4>
              <p>Contraste detallado de cursos exigidos, completados y déficit competencial (Skill Gap).</p>
            </div>

            <!-- Filtros de Píldoras -->
            <div class="brechas-pills-list">
              <button
                class="filter-pill"
                :class="{ active: selectedRol === 'todos' }"
                @click="selectedRol = 'todos'"
              >
                Todos los Roles ({{ chatStore.matrizBrechas?.roles?.length || 4 }})
              </button>
              <button
                v-for="r in chatStore.matrizBrechas?.roles || []"
                :key="r.rol"
                class="filter-pill"
                :class="{ active: selectedRol === r.rol }"
                @click="selectedRol = r.rol"
              >
                {{ r.nombre_rol.split(' ')[0] }} ({{ r.gap_pct }}% Gap)
              </button>
            </div>
          </div>

          <div class="brechas-table-wrap">
            <table class="brechas-table">
              <thead>
                <tr>
                  <th style="width: 18%;">Estamento / Rol</th>
                  <th style="width: 14%;">Control ISO / Ley</th>
                  <th style="width: 28%;">Competencia & Curso PIMS</th>
                  <th style="width: 16%;">Cumplimiento Actual</th>
                  <th style="width: 10%;">Brecha (Gap)</th>
                  <th style="width: 8%;">Severidad</th>
                  <th style="width: 6%;">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in competenciasFiltradas" :key="idx">
                  <td>
                    <span class="table-role-badge">{{ item.nombre_rol }}</span>
                    <div style="font-size: 0.72rem; color: #64748b;">{{ item.total_usuarios }} usuarios</div>
                  </td>
                  <td>
                    <span class="table-iso-tag">{{ item.control_iso }}</span>
                    <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">{{ item.clausula_iso }}</div>
                  </td>
                  <td>
                    <div class="table-course-title">
                      <span style="font-family: var(--font-mono); color: #8b1524; font-size: 0.78rem;">[{{ item.formacion_id }}]</span>
                      {{ item.titulo }}
                    </div>
                    <div class="table-course-desc">{{ item.competencia }}</div>
                  </td>
                  <td>
                    <div class="table-progress-wrap">
                      <div class="table-progress-bar">
                        <div
                          class="table-progress-fill"
                          :style="{ width: item.cumplimiento_pct + '%', backgroundColor: item.cumplimiento_pct > 50 ? '#059669' : '#8b1524' }"
                        ></div>
                      </div>
                      <div class="table-progress-text">
                        <span>{{ item.cumplimiento_pct }}%</span>
                        <span>{{ item.completados }}/{{ item.exigidos }}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span
                      class="gap-value-text"
                      :class="item.gap_pct > 40 ? 'gap-critical' : item.gap_pct > 15 ? 'gap-warning' : 'gap-good'"
                    >
                      {{ item.gap_pct }}%
                    </span>
                  </td>
                  <td>
                    <span class="severity-pill" :class="'severity-' + item.severidad">
                      {{ item.severidad }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn-table-action"
                      @click="remediarConCopiloto(item.nombre_rol, item.titulo, item.pendientes + item.sin_asignar + item.vencidos)"
                      title="Solicitar al copiloto plan de nivelación para este curso"
                    >
                      Remediar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 4. SECCIÓN PERSONAL AFECTADO CON BRECHAS -->
        <div class="personal-afectado-section">
          <div class="afectados-header">
            <div>
              <h4>Personal Universitario con Brechas Formativas Detectadas</h4>
              <p style="font-size: 0.8rem; color: #64748b; margin: 2px 0 0 0;">
                Usuarios con cursos obligatorios vencidos o pendientes según los requisitos de ISO 27701.
              </p>
            </div>
            <span class="afectados-count-badge">
              {{ personalAfectadoFiltrado.length }} Usuarios con brecha
            </span>
          </div>

          <div class="afectados-grid">
            <div
              v-for="user in personalAfectadoFiltrado"
              :key="user.user_id"
              class="afectado-card"
            >
              <div class="afectado-top">
                <div>
                  <div class="afectado-nombre">{{ user.nombre }}</div>
                  <div class="afectado-meta">{{ user.email }} • {{ user.facultad || 'UNSA' }}</div>
                </div>
                <span class="table-role-badge">{{ user.rol || 'personal' }}</span>
              </div>

              <div class="afectado-pendientes-list">
                <div
                  v-for="(c, cIdx) in user.cursos_pendientes"
                  :key="cIdx"
                  class="afectado-chip"
                  :class="'chip-' + c.estado"
                >
                  <span><strong>[{{ c.curso_id }}]</strong> {{ c.curso_titulo }}</span>
                  <span style="text-transform: uppercase; font-size: 0.68rem;">{{ c.estado }}</span>
                </div>
              </div>

              <button
                class="btn-notificar-afectado"
                @click="notificarUsuarioIndividual(user.user_id, user.nombre)"
              >
                ✉️ Coordinar Notificación con Copiloto
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- VISTA 3: MAPA DE CALOR DE RIESGOS PII (HEATMAP ISO 27701:2025 CONTROL A.3.17 & A.3.11) -->
      <section v-show="chatStore.activeTab === 'heatmap'" class="tab-content-section analytics-section">
        <div class="analytics-header">
          <div class="analytics-title-group">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <span class="analytics-badge">Control A.3.17 & Control A.3.11 (ISO/IEC 27701:2025)</span>
              <span class="analytics-badge" style="background-color: #ffedd5; color: #c2410c;">Ley N° 29733 Art. 19 (Principio de Seguridad)</span>
            </div>
            <h3>Mapa de Calor (Heatmap): Índice de Sensibilización sobre Riesgos de PII</h3>
            <p class="analytics-subtitle">
              Distribución termográfica de susceptibilidad, nivel de conciencia y puntos de vulnerabilidad en tratamiento de datos personales por dominio temático y facultad.
            </p>
          </div>
        </div>

        <!-- 1. KPIs TÉRMICOS EJECUTIVOS -->
        <div class="heatmap-kpi-grid">
          <div class="heatmap-kpi-card" :class="kpiSensibilizacionClass">
            <span class="heatmap-kpi-label">Índice Global de Sensibilización</span>
            <span class="heatmap-kpi-value">{{ chatStore.heatmapData?.kpis?.indice_global_sensibilizacion ?? '--' }} / 100</span>
            <span class="heatmap-kpi-hint">
              Meta institucional: &gt; 80 pts (Resiliencia PIMS)
            </span>
          </div>

          <div class="heatmap-kpi-card" :class="kpiVulnerabilidadClass">
            <span class="heatmap-kpi-label">Grado de Vulnerabilidad</span>
            <span class="heatmap-kpi-value">{{ chatStore.heatmapData?.kpis?.vulnerabilidad_promedio_pct ?? '--' }}%</span>
            <span class="heatmap-kpi-hint">Temperatura promedio del riesgo institucional</span>
          </div>

          <div class="heatmap-kpi-card termico-critico">
            <span class="heatmap-kpi-label">Zona Térmica Crítica</span>
            <span class="heatmap-kpi-value" style="font-size: 1.15rem; color: #dc2626; line-height: 1.2;">
              {{ chatStore.heatmapData?.kpis?.zona_termica_critica || 'Evaluando...' }}
            </span>
            <span class="heatmap-kpi-hint">Mayor temperatura de susceptibilidad</span>
          </div>

          <div class="heatmap-kpi-card termico-alerta">
            <span class="heatmap-kpi-label">Ejes en Alerta Roja</span>
            <span class="heatmap-kpi-value" style="color: #ea580c;">
              {{ chatStore.heatmapData?.kpis?.ejes_en_alerta_roja ?? 0 }} de 6
            </span>
            <span class="heatmap-kpi-hint">{{ chatStore.heatmapData?.kpis?.facultades_evaluadas || 5 }} unidades académicas auditadas</span>
          </div>
        </div>

        <!-- 2. DICTAMEN TERMOGRÁFICO OFICIAL DEL COPILOTO IA -->
        <div class="brechas-dictamen-card heatmap-dictamen-card">
          <div class="dictamen-header">
            <div class="dictamen-title-wrap">
              <span class="dictamen-icon">🔥</span>
              <div>
                <h4>Dictamen Termográfico del Copiloto PIMS UNSA (Agente #8)</h4>
                <div class="dictamen-meta">
                  <span class="termico-code" v-if="chatStore.heatmapData?.evidencia_documentada_id">
                    ID Evidencia: {{ chatStore.heatmapData.evidencia_documentada_id }}
                  </span>
                  <span class="dictamen-date" v-if="chatStore.heatmapData?.fecha_diagnostico">
                    Termografía: {{ formatFecha(chatStore.heatmapData.fecha_diagnostico) }}
                  </span>
                  <span class="severity-pill severity-critico">
                    Alerta Máxima: Control A.3.11 & Control A.3.17
                  </span>
                </div>
              </div>
            </div>

            <div class="dictamen-btn-group">
              <button
                class="btn-ia-refresh"
                style="background-color: #c2410c;"
                :disabled="chatStore.iaDiagnosingHeatmap"
                @click="forzarDiagnosticoHeatmapIA"
                title="Ejecuta una nueva evaluación termográfica con el LLM"
              >
                <span v-if="chatStore.iaDiagnosingHeatmap" class="spin-icon">⏳</span>
                <span v-else>🔥</span>
                {{ chatStore.iaDiagnosingHeatmap ? 'Computando Termografía IA...' : 'Actualizar Termografía con IA' }}
              </button>
              <button
                class="btn-copiloto-chat"
                style="color: #c2410c; border-color: #fed7aa;"
                @click="consultarCopilotoPor('Analiza el mapa de calor de riesgos de PII y propone el cronograma de mitigación térmica por facultad.')"
              >
                💬 Analizar en Chat
              </button>
            </div>
          </div>

          <div class="dictamen-body">
            <p class="dictamen-lead">
              {{ chatStore.heatmapData?.diagnostico_ia?.diagnostico_termografico || 'Procesando diagnóstico térmico de susceptibilidad institucional...' }}
            </p>

            <div v-if="chatStore.heatmapData?.diagnostico_ia?.foco_critico_principal" class="hallazgos-box" style="border-left: 4px solid #dc2626;">
              <h5 class="hallazgos-title" style="color: #dc2626;">🎯 Foco Térmico Principal de Exposición</h5>
              <p style="font-size: 0.88rem; color: #334155; margin: 0; line-height: 1.5;">
                {{ chatStore.heatmapData.diagnostico_ia.foco_critico_principal }}
              </p>
            </div>

            <div v-if="chatStore.heatmapData?.diagnostico_ia?.medidas_preventivas?.length" class="dictamen-plan-box">
              <h5 class="plan-title">🛡️ Medidas Preventivas de Mitigación Térmica</h5>
              <div class="plan-grid">
                <div
                  v-for="(medida, mIdx) in chatStore.heatmapData.diagnostico_ia.medidas_preventivas"
                  :key="mIdx"
                  class="plan-item-card"
                >
                  <div class="plan-item-top">
                    <span class="plan-step-num">{{ medida.metodo || 'Acción' }}</span>
                    <span class="plan-priority-badge" :class="'priority-' + (medida.prioridad?.toLowerCase() || 'alta')">
                      {{ medida.prioridad }}
                    </span>
                  </div>
                  <div class="plan-action-text">{{ medida.accion }}</div>
                  <div class="plan-meta-row">
                    <span><strong>Eje:</strong> {{ medida.eje_afectado }}</span>
                    <span><strong>Enfoque:</strong> Conciencia Activa</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="chatStore.heatmapData?.diagnostico_ia?.dictamen_anpd" style="margin-top: 10px; font-size: 0.8rem; color: #b45309; background-color: #fffbeb; padding: 10px 14px; border-radius: 6px; border: 1px solid #fde68a;">
              <strong>⚖️ Advertencia Regulatoria ANPD:</strong> {{ chatStore.heatmapData.diagnostico_ia.dictamen_anpd }}
            </div>
          </div>

          <div class="dictamen-footer">
            <span class="dictamen-norma-quote">
              "The organization shall evaluate the effectiveness of the awareness and training actions taken." — ISO/IEC 27701:2025 Cláusula 7.2
            </span>
          </div>
        </div>

        <!-- 3. GRILLA DE LOS 6 EJES DE RIESGO DE PRIVACIDAD -->
        <div>
          <div style="margin-bottom: 14px;">
            <h4 style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0 0 4px 0;">
              Gradiente Térmico en los 6 Ejes Clave de Privacidad
            </h4>
            <p style="font-size: 0.82rem; color: #64748b; margin: 0;">
              Nivel de susceptibilidad calculado a partir de capacitaciones vencidas, pendientes y cobertura demostrable en cada dominio.
            </p>
          </div>

          <div class="heatmap-ejes-grid">
            <div
              v-for="eje in chatStore.heatmapData?.ejes || []"
              :key="eje.id"
              class="eje-card"
              :style="{ borderTop: '4px solid ' + eje.zona_color }"
            >
              <div class="eje-top-bar">
                <div class="eje-identity">
                  <div class="eje-icon-box">{{ eje.icono }}</div>
                  <div class="eje-title-group">
                    <h4>{{ eje.nombre }}</h4>
                    <span>{{ eje.control_iso }} • {{ eje.norma_ref }}</span>
                  </div>
                </div>
                <div class="eje-temp-badge" :class="'temp-badge-' + eje.nivel_termico">
                  {{ eje.temperatura_vulnerabilidad }}°
                </div>
              </div>

              <p class="eje-desc">{{ eje.descripcion }}</p>

              <!-- Termómetro del Eje -->
              <div class="eje-meter-wrap">
                <div class="eje-meter-labels">
                  <span :style="{ color: eje.zona_color }">{{ eje.etiqueta_termica }}</span>
                  <span style="color: #64748b;">Sensibilización: {{ eje.indice_sensibilizacion }}/100</span>
                </div>
                <div class="eje-meter-bar">
                  <div
                    class="eje-meter-fill"
                    :style="{ width: eje.temperatura_vulnerabilidad + '%', backgroundColor: eje.zona_color }"
                  ></div>
                </div>
              </div>

              <div class="eje-stats-row">
                <span><strong>Cursos:</strong> {{ eje.cursos_asociados?.join(', ') }}</span>
                <span><strong>Vencidos:</strong> {{ eje.vencidos }}</span>
                <span><strong>Pendientes:</strong> {{ eje.pendientes }}</span>
              </div>

              <button
                class="eje-action-btn"
                @click="simularCampanaEje(eje.nombre, eje.control_iso)"
              >
                🚀 Iniciar Campaña Preventiva
              </button>
            </div>
          </div>
        </div>

        <!-- 4. MATRIZ BIDIMENSIONAL (EJE TEMÁTICO X FACULTAD) -->
        <div class="matrix-card">
          <div class="matrix-header">
            <div>
              <h4>Distribución Térmica Cruzada (Eje Temático vs. Facultad)</h4>
              <p>Gradiente de calor de vulnerabilidad para cada unidad académica de la UNSA.</p>
            </div>

            <!-- Leyenda Térmica -->
            <div class="heatmap-legend">
              <div class="legend-item">
                <span class="legend-color-box" style="background-color: #dc2626;"></span>
                <span>&gt; 75° Crítico (Rojo)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color-box" style="background-color: #ea580c;"></span>
                <span>50°-74° Alto (Naranja)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color-box" style="background-color: #d97706;"></span>
                <span>25°-49° Moderado (Ámbar)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color-box" style="background-color: #059669;"></span>
                <span>&lt; 25° Resiliente (Verde)</span>
              </div>
            </div>
          </div>

          <div class="matrix-table-wrap">
            <table class="thermal-matrix-table">
              <thead>
                <tr>
                  <th>Facultad / Unidad</th>
                  <th v-for="eje in chatStore.heatmapData?.ejes || []" :key="eje.id">
                    {{ eje.icono }} {{ eje.nombre.split(' ')[0] }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in chatStore.heatmapData?.matriz_bidimensional || []" :key="row.facultad">
                  <td>
                    {{ row.facultad }}
                    <div style="font-size: 0.7rem; color: #64748b; font-weight: normal;">{{ row.usuarios }} usuarios</div>
                  </td>
                  <td
                    v-for="eje in chatStore.heatmapData?.ejes || []"
                    :key="eje.id"
                    class="thermal-cell"
                    :style="{ backgroundColor: row.scores[eje.id]?.color || '#dc2626' }"
                    @click="consultarCopilotoPor('Analiza el riesgo térmico de ' + eje.nombre + ' en la facultad de ' + row.facultad + ' y prepara un plan de nivelación.')"
                    :title="'Click para analizar con el copiloto: ' + eje.nombre + ' en ' + row.facultad"
                  >
                    {{ row.scores[eje.id]?.vulnerabilidad ?? 95 }}°
                    <span class="thermal-cell-sub">
                      {{ row.scores[eje.id]?.vencidos ? '🚨 ' + row.scores[eje.id].vencidos + ' vencido' : row.scores[eje.id]?.nivel }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- VISTA 4: RADAR DE COBERTURA MULTIAXIAL POR ESTAMENTO (CONTROL A.3.17 & CLÁUSULA 7.2 ISO 27701) -->
      <section v-show="chatStore.activeTab === 'radar'" class="tab-content-section analytics-section">
        <div class="analytics-header">
          <div class="analytics-title-group">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <span class="analytics-badge">Control A.3.17 & Cláusula 7.2 ISO/IEC 27701:2025</span>
              <span class="analytics-badge" style="background-color: #ede9fe; color: #6d28d9;">Cláusula 7.2 (Competencia y Eficacia)</span>
              <span class="analytics-badge" style="background-color: #ffedd5; color: #c2410c;">Ley N° 29733 Art. 19</span>
            </div>
            <h3>Gráfico de Radar: Cobertura Multiaxial de Capacitación por Estamento Universitario</h3>
            <p class="analytics-subtitle">
              Evaluación geométrica y multidimensional de alcance formativo, masa crítica y eficacia del programa anual PIMS en la comunidad universitaria de la UNSA.
            </p>
          </div>
        </div>

        <!-- 1. KPIs EJECUTIVOS DE COBERTURA -->
        <div class="heatmap-kpi-grid">
          <div class="heatmap-kpi-card" :class="kpiCoberturaClass">
            <span class="heatmap-kpi-label">Cobertura Institucional Ponderada</span>
            <span class="heatmap-kpi-value">{{ chatStore.radarData?.kpis?.cobertura_global_pct ?? '--' }}%</span>
            <span class="heatmap-kpi-hint">
              Meta institucional: &gt; 90% (Certificación ISO)
            </span>
          </div>

          <div class="heatmap-kpi-card" :class="kpiEficaciaClass">
            <span class="heatmap-kpi-label">Eficacia Formativa Global</span>
            <span class="heatmap-kpi-value">{{ chatStore.radarData?.kpis?.eficacia_global_pct ?? '--' }}%</span>
            <span class="heatmap-kpi-hint">Tasa de aprobación efectiva con nota &ge; 14</span>
          </div>

          <div class="heatmap-kpi-card termico-optimo">
            <span class="heatmap-kpi-label">Estamento Líder de Cumplimiento</span>
            <span class="heatmap-kpi-value" style="font-size: 1.15rem; color: #059669; line-height: 1.2;">
              {{ chatStore.radarData?.kpis?.estamento_lider || 'Evaluando...' }}
            </span>
            <span class="heatmap-kpi-hint">Mayor índice de cobertura y aprobación</span>
          </div>

          <div class="heatmap-kpi-card termico-critico">
            <span class="heatmap-kpi-label">Estamento Rezagado / Brecha Crítica</span>
            <span class="heatmap-kpi-value" style="font-size: 1.15rem; color: #dc2626; line-height: 1.2;">
              {{ chatStore.radarData?.kpis?.estamento_rezagado || 'Evaluando...' }}
            </span>
            <span class="heatmap-kpi-hint">Mayor vulnerabilidad operativa por falta de inducción</span>
          </div>
        </div>

        <!-- 2. DICTAMEN OFICIAL DEL COPILOTO IA -->
        <div class="brechas-dictamen-card radar-dictamen-card">
          <div class="dictamen-header">
            <div class="dictamen-title-wrap">
              <span class="dictamen-icon">🕸️</span>
              <div>
                <h4>Dictamen de Cobertura Multiaxial del Copiloto PIMS UNSA (Agente #8)</h4>
                <div class="dictamen-meta">
                  <span class="termico-code" v-if="chatStore.radarData?.evidencia_documentada_id">
                    ID Evidencia: {{ chatStore.radarData.evidencia_documentada_id }}
                  </span>
                  <span class="dictamen-date" v-if="chatStore.radarData?.fecha_diagnostico">
                    Auditoría: {{ formatFecha(chatStore.radarData.fecha_diagnostico) }}
                  </span>
                  <span class="severity-pill severity-alta">
                    Alcance: Control A.3.17 & Cláusula 7.2 (Competencia)
                  </span>
                </div>
              </div>
            </div>

            <div class="dictamen-btn-group">
              <button
                class="btn-ia-refresh"
                style="background-color: #6d28d9;"
                :disabled="chatStore.iaDiagnosingRadar"
                @click="forzarDiagnosticoRadarIA"
                title="Ejecuta una nueva evaluación multiaxial con el LLM"
              >
                <span v-if="chatStore.iaDiagnosingRadar" class="spin-icon">⏳</span>
                <span v-else>🕸️</span>
                {{ chatStore.iaDiagnosingRadar ? 'Computando Radar IA...' : 'Actualizar Radar con IA' }}
              </button>
              <button
                class="btn-copiloto-chat"
                style="color: #6d28d9; border-color: #ddd6fe;"
                @click="consultarCopilotoPor('Analiza el gráfico de radar de cobertura y propone una estrategia para nivelar los estamentos rezagados.')"
              >
                💬 Analizar en Chat
              </button>
            </div>
          </div>

          <div class="dictamen-body">
            <p class="dictamen-lead">
              {{ chatStore.radarData?.diagnostico_ia?.diagnostico_cobertura || 'Procesando diagnóstico multiaxial de cobertura estamental con IA...' }}
            </p>

            <div v-if="chatStore.radarData?.diagnostico_ia?.estamento_critico_prioritario" class="hallazgos-box" style="border-left: 4px solid #dc2626;">
              <h5 class="hallazgos-title" style="color: #dc2626;">🎯 Estamento Crítico Prioritario para Intervención</h5>
              <p style="font-size: 0.88rem; color: #334155; margin: 0; line-height: 1.5;">
                {{ chatStore.radarData.diagnostico_ia.estamento_critico_prioritario }}
              </p>
            </div>

            <!-- Plan de nivelación estamental -->
            <div v-if="chatStore.radarData?.diagnostico_ia?.plan_nivelacion_estamental?.length" class="dictamen-plan-box">
              <h5 class="plan-title">📋 Plan de Nivelación Estamental Recomendado</h5>
              <div class="plan-grid">
                <div
                  v-for="(plan, pIdx) in chatStore.radarData.diagnostico_ia.plan_nivelacion_estamental"
                  :key="pIdx"
                  class="plan-item-card"
                >
                  <div class="plan-item-top">
                    <span class="plan-step-num">{{ plan.estamento }}</span>
                    <span class="plan-priority-badge" :class="'priority-' + (plan.prioridad?.toLowerCase() || 'alta')">
                      {{ plan.prioridad }}
                    </span>
                  </div>
                  <div class="plan-action-text">{{ plan.accion }}</div>
                  <div class="plan-meta-row">
                    <span class="plan-meta-pill">⏱️ Plazo: {{ plan.plazo_dias }} días</span>
                    <span class="plan-meta-pill" style="background-color: #f3e8ff; color: #7e22ce;">
                      📡 Canal: {{ plan.canal || 'LMS UNSA' }}
                    </span>
                  </div>
                  <div style="margin-top: 8px; display: flex; gap: 6px;">
                    <button
                      class="cell-action-btn"
                      style="font-size: 0.72rem; padding: 4px 8px;"
                      @click="consultarCopilotoPor(`Prepara una campaña inmediata para el estamento de ${plan.estamento}: ${plan.accion}`)"
                    >
                      🚀 Ejecutar Plan
                    </button>
                    <button
                      class="cell-action-btn"
                      style="font-size: 0.72rem; padding: 4px 8px; background-color: #673ab7; color: #fff;"
                      @click="abrirGoogleFormParaEstamento(plan.estamento)"
                    >
                      📝 Google Form
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Conclusiones de auditoría -->
            <div v-if="chatStore.radarData?.diagnostico_ia?.conclusiones_auditoria?.length" class="hallazgos-box" style="margin-top: 14px; border-left: 4px solid #6d28d9;">
              <h5 class="hallazgos-title" style="color: #6d28d9;">⚖️ Conclusiones de Auditoría Normativa PIMS</h5>
              <ul style="margin: 6px 0 0 16px; padding: 0; font-size: 0.86rem; color: #475569; line-height: 1.5;">
                <li v-for="(c, cIdx) in chatStore.radarData.diagnostico_ia.conclusiones_auditoria" :key="cIdx">
                  {{ c }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 3. GRÁFICO DE RADAR SVG INTERACTIVO Y PANEL DE CONTROL -->
        <div class="radar-main-layout">
          <!-- Gráfico SVG del Radar -->
          <div class="radar-chart-container">
            <div class="radar-chart-header">
              <h4>Polígono Multiaxial de Cobertura Institucional</h4>
              <span class="radar-subtext">5 Estamentos Auditados vs Meta Institucional (90%)</span>
            </div>

            <div class="radar-svg-wrapper">
              <svg viewBox="0 0 300 300" class="radar-svg" aria-label="Gráfico de Radar de Cobertura">
                <defs>
                  <linearGradient id="radarAreaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.55" />
                    <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.30" />
                  </linearGradient>
                </defs>

                <!-- Círculos concéntricos de referencia (20%, 40%, 60%, 80%, 100%) -->
                <circle
                  v-for="anillo in [22, 44, 66, 88, 110]"
                  :key="anillo"
                  cx="150"
                  cy="150"
                  :r="anillo"
                  class="radar-grid-ring"
                />

                <!-- Etiquetas de porcentaje en los anillos -->
                <text x="153" y="129" class="radar-ring-label">20%</text>
                <text x="153" y="107" class="radar-ring-label">40%</text>
                <text x="153" y="85" class="radar-ring-label">60%</text>
                <text x="153" y="63" class="radar-ring-label">80%</text>
                <text x="153" y="41" class="radar-ring-label">100%</text>

                <!-- Rayos radiales a cada vértice -->
                <line
                  v-for="(vert, idx) in radarVertices"
                  :key="'line_' + idx"
                  x1="150"
                  y1="150"
                  :x2="vert.x_label"
                  :y2="vert.y_label"
                  class="radar-axis-line"
                />

                <!-- Polígono de Meta Institucional (90% - Línea dorada punteada) -->
                <polygon
                  v-if="puntosPoligonoMeta"
                  :points="puntosPoligonoMeta"
                  class="radar-meta-polygon"
                />

                <!-- Polígono de Cobertura Actual Real -->
                <polygon
                  v-if="puntosPoligonoReal"
                  :points="puntosPoligonoReal"
                  class="radar-real-polygon"
                  fill="url(#radarAreaGradient)"
                />

                <!-- Vértices interactivos reales con tooltip hover -->
                <g v-for="(vert, idx) in radarVertices" :key="'dot_' + idx">
                  <circle
                    :cx="vert.x_real"
                    :cy="vert.y_real"
                    r="5"
                    class="radar-vertex-dot"
                    @mouseenter="hoveredVertex = vert"
                    @mouseleave="hoveredVertex = null"
                  />
                  <!-- Etiqueta externa del estamento -->
                  <text
                    :x="vert.x_label"
                    :y="vert.y_label"
                    class="radar-vertex-label"
                    :text-anchor="vert.x_label > 155 ? 'start' : vert.x_label < 145 ? 'end' : 'middle'"
                  >
                    {{ vert.icono }} {{ vert.estamento.split(' ')[0] }} ({{ vert.valor }}%)
                  </text>
                </g>
              </svg>

              <!-- Tooltip flotante de vértice activo -->
              <div v-if="hoveredVertex" class="radar-tooltip">
                <div class="tooltip-title">{{ hoveredVertex.icono }} {{ hoveredVertex.estamento }}</div>
                <div class="tooltip-row">
                  <span>Cobertura Real:</span>
                  <strong>{{ hoveredVertex.valor }}%</strong>
                </div>
                <div class="tooltip-row">
                  <span>Meta Institucional:</span>
                  <span>{{ hoveredVertex.meta }}%</span>
                </div>
                <div class="tooltip-row">
                  <span>Brecha:</span>
                  <span style="color: #dc2626;">{{ Math.max(0, hoveredVertex.meta - hoveredVertex.valor).toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <!-- Leyenda del Gráfico de Radar -->
            <div class="radar-legend-bar">
              <div class="radar-legend-item">
                <span class="legend-color-box real-box"></span>
                <span>Cobertura Actual Auditada (Polígono Real)</span>
              </div>
              <div class="radar-legend-item">
                <span class="legend-color-box meta-box"></span>
                <span>Meta Institucional UNSA 90% (Control A.3.17 & Cláusula 7.2)</span>
              </div>
            </div>
          </div>

          <!-- Comparativa de Facultades -->
          <div class="radar-facultades-panel">
            <div class="panel-header-row">
              <h4>Alcance Formativo por Facultad</h4>
              <span class="panel-badge">5 Sedes Académicas</span>
            </div>

            <div class="facultades-progress-list">
              <div
                v-for="(fac, fIdx) in (chatStore.radarData?.facultades || [])"
                :key="fIdx"
                class="facultad-progress-card"
              >
                <div class="fac-card-top">
                  <span class="fac-name">{{ fac.facultad }}</span>
                  <span class="fac-pct" :class="fac.cobertura_pct >= 80 ? 'text-optimo' : fac.cobertura_pct >= 40 ? 'text-alerta' : 'text-critico'">
                    {{ fac.cobertura_pct }}%
                  </span>
                </div>
                <div class="fac-bar-track">
                  <div
                    class="fac-bar-fill"
                    :style="{ width: Math.min(100, fac.cobertura_pct) + '%' }"
                    :class="fac.cobertura_pct >= 80 ? 'fill-optimo' : fac.cobertura_pct >= 40 ? 'fill-alerta' : 'fill-critico'"
                  ></div>
                </div>
                <div class="fac-card-bottom">
                  <span>Padrón: {{ fac.padron_total }} pers. · Inscritos: {{ fac.inscritos }}</span>
                  <button
                    class="btn-fac-action"
                    @click="consultarCopilotoPor(`Prepara una convocatoria formativa urgente para la Facultad de ${fac.facultad}`)"
                  >
                    Convocatoria ✉️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. TABLA DESGLOSADA POR ESTAMENTO UNIVERSITARIO -->
        <div class="brechas-table-card" style="margin-top: 24px;">
          <div class="brechas-table-header">
            <div>
              <h4>Padrón y Métricas Multiaxiales por Estamento Universitario</h4>
              <p class="brechas-table-subtitle">
                Supervisión cuantitativa de matrícula, aprobación efectiva y brecha respecto a la meta institucional.
              </p>
            </div>
          </div>

          <div class="table-responsive">
            <table class="brechas-table">
              <thead>
                <tr>
                  <th>Estamento</th>
                  <th style="text-align: center;">Padrón</th>
                  <th style="text-align: center;">Inscritos</th>
                  <th style="text-align: center;">Aprobados</th>
                  <th style="text-align: center;">% Cobertura</th>
                  <th style="text-align: center;">% Eficacia</th>
                  <th style="text-align: center;">Brecha vs Meta</th>
                  <th>Estado Radar</th>
                  <th>Acciones Preventivas</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(em, eIdx) in (chatStore.radarData?.estamentos || [])"
                  :key="eIdx"
                >
                  <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span style="font-size: 1.3rem;">{{ em.icono }}</span>
                      <div>
                        <strong>{{ em.nombre }}</strong>
                        <div style="font-size: 0.76rem; color: #64748b;">
                          {{ em.descripcion }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td style="text-align: center; font-weight: 600;">
                    {{ em.padron_total }}
                  </td>
                  <td style="text-align: center;">
                    {{ em.inscritos }}
                  </td>
                  <td style="text-align: center; color: #059669; font-weight: 600;">
                    {{ em.completados }}
                  </td>
                  <td style="text-align: center;">
                    <span class="severity-pill" :class="'severity-' + em.severidad">
                      {{ em.cobertura_pct }}%
                    </span>
                  </td>
                  <td style="text-align: center; font-weight: 600;">
                    {{ em.eficacia_pct }}%
                  </td>
                  <td style="text-align: center; color: #dc2626; font-weight: 600;">
                    -{{ em.gap_pct }}%
                  </td>
                  <td>
                    <span class="temp-badge" :class="'temp-badge-' + (em.severidad === 'optimo' ? 'bajo' : em.severidad === 'moderado' ? 'moderado' : 'critico')">
                      {{ em.estado_radar }}
                    </span>
                  </td>
                  <td>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                      <button
                        class="cell-action-btn"
                        @click="consultarCopilotoPor(`Prepara un plan de nivelación para el estamento de ${em.nombre} con ${em.sin_asignar} usuarios sin asignar.`)"
                      >
                        Nivelar 🚀
                      </button>
                      <button
                        class="cell-action-btn"
                        style="background-color: #673ab7; color: white;"
                        @click="abrirGoogleFormParaEstamento(em.nombre)"
                      >
                        Google Form 📝
                      </button>
                      <button
                        class="cell-action-btn"
                        style="background-color: #0284c7; color: white;"
                        @click="agendarCalendarioParaEstamento(em.nombre)"
                      >
                        Calendario 📅
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Interactivo Estilo Google Forms -->
    <ModalGoogleForm />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';
import Sidebar from '../components/Sidebar.vue';
import ChatMessage from '../components/ChatMessage.vue';
import TarjetaConfirmacion from '../components/TarjetaConfirmacion.vue';
import ModalGoogleForm from '../components/ModalGoogleForm.vue';

const authStore = useAuthStore();
const chatStore = useChatStore();

const inputMessage = ref('');
const messagesContainer = ref(null);
const textareaRef = ref(null);
const selectedRol = ref('todos');

const sugerenciasAcciones = computed(() => {
  if (authStore.isAdmin) {
    return [
      'Genera un formulario de capacitación tipo Google Forms sobre la Ley 29733',
      'Agenda un recordatorio en el calendario para el taller de phishing del lunes',
      'Genera un análisis de brechas de competencia por rol (Skill Gap Analysis)',
      '¿Quiénes son los usuarios nuevos?',
      'Envíales un correo sobre el curso del lunes a las 10',
      'Inscribe a todos los docentes de Ingeniería en el curso f001'
    ];
  }
  return [
    '¿Qué cursos de privacidad tengo pendientes?',
    '¿Qué dice el control A.3.17 de ISO 27701?',
    '¿Cómo reportar una brecha de datos?',
    '¿Cuáles son mis obligaciones bajo la Ley 29733?'
  ];
});

// KPIs reactivos
const kpiGapClass = computed(() => {
  const gap = chatStore.matrizBrechas?.kpis?.gap_promedio_pct;
  if (gap === undefined || gap === null) return '';
  if (gap > 40) return 'critical-kpi';
  if (gap > 15) return 'warning-kpi';
  return 'success-kpi';
});

const kpiCumplimientoClass = computed(() => {
  const c = chatStore.matrizBrechas?.kpis?.cumplimiento_global_pct;
  if (c === undefined || c === null) return '';
  if (c >= 85) return 'success-kpi';
  if (c >= 50) return 'warning-kpi';
  return 'critical-kpi';
});

// Competencias aplanadas para la tabla matricial
const competenciasFiltradas = computed(() => {
  const roles = chatStore.matrizBrechas?.roles || [];
  const filtrados = (selectedRol.value === 'todos')
    ? roles
    : roles.filter(r => r.rol === selectedRol.value);

  const lista = [];
  for (const r of filtrados) {
    for (const c of (r.competencias || [])) {
      lista.push({
        ...c,
        rol: r.rol,
        nombre_rol: r.nombre_rol,
        total_usuarios: r.total_usuarios
      });
    }
  }
  return lista;
});

// Personal afectado filtrado por rol
const personalAfectadoFiltrado = computed(() => {
  const roles = chatStore.matrizBrechas?.roles || [];
  const filtrados = (selectedRol.value === 'todos')
    ? roles
    : roles.filter(r => r.rol === selectedRol.value);

  const map = new Map();
  for (const r of filtrados) {
    for (const p of (r.personal_afectado || [])) {
      if (!map.has(p.user_id)) {
        map.set(p.user_id, { ...p, rol: r.nombre_rol });
      }
    }
  }
  return Array.from(map.values());
});

function formatFecha(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('es-PE', {
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

async function forzarDiagnosticoIA() {
  try {
    await chatStore.ejecutarDiagnosticoBrechasIA();
  } catch (err) {
    alert(`No se pudo generar el diagnóstico con IA: ${err.message}`);
  }
}

function remediarConCopiloto(nombreRol, cursoTitulo, count) {
  consultarCopilotoPor(
    `Prepara un plan de nivelación urgente para el estamento de ${nombreRol} respecto al curso '${cursoTitulo}' (Control A.3.17 / ISO 27701). Hay ${count} cursos pendientes o sin asignar.`
  );
}

function notificarUsuarioIndividual(userId, nombre) {
  consultarCopilotoPor(
    `Redacta una convocatoria formal por correo para ${nombre} (${userId}) advirtiéndole sobre sus cursos de privacidad pendientes conforme a la Ley 29733 y el control A.3.17 de ISO 27701.`
  );
}

// KPIs reactivos de Heatmap
const kpiSensibilizacionClass = computed(() => {
  const sens = chatStore.heatmapData?.kpis?.indice_global_sensibilizacion;
  if (sens === undefined || sens === null) return '';
  if (sens >= 80) return 'termico-optimo';
  if (sens >= 40) return 'termico-alerta';
  return 'termico-critico';
});

const kpiVulnerabilidadClass = computed(() => {
  const vuln = chatStore.heatmapData?.kpis?.vulnerabilidad_promedio_pct;
  if (vuln === undefined || vuln === null) return '';
  if (vuln > 70) return 'termico-critico';
  if (vuln > 40) return 'termico-alerta';
  return 'termico-optimo';
});

async function forzarDiagnosticoHeatmapIA() {
  try {
    await chatStore.ejecutarDiagnosticoHeatmapIA();
  } catch (err) {
    alert(`No se pudo generar la termografía con IA: ${err.message}`);
  }
}

function simularCampanaEje(ejeNombre, controlIso) {
  consultarCopilotoPor(
    `Diseña una campaña urgente de sensibilización y simulación para el eje de '${ejeNombre}' (${controlIso} / ISO 27701). Define destinatarios prioritarios y redacta el comunicado preventivo.`
  );
}

// Radar de Cobertura Multiaxial
const hoveredVertex = ref(null);

const kpiCoberturaClass = computed(() => {
  const cob = chatStore.radarData?.kpis?.cobertura_global_pct;
  if (cob === undefined || cob === null) return '';
  if (cob >= 90) return 'termico-optimo';
  if (cob >= 65) return 'termico-alerta';
  return 'termico-critico';
});

const kpiEficaciaClass = computed(() => {
  const ef = chatStore.radarData?.kpis?.eficacia_global_pct;
  if (ef === undefined || ef === null) return '';
  if (ef >= 70) return 'termico-optimo';
  if (ef >= 40) return 'termico-alerta';
  return 'termico-critico';
});

const radarVertices = computed(() => {
  return chatStore.radarData?.radar_chart?.vertices || [];
});

const puntosPoligonoReal = computed(() => {
  const verts = radarVertices.value;
  if (!verts.length) return '';
  return verts.map(v => `${v.x_real},${v.y_real}`).join(' ');
});

const puntosPoligonoMeta = computed(() => {
  const verts = radarVertices.value;
  if (!verts.length) return '';
  return verts.map(v => `${v.x_meta},${v.y_meta}`).join(' ');
});

async function forzarDiagnosticoRadarIA() {
  try {
    await chatStore.ejecutarDiagnosticoRadarIA();
  } catch (err) {
    alert(`No se pudo generar el diagnóstico multiaxial con IA: ${err.message}`);
  }
}

function abrirGoogleFormParaEstamento(nombreEstamento) {
  consultarCopilotoPor(
    `Genera un formulario de evaluación y diagnóstico tipo Google Forms para el estamento de ${nombreEstamento} sobre la Ley 29733 e ISO 27701, con preguntas de opción múltiple y escala.`
  );
}

function agendarCalendarioParaEstamento(nombreEstamento) {
  consultarCopilotoPor(
    `Programa un evento y recordatorio en el calendario institucional para el estamento de ${nombreEstamento} sobre el taller de privacidad de datos personales.`
  );
}

onMounted(async () => {
  await chatStore.loadConversaciones();
  await chatStore.loadMatrizBrechas();
  await chatStore.loadHeatmap();
  await chatStore.loadRadar();
  scrollToBottom();
});

watch(
  () => chatStore.activeTab,
  (newTab) => {
    if (newTab === 'brechas' && !chatStore.matrizBrechas) {
      chatStore.loadMatrizBrechas();
    } else if (newTab === 'heatmap' && !chatStore.heatmapData) {
      chatStore.loadHeatmap();
    } else if (newTab === 'radar' && !chatStore.radarData) {
      chatStore.loadRadar();
    }
  }
);

watch(
  () => chatStore.mensajes.length,
  () => {
    nextTick(scrollToBottom);
  }
);

watch(
  () => chatStore.streamingText,
  () => {
    nextTick(scrollToBottom);
  }
);

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function autoResize(e) {
  const target = e.target;
  target.style.height = 'auto';
  target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
}

async function handleSendMessage() {
  const text = inputMessage.value.trim();
  if (!text || chatStore.isStreaming) return;

  inputMessage.value = '';
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }

  await chatStore.sendUserMessage(text);
}

function ejecutarSugerencia(texto) {
  inputMessage.value = texto;
  handleSendMessage();
}

async function handleConfirmApproval() {
  await chatStore.respondApproval(true);
}

async function handleCancelApproval() {
  await chatStore.respondApproval(false);
}

async function consultarCopilotoPor(texto) {
  chatStore.setActiveTab('chat');
  await nextTick();
  inputMessage.value = texto;
  await handleSendMessage();
}
</script>
