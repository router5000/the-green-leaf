'use client'

import Link from 'next/link'

export default function LogoLink({ className, dark = false }: { className: string; dark?: boolean }) {
  return (
    <Link href="/" className={className}>
      <img
        src="/images/logo/cannabis-logo.svg"
        alt="The Green Leaf logo"
        width={48}
        height={48}
        style={{ width: '48px', height: '48px' }}
      />
      <span className={dark ? 'text-white' : 'text-leaf-900'} style={{ fontSize: '24px' }}>The Green</span>
      <span className={dark ? 'text-green-300' : 'text-leaf-900'} style={{ fontSize: '24px' }}>Leaf</span>
    </Link>
  )
}
