import type { ReactNode } from 'react'

export function BackgroundBeams({ className = '' }: { className?: string }) {
  return (
    <div className={`background-beams ${className}`} aria-hidden="true">
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
  return <div className={`spotlight ${className}`} aria-hidden="true" />
}

export function MovingBorderButton({
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
    <button className={`moving-border ${className}`} onClick={onClick} type={type}>
      <span className="moving-border__glow" aria-hidden="true" />
      <span className="moving-border__content">{children}</span>
    </button>
  )
}

export function ShimmerText({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={`text-shimmer ${className}`}>{children}</span>
}

export function BentoGrid({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`bento-grid ${className}`}>{children}</section>
}

export function BentoCard({
  children,
  className = '',
  dark = false,
}: {
  children: ReactNode
  className?: string
  dark?: boolean
}) {
  return <article className={`bento-card ${dark ? 'bento-card--dark' : ''} ${className}`}>{children}</article>
}

export function DataRail({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`data-rail ${className}`}>{children}</div>
}

export function SignalMap({ className = '' }: { className?: string }) {
  return (
    <svg className={`signal-map ${className}`} viewBox="0 0 240 360" role="img" aria-label="Sri Lanka signal map">
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
