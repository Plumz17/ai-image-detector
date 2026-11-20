import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Port 5173 is one of the addresses the backend allows by default (CORS_ORIGINS).
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
});
