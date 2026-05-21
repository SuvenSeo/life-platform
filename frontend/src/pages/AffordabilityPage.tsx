import { useQuery } from '@tanstack/react-query'
import { Calculator, MapPin, WalletCards } from 'lucide-react'
import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { getAffordability } from '../lib/api'
import { districts, formatDate, formatLkr, profiles } from '../lib/format'
import type { Profile } from '../types'

export function AffordabilityPage() {
  const [district, setDistrict] = useState('Colombo')
  const [profile, setProfile] = useState<Profile>('family')
  const affordability = useQuery({
    queryKey: ['affordability-detail', district, profile],
    queryFn: () => getAffordability(district, profile),
  })
  const data = affordability.data
  const chartData =
    data?.breakdown.map((item) => ({
      name: item.label.replace(' and ', ' & '),
      value: item.monthly_lkr,
      confidence: item.confidence,
    })) ?? []

  return (
    <div className="space-y-5">
      <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <div className="rounded-lg border border-ink bg-ink p-5 text-paper shadow-panel">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-paper/65">Ariva affordability index</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-normal md:text-4xl">{data ? formatLkr(data.total_monthly_lkr) : 'Loading'}</h1>
              <p className="mt-3 text-sm leading-6 text-paper/72">
                {data ? `${data.district}, ${data.profile} profile, ${data.confidence} confidence.` : 'Calculating current household basket.'}
              </p>
            </div>
            <WalletCards className="h-6 w-6 text-paper/70" aria-hidden="true" />
          </div>

          <div className="mt-6 grid gap-3">
            <label className="grid gap-2 text-sm font-semibold">
              District
              <select className="h-11 rounded-lg border border-paper/20 bg-paper px-3 text-sm text-ink" onChange={(event) => setDistrict(event.target.value)} value={district}>
                {districts.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <div>
              <p className="text-sm font-semibold">Profile</p>
              <div className="mt-2 grid grid-cols-3 gap-2">
                {profiles.map((item) => (
                  <button
                    key={item.key}
                    className={`h-10 rounded-lg border text-sm font-semibold ${
                      profile === item.key ? 'border-paper bg-paper text-ink' : 'border-paper/20 text-paper hover:bg-paper/10'
                    }`}
                    onClick={() => setProfile(item.key)}
                    type="button"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
            <p className="flex items-center gap-2 text-sm text-paper/72">
              <MapPin className="h-4 w-4" aria-hidden="true" />
              Generated {data ? formatDate(data.generated_at) : 'after source refresh'}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Monthly components</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">Household cost pressure</h2>
            </div>
            <Calculator className="h-5 w-5 text-muted" aria-hidden="true" />
          </div>
          <div className="mt-5 h-80">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 30, right: 24, top: 10, bottom: 10 }}>
                <CartesianGrid horizontal={false} stroke="#e6dcc8" />
                <XAxis dataKey="value" hide type="number" />
                <YAxis dataKey="name" tick={{ fill: '#6f695d', fontSize: 12 }} type="category" width={132} />
                <Tooltip formatter={(value) => formatLkr(Number(value))} />
                <Bar dataKey="value" fill="#c53a25" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Breakdown</p>
          <div className="mt-4 divide-y divide-line">
            {data?.breakdown.map((item) => (
              <div key={item.key} className="grid gap-3 py-4 md:grid-cols-[1fr_auto]">
                <div>
                  <p className="font-semibold text-ink">{item.label}</p>
                  <p className="mt-1 text-sm leading-6 text-muted">{item.note}</p>
                  <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-muted">{item.confidence} confidence</p>
                </div>
                <p className="text-xl font-semibold text-ink">{formatLkr(item.monthly_lkr)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Assumptions</p>
          <div className="mt-4 space-y-3">
            {data?.assumptions.map((assumption) => (
              <p key={assumption} className="rounded-lg border border-stone-200 bg-stone-50 p-3 text-sm leading-6 text-muted">
                {assumption}
              </p>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
