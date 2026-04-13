import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import AgreementTable from './AgreementTable'

const claims = [
  { claim: 'Use PostgreSQL', positions: { 'gpt-4o': 'AGREE', 'claude': 'DISAGREE' } },
  { claim: 'Avoid MongoDB', positions: { 'gpt-4o': 'PARTIAL', 'claude': 'AGREE' } },
]
const models = [
  { model_id: 'gpt-4o', display_name: 'GPT-4o' },
  { model_id: 'claude', display_name: 'Claude' },
]

describe('AgreementTable', () => {
  it('renders all claim rows', () => {
    render(<AgreementTable claims={claims} models={models} />)
    expect(screen.getByText('Use PostgreSQL')).toBeInTheDocument()
    expect(screen.getByText('Avoid MongoDB')).toBeInTheDocument()
  })

  it('renders model column headers', () => {
    render(<AgreementTable claims={claims} models={models} />)
    expect(screen.getByText('GPT-4o')).toBeInTheDocument()
    expect(screen.getByText('Claude')).toBeInTheDocument()
  })

  it('shows correct position labels', () => {
    render(<AgreementTable claims={claims} models={models} />)
    expect(screen.getAllByText('Agree').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Disagree').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Partial').length).toBeGreaterThan(0)
  })
})
