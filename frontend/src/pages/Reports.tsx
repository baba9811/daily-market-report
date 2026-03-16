import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import ReportCard from '../components/ReportCard'

export default function Reports() {
  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => api.reports(1),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">리포트</h2>
        <p className="text-sm text-slate-400 mt-1">생성된 일일/주간 리포트 목록</p>
      </div>

      {isLoading ? (
        <div className="text-slate-400">로딩 중...</div>
      ) : !reports?.length ? (
        <div className="bg-bg-card rounded-xl p-12 border border-slate-700 text-center">
          <p className="text-slate-400">아직 생성된 리포트가 없습니다.</p>
          <p className="text-sm text-slate-500 mt-2">
            대시보드에서 수동 실행하거나, 스케줄러가 자동으로 생성합니다.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(reports as any[]).map((r) => (
            <ReportCard
              key={r.id}
              id={r.id}
              date={r.report_date}
              type={r.report_type}
              summary={r.summary}
              generationTime={r.generation_time_s}
            />
          ))}
        </div>
      )}
    </div>
  )
}
