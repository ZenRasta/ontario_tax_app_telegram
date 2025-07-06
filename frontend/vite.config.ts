import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/v1': {                        // anything starting with /v1…
        target: 'http://localhost:8003', // …is forwarded to FastAPI
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
