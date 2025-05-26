import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {                       // anything starting with /api…
        target: 'http://localhost:8000', // …is forwarded to FastAPI
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
