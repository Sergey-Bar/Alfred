import React from 'react'

test('test environment runs', () => {
    render(React.createElement('div', null, 'test-ok'))
    expect(screen.getByText(/test-ok/i)).toBeInTheDocument()
})

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Sanity test to verify test environment and React Testing Library setup.
// Why: Ensures test runner and DOM assertions work before running real tests.
// Root Cause: Broken test setup can cause false negatives/positives in CI.
// Context: Run in CI for every PR. Future: expand to cover App rendering and routing.
// Model Suitability: Sanity test logic is standard; GPT-4.1 is sufficient.
