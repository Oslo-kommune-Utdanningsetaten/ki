import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';


// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd(), '') };

  // Proxy requests with Vite in dev, Nginx in prod
  const proxyConfig = process.env.VITE_API_BASE_URL ? {
    '/api': {
      target: process.env.VITE_API_BASE_URL,
      changeOrigin: true,
      secure: false
      // rewrite: (path: string) => path.replace(/^\/api/, ''),
    },
    '/auth/': {
      target: process.env.VITE_API_BASE_URL,
      changeOrigin: true,
      secure: false
      // rewrite: (path: string) => path.replace(/^\/api/, ''),
    },
  } : undefined;

  return {
    plugins: [
      // basicSsl(),
      vue(),
      vueJsx(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      // port: 5000,
      proxy: proxyConfig
    }
  };
});
