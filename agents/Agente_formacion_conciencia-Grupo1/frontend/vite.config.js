import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/formularios': 'http://127.0.0.1:8000',
      '/eventos': 'http://127.0.0.1:8000',
    }
  }
});
