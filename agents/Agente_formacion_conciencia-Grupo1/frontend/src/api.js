const API_BASE = ''; // Usa el proxy configurado en vite.config.js o relativo

function getHeaders() {
  const token = localStorage.getItem('pims_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error en inicio de sesión');
    }
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Sesión no válida');
    return res.json();
  },

  async getConversaciones() {
    const res = await fetch(`${API_BASE}/chat/conversaciones`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error obteniendo conversaciones');
    return res.json();
  },

  async crearConversacion(titulo = 'Nueva consulta') {
    const res = await fetch(`${API_BASE}/chat/conversaciones`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ titulo })
    });
    if (!res.ok) throw new Error('Error creando conversación');
    return res.json();
  },

  async getConversacion(id) {
    const res = await fetch(`${API_BASE}/chat/conversaciones/${id}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error cargando mensajes de la conversación');
    return res.json();
  },

  async sendMessage(conversacionId, mensaje, { onToken, onApprovalRequired, onDone, onError }) {
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          conversacion_id: conversacionId,
          mensaje: mensaje
        })
      });

      if (response.status === 401) {
        localStorage.removeItem('pims_token');
        localStorage.removeItem('pims_user');
        window.location.href = '/login';
        throw new Error('Sesión no válida o expirada. Redirigiendo a inicio de sesión...');
      }

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          if (!block.trim()) continue;

          let eventType = 'message';
          let dataStr = '';

          const blockLines = block.split('\n');
          for (const line of blockLines) {
            if (line.startsWith('event: ')) {
              eventType = line.substring(7).trim();
            } else if (line.startsWith('data: ')) {
              dataStr = line.substring(6).trim();
            }
          }

          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr);
              if (eventType === 'token' && onToken) {
                onToken(parsed.content || '');
              } else if (eventType === 'approval_required' && onApprovalRequired) {
                onApprovalRequired(parsed);
              } else if (eventType === 'done' && onDone) {
                onDone(parsed);
              } else if (eventType === 'error' && onError) {
                onError(parsed.error || 'Error en agente');
              }
            } catch (e) {
              console.warn('Error parseando SSE data:', e, dataStr);
            }
          }
        }
      }

      if (onDone) onDone();
    } catch (err) {
      if (onError) onError(err.message || 'Error de conexión');
    }
  },

  async approveAction(conversacionId, actionId, approved) {
    const res = await fetch(`${API_BASE}/chat/approve`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        conversacion_id: conversacionId,
        action_id: actionId,
        approved: approved
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error procesando aprobación');
    }
    return res.json();
  },

  async getDashboardEstado() {
    const res = await fetch(`${API_BASE}/dashboard/estado`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar panel de estado');
    return res.json();
  },

  async getAdminCorreos() {
    const res = await fetch(`${API_BASE}/admin/correos`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al consultar auditoría de correos');
    return res.json();
  },

  async getMatrizBrechas(rol = null) {
    const query = rol ? `?rol=${encodeURIComponent(rol)}` : '';
    const res = await fetch(`${API_BASE}/dashboard/brechas${query}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar la Matriz de Brechas');
    return res.json();
  },

  async diagnosticarBrechas() {
    const res = await fetch(`${API_BASE}/dashboard/brechas/diagnosticar`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al ejecutar diagnóstico IA de brechas');
    }
    return res.json();
  },

  async getHeatmap(facultad = null) {
    const query = facultad ? `?facultad=${encodeURIComponent(facultad)}` : '';
    const res = await fetch(`${API_BASE}/dashboard/heatmap${query}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar el Mapa de Calor');
    return res.json();
  },

  async diagnosticarHeatmap() {
    const res = await fetch(`${API_BASE}/dashboard/heatmap/diagnosticar`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al ejecutar diagnóstico IA de mapa de calor');
    }
    return res.json();
  },

  async getRadar(estamento = null, facultad = null) {
    const params = new URLSearchParams();
    if (estamento) params.append('estamento', estamento);
    if (facultad) params.append('facultad', facultad);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/dashboard/radar${qs}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar el Radar de Cobertura');
    return res.json();
  },

  async diagnosticarRadar() {
    const res = await fetch(`${API_BASE}/dashboard/radar/diagnosticar`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al ejecutar diagnóstico IA de radar');
    }
    return res.json();
  },

  async getFormularios() {
    const res = await fetch(`${API_BASE}/formularios`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar formularios de capacitación');
    return res.json();
  },

  async getEventosCalendario() {
    const res = await fetch(`${API_BASE}/eventos/calendario`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Error al cargar eventos del calendario');
    return res.json();
  }
};
