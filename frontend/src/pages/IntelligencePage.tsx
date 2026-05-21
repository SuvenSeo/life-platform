import { BellPlus, BookmarkPlus, Brain, Search, TrendingUp } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'

import { AtlasPanel } from '../components/AtlasPanel'
import { SourcePill } from '../components/SourcePill'
import { domainLabel, statusLabel, t } from '../i18n'
import { domainMeta, formatLkrLocale, severityTone } from '../lib/format'
import type { DomainSignal, InsightsResponse, LocaleCode, RetailOffersResponse } from '../types'

export function IntelligencePage({
  domains,
  insights,
  isSignedIn,
  locale,
  onCreateAlert,
  onSaveDomain,
  retail,
  searchQuery,
  setSearchQuery,
}: {
  domains: DomainSignal[]
  insights: InsightsResponse | undefined
  isSignedIn: boolean
  locale: LocaleCode
  onCreateAlert: (domainKey: DomainSignal['key']) => void
  onSaveDomain: (domainKey: DomainSignal['key']) => void
  retail: RetailOffersResponse | undefined
  searchQuery: string
  setSearchQuery: Dispatch<SetStateAction<string>>
}) {
  return (
    <div className="space-y-5">
      <section className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
        <AtlasPanel className="bg-ink text-paper">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-gold" aria-hidden="true" />
            <h1 className="text-3xl font-semibold tracking-normal">{t(locale, 'intelligence')}</h1>
          </div>
          <p className="mt-3 text-sm leading-6 text-paper/72">
            {t(locale, 'intelligenceIntro')}
          </p>
          <div className="relative mt-6">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-paper/55" aria-hidden="true" />
            <input
              className="h-11 w-full rounded-lg border border-white/15 bg-white/8 pl-9 pr-3 text-sm text-paper outline-none placeholder:text-paper/45"
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder={t(locale, 'search')}
              value={searchQuery}
            />
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-chili" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'publicInsightCards')}</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {insights?.insights.map((item) => (
              <article key={item.id} className={`rounded-lg border p-4 ${severityTone(item.severity)}`}>
                <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-70">{item.domain}</p>
                <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6">{item.message}</p>
              </article>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'retailSubstitution')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'publicRetailQuotes')}</h2>
          <div className="mt-5 space-y-3">
            {retail?.offers.map((offer) => (
              <div key={`${offer.item_name}-${offer.retailer}-${offer.price_lkr}`} className="flex items-start justify-between gap-4 rounded-lg border border-line bg-white/75 p-3">
                <span>
                  <span className="block font-semibold text-ink">{offer.item_name}</span>
                  <span className="block text-xs text-muted">{offer.retailer} / {offer.unit} / {offer.confidence}</span>
                </span>
                <span className="text-right font-semibold text-ink">{formatLkrLocale(offer.price_lkr, locale === 'en' ? 'en-LK' : locale)}</span>
              </div>
            ))}
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'domainMovement')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'fastestPublicSignals')}</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {domains.slice(0, 10).map((domain) => {
              const meta = domainMeta[domain.key]
              const Icon = meta.icon
              return (
                <div key={domain.key} className="rounded-lg border border-line bg-white/75 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <Icon className="h-5 w-5" style={{ color: meta.accent }} aria-hidden="true" />
                    <span className="rounded-md border border-line bg-paper px-2 py-1 text-xs font-semibold text-muted">{statusLabel(locale, domain.status)}</span>
                  </div>
                  <p className="mt-3 font-semibold text-ink">{domainLabel(locale, domain.key, domain.label)}</p>
                  <p className="mt-1 text-sm leading-5 text-muted">{domain.highlights[0]?.label}: {domain.highlights[0]?.value}</p>
                  {isSignedIn ? (
                    <div className="mt-4 flex gap-2">
                      <button
                        className="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-line bg-white px-2 text-xs font-semibold text-ink hover:bg-stone-50"
                        onClick={() => onSaveDomain(domain.key)}
                        type="button"
                      >
                        <BookmarkPlus className="h-4 w-4" aria-hidden="true" />
                        Save
                      </button>
                      <button
                        className="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-gold/40 bg-gold/10 px-2 text-xs font-semibold text-[#735313] hover:bg-gold/15"
                        onClick={() => onCreateAlert(domain.key)}
                        type="button"
                      >
                        <BellPlus className="h-4 w-4" aria-hidden="true" />
                        Alert
                      </button>
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        </AtlasPanel>
      </section>

      <AtlasPanel>
        <p className="atlas-label">{t(locale, 'insightSources')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {insights?.sources.map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </AtlasPanel>
    </div>
  )
}
