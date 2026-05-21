import { Map, Navigation, Radar } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'
import { PolarAngleAxis, PolarGrid, Radar as RadarShape, RadarChart, ResponsiveContainer } from 'recharts'

import { AtlasPanel } from '../components/AtlasPanel'
import { SourcePill } from '../components/SourcePill'
import { profileLabel, t } from '../i18n'
import { districts, profiles } from '../lib/format'
import type { AtlasResponse, LocaleCode, Profile } from '../types'

export function AtlasPage({
  atlas,
  district,
  locale,
  profile,
  setDistrict,
  setProfile,
}: {
  atlas: AtlasResponse | undefined
  district: string
  locale: LocaleCode
  profile: Profile
  setDistrict: Dispatch<SetStateAction<string>>
  setProfile: Dispatch<SetStateAction<Profile>>
}) {
  const selected = atlas?.selected
  const radarData = selected?.components.map((component) => ({ metric: component.label, score: component.score })) ?? []

  return (
    <div className="space-y-5">
      <section className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <AtlasPanel className="relative overflow-hidden bg-ink text-paper">
          <div className="atlas-mini-map" aria-hidden="true" />
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">{t(locale, 'atlas')}</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-normal">{selected?.district ?? district}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-paper/72">{atlas?.narrative ?? t(locale, 'districtScoreFallback')}</p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <label className="atlas-control light">
              {t(locale, 'district')}
              <select value={district} onChange={(event) => setDistrict(event.target.value)}>
                {districts.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label className="atlas-control light">
              {t(locale, 'profile')}
              <select value={profile} onChange={(event) => setProfile(event.target.value as Profile)}>
                {profiles.map((item) => (
                  <option key={item.key} value={item.key}>
                    {profileLabel(locale, item.key)}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-white/15 bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.14em] text-paper/55">{t(locale, 'lifeScore')}</p>
              <p className="mt-2 text-4xl font-semibold">{selected?.score ?? 0}</p>
            </div>
            <div className="rounded-lg border border-white/15 bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.14em] text-paper/55">{t(locale, 'grade')}</p>
              <p className="mt-2 text-4xl font-semibold">{selected?.grade ?? 'N/A'}</p>
            </div>
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2">
            <Radar className="h-5 w-5 text-steel" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'areaScores')}</h2>
          </div>
          <div className="mt-5 h-80">
            <ResponsiveContainer height="100%" width="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#d7c8a8" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#6f695d', fontSize: 12 }} />
                <RadarShape dataKey="score" fill="#315f7d" fillOpacity={0.28} stroke="#315f7d" strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <AtlasPanel>
          <div className="flex items-center gap-2">
            <Map className="h-5 w-5 text-leaf" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'districtHeatPanels')}</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {atlas?.district_scores.map((item) => (
              <button
                key={item.district}
                className={`district-tile ${item.district === district ? 'active' : ''}`}
                onClick={() => setDistrict(item.district)}
                type="button"
              >
                <span className="text-sm font-semibold">{item.district}</span>
                <span className="text-3xl font-semibold">{item.score}</span>
                <span className="text-xs uppercase tracking-[0.14em]">{t(locale, 'grade')} {item.grade}</span>
              </button>
            ))}
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2">
            <Navigation className="h-5 w-5 text-chili" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'scoreAnatomy')}</h2>
          </div>
          <div className="mt-5 space-y-3">
            {selected?.components.map((component) => (
              <div key={component.key}>
                <div className="flex justify-between gap-4 text-sm">
                  <span className="font-semibold text-ink">{component.label}</span>
                  <span className="text-muted">{component.value}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-200">
                  <div className="h-full rounded-full bg-leaf" style={{ width: `${component.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <AtlasPanel>
        <p className="atlas-label">{t(locale, 'atlasSources')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {atlas?.sources.slice(0, 12).map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </AtlasPanel>
    </div>
  )
}
