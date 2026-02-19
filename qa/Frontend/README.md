# Frontend Tests

## Location

Frontend unit tests are located in:
```
src/frontend/src/__tests__/
```

## Why Not in QA Directory?

Frontend tests remain co-located with source code for several important reasons:

1. **Module Resolution**: Vite/Vitest works best when tests are within the `src/` directory tree. Moving tests outside requires complex path aliasing.

2. **Import Paths**: Tests can use clean relative imports like `import App from '../App'` instead of complex path navigation.

3. **Industry Standard**: React/Vite projects conventionally keep unit tests alongside source code for easier maintenance.

4. **Hot Module Replacement**: Vitest watch mode works more reliably with tests in the source tree.

## Test Structure

```
src/frontend/src/__tests__/
├── App.test.jsx              # Main App component tests
└── Skeleton.test.jsx         # Skeleton UI component tests
```

## Running Tests

```bash
# From dev/frontend directory
npm run test:unit              # Run tests in watch mode
npm run test:unit -- --run     # Run tests once (CI mode)
npm run test:unit -- --coverage # Run with coverage report
```

## Configuration

- **Config File**: `src/frontend/vitest.config.js`
- **Test Pattern**: `src/**/*.test.{js,jsx,ts,tsx}`
- **Environment**: jsdom (browser simulation)
- **Setup**: `src/setupTests.js` (global test utilities)

## Coverage

Coverage reports are generated in:
```
qa/results/coverage/
```

## Best Practices

1. **Co-location**: Keep test files near the components they test
2. **Naming**: Use `*.test.jsx` for test files
3. **React Testing Library**: Use RTL patterns for component testing
4. **Fast Tests**: Unit tests should complete in < 100ms each
5. **Isolation**: Each test should be independent

## Test Categories

- **Component Tests**: Rendering, props, user interactions
- **Utility Tests**: Helper functions, business logic
- **Hook Tests**: Custom React hooks behavior

## See Also

- End-to-end tests: `qa/E2E/`
- Backend tests: `qa/Backend/`
- Test documentation: `qa/README_STRUCTURE.md`

## Status

✅ **4 passing tests** in 2 test files
