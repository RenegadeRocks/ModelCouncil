import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ModelCard from './ModelCard'

const base = { display_name: 'GPT-4o', round1: null, debate: null, status: 'pending', elapsed: null }

describe('ModelCard', () => {
  it('shows model name', () => {
    render(<ModelCard model={base} phase="round1" />)
    expect(screen.getByText('GPT-4o')).toBeInTheDocument()
  })

  it('shows loading skeleton when status is loading', () => {
    render(<ModelCard model={{ ...base, status: 'loading' }} phase="round1" />)
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
  })

  it('shows round1 content when done in round1 phase', () => {
    render(<ModelCard model={{ ...base, status: 'done', round1: 'Use PostgreSQL', elapsed: 2.1 }} phase="round1" />)
    expect(screen.getByText('Use PostgreSQL')).toBeInTheDocument()
    expect(screen.getByText(/2\.1s/)).toBeInTheDocument()
  })

  it('shows error message when status is error', () => {
    render(<ModelCard model={{ ...base, status: 'error' }} phase="round1" />)
    expect(screen.getByText(/failed/i)).toBeInTheDocument()
  })
})
