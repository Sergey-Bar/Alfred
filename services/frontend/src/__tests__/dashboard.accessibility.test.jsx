import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import Dashboard from '../components/Dashboard';

expect.extend(toHaveNoViolations);

test('Dashboard is accessible', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
});
