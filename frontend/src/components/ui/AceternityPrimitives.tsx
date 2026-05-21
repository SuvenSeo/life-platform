import type { CSSProperties, ElementType, InputHTMLAttributes, PointerEvent, ReactNode } from 'react'
import { TrendingDown, TrendingUp } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

type Tone = 'gold' | 'leaf' | 'steel' | 'chili' | 'clay' | 'paper'

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export function BackgroundBeams({ className = '' }: { className?: string }) {
  return (
    <div className={cn('background-beams', className)} aria-hidden="true">
      <svg viewBox="0 0 1200 720" preserveAspectRatio="none">
        <path d="M-120 120C190 20 392 178 655 105C858 49 969-42 1320 28" />
        <path d="M-160 420C160 286 344 448 604 346C841 253 994 219 1330 304" />
        <path d="M-120 650C190 502 399 635 681 531C902 450 1065 460 1320 392" />
        <path d="M90-80C282 132 224 322 406 520C490 611 585 673 732 790" />
        <path d="M1012-90C850 118 874 332 713 504C630 594 530 666 405 785" />
      </svg>
    </div>
  )
}

export function Spotlight({ className = '' }: { className?: string }) {
  return <div className={cn('spotlight', className)} aria-hidden="true" />
}

export function BorderBeam({
  className = '',
  colorFrom = '#d5aa41',
  colorTo = '#255378',
  delay = 0,
  duration = 8,
  reverse = false,
  width = 1,
}: {
  className?: string
  colorFrom?: string
  colorTo?: string
  delay?: number
  duration?: number
  reverse?: boolean
  width?: number
}) {
  return (
    <span
      className={cn('border-beam', reverse && 'border-beam--reverse', className)}
      style={
        {
          '--beam-delay': `${delay}s`,
          '--beam-duration': `${duration}s`,
          '--beam-from': colorFrom,
          '--beam-to': colorTo,
          '--beam-width': `${width}px`,
        } as CSSProperties
      }
      aria-hidden="true"
    />
  )
}

export function ShimmerButton({
  children,
  className = '',
  onClick,
  type = 'button',
}: {
  children: ReactNode
  className?: string
  onClick?: () => void
  type?: 'button' | 'submit'
}) {
  return (
    <button className={cn('shimmer-button', className)} onClick={onClick} type={type}>
      <span className="shimmer-button__spark" aria-hidden="true" />
      <span className="shimmer-button__backdrop" aria-hidden="true" />
      <span className="shimmer-button__content">{children}</span>
    </button>
  )
}

export function ShimmerText({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={cn('text-shimmer', className)}>{children}</span>
}

export function MagicCard({
  as,
  children,
  className = '',
  glowFrom = '#d5aa41',
  glowTo = '#255378',
}: {
  as?: ElementType
  children: ReactNode
  className?: string
  glowFrom?: string
  glowTo?: string
}) {
  const Component = as ?? 'div'

  function handlePointerMove(event: PointerEvent<HTMLElement>) {
    const rect = event.currentTarget.getBoundingClientRect()
    event.currentTarget.style.setProperty('--mouse-x', `${event.clientX - rect.left}px`)
    event.currentTarget.style.setProperty('--mouse-y', `${event.clientY - rect.top}px`)
  }

  return (
    <Component
      className={cn('magic-card', className)}
      onPointerMove={handlePointerMove}
      style={
        {
          '--glow-from': glowFrom,
          '--glow-to': glowTo,
        } as CSSProperties
      }
    >
      <span className="magic-card__glow" aria-hidden="true" />
      {children}
    </Component>
  )
}

export function BentoGrid({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={cn('bento-grid', className)}>{children}</section>
}

export function BentoCard({
  children,
  className = '',
  dark = false,
  beam = false,
  tone = 'gold',
}: {
  children: ReactNode
  className?: string
  dark?: boolean
  beam?: boolean
  tone?: Tone
}) {
  const beamColors: Record<Tone, [string, string]> = {
    gold: ['#d5aa41', '#c97835'],
    leaf: ['#d5aa41', '#225e45'],
    steel: ['#d5aa41', '#255378'],
    chili: ['#d5aa41', '#912a20'],
    clay: ['#c97835', '#912a20'],
    paper: ['#f7f0e2', '#d5aa41'],
  }
  const [colorFrom, colorTo] = beamColors[tone]

  return (
    <MagicCard as="article" className={cn('bento-card', dark && 'bento-card--dark', className)} glowFrom={colorFrom} glowTo={colorTo}>
      {beam ? <BorderBeam colorFrom={colorFrom} colorTo={colorTo} delay={tone === 'steel' ? 1.2 : 0} /> : null}
      {children}
    </MagicCard>
  )
}

export function BentoGridShowcase({
  className = '',
  featureTags,
  integrations,
  journey,
  mainFeature,
  secondaryFeature,
  statistic,
}: {
  className?: string
  featureTags: ReactNode
  integrations: ReactNode
  journey: ReactNode
  mainFeature: ReactNode
  secondaryFeature: ReactNode
  statistic: ReactNode
}) {
  return (
    <section className={cn('bento-showcase', className)}>
      <div className="bento-showcase__slot">{integrations}</div>
      <div className="bento-showcase__slot bento-showcase__slot--tall">{mainFeature}</div>
      <div className="bento-showcase__slot">{featureTags}</div>
      <div className="bento-showcase__slot">{secondaryFeature}</div>
      <div className="bento-showcase__slot bento-showcase__slot--double">{statistic}</div>
      <div className="bento-showcase__slot">{journey}</div>
    </section>
  )
}

export function DataRail({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={cn('data-rail', className)}>{children}</div>
}

export function IconInput({
  className = '',
  icon: Icon,
  inputClassName = '',
  label,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  className?: string
  icon: LucideIcon
  inputClassName?: string
  label?: string
}) {
  return (
    <label className={cn('icon-input', className)}>
      <Icon className="icon-input__icon" aria-hidden="true" />
      <input aria-label={label} className={cn('icon-input__field', inputClassName)} {...props} />
    </label>
  )
}

export function MetricDeck({
  className = '',
  items,
}: {
  className?: string
  items: Array<{
    description?: string
    icon?: LucideIcon
    label: string
    tone?: Tone
    trend?: 'up' | 'down' | 'flat'
    trendLabel?: string
    value: string | number
  }>
}) {
  return (
    <div className={cn('metric-deck', className)}>
      {items.map((item) => {
        const Icon = item.icon
        const TrendIcon = item.trend === 'down' ? TrendingDown : TrendingUp

        return (
          <MagicCard key={item.label} className={cn('metric-card', item.tone && `metric-card--${item.tone}`)}>
            <div className="metric-card__top">
              <div>
                <p className="metric-card__label">{item.label}</p>
                <p className="metric-card__value">{item.value}</p>
              </div>
              {Icon ? <Icon className="metric-card__icon" aria-hidden="true" /> : null}
            </div>
            <div className="metric-card__footer">
              {item.trend && item.trend !== 'flat' ? <TrendIcon className="h-4 w-4" aria-hidden="true" /> : null}
              <span>{item.trendLabel ?? item.description ?? 'Current signal'}</span>
            </div>
            {item.description && item.trendLabel ? <p className="metric-card__description">{item.description}</p> : null}
          </MagicCard>
        )
      })}
    </div>
  )
}

export function FloatingSurface({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={cn('floating-surface', className)}>{children}</div>
}

export function SignalMap({ className = '' }: { className?: string }) {
  return (
    <svg className={cn('signal-map', className)} viewBox="0 0 240 360" role="img" aria-label="Sri Lanka signal map">
      <path
        d="M132 12c23 18 38 49 39 80 1 27-10 44-4 70 7 35 34 60 31 99-2 33-28 54-42 82-11 22-16 50-40 57-25 7-55-8-70-30-16-23-9-51-18-76-10-30-36-51-32-85 3-27 24-43 35-66 12-27 2-61 23-87 18-22 42-35 78-44Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
      />
      <path d="M86 72c33 21 66 57 76 103 7 36-7 65-30 96-20 27-33 47-30 84" fill="none" stroke="currentColor" strokeWidth="1.25" />
      <path d="M55 158c39-10 82-2 129 22" fill="none" stroke="currentColor" strokeWidth="1" />
      <path d="M58 233c38 13 78 13 115 0" fill="none" stroke="currentColor" strokeWidth="1" />
      <path d="M41 315c47-33 94-25 143-4" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="2" />
      <circle cx="104" cy="112" r="4.5" />
      <circle cx="150" cy="183" r="4" />
      <circle cx="92" cy="255" r="4" />
      <circle cx="133" cy="313" r="3.5" />
    </svg>
  )
}
