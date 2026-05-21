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
    stone: 'border-white/15 bg-white/10 text-paper',
    red: 'border-chili/35 bg-chili/15 text-[#ffd7d2]',
    green: 'border-leaf/35 bg-leaf/15 text-[#d9f5e8]',
    blue: 'border-steel/40 bg-steel/15 text-[#d9ecff]',
    gold: 'border-gold/45 bg-gold/15 text-[#fff0bd]',
  }

  return (
    <div className={`rounded-lg border p-4 shadow-[0_18px_45px_-34px_rgba(0,0,0,.7)] backdrop-blur ${tones[tone]}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-current/70">{label}</p>
          <p className="mt-2 break-words text-2xl font-semibold leading-tight tracking-normal">{value}</p>
        </div>
        <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
      </div>
      {note ? <p className="mt-3 text-sm leading-5 text-current/70">{note}</p> : null}
    </div>
  )
}
