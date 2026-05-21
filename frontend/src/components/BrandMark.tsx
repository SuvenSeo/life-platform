export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <span className={`brand-mark ${compact ? 'brand-mark-compact' : ''}`} aria-hidden="true">
      <svg viewBox="0 0 44 44" role="img">
        <path
          d="M25.8 4.2c4.1 3.4 7 8.4 7.2 13.7.2 4.5-2.1 7.4-1.1 11.4.9 3.9 4.6 6.8 4.1 10.6-.5 3.9-4.4 5.8-8.4 5.2-4.4-.7-7-4.4-8-8.1-.8-3.1-.4-6.2-2.6-8.9-2.4-2.9-6.1-4.8-5.6-8.9.4-3.5 3.4-5.7 4.6-8.8 1.3-3.2.5-7 3.5-9.1 1.8-1.2 4-.2 6.3 2.9Z"
          fill="currentColor"
          opacity="0.95"
        />
        <path d="M18.4 14.4c5.1 2.7 10 7.2 11 13.8.6 4.3-1 8-4.3 12.3" fill="none" stroke="#11130f" strokeLinecap="round" strokeWidth="2.1" />
        <path d="M14.8 23.5c5.8-1.4 12.4-.4 18.5 2.8" fill="none" stroke="#11130f" strokeLinecap="round" strokeWidth="1.45" />
      </svg>
    </span>
  )
}
