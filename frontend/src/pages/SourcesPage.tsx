import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, DatabaseZap, ExternalLink } from 'lucide-react'

import { AtlasPanel } from '../components/AtlasPanel'
import { SourcePill } from '../components/SourcePill'
import { BackgroundBeams, BorderBeam, Spotlight } from '../components/ui/AceternityPrimitives'
import { domainLabel, sourceTypeLabel, statusLabel, t } from '../i18n'
import { getPipeline } from '../lib/api'
import { domainMeta, formatDate, sourceTypeTone, statusTone } from '../lib/format'
import type { DomainSignal, LocaleCode, SourceType } from '../types'

const sourceClasses = [
  { type: 'official', labelKey: 'sourceClassOfficial' },
  { type: 'retail', labelKey: 'sourceClassRetail' },
  { type: 'platform', labelKey: 'sourceClassPlatform' },
  { type: 'derived', labelKey: 'sourceClassDerived' },
] as const satisfies Array<{ type: SourceType; labelKey: 'sourceClassOfficial' | 'sourceClassRetail' | 'sourceClassPlatform' | 'sourceClassDerived' }>

export function SourcesPage({ domains, locale }: { domains: DomainSignal[]; locale: LocaleCode }) {
  const pipeline = useQuery({
    queryKey: ['life-pipeline'],
    queryFn: getPipeline,
  })
  const data = pipeline.data
  const sources = domains.flatMap((domain) => domain.sources)
  const uniqueSources = Array.from(new Map(sources.map((source) => [source.key, source])).values())

  return (
    <div className="space-y-5">
      <AtlasPanel className="bg-ink text-paper">
        <BackgroundBeams />
        <Spotlight />
        <BorderBeam colorFrom="#d5aa41" colorTo="#225e45" duration={8} />
        <div className="grid gap-5 lg:grid-cols-[1fr_16rem]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">{t(locale, 'sourceRegistry')}</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal">{t(locale, 'sources')}</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-paper/72">
              {t(locale, 'sourceRegistryIntro')}
            </p>
          </div>
          <div className="source-network border border-white/15 bg-white/10">
            <span className={`relative z-10 m-3 inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${data ? statusTone(data.overall_status) : 'border-white/20 bg-white/10 text-paper/70'}`}>
              <DatabaseZap className="h-4 w-4" aria-hidden="true" />
              {data ? statusLabel(locale, data.overall_status) : statusLabel(locale, 'loading')}
            </span>
          </div>
        </div>
      </AtlasPanel>

      <section className="grid gap-5 xl:grid-cols-[1.12fr_0.88fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'upstreamHealth')}</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-[0.14em] text-muted">
                  <th className="py-3 pr-4">{t(locale, 'domain')}</th>
                  <th className="py-3 pr-4">{t(locale, 'status')}</th>
                  <th className="py-3 pr-4">{t(locale, 'score')}</th>
                  <th className="py-3 pr-4">{t(locale, 'lastUpdate')}</th>
                  <th className="py-3">{t(locale, 'freshnessNote')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {(data?.domains ?? []).map((domain) => (
                  <tr key={domain.domain}>
                    <td className="py-3 pr-4 font-semibold text-ink">{domainLabel(locale, domain.domain, domain.label)}</td>
                    <td className="py-3 pr-4">
                      <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${statusTone(domain.status)}`}>{statusLabel(locale, domain.status)}</span>
                    </td>
                    <td className="py-3 pr-4 text-muted">{domain.health_score}/100</td>
                    <td className="py-3 pr-4 text-muted">{formatDate(domain.last_updated_at)}</td>
                    <td className="py-3 text-muted">{domain.freshness_note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'sourceClasses')}</p>
          <div className="mt-4 space-y-3">
            {sourceClasses.map((item) => (
              <div key={item.type} className={`rounded-lg border p-3 ${sourceTypeTone(item.type)}`}>
                <p className="font-semibold">{sourceTypeLabel(locale, item.type)}</p>
                <p className="mt-1 text-sm leading-5 opacity-75">{t(locale, item.labelKey)}</p>
              </div>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'currentAdapters')}</p>
          <div className="mt-4 space-y-3">
            {domains.map((domain) => {
              const meta = domainMeta[domain.key]
              const Icon = meta.icon
              return (
                <a
                  key={domain.key}
                  className="flex items-start gap-3 rounded-lg border border-line bg-white/70 p-3 hover:border-stone-300"
                  href={domain.homepage_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white" style={{ color: meta.accent }}>
                    <Icon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  <span className="min-w-0">
                    <span className="block font-semibold text-ink">{domainLabel(locale, domain.key, domain.label)}</span>
                    <span className="block break-all text-xs text-muted">{domain.category}</span>
                  </span>
                  <ExternalLink className="ml-auto h-4 w-4 shrink-0 text-muted" aria-hidden="true" />
                </a>
              )
            })}
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2 text-emerald-800">
            <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
            <h2 className="text-xl font-semibold">{t(locale, 'activeSourceRegistry')}</h2>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {uniqueSources.map((source) => (
              <SourcePill key={source.key} locale={locale} source={source} />
            ))}
          </div>
        </AtlasPanel>
      </section>

      <AtlasPanel>
        <div className="flex items-center gap-2 text-amber-800">
          <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          <h2 className="text-xl font-semibold">{t(locale, 'dataLimits')}</h2>
        </div>
        <div className="mt-4 grid gap-3 text-sm leading-6 text-muted md:grid-cols-3">
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit1')}</p>
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit2')}</p>
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit3')}</p>
        </div>
      </AtlasPanel>
    </div>
  )
}
