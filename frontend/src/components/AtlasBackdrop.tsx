export function AtlasBackdrop() {
  return (
    <div className="atlas-backdrop" aria-hidden="true">
      <svg className="atlas-map" viewBox="0 0 220 360" role="img">
        <path
          d="M122 8c20 16 35 42 37 70 2 24-8 39-4 62 5 31 31 54 28 88-2 29-24 48-37 73-10 19-13 44-34 50-22 6-48-7-61-26-14-20-8-44-15-66-8-27-31-45-27-75 3-24 22-38 31-59 10-24 2-54 20-76C76 29 96 18 122 8Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.4"
        />
        <path d="M79 69c29 19 58 51 66 91 6 32-6 58-27 86-18 24-29 42-26 74" fill="none" stroke="currentColor" strokeWidth="1.35" />
        <path d="M57 151c31-6 65 0 103 18" fill="none" stroke="currentColor" strokeWidth="1" />
        <path d="M55 226c34 11 65 11 93 1" fill="none" stroke="currentColor" strokeWidth="1" />
        <path d="M39 289c32-14 68-13 111 3" fill="none" stroke="currentColor" strokeWidth="0.9" />
        <circle cx="96" cy="112" r="4" fill="#d5aa41" />
        <circle cx="134" cy="178" r="3.4" fill="#d5aa41" />
        <circle cx="86" cy="245" r="3.2" fill="#d5aa41" />
        <path d="M27 316c42-30 85-23 128-5" fill="none" stroke="#d5aa41" strokeLinecap="round" strokeWidth="2" opacity="0.75" />
      </svg>
    </div>
  )
}
