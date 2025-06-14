"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

interface DynamicValueProps {
  value: number | string | null | undefined
  fallback?: string
  format?: (value: number | string) => string
  className?: string
  animate?: boolean
  precision?: number
}

export function DynamicValue({ 
  value, 
  fallback = "--", 
  format, 
  className,
  animate = true,
  precision = 1
}: DynamicValueProps) {
  const [displayValue, setDisplayValue] = useState<string>(fallback)
  const [isLoading, setIsLoading] = useState(false)
  const [previousValue, setPreviousValue] = useState<number | string | null>(null)

  useEffect(() => {
    if (value === null || value === undefined) {
      setDisplayValue(fallback)
      return
    }

    setIsLoading(true)
    
    // Simulate a brief loading state for smooth transitions
    const timer = setTimeout(() => {
      let formattedValue: string

      if (format && typeof format === 'function') {
        formattedValue = format(value)
      } else if (typeof value === 'number') {
        formattedValue = value.toFixed(precision)
      } else {
        formattedValue = String(value)
      }

      setPreviousValue(displayValue !== fallback ? value : null)
      setDisplayValue(formattedValue)
      setIsLoading(false)
    }, animate ? 100 : 0)

    return () => clearTimeout(timer)
  }, [value, format, fallback, precision, animate, displayValue])

  // Determine if the value has changed and in what direction
  const getChangeDirection = () => {
    if (!previousValue || typeof value !== 'number' || typeof previousValue !== 'number') {
      return 'none'
    }
    
    if (value > previousValue) return 'up'
    if (value < previousValue) return 'down'
    return 'same'
  }

  const changeDirection = getChangeDirection()

  return (
    <span 
      className={cn(
        "inline-block transition-all duration-300 ease-in-out",
        {
          "opacity-50": isLoading,
          "text-green-400": changeDirection === 'up' && animate,
          "text-red-400": changeDirection === 'down' && animate,
          "animate-pulse": isLoading,
        },
        className
      )}
      style={{
        transform: isLoading && animate ? 'scale(0.95)' : 'scale(1)',
      }}
    >
      {displayValue}
    </span>
  )
}

// Enhanced version with more features
export function AnimatedDynamicValue({
  value,
  fallback = "--",
  format,
  className,
  showTrend = false,
  trendThreshold = 0.1,
  duration = 300,
}: DynamicValueProps & {
  showTrend?: boolean
  trendThreshold?: number
  duration?: number
}) {
  const [displayValue, setDisplayValue] = useState<string>(fallback)
  const [previousValue, setPreviousValue] = useState<number | null>(null)
  const [trend, setTrend] = useState<'up' | 'down' | 'stable' | 'none'>('none')

  useEffect(() => {
    if (value === null || value === undefined) {
      setDisplayValue(fallback)
      setTrend('none')
      return
    }

    const numValue = typeof value === 'number' ? value : parseFloat(String(value))
    
    if (!isNaN(numValue) && previousValue !== null) {
      const change = numValue - previousValue
      const percentChange = Math.abs(change / previousValue)
      
      if (percentChange > trendThreshold) {
        setTrend(change > 0 ? 'up' : 'down')
      } else {
        setTrend('stable')
      }
    }

    const timer = setTimeout(() => {
      let formattedValue: string

      if (format && typeof format === 'function') {
        formattedValue = format(value)
      } else if (typeof value === 'number') {
        formattedValue = value.toFixed(1)
      } else {
        formattedValue = String(value)
      }

      setDisplayValue(formattedValue)
      setPreviousValue(numValue)
    }, 50)

    return () => clearTimeout(timer)
  }, [value, format, fallback, previousValue, trendThreshold])

  return (
    <span 
      className={cn(
        "inline-flex items-center gap-1 transition-all ease-in-out",
        {
          "text-green-400": trend === 'up',
          "text-red-400": trend === 'down',
          "text-gray-300": trend === 'stable' || trend === 'none',
        },
        className
      )}
      style={{
        transitionDuration: `${duration}ms`,
      }}
    >
      {displayValue}
      {showTrend && trend !== 'none' && (
        <span className="text-xs">
          {trend === 'up' && '↗'}
          {trend === 'down' && '↘'}
          {trend === 'stable' && '→'}
        </span>
      )}
    </span>
  )
}
