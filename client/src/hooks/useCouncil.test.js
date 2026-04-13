import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useCouncil } from './useCouncil'

function makeStream(events) {
  const encoder = new TextEncoder()
  const chunks = events.map(e => encoder.encode(`data: ${JSON.stringify(e)}\n\n`))
  let index = 0
  return {
    getReader: () => ({
      read: vi.fn(async () => {
        if (index < chunks.length) return { done: false, value: chunks[index++] }
        return { done: true, value: undefined }
      }),
      cancel: vi.fn(),
    }),
  }
}

beforeEach(() => {
  global.fetch = vi.fn()
})

describe('useCouncil', () => {
  it('starts in idle phase', () => {
    const { result } = renderHook(() => useCouncil())
    expect(result.current.state.phase).toBe('idle')
    expect(result.current.state.finalAnswer).toBeNull()
  })

  it('transitions through phases and populates model data', async () => {
    const events = [
      { type: 'phase', phase: 'round1' },
      { type: 'model_response', phase: 'round1', model_id: 'gpt-4o', display_name: 'GPT-4o', content: 'Use PostgreSQL', error: null, elapsed: 2.1 },
      { type: 'model_response', phase: 'round1', model_id: 'claude', display_name: 'Claude', content: 'Also PostgreSQL', error: null, elapsed: 1.8 },
      { type: 'phase', phase: 'debate' },
      { type: 'model_response', phase: 'debate', model_id: 'gpt-4o', display_name: 'GPT-4o', content: 'I agree with Claude', error: null, elapsed: 1.5 },
      { type: 'table', claims: [{ claim: 'Use PostgreSQL', positions: { 'gpt-4o': 'AGREE', claude: 'AGREE' } }], models: [{ model_id: 'gpt-4o', display_name: 'GPT-4o' }, { model_id: 'claude', display_name: 'Claude' }] },
      { type: 'final_answer', content: 'PostgreSQL is best.', synthesizer: 'Claude' },
      { type: 'done' },
    ]

    global.fetch.mockResolvedValue({ ok: true, body: makeStream(events) })

    const { result } = renderHook(() => useCouncil())

    await act(async () => {
      await result.current.run('best database?')
    })

    expect(result.current.state.phase).toBe('done')
    expect(result.current.state.models['gpt-4o'].round1).toBe('Use PostgreSQL')
    expect(result.current.state.models['gpt-4o'].debate).toBe('I agree with Claude')
    expect(result.current.state.claims).toHaveLength(1)
    expect(result.current.state.finalAnswer).toBe('PostgreSQL is best.')
    expect(result.current.state.synthesizer).toBe('Claude')
  })

  it('sets error phase on error event', async () => {
    const events = [
      { type: 'error', message: 'Fewer than 2 models responded.' },
      { type: 'done' },
    ]

    global.fetch.mockResolvedValue({ ok: true, body: makeStream(events) })

    const { result } = renderHook(() => useCouncil())

    await act(async () => {
      await result.current.run('test?')
    })

    expect(result.current.state.phase).toBe('error')
    expect(result.current.state.error).toBe('Fewer than 2 models responded.')
  })
})
