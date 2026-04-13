export default function FinalAnswer({ content, synthesizer }) {
  return (
    <div className="rounded-neu bg-surface shadow-neu-extruded overflow-hidden">
      <div className="h-1.5 bg-accent" />
      <div className="p-8">
        <div className="mb-4">
          <span className="font-display font-bold text-text-primary text-xl">Final Answer</span>
          {synthesizer && (
            <span className="ml-3 text-text-muted text-sm font-body">
              synthesized by {synthesizer}
            </span>
          )}
        </div>
        <p className="text-text-primary text-base leading-relaxed whitespace-pre-wrap font-body">
          {content}
        </p>
      </div>
    </div>
  )
}
