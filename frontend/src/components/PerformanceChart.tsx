import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface DataPoint {
  date: string
  cumulative_pnl: number
  win_rate: number
  recommendations_count: number
}

export default function PerformanceChart({ data }: { data: DataPoint[] }) {
  if (!data.length) {
    return (
      <div className="bg-bg-card rounded-xl p-6 border border-slate-700 text-center text-slate-500">
        아직 성과 데이터가 없습니다
      </div>
    )
  }

  return (
    <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
      <h3 className="text-sm font-medium text-slate-300 mb-4">누적 수익률 (P&L)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#94a3b8' }}
            tickFormatter={(v: string) => v.slice(5)}
          />
          <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v: number) => `${v}%`} />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
            labelStyle={{ color: '#e2e8f0' }}
            formatter={(value: number) => [`${value.toFixed(2)}%`, '누적 P&L']}
          />
          <Area
            type="monotone"
            dataKey="cumulative_pnl"
            stroke="#10b981"
            fillOpacity={1}
            fill="url(#pnlGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
