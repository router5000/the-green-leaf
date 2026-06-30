'use client'

import Link from 'next/link'

export default function LogoLink({ className, dark = false }: { className: string; dark?: boolean }) {
  return (
    <Link href="/" className={className}>
      <img
        src="/images/logo/cannabis-logo.svg"
        alt="The Strain Report logo"
        width={48}
        height={48}
        className="w-9 h-9 sm:w-12 sm:h-12 shrink-0"
      />
      <span className={`text-lg sm:text-2xl whitespace-nowrap ${dark ? 'text-white' : 'text-leaf-900'}`}>The Strain</span>
      <span className={`text-lg sm:text-2xl whitespace-nowrap ${dark ? 'text-green-300' : 'text-leaf-900'}`}>Report</span>
    </Link>
  )
}
