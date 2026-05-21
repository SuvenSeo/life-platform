import { ArrowRight, Bell, Bookmark, DatabaseZap, Gauge, RefreshCcw, Save, ShieldCheck, WalletCards } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { AtlasBackdrop } from '../components/AtlasBackdrop'
import { AtlasPanel } from '../components/AtlasPanel'
import { MetricTile } from '../components/MetricTile'
import { SourcePill } from '../components/SourcePill'
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
      <section className="hero-atlas relative overflow-hidden rounded-xl border border-white/20 bg-ink text-paper shadow-[0_34px_90px_-60px_rgba(0,0,0,.85)]">
        <AtlasBackdrop />
        <div className="relative grid gap-5 p-5 md:p-7 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="flex min-h-[31rem] flex-col justify-between">
            <div>
              <div className="mb-5 flex flex-wrap gap-2">
                <span className="atlas-chip">{t(locale, 'publicOnly')}</span>
                <span className="atlas-chip">{t(locale, 'noAccounts')}</span>
              </div>
              <h1 className="max-w-4xl text-4xl font-semibold leading-[1.02] tracking-normal md:text-6xl">
                {t(locale, 'livingAtlas')}
              </h1>
              <p className="mt-5 max-w-3xl text-base leading-7 text-paper/74">
                {t(locale, 'platformPromise')}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
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
              <button className="atlas-action" onClick={() => setActivePage('cost')} type="button">
                {t(locale, 'costCommand')}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </div>

          <div className="grid gap-3">
            <MetricTile
              icon={WalletCards}
              label={t(locale, 'dailyTotal')}
                note={`${district} / ${profileLabel(locale, profile)} / ${formatDate(costCommand?.generated_at ?? overview.generated_at)}`}
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
              note={`${overview.source_health.healthy} ${statusLabel(locale, 'healthy')}, ${overview.source_health.degraded} ${statusLabel(locale, 'degraded')}, ${overview.source_health.offline} ${statusLabel(locale, 'offline')}`}
              tone={overview.source_health.offline ? 'red' : overview.source_health.degraded ? 'gold' : 'green'}
              value={`${overview.source_health.average_score}/100`}
            />
            <button className="atlas-refresh" onClick={onRefresh} type="button">
              <RefreshCcw className="h-4 w-4" aria-hidden="true" />
              {t(locale, 'refreshData')}
            </button>
          </div>
        </div>
      </section>

      {lifePulse ? (
        <section className="grid gap-5 xl:grid-cols-[0.86fr_1.14fr]">
          <AtlasPanel>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="atlas-label">Optional account</p>
                <h2 className="mt-1 text-2xl font-semibold text-ink">My Life Pulse</h2>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {lifePulse.profile.district} / {profileLabel(locale, lifePulse.profile.profile)} / {lifePulse.profile.default_locale.toUpperCase()}
                </p>
              </div>
              <button
                className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm font-semibold text-ink hover:bg-stone-50"
                disabled={saveProfilePending}
                onClick={onSaveProfile}
                type="button"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
                {saveProfilePending ? 'Saving' : 'Save filters'}
              </button>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-line bg-white/70 p-3">
                <Bookmark className="h-4 w-4 text-steel" aria-hidden="true" />
                <p className="mt-2 text-2xl font-semibold text-ink">{lifePulse.saved_items.length}</p>
                <p className="text-sm text-muted">Saved watches</p>
              </div>
              <div className="rounded-lg border border-line bg-white/70 p-3">
                <ShieldCheck className="h-4 w-4 text-leaf" aria-hidden="true" />
                <p className="mt-2 text-2xl font-semibold text-ink">{lifePulse.alert_rules.length}</p>
                <p className="text-sm text-muted">Active rules</p>
              </div>
              <div className="rounded-lg border border-line bg-white/70 p-3">
                <Bell className="h-4 w-4 text-chili" aria-hidden="true" />
                <p className="mt-2 text-2xl font-semibold text-ink">{lifePulse.unread_count}</p>
                <p className="text-sm text-muted">Unread</p>
              </div>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              <div className="rounded-lg border border-line bg-white/60 p-3">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Watchlist</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.saved_items.slice(0, 3).map((item) => (
                    <p key={item.id} className="truncate text-sm font-semibold text-ink">{item.label}</p>
                  ))}
                  {!lifePulse.saved_items.length ? <p className="text-sm text-muted">No saved watches</p> : null}
                </div>
              </div>
              <div className="rounded-lg border border-line bg-white/60 p-3">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Alert rules</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.alert_rules.slice(0, 3).map((rule) => (
                    <p key={rule.id} className="truncate text-sm font-semibold text-ink">{rule.label}</p>
                  ))}
                  {!lifePulse.alert_rules.length ? <p className="text-sm text-muted">No alert rules</p> : null}
                </div>
              </div>
            </div>
          </AtlasPanel>

          <AtlasPanel>
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
                    <span className="block text-sm font-semibold">{notification.title}</span>
                    <span className="mt-1 block text-xs leading-5">{notification.message}</span>
                  </button>
                ))
              ) : (
                <p className="rounded-lg border border-line bg-white/70 p-4 text-sm leading-6 text-muted">
                  No account alerts yet. Save a source or add a watch from Intelligence to start building your private pulse.
                </p>
              )}
            </div>
          </AtlasPanel>
        </section>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <AtlasPanel>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="atlas-label">{t(locale, 'nationalPulse')}</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'costCommand')}</h2>
            </div>
            <ShieldCheck className="h-5 w-5 text-leaf" aria-hidden="true" />
          </div>
          <div className="mt-5 h-80">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 28, right: 24, top: 10, bottom: 10 }}>
                <CartesianGrid horizontal={false} stroke="#d7c8a8" />
                <XAxis dataKey="value" hide type="number" />
                <YAxis dataKey="name" tick={{ fill: '#6f695d', fontSize: 12 }} type="category" width={142} />
                <Tooltip formatter={(value) => formatLkrLocale(Number(value), locale === 'en' ? 'en-LK' : locale)} />
                <Bar dataKey="value" fill="#2f6a4f" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'essentialsKicker')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'essentialsTitle')}</h2>
          <div className="mt-5 grid gap-3">
            {overview.domains
              .filter((domain) => ['fuel', 'gas', 'utilities', 'transport'].includes(domain.key))
              .map((domain) => (
                <div key={domain.key} className="rounded-lg border border-line/80 bg-white/70 p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-ink">{domainLabel(locale, domain.key, domain.label)}</p>
                      <p className="mt-1 text-sm leading-5 text-muted">{domain.metrics[0]?.label}: {domain.metrics[0]?.value} {domain.metrics[0]?.unit}</p>
                    </div>
                    <span className="rounded-md border border-line bg-paper px-2 py-1 text-xs font-semibold text-muted">{statusLabel(locale, domain.status)}</span>
                  </div>
                </div>
              ))}
            {utilities?.gas[0] ? (
              <p className="rounded-lg border border-gold/30 bg-gold/10 p-3 text-sm leading-6 text-[#72520f]">
                {t(locale, 'lpgSignal')}: {utilities.gas[0].label} {formatLkrLocale(utilities.gas[0].amount_lkr, locale === 'en' ? 'en-LK' : locale)}
              </p>
            ) : null}
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.82fr_1.18fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'publicIntelligence')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'signalsToWatch')}</h2>
          <div className="mt-5 space-y-2">
            {overview.top_movers.map((mover) => (
              <div
                key={`${mover.label}-${mover.value}`}
                className={`flex items-start justify-between gap-4 rounded-lg border px-3 py-3 ${severityTone(mover.severity)}`}
              >
                <span className="min-w-0 text-sm font-semibold">{mover.label}</span>
                <span className="text-right text-sm">{mover.value}</span>
              </div>
            ))}
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'sourceClassified')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'liveSources')}</h2>
          <div className="mt-5 flex flex-wrap gap-2">
            {liveSources.map((source) => (
              <SourcePill key={source.key} locale={locale} source={source} />
            ))}
          </div>
        </AtlasPanel>
      </section>
    </div>
  )
}
