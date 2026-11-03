<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-title">
        <span class="unsa-symbol">🏛️</span>
        <span>PIMS UNSA</span>
        <span class="brand-tag">Agente #8</span>
      </div>
      <button class="btn-new-chat" @click="handleNewChat">
        <span>+</span> Nueva conversación
      </button>
    </div>

    <div class="sidebar-conversations">
      <div class="conversations-title">Historial de Consultas</div>
      <div
        v-for="conv in chatStore.conversaciones"
        :key="conv.id"
        class="conversation-item"
        :class="{ active: conv.id === chatStore.currentConversacionId }"
        @click="chatStore.selectConversacion(conv.id)"
      >
        <span class="conv-title">{{ conv.titulo || 'Consulta de Privacidad' }}</span>
        <span class="conv-date">{{ formatDate(conv.updated_at) }}</span>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="user-info">
        <span class="user-name">{{ authStore.user?.nombre || 'Usuario' }}</span>
        <span class="user-role-badge">Rol: {{ authStore.user?.rol || 'docente' }}</span>
      </div>
      <button class="btn-logout" title="Cerrar sesión" @click="handleLogout">
        Salir 🚪
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const chatStore = useChatStore();
const router = useRouter();

function handleNewChat() {
  chatStore.createNewConversacion();
}

function handleLogout() {
  authStore.logout();
  router.push('/login');
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}
</script>
