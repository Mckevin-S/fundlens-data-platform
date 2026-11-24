import { defineConfig } from "@playwright/test";

/**
 * Parcours de bout en bout des deux fronts. Par défaut les API sont simulées (page.route) pour un retour rapide ;
 * avec E2E_FULL_STACK=1, les tests visent la pile Docker Compose réelle (ports 8081 et 4200).
 */
const fullStack = process.env.E2E_FULL_STACK === "1";

export default defineConfig({
  testDir: "tests",
  reporter: [["list"]],
  use: { trace: "retain-on-failure" },
  projects: [
    { name: "portail", testMatch: /portal\.spec\.ts/, use: { baseURL: fullStack ? "http://localhost:8081" : "http://localhost:4173" } },
    { name: "cockpit", testMatch: /cockpit\.spec\.ts/, use: { baseURL: fullStack ? "http://localhost:4200" : "http://localhost:4300" } },
  ],
  webServer: fullStack ? undefined : [
    { command: "npx vite preview --port 4173 --strictPort", cwd: "../investor-portal", port: 4173, reuseExistingServer: true },
    { command: "npx http-server dist/cockpit/browser -p 4300 -s", cwd: "../cockpit", port: 4300, reuseExistingServer: true },
  ],
});
