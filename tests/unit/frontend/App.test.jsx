import React from 'react'

test('test environment runs', () => {
    render(React.createElement('div', null, 'test-ok'))
    expect(screen.getByText(/test-ok/i)).toBeInTheDocument()
})

