import type { LucideIcon } from 'lucide-react'

export function MetricTile({
  icon: Icon,
  label,
  value,
  note,
  tone = 'stone',
}: {
  icon: LucideIcon
  label: string
  value: string
  note?: string
  tone?: 'stone' | 'red' | 'green' | 'blue' | 'gold'
}) {
  const tones = {
    stone: 'border-line bg-paper/90 text-ink',
    red: 'border-chili/25 bg-chili/10 text-[#4b1712]',
    green: 'border-leaf/25 bg-leaf/10 text-[#123426]',
    blue: 'border-steel/25 bg-steel/10 text-[#10283b]',
    gold: 'border-gold/35 bg-gold/10 text-[#4f3a10]',
  }

  return (
    <div className={`rounded-lg border p-4 shadow-[0_18px_45px_-34px_rgba(17,19,15,.48)] ${tones[tone]}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-current/65">{label}</p>
          <p className="mt-2 break-words text-2xl font-semibold leading-tight tracking-normal">{value}</p>
        </div>
        <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
      </div>
      {note ? <p className="mt-3 text-sm leading-5 text-current/70">{note}</p> : null}
    </div>
  )
}
