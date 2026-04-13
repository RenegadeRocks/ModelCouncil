import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import FinalAnswer from './FinalAnswer'

describe('FinalAnswer', () => {
  it('renders the synthesizer name', () => {
    render(<FinalAnswer content="PostgreSQL is best." synthesizer="Claude Sonnet 4.6" />)
    expect(screen.getByText(/Claude Sonnet 4\.6/)).toBeInTheDocument()
  })

  it('renders the answer content', () => {
    render(<FinalAnswer content="PostgreSQL is best." synthesizer="Claude Sonnet 4.6" />)
    expect(screen.getByText('PostgreSQL is best.')).toBeInTheDocument()
  })
})
