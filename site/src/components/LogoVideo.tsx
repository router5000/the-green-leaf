'use client'

import React, { useRef, useEffect, useState } from 'react'
import Link from 'next/link'

function Video({ isHovered }: { isHovered: boolean }) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current && isHovered) {
      videoRef.current.currentTime = 0
      videoRef.current.play()
    }
    // On hover exit, let video continue playing to the end
  }, [isHovered])

  return (
    <video
      ref={videoRef}
      src="/images/lawn_care_center_hover.mp4"
      muted
      playsInline
      className="h-8 sm:h-10 md:h-14 lg:h-16 w-auto"
    />
  )
}

export default function LogoLink({ className }: { className: string }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Link
      href="/"
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className="text-grass-900">Lawn Care</span>
      <span className="text-amber-600">Center</span>
      <Video isHovered={isHovered} />
    </Link>
  )
}
