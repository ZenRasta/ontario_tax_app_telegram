import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {                       // anything starting with /api…
        target: 'http://localhost:8003', // …is forwarded to FastAPI
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
