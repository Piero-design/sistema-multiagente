<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <span class="unsa-badge">PIMS UNSA • ISO 27701:2025</span>
        <h1>Agente de Formación y Conciencia</h1>
        <p>Control A.3.17 • Ley 29733 (Perú)</p>
      </div>

      <div v-if="errorMessage" class="error-msg">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Usuario o Correo Institucional</label>
          <input
            id="email"
            v-model="email"
            type="text"
            required
            placeholder="admin o usuario@unsa.edu.pe"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Autenticando...' : 'Iniciar Sesión' }}
        </button>
      </form>

      <div class="demo-credentials">
        <strong>Credenciales de prueba:</strong><br />
        • Administrador: <code>admin</code> / <code>admin</code><br />
        • Jefatura (Ingeniería): <code>maria.lopez</code> / <code>maria123</code><br />
        • Docente: <code>juan.perez</code> / <code>juan123</code><br />
        • Administrativo: <code>carlos.ruiz</code> / <code>carlos123</code><br />
        • Personal Nuevo: <code>nuevo1</code> / <code>nuevo1</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const email = ref('admin');
const password = ref('admin');
const errorMessage = ref('');
const loading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

async function handleLogin() {
  errorMessage.value = '';
  loading.value = true;
  try {
    await authStore.login(email.value, password.value);
    router.push('/chat');
  } catch (err) {
    errorMessage.value = err.message || 'Error de autenticación';
  } finally {
    loading.value = false;
  }
}
</script>
