'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface HeaderContextType {
  isSearchActive: boolean
  setSearchActive: (active: boolean) => void
}

const HeaderContext = createContext<HeaderContextType | undefined>(undefined)

export function HeaderProvider({ children }: { children: ReactNode }) {
  const [isSearchActive, setSearchActive] = useState(false)

  return (
    <HeaderContext.Provider value={{ isSearchActive, setSearchActive }}>
      {children}
    </HeaderContext.Provider>
  )
}

export function useHeader() {
  const context = useContext(HeaderContext)
  if (!context) {
    throw new Error('useHeader must be used within a HeaderProvider')
  }
  return context
}
