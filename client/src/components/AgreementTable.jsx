const POSITIONS = {
  AGREE:    { label: 'Agree',    dot: 'bg-accent-teal' },
  DISAGREE: { label: 'Disagree', dot: 'bg-red-400' },
  PARTIAL:  { label: 'Partial',  dot: 'bg-accent' },
}

function PositionCell({ position }) {
  const config = POSITIONS[position]
  if (!config) return <span className="text-text-muted text-xs">—</span>
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`w-8 h-8 rounded-full shadow-neu-inset-deep flex items-center justify-center`}>
        <div className={`w-4 h-4 rounded-full ${config.dot}`} />
      </div>
      <span className="text-xs text-text-muted font-body">{config.label}</span>
    </div>
  )
}

export default function AgreementTable({ claims, models }) {
  if (!claims.length) return null

  return (
    <div className="rounded-neu bg-surface shadow-neu-inset p-8 overflow-x-auto">
      <h2 className="font-display font-bold text-text-primary text-xl mb-6">Agreement Table</h2>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left font-body font-medium text-text-muted text-sm pb-4 pr-6 w-1/3">
              Key Claim
            </th>
            {models.map(m => (
              <th key={m.model_id} className="text-center font-display font-bold text-text-primary text-sm pb-4 px-4">
                {m.display_name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {claims.map((row, i) => (
            <tr key={i}>
              <td className="text-text-primary text-sm py-4 pr-6 align-middle leading-snug">
                {row.claim}
              </td>
              {models.map(m => (
                <td key={m.model_id} className="text-center py-4 px-4 align-middle">
                  <PositionCell position={row.positions[m.model_id]} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
