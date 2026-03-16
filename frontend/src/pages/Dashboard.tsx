import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { TrendingUp, Target, AlertTriangle, Play } from 'lucide-react'
import WinRateGauge from '../components/WinRateGauge'

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: api.dashboard })
  const { data: summary } = useQuery({
    queryKey: ['performance-summary'],
    queryFn: () => api.performanceSummary('30d'),
  })

  const handleTrigger = async () => {
    try {
      await api.triggerPipeline()
      alert('Pipeline started. Please refresh shortly.')
    } catch {
      alert('Failed to start pipeline')
    }
  }

  if (isLoading) {
    return <div className="text-slate-400">Loading...</div>
  }

  const d = data as any

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Dashboard</h2>
          <p className="text-sm text-slate-400 mt-1">Today's trading report overview</p>
        </div>
        <button
          onClick={handleTrigger}
          className="flex items-center gap-2 bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Play size={16} />
          Run Now
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-bg-card rounded-xl p-5 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <Target size={16} />
            Active Picks
          </div>
          <div className="text-2xl font-bold text-white">{d?.open_recommendations ?? 0}</div>
        </div>
        <div className="bg-bg-card rounded-xl p-5 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <TrendingUp size={16} />
            Weekly Win Rate
          </div>
          <div className="text-2xl font-bold text-accent-green">{d?.weekly_win_rate ?? 0}%</div>
        </div>
        <div className="bg-bg-card rounded-xl p-5 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <TrendingUp size={16} />
            Weekly Closed
          </div>
          <div className="text-2xl font-bold text-white">{d?.weekly_closed ?? 0}</div>
        </div>
        <div className="bg-bg-card rounded-xl p-5 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <AlertTriangle size={16} />
            Alerts Today
          </div>
          <div className="text-2xl font-bold text-accent-yellow">{d?.alerts?.length ?? 0}</div>
        </div>
      </div>

      {/* Win Rate + Latest Report */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Win Rate */}
        <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-6">30-Day Performance</h3>
          {summary ? (
            <div className="flex justify-around">
              <WinRateGauge rate={(summary as any).win_rate} label="Win Rate" />
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {(summary as any).avg_pnl >= 0 ? '+' : ''}
                  {(summary as any).avg_pnl.toFixed(1)}%
                </div>
                <div className="text-xs text-slate-400 mt-1">Avg Return</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {(summary as any).total_recommendations}
                </div>
                <div className="text-xs text-slate-400 mt-1">Total Picks</div>
              </div>
            </div>
          ) : (
            <div className="text-slate-500 text-center">No data</div>
          )}
        </div>

        {/* Latest Report */}
        <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Latest Report</h3>
          {d?.latest_report ? (
            <div>
              <div className="text-lg font-medium text-white mb-2">{d.latest_report.date}</div>
              <p className="text-sm text-slate-400 line-clamp-3">{d.latest_report.summary}</p>
              <a
                href={`/reports/${d.latest_report.id}`}
                className="inline-block mt-4 text-sm text-accent-blue hover:underline"
              >
                View Report &rarr;
              </a>
            </div>
          ) : (
            <div className="text-slate-500 text-center py-4">
              No reports generated yet.
              <br />
              <span className="text-xs">Click "Run Now" to generate your first report.</span>
            </div>
          )}
        </div>
      </div>

      {/* Today's Alerts */}
      {d?.alerts?.length > 0 && (
        <div className="bg-bg-card rounded-xl p-6 border border-accent-yellow/30">
          <h3 className="text-sm font-medium text-accent-yellow mb-4">Alerts Today</h3>
          <div className="space-y-2">
            {d.alerts.map((alert: any, i: number) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0">
                <div>
                  <span className="text-white font-medium">{alert.name}</span>
                  <span className="text-slate-400 text-sm ml-2">({alert.ticker})</span>
                </div>
                <span
                  className={`text-sm font-medium ${
                    alert.status === 'TARGET_HIT' ? 'text-accent-green' : 'text-accent-red'
                  }`}
                >
                  {alert.status === 'TARGET_HIT' ? 'Target Hit' : 'Stop Loss'}{' '}
                  {alert.pnl_percent != null && `(${alert.pnl_percent >= 0 ? '+' : ''}${alert.pnl_percent.toFixed(1)}%)`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
