import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import PromptInput from './PromptInput'

describe('PromptInput', () => {
  it('renders the textarea and button', () => {
    render(<PromptInput onSubmit={() => {}} disabled={false} />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /run council/i })).toBeInTheDocument()
  })

  it('calls onSubmit with trimmed prompt when button clicked', () => {
    const onSubmit = vi.fn()
    render(<PromptInput onSubmit={onSubmit} disabled={false} />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '  best database?  ' } })
    fireEvent.click(screen.getByRole('button', { name: /run council/i }))
    expect(onSubmit).toHaveBeenCalledWith('best database?')
  })

  it('does not call onSubmit when prompt is empty', () => {
    const onSubmit = vi.fn()
    render(<PromptInput onSubmit={onSubmit} disabled={false} />)
    fireEvent.click(screen.getByRole('button', { name: /run council/i }))
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('disables button when disabled=true', () => {
    render(<PromptInput onSubmit={() => {}} disabled={true} />)
    expect(screen.getByRole('button', { name: /running/i })).toBeDisabled()
  })
})
