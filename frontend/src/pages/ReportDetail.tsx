import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { ArrowLeft, Clock, Calendar } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ReportDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: report, isLoading } = useQuery({
    queryKey: ['report', id],
    queryFn: () => api.report(Number(id)),
    enabled: !!id,
  })

  if (isLoading) return <div className="text-slate-400">Loading...</div>
  if (!report) return <div className="text-slate-400">Report not found</div>

  const r = report as any

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          to="/reports"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={16} /> Back
        </Link>
        <div className="flex items-center gap-4 text-sm text-slate-400">
          <span className="flex items-center gap-1">
            <Calendar size={14} /> {r.report_date}
          </span>
          {r.generation_time_s && (
            <span className="flex items-center gap-1">
              <Clock size={14} /> {r.generation_time_s.toFixed(1)}s
            </span>
          )}
          <span
            className={`px-2 py-0.5 rounded-full text-xs ${
              r.report_type === 'weekly'
                ? 'bg-accent-yellow/10 text-accent-yellow'
                : 'bg-accent-blue/10 text-accent-blue'
            }`}
          >
            {r.report_type === 'weekly' ? 'Weekly' : 'Daily'}
          </span>
        </div>
      </div>

      {/* Embedded HTML report */}
      <div className="bg-white rounded-xl overflow-hidden">
        <iframe
          srcDoc={r.html_content}
          title="Report"
          className="w-full border-0"
          style={{ minHeight: '80vh' }}
          sandbox="allow-same-origin"
        />
      </div>
    </div>
  )
}
