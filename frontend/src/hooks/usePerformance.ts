import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function usePerformanceSummary(period = '30d') {
  return useQuery({
    queryKey: ['performance-summary', period],
    queryFn: () => api.performanceSummary(period),
  })
}

export function useTimeseries(period = '30d') {
  return useQuery({
    queryKey: ['timeseries', period],
    queryFn: () => api.timeseries(period),
  })
}

export function useSectors(period = '30d') {
  return useQuery({
    queryKey: ['sectors', period],
    queryFn: () => api.sectors(period),
  })
}
