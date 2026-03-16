import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useReports(page = 1) {
  return useQuery({
    queryKey: ['reports', page],
    queryFn: () => api.reports(page),
  })
}

export function useReport(id: number) {
  return useQuery({
    queryKey: ['report', id],
    queryFn: () => api.report(id),
    enabled: id > 0,
  })
}
