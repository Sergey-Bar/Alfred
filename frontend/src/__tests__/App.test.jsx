import { render, screen } from '@testing-library/react'
import React from 'react'

test('test environment runs', () => {
    render(React.createElement('div', null, 'test-ok'))
    expect(screen.getByText(/test-ok/i)).toBeInTheDocument()
})
