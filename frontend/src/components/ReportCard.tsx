import { Link } from 'react-router-dom'
import { FileText, Clock } from 'lucide-react'

interface ReportCardProps {
  id: number
  date: string
  type: string
  summary: string
  generationTime: number | null
}

export default function ReportCard({ id, date, type, summary, generationTime }: ReportCardProps) {
  return (
    <Link
      to={`/reports/${id}`}
      className="block bg-bg-card rounded-xl p-5 border border-slate-700 hover:border-accent-blue/50 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-accent-blue" />
          <span className="text-sm font-medium text-white">{date}</span>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            type === 'weekly'
              ? 'bg-accent-yellow/10 text-accent-yellow'
              : 'bg-accent-blue/10 text-accent-blue'
          }`}
        >
          {type === 'weekly' ? '주간' : '일일'}
        </span>
      </div>
      <p className="text-sm text-slate-400 line-clamp-2">{summary || '리포트 요약 없음'}</p>
      {generationTime && (
        <div className="flex items-center gap-1 mt-3 text-xs text-slate-500">
          <Clock size={12} />
          {generationTime.toFixed(1)}s
        </div>
      )}
    </Link>
  )
}
