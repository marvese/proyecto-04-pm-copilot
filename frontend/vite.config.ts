/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
        navigateFallback: "/index.html",
        runtimeCaching: [
          {
            urlPattern: /^\/api\//,
            handler: "NetworkFirst",
            options: { cacheName: "api-cache", expiration: { maxAgeSeconds: 300 } },
          },
        ],
      },
      manifest: {
        name: "PM Copilot",
        short_name: "PMCopilot",
        description: "Intelligent project management assistant with RAG",
        start_url: "/",
        display: "standalone",
        theme_color: "#1a1a2e",
        background_color: "#0d1b2a",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any maskable" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    exclude: ["**/node_modules/**", "**/dist/**"],
  },
});
