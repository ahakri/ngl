import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const api = process.env.API_URL || 'http://localhost:8080';

export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/v1': api, '/api': api } },
});
