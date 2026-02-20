import { render, screen } from '@testing-library/react';
import Dashboard from '../dashboard';

test('renders dashboard heading', () => {
    render(<Dashboard />);
    const heading = screen.getByText(/Welcome to Alfred Dashboard/i);
    expect(heading).toBeInTheDocument();
});