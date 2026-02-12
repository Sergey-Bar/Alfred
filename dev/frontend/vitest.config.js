import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: './src/setupTests.js',
        include: ['src/**/*.test.{js,jsx,ts,tsx}'],
        exclude: ['**/node_modules/**', 'playwright/**', '../QA/**'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            reportsDirectory: '../QA/results/coverage'
        }
    }
})
