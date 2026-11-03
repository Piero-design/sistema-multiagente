<template>
  <div class="message-wrapper" :class="message.rol">
    <div class="avatar" :class="message.rol === 'user' ? 'user-avatar' : 'agent-avatar'">
      {{ message.rol === 'user' ? 'U' : '🛡️' }}
    </div>
    <div class="message-bubble">
      <div v-if="message.rol === 'user'" class="user-text">
        {{ message.contenido }}
      </div>
      <div v-else class="markdown-body" v-html="renderedMarkdown" @click="handleBodyClick"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked';
import { useChatStore } from '../stores/chat';

const chatStore = useChatStore();

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
});

const renderedMarkdown = computed(() => {
  if (!props.message.contenido) return '<em>Escribiendo...</em>';
  try {
    return marked.parse(props.message.contenido, { breaks: true });
  } catch (err) {
    return props.message.contenido;
  }
});

function handleBodyClick(event) {
  const target = event.target.closest('a');
  if (target) {
    const href = target.getAttribute('href') || '';
    if (href.includes('#tab=')) {
      event.preventDefault();
      const tabName = href.split('#tab=')[1];
      if (tabName) {
        chatStore.setActiveTab(tabName);
      }
    }
  }
}
</script>
