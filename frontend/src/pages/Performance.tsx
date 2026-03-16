import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import PerformanceChart from '../components/PerformanceChart'
import RecommendationTable from '../components/RecommendationTable'
import WinRateGauge from '../components/WinRateGauge'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const periods = ['7d', '30d', '90d'] as const

export default function Performance() {
  const [period, setPeriod] = useState<string>('30d')
  const [statusFilter, setStatusFilter] = useState('all')

  const { data: summary } = useQuery({
    queryKey: ['perf-summary', period],
    queryFn: () => api.performanceSummary(period),
  })
  const { data: timeseries } = useQuery({
    queryKey: ['perf-timeseries', period],
    queryFn: () => api.timeseries(period),
  })
  const { data: sectors } = useQuery({
    queryKey: ['perf-sectors', period],
    queryFn: () => api.sectors(period),
  })
  const { data: recs } = useQuery({
    queryKey: ['perf-recs', statusFilter],
    queryFn: () => api.recommendations(statusFilter),
  })

  const s = summary as any

  return (
    <div className="space-y-8">
      {/* Header with period selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Performance</h2>
          <p className="text-sm text-slate-400 mt-1">Track recommendation performance</p>
        </div>
        <div className="flex gap-1 bg-bg-card rounded-lg p-1 border border-slate-700">
          {periods.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                period === p ? 'bg-accent-blue text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      {s && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-bg-card rounded-xl p-4 border border-slate-700 flex flex-col items-center">
            <WinRateGauge rate={s.win_rate} label="Win Rate" />
          </div>
          <div className="bg-bg-card rounded-xl p-4 border border-slate-700 text-center">
            <div className="text-2xl font-bold text-white">{s.total_recommendations}</div>
            <div className="text-xs text-slate-400 mt-1">Total Picks</div>
          </div>
          <div className="bg-bg-card rounded-xl p-4 border border-slate-700 text-center">
            <div className={`text-2xl font-bold ${s.avg_pnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
              {s.avg_pnl >= 0 ? '+' : ''}{s.avg_pnl.toFixed(1)}%
            </div>
            <div className="text-xs text-slate-400 mt-1">Avg Return</div>
          </div>
          <div className="bg-bg-card rounded-xl p-4 border border-slate-700 text-center">
            <div className="text-lg font-bold text-accent-green">{s.best_ticker}</div>
            <div className="text-xs text-accent-green">+{s.best_pnl.toFixed(1)}%</div>
            <div className="text-xs text-slate-400 mt-1">Best Profit</div>
          </div>
          <div className="bg-bg-card rounded-xl p-4 border border-slate-700 text-center">
            <div className="text-lg font-bold text-accent-red">{s.worst_ticker}</div>
            <div className="text-xs text-accent-red">{s.worst_pnl.toFixed(1)}%</div>
            <div className="text-xs text-slate-400 mt-1">Worst Loss</div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PerformanceChart data={(timeseries as any[]) || []} />

        {/* Sector Performance */}
        <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Sector Performance</h3>
          {sectors && (sectors as any[]).length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sectors as any[]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="sector" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v: number) => `${v}%`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="win_rate" name="Win Rate" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-slate-500 text-center py-12">No sector data</div>
          )}
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-slate-300">Recommendations</h3>
          <div className="flex gap-1">
            {['all', 'open', 'target_hit', 'stop_hit'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1 rounded-md text-xs transition-colors ${
                  statusFilter === s ? 'bg-accent-blue/20 text-accent-blue' : 'text-slate-400 hover:text-white'
                }`}
              >
                {s === 'all' ? 'All' : s === 'open' ? 'Open' : s === 'target_hit' ? 'Target Hit' : 'Stop Loss'}
              </button>
            ))}
          </div>
        </div>
        <RecommendationTable data={(recs as any[]) || []} />
      </div>
    </div>
  )
}
