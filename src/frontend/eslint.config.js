
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: ESLint config for React frontend. Sets up recommended rules, React hooks, Vite, and ignores dist/.
// Why: Enforces code quality and style for all JS/JSX files in the project.
// Root Cause: Missing or misconfigured lint config leads to inconsistent code and bugs.
// Context: Used by all frontend devs and CI. Future: add custom rules and TypeScript support.
// Model Suitability: ESLint config logic is standard; GPT-4.1 is sufficient.
import js from '@eslint/js'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
])
