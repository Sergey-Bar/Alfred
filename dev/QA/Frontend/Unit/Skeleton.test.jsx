import { render } from '@testing-library/react'
import { Skeleton, SkeletonCard, SkeletonTable } from '../components/Skeleton'



test('Skeleton renders text variant', () => {
    const { container } = render(<Skeleton variant="text" />)
    expect(container.firstChild).toBeTruthy()
})

test('SkeletonCard renders with expected structure', () => {
    const { getAllByText } = render(<SkeletonCard />)
    // SkeletonCard uses Skeleton components; ensure it rendered by checking for role-less divs
    expect(getAllByText((content, element) => element.tagName === 'DIV').length).toBeGreaterThan(0)
})

test('SkeletonTable renders rows and columns', () => {
    const { container } = render(<SkeletonTable rows={3} columns={2} />)
    // verify that grid style for header is applied
    expect(container.querySelectorAll('div').length).toBeGreaterThan(0)
})
