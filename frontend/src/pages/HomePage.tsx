import { ArrowRight, Bell, Bookmark, DatabaseZap, Gauge, RefreshCcw, Save, ShieldCheck, WalletCards } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { BrandMark } from '../components/BrandMark'
import { MetricTile } from '../components/MetricTile'
import { SourcePill } from '../components/SourcePill'
import { BackgroundBeams, BentoCard, BentoGrid, BorderBeam, DataRail, MetricDeck, ShimmerButton, ShimmerText, SignalMap, Spotlight } from '../components/ui/AceternityPrimitives'
import { domainLabel, profileLabel, statusLabel, t } from '../i18n'
import { districts, formatDate, formatLkrLocale, profiles, severityTone } from '../lib/format'
import type { AtlasResponse, CostCommandResponse, LifeOverviewResponse, LifePulseResponse, LocaleCode, PageKey, Profile, UtilitiesResponse } from '../types'

export function HomePage({
  atlas,
  costCommand,
  district,
  isLoading,
  lifePulse,
  locale,
  onMarkNotificationRead,
  onRefresh,
  onSaveProfile,
  overview,
  profile,
  saveProfilePending,
  setActivePage,
  setDistrict,
  setProfile,
  utilities,
}: {
  atlas: AtlasResponse | undefined
  costCommand: CostCommandResponse | undefined
  district: string
  isLoading: boolean
  lifePulse: LifePulseResponse | undefined
  locale: LocaleCode
  onMarkNotificationRead: (notificationId: number) => void
  onRefresh: () => void
  onSaveProfile: () => void
  overview: LifeOverviewResponse | undefined
  profile: Profile
  saveProfilePending: boolean
  setActivePage: Dispatch<SetStateAction<PageKey>>
  setDistrict: Dispatch<SetStateAction<string>>
  setProfile: Dispatch<SetStateAction<Profile>>
  utilities: UtilitiesResponse | undefined
}) {
  if (isLoading && !overview) {
    return (
      <div className="grid min-h-[70vh] place-items-center rounded-lg border border-line bg-white/80">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-line border-t-chili" />
          <p className="mt-4 text-sm font-semibold text-muted">{t(locale, 'loadingDesk')}</p>
        </div>
      </div>
    )
  }

  if (!overview) {
    return (
      <div className="rounded-lg border border-line bg-white p-6">
        <p className="font-semibold text-ink">{t(locale, 'noOverview')}</p>
      </div>
    )
  }

  const costItems = costCommand?.items ?? []
  const chartData = costItems.slice(0, 8).map((item) => ({ name: item.label, value: item.monthly_lkr }))
  const liveSources = Array.from(
    new Map([...(costCommand?.sources ?? []), ...(atlas?.sources ?? [])].map((source) => [source.key, source])).values(),
  ).slice(0, 8)

  return (
    <div className="space-y-5">
      <section className="hero-section">
        <BackgroundBeams />
        <Spotlight />
        <BorderBeam colorFrom="#d5aa41" colorTo="#225e45" duration={9} />
        <div className="relative grid gap-6 p-4 md:p-6 xl:grid-cols-[1.02fr_0.98fr]">
          <div className="flex min-h-[34rem] flex-col justify-between gap-8">
            <div>
              <div className="flex items-center gap-3">
                <BrandMark />
                <div>
                  <p className="text-3xl font-black leading-none tracking-normal text-paper">{t(locale, 'brandName')}</p>
                  <p className="mt-1 text-xs font-extrabold uppercase tracking-[0.18em] text-gold">{t(locale, 'livingAtlas')}</p>
                </div>
              </div>
              <h1 className="hero-title mt-9 max-w-4xl text-[clamp(3rem,6vw,6.35rem)] text-paper">
                {t(locale, 'heroTitle')}
              </h1>
              <p className="mt-6 max-w-2xl text-base font-medium leading-8 text-paper/78 md:text-lg">
                {t(locale, 'platformPromise')}
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <ShimmerButton className="min-w-[13rem]" onClick={() => setActivePage('cost')}>
                  {t(locale, 'costCommand')}
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </ShimmerButton>
                <button
                  className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/10 px-4 text-sm font-extrabold text-paper hover:bg-white/15"
                  onClick={() => setActivePage('sources')}
                  type="button"
                >
                  {t(locale, 'sources')}
                  <DatabaseZap className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            </div>

            <DataRail className="grid gap-3 p-3 sm:grid-cols-[1fr_1fr_auto]">
              <label className="atlas-control">
                {t(locale, 'district')}
                <select value={district} onChange={(event) => setDistrict(event.target.value)}>
                  {districts.map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </label>
              <label className="atlas-control">
                {t(locale, 'profile')}
                <select value={profile} onChange={(event) => setProfile(event.target.value as Profile)}>
                  {profiles.map((item) => (
                    <option key={item.key} value={item.key}>
                      {profileLabel(locale, item.key)}
                    </option>
                  ))}
                </select>
              </label>
              <button className="atlas-refresh sm:min-w-[12rem]" onClick={onRefresh} type="button">
                <RefreshCcw className="h-4 w-4" aria-hidden="true" />
                {t(locale, 'refreshData')}
              </button>
            </DataRail>
          </div>

          <div className="hero-console p-3 md:p-4">
            <BorderBeam colorFrom="#d5aa41" colorTo="#255378" duration={10} reverse />
            <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-gold"><ShimmerText>{t(locale, 'nationalPulse')}</ShimmerText></p>
                <p className="mt-1 text-sm font-semibold text-paper/65">{formatDate(costCommand?.generated_at ?? overview.generated_at)}</p>
              </div>
              <span className="rounded-lg border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-extrabold text-paper/80">{t(locale, 'publicOnly')}</span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-[0.92fr_1.08fr]">
              <div className="grid gap-3">
                <MetricTile
                  icon={WalletCards}
                  label={t(locale, 'dailyTotal')}
                  note={`${district} / ${profileLabel(locale, profile)}`}
                  tone="gold"
                  value={formatLkrLocale(costCommand?.daily_lkr ?? overview.affordability.total_monthly_lkr / 30.4, locale === 'en' ? 'en-LK' : locale)}
                />
                <MetricTile
                  icon={Gauge}
                  label={t(locale, 'areaScores')}
                  note={atlas?.narrative ?? t(locale, 'districtScoreFallback')}
                  tone="blue"
                  value={`${atlas?.selected.score ?? 0}/100`}
                />
                <MetricTile
                  icon={DatabaseZap}
                  label={t(locale, 'sourceHealth')}
                  note={`${overview.source_health.healthy} ${statusLabel(locale, 'healthy')}, ${overview.source_health.degraded} ${statusLabel(locale, 'degraded')}`}
                  tone={overview.source_health.offline ? 'red' : overview.source_health.degraded ? 'gold' : 'green'}
                  value={`${overview.source_health.average_score}/100`}
                />
              </div>
              <div className="relative grid min-h-[24rem] place-items-center overflow-hidden rounded-lg border border-white/10 bg-white/5">
                <div className="signal-ribbon absolute bottom-0 left-0 right-0 opacity-75" aria-hidden="true" />
                <SignalMap />
              </div>
            </div>
          </div>
        </div>
      </section>

      {lifePulse ? (
        <BentoGrid>
          <BentoCard beam className="md:col-span-5 xl:col-span-5" tone="leaf">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="atlas-label">Optional account</p>
                <h2 className="mt-1 text-2xl font-bold text-ink">My Ariva Pulse</h2>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {lifePulse.profile.district} / {profileLabel(locale, lifePulse.profile.profile)} / {lifePulse.profile.default_locale.toUpperCase()}
                </p>
              </div>
              <button
                className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm font-bold text-ink hover:bg-stone-50"
                disabled={saveProfilePending}
                onClick={onSaveProfile}
                type="button"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
                {saveProfilePending ? 'Saving' : 'Save filters'}
              </button>
            </div>
            <MetricDeck
              className="mt-5"
              items={[
                { icon: Bookmark, label: 'Saved watches', tone: 'steel', trend: 'up', trendLabel: 'Private pulse', value: lifePulse.saved_items.length },
                { icon: ShieldCheck, label: 'Active rules', tone: 'leaf', trend: 'up', trendLabel: 'Watching signals', value: lifePulse.alert_rules.length },
                { icon: Bell, label: 'Unread', tone: 'chili', trend: lifePulse.unread_count ? 'up' : 'flat', trendLabel: 'Needs attention', value: lifePulse.unread_count },
              ]}
            />
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              <div className="rounded-lg border border-line bg-white/65 p-3">
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">Watchlist</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.saved_items.slice(0, 3).map((item) => (
                    <p key={item.id} className="truncate text-sm font-bold text-ink">{item.label}</p>
                  ))}
                  {!lifePulse.saved_items.length ? <p className="text-sm text-muted">No saved watches</p> : null}
                </div>
              </div>
              <div className="rounded-lg border border-line bg-white/65 p-3">
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">Alert rules</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.alert_rules.slice(0, 3).map((rule) => (
                    <p key={rule.id} className="truncate text-sm font-bold text-ink">{rule.label}</p>
                  ))}
                  {!lifePulse.alert_rules.length ? <p className="text-sm text-muted">No alert rules</p> : null}
                </div>
              </div>
            </div>
          </BentoCard>

          <BentoCard beam className="md:col-span-7 xl:col-span-7" tone="steel">
            <p className="atlas-label">Consolidated notifications</p>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {lifePulse.notifications.length ? (
                lifePulse.notifications.slice(0, 4).map((notification) => (
                  <button
                    key={notification.id}
                    className={`rounded-lg border p-3 text-left ${severityTone(notification.severity)} ${notification.read_at ? 'opacity-70' : ''}`}
                    onClick={() => onMarkNotificationRead(notification.id)}
                    type="button"
                  >
                    <span className="block text-sm font-bold">{notification.title}</span>
                    <span className="mt-1 block text-xs leading-5">{notification.message}</span>
                  </button>
                ))
              ) : (
                <p className="rounded-lg border border-line bg-white/70 p-4 text-sm leading-6 text-muted">
                  No account alerts yet. Save a source or add a watch from Signals to start building your private pulse.
                </p>
              )}
            </div>
          </BentoCard>
        </BentoGrid>
      ) : null}

      <BentoGrid>
        <BentoCard beam className="md:col-span-8 xl:col-span-8" tone="leaf">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="atlas-label">{t(locale, 'nationalPulse')}</p>
              <h2 className="mt-1 text-2xl font-bold text-ink">{t(locale, 'costCommand')}</h2>
            </div>
            <ShieldCheck className="h-5 w-5 text-leaf" aria-hidden="true" />
          </div>
          <div className="mt-5 h-80">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 28, right: 24, top: 10, bottom: 10 }}>
                <CartesianGrid horizontal={false} stroke="#d7c8a8" />
                <XAxis dataKey="value" hide type="number" />
                <YAxis dataKey="name" tick={{ fill: '#6f695d', fontSize: 12, fontWeight: 700 }} type="category" width={142} />
                <Tooltip formatter={(value) => formatLkrLocale(Number(value), locale === 'en' ? 'en-LK' : locale)} />
                <Bar dataKey="value" fill="#225e45" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </BentoCard>

        <BentoCard beam dark className="md:col-span-4 xl:col-span-4" tone="gold">
          <p className="atlas-label">{t(locale, 'essentialsKicker')}</p>
          <h2 className="mt-1 text-2xl font-bold text-paper">{t(locale, 'essentialsTitle')}</h2>
          <div className="mt-5 grid gap-3">
            {overview.domains
              .filter((domain) => ['fuel', 'gas', 'utilities', 'transport'].includes(domain.key))
              .map((domain) => (
                <div key={domain.key} className="rounded-lg border border-white/10 bg-white/10 p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-bold text-paper">{domainLabel(locale, domain.key, domain.label)}</p>
                      <p className="mt-1 text-sm leading-5 text-paper/64">{domain.metrics[0]?.label}: {domain.metrics[0]?.value} {domain.metrics[0]?.unit}</p>
                    </div>
                    <span className="rounded-md border border-white/15 bg-white/10 px-2 py-1 text-xs font-bold text-paper/72">{statusLabel(locale, domain.status)}</span>
                  </div>
                </div>
              ))}
            {utilities?.gas[0] ? (
              <p className="rounded-lg border border-gold/35 bg-gold/15 p-3 text-sm font-semibold leading-6 text-[#fff0bd]">
                {t(locale, 'lpgSignal')}: {utilities.gas[0].label} {formatLkrLocale(utilities.gas[0].amount_lkr, locale === 'en' ? 'en-LK' : locale)}
              </p>
            ) : null}
          </div>
        </BentoCard>

        <BentoCard beam className="md:col-span-5 xl:col-span-5" tone="chili">
          <p className="atlas-label">{t(locale, 'publicIntelligence')}</p>
          <h2 className="mt-1 text-2xl font-bold text-ink">{t(locale, 'signalsToWatch')}</h2>
          <div className="mt-5 space-y-2">
            {overview.top_movers.map((mover) => (
              <div
                key={`${mover.label}-${mover.value}`}
                className={`flex items-start justify-between gap-4 rounded-lg border px-3 py-3 ${severityTone(mover.severity)}`}
              >
                <span className="min-w-0 text-sm font-bold">{mover.label}</span>
                <span className="text-right text-sm">{mover.value}</span>
              </div>
            ))}
          </div>
        </BentoCard>

        <BentoCard beam className="md:col-span-7 xl:col-span-7" tone="steel">
          <p className="atlas-label">{t(locale, 'sourceClassified')}</p>
          <h2 className="mt-1 text-2xl font-bold text-ink">{t(locale, 'liveSources')}</h2>
          <div className="mt-5 flex flex-wrap gap-2">
            {liveSources.map((source) => (
              <SourcePill key={source.key} locale={locale} source={source} />
            ))}
          </div>
        </BentoCard>
      </BentoGrid>
    </div>
  )
}
