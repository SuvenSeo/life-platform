import { ExternalLink } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { DomainPanel } from '../components/DomainPanel'
import { domainMeta, formatMetric, numericMetricRows } from '../lib/format'
import type { DomainKey, DomainSignal } from '../types'

function readItem(item: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = item[key]
    if (value !== undefined && value !== null && value !== '') return String(value)
  }
  return 'Signal'
}

function readOptionalItem(item: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = item[key]
    if (value !== undefined && value !== null && value !== '') return String(value)
  }
  return null
}

export function DomainsPage({ domains }: { domains: DomainSignal[] }) {
  const [selected, setSelected] = useState<DomainKey>('food')
  const active = domains.find((domain) => domain.key === selected) ?? domains[0]
  const chartData = useMemo(() => (active ? numericMetricRows(active.metrics).slice(0, 8) : []), [active])

  if (!active) {
    return <div className="rounded-lg border border-line bg-white p-6 text-muted">Domain signals will appear when the API responds.</div>
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[18rem_1fr]">
      <aside className="rounded-lg border border-line bg-white p-3 shadow-panel xl:sticky xl:top-24 xl:self-start">
        <p className="px-2 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted">Domains</p>
        <div className="space-y-1">
          {domains.map((domain) => {
            const meta = domainMeta[domain.key]
            const Icon = meta.icon
            const activeItem = selected === domain.key
            return (
              <button
                key={domain.key}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition ${
                  activeItem ? 'bg-ink text-paper' : 'text-ink hover:bg-stone-50'
                }`}
                onClick={() => setSelected(domain.key)}
                type="button"
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span className="min-w-0">
                  <span className="block text-sm font-semibold">{domain.label}</span>
                  <span className={`block truncate text-xs ${activeItem ? 'text-paper/65' : 'text-muted'}`}>{domain.status}</span>
                </span>
              </button>
            )
          })}
        </div>
      </aside>

      <div className="space-y-5">
        <DomainPanel domain={active} />

        <section className="grid gap-5 xl:grid-cols-[1fr_0.85fr]">
          <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Metric spread</p>
                <h2 className="mt-1 text-2xl font-semibold text-ink">{active.label}</h2>
              </div>
              <a className="inline-flex items-center gap-1.5 rounded-lg border border-line px-3 py-2 text-sm font-semibold text-ink" href={active.api_base} target="_blank" rel="noreferrer">
                API
                <ExternalLink className="h-4 w-4" aria-hidden="true" />
              </a>
            </div>
            <div className="mt-5 h-80">
              {chartData.length ? (
                <ResponsiveContainer height="100%" width="100%">
                  <BarChart data={chartData} margin={{ left: 10, right: 20, top: 10, bottom: 42 }}>
                    <CartesianGrid vertical={false} stroke="#e6dcc8" />
                    <XAxis dataKey="name" interval={0} tick={{ fill: '#6f695d', fontSize: 11 }} angle={-24} textAnchor="end" />
                    <YAxis tick={{ fill: '#6f695d', fontSize: 12 }} />
                    <Tooltip formatter={(value, _name, item) => [`${value} ${item.payload.unit}`.trim(), 'Value']} />
                    <Bar dataKey="value" fill={domainMeta[active.key].accent} radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="grid h-full place-items-center rounded-lg border border-dashed border-line text-sm text-muted">
                  Numeric metrics are not available for this source yet.
                </div>
              )}
            </div>
          </div>

          <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Source payload</p>
            <h2 className="mt-1 text-2xl font-semibold text-ink">Top items</h2>
            <div className="mt-5 divide-y divide-line">
              {active.top_items.length ? (
                active.top_items.slice(0, 8).map((item, index) => (
                  <div key={`${active.key}-${index}`} className="grid grid-cols-[1fr_auto] gap-3 py-3 text-sm">
                    <span className="min-w-0 font-semibold text-ink">{readItem(item, ['label', 'item_name', 'fuel_type', 'title', 'model'])}</span>
                    <span className="text-right text-muted">{formatMetric(readOptionalItem(item, ['price', 'avg_price', 'amount', 'value']), readOptionalItem(item, ['unit']))}</span>
                  </div>
                ))
              ) : (
                <p className="rounded-lg border border-dashed border-line p-4 text-sm text-muted">This adapter has summary signals but no item list yet.</p>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
