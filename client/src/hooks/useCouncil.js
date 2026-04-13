import { useState, useCallback } from 'react'

const INITIAL_STATE = {
  phase: 'idle',
  models: {},
  claims: [],
  tableModels: [],
  finalAnswer: null,
  synthesizer: null,
  error: null,
}

function applyEvent(state, event) {
  switch (event.type) {
    case 'phase': {
      // When debate starts, mark all existing models as 'loading' so skeleton shows
      if (event.phase === 'debate') {
        const updatedModels = {}
        for (const [id, m] of Object.entries(state.models)) {
          updatedModels[id] = { ...m, status: m.status === 'done' ? 'loading' : m.status }
        }
        return { ...state, phase: event.phase, models: updatedModels }
      }
      return { ...state, phase: event.phase }
    }

    case 'model_response': {
      const existing = state.models[event.model_id] ?? {
        display_name: event.display_name,
        round1: null,
        debate: null,
        status: 'pending',
        elapsed: null,
      }
      const updated = {
        ...existing,
        display_name: event.display_name,
        status: event.error ? 'error' : 'done',
        elapsed: event.elapsed,
      }
      if (event.phase === 'round1') updated.round1 = event.error ? null : event.content
      if (event.phase === 'debate') updated.debate = event.error ? null : event.content
      return { ...state, models: { ...state.models, [event.model_id]: updated } }
    }

    case 'table':
      return { ...state, claims: event.claims, tableModels: event.models }

    case 'table_error':
      return state

    case 'final_answer':
      return { ...state, finalAnswer: event.content, synthesizer: event.synthesizer }

    case 'error':
      return { ...state, phase: 'error', error: event.message }

    case 'done':
      return state.phase === 'error' ? state : { ...state, phase: 'done' }

    default:
      return state
  }
}

export function useCouncil() {
  const [state, setState] = useState(INITIAL_STATE)

  const run = useCallback(async (prompt) => {
    setState({ ...INITIAL_STATE, phase: 'round1' })

    try {
      const response = await fetch('/api/council', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        setState(prev => ({ ...prev, phase: 'error', error: `Server error ${response.status}` }))
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const chunks = buffer.split('\n\n')
        buffer = chunks.pop()

        for (const chunk of chunks) {
          const line = chunk.trim()
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            setState(prev => applyEvent(prev, event))
          } catch {
            // malformed JSON — skip
          }
        }
      }
    } catch (err) {
      setState(prev => ({ ...prev, phase: 'error', error: err.message }))
    }
  }, [])

  return { state, run }
}
