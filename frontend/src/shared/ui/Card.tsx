import { cn } from '@shared/lib/cn'
import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  onClick?: () => void
}

export const Card = ({ children, className, onClick }: CardProps) => (
  <div
    className={cn(
      'bg-bg-card border border-border-subtle rounded-card',
      onClick && 'cursor-pointer hover:bg-bg-card-hover transition-colors',
      className,
    )}
    onClick={onClick}
  >
    {children}
  </div>
)
