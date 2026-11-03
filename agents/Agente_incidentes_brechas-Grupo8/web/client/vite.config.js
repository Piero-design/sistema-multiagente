import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// En desarrollo (npm run dev) las llamadas /api van al servidor Node del puerto 3000.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:3100' } },
  build: { outDir: 'dist', chunkSizeWarningLimit: 900 },
});
