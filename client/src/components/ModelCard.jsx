function Skeleton() {
  return (
    <div data-testid="skeleton" className="space-y-3 animate-pulse">
      <div className="h-3 bg-surface shadow-neu-inset rounded-full w-3/4" />
      <div className="h-3 bg-surface shadow-neu-inset rounded-full w-full" />
      <div className="h-3 bg-surface shadow-neu-inset rounded-full w-5/6" />
      <div className="h-3 bg-surface shadow-neu-inset rounded-full w-2/3" />
    </div>
  )
}

export default function ModelCard({ model, phase }) {
  const content = phase === 'debate' || phase === 'extracting' || phase === 'synthesizing' || phase === 'done'
    ? (model.debate ?? model.round1)
    : model.round1

  return (
    <div className="rounded-neu bg-surface shadow-neu-extruded
                    hover:-translate-y-2 hover:shadow-neu-extruded-hover
                    transition-all duration-300 p-8 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="font-display font-bold text-text-primary text-lg">{model.display_name}</span>
        {model.elapsed !== null && model.status === 'done' && (
          <span className="text-text-muted text-sm">{model.elapsed}s</span>
        )}
      </div>

      {model.status === 'pending' && (
        <p className="text-text-muted text-sm">Waiting...</p>
      )}
      {model.status === 'loading' && <Skeleton />}
      {model.status === 'done' && content && (
        <p className="text-text-primary text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      )}
      {model.status === 'error' && (
        <p className="text-red-500 text-sm">Failed to respond.</p>
      )}
    </div>
  )
}
