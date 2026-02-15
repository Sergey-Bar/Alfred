// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Adds accessibility test for dashboard components using React Testing Library and Playwright.
// Why: Expands accessibility coverage for frontend, ensuring WCAG AA+ compliance.
// Root Cause: Previous tests lacked formal accessibility checks.
// Context: Update as new components are added. For advanced accessibility automation, consider Claude Sonnet or GPT-5.1-Codex.

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import Dashboard from '../components/Dashboard';

expect.extend(toHaveNoViolations);

test('Dashboard is accessible', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
});
