import { useState } from 'react'

export default function PromptInput({ onSubmit, disabled }) {
  const [value, setValue] = useState('')

  function handleSubmit() {
    const trimmed = value.trim()
    if (!trimmed) return
    onSubmit(trimmed)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit()
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <textarea
        className="w-full resize-none rounded-neu-sm bg-surface shadow-neu-inset-deep
                   focus:shadow-neu-inset-deep focus:outline-none focus:ring-2 focus:ring-accent
                   p-6 text-text-primary font-body text-base placeholder:text-text-muted
                   transition-shadow duration-300 min-h-[120px]"
        placeholder="Ask your council anything... (Ctrl+Enter to run)"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={disabled}
          className="rounded-neu-sm bg-accent px-8 py-3 font-body font-medium text-white
                     shadow-neu-extruded
                     hover:-translate-y-1 hover:shadow-neu-extruded-hover
                     active:translate-y-0.5 active:shadow-neu-inset
                     disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                     transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-surface"
        >
          {disabled ? 'Running...' : 'Run Council'}
        </button>
      </div>
    </div>
  )
}
