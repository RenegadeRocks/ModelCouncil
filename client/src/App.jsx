import { useCouncil } from './hooks/useCouncil'
import PromptInput from './components/PromptInput'
import ModelCard from './components/ModelCard'
import AgreementTable from './components/AgreementTable'
import FinalAnswer from './components/FinalAnswer'

const PHASE_LABELS = {
  idle: '',
  round1: 'Round 1 — Querying all models...',
  debate: 'Round 2 — Models are debating...',
  extracting: 'Extracting agreement positions...',
  synthesizing: 'Synthesizing final answer...',
  done: '',
  error: '',
}

export default function App() {
  const { state, run } = useCouncil()
  const isRunning = !['idle', 'done', 'error'].includes(state.phase)
  const modelList = Object.entries(state.models).map(([id, m]) => ({ id, ...m }))

  return (
    <div className="min-h-screen bg-surface font-body">
      {/* Header */}
      <header className="pt-16 pb-8 text-center px-6">
        <h1 className="font-display font-extrabold text-5xl md:text-7xl text-text-primary tracking-tight">
          Model Council
        </h1>
        <p className="mt-4 text-text-muted text-lg max-w-xl mx-auto">
          One prompt. Three models. A structured debate. One synthesized answer.
        </p>
      </header>

      {/* Prompt */}
      <section className="px-6 pb-12">
        <PromptInput onSubmit={run} disabled={isRunning} />
      </section>

      {/* Phase status */}
      {PHASE_LABELS[state.phase] && (
        <div className="text-center text-text-muted text-sm mb-8 animate-pulse">
          {PHASE_LABELS[state.phase]}
        </div>
      )}

      {/* Error */}
      {state.phase === 'error' && (
        <div className="max-w-3xl mx-auto px-6 mb-8">
          <div className="rounded-neu-sm bg-surface shadow-neu-inset p-6 text-red-500 text-sm">
            {state.error}
          </div>
        </div>
      )}

      {/* Model cards */}
      {modelList.length > 0 && (
        <section className="px-6 mb-12">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-display font-bold text-text-primary text-2xl mb-6">
              {state.phase === 'debate' || state.phase === 'extracting' || state.phase === 'synthesizing' || state.phase === 'done'
                ? 'Debate Positions'
                : 'Initial Answers'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modelList.map(m => (
                <ModelCard key={m.id} model={m} phase={state.phase} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Agreement Table */}
      {state.claims.length > 0 && (
        <section className="px-6 mb-12">
          <div className="max-w-6xl mx-auto">
            <AgreementTable claims={state.claims} models={state.tableModels} />
          </div>
        </section>
      )}

      {/* Final Answer */}
      {state.finalAnswer && (
        <section className="px-6 pb-16">
          <div className="max-w-3xl mx-auto">
            <FinalAnswer content={state.finalAnswer} synthesizer={state.synthesizer} />
          </div>
        </section>
      )}
    </div>
  )
}
