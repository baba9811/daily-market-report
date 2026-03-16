import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { TrendingUp, TrendingDown, Calendar } from 'lucide-react'

export default function Retrospective() {
  const { data: weekly, isLoading: loadingWeekly } = useQuery({
    queryKey: ['weekly-analyses'],
    queryFn: api.weeklyAnalyses,
  })
  const { data: dailyChecks } = useQuery({
    queryKey: ['daily-checks'],
    queryFn: api.dailyChecks,
  })

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white">Retrospective</h2>
        <p className="text-sm text-slate-400 mt-1">Weekly analysis and daily check records</p>
      </div>

      {/* Daily Checks */}
      <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-4">Daily Checks</h3>
        {dailyChecks && (dailyChecks as any[]).length > 0 ? (
          <div className="grid grid-cols-7 gap-2">
            {(dailyChecks as any[]).map((check: any) => (
              <div
                key={check.id}
                className="bg-bg-primary rounded-lg p-3 text-center border border-slate-800"
              >
                <div className="text-xs text-slate-400 mb-1">{check.report_date.slice(5)}</div>
                <div className="flex justify-center gap-2 text-xs">
                  {check.targets_hit > 0 && (
                    <span className="flex items-center gap-0.5 text-accent-green">
                      <TrendingUp size={10} /> {check.targets_hit}
                    </span>
                  )}
                  {check.stops_hit > 0 && (
                    <span className="flex items-center gap-0.5 text-accent-red">
                      <TrendingDown size={10} /> {check.stops_hit}
                    </span>
                  )}
                  {check.targets_hit === 0 && check.stops_hit === 0 && (
                    <span className="text-slate-600">-</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-slate-500 text-center py-6">No check records</div>
        )}
      </div>

      {/* Weekly Analyses */}
      <div>
        <h3 className="text-sm font-medium text-slate-300 mb-4">Weekly Analysis</h3>
        {loadingWeekly ? (
          <div className="text-slate-400">Loading...</div>
        ) : !weekly?.length ? (
          <div className="bg-bg-card rounded-xl p-12 border border-slate-700 text-center text-slate-500">
            No weekly analysis data yet. Will be generated after the first Monday report.
          </div>
        ) : (
          <div className="space-y-4">
            {(weekly as any[]).map((w: any) => (
              <div key={w.id} className="bg-bg-card rounded-xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-accent-blue" />
                    <span className="font-medium text-white">
                      {w.week_start} ~ {w.week_end}
                    </span>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <span className="text-accent-green">W: {w.win_count}</span>
                    <span className="text-accent-red">L: {w.loss_count}</span>
                    <span className={w.avg_return_pct >= 0 ? 'text-accent-green' : 'text-accent-red'}>
                      Avg: {w.avg_return_pct >= 0 ? '+' : ''}{w.avg_return_pct?.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">Total: </span>
                    <span className="text-white">{w.total_recommendations}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Best: </span>
                    <span className="text-accent-green">{w.best_pick_ticker || '-'}</span>
                    <span className="text-slate-400 mx-2">Worst: </span>
                    <span className="text-accent-red">{w.worst_pick_ticker || '-'}</span>
                  </div>
                </div>
                {w.analysis_text && (
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 whitespace-pre-line line-clamp-6">
                      {w.analysis_text.slice(0, 500)}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
