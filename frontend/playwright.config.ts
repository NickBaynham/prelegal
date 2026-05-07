import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const BACKEND_PORT = 8001;
const FRONTEND_PORT = 3001;
const E2E_DB = path.resolve(__dirname, "tests/e2e/.tmp/e2e.db");

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: `http://localhost:${FRONTEND_PORT}`,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `pdm run uvicorn prelegal.main:app --host 127.0.0.1 --port ${BACKEND_PORT}`,
      cwd: path.resolve(__dirname, "../backend"),
      url: `http://localhost:${BACKEND_PORT}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        DATABASE_PATH: E2E_DB,
        CORS_ORIGINS: `http://localhost:${FRONTEND_PORT}`,
      },
    },
    {
      command: `next dev --port ${FRONTEND_PORT} --hostname 127.0.0.1`,
      cwd: __dirname,
      url: `http://localhost:${FRONTEND_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        NEXT_PUBLIC_API_URL: `http://localhost:${BACKEND_PORT}`,
        INTERNAL_API_URL: `http://localhost:${BACKEND_PORT}`,
      },
    },
  ],
});
