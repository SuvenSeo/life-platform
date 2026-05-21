import type { ReactNode } from 'react'

export function AtlasPanel({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return <section className={`atlas-panel ${className}`}>{children}</section>
}
