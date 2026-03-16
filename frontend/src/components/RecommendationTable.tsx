import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface Recommendation {
  id: number
  ticker: string
  name: string
  market: string
  direction: string
  timeframe: string
  entry_price: number
  target_price: number
  stop_loss: number
  current_price: number | null
  status: string
  pnl_percent: number | null
  created_at: string
}

const statusBadge: Record<string, { bg: string; text: string; label: string }> = {
  OPEN: { bg: 'bg-accent-blue/10', text: 'text-accent-blue', label: '진행중' },
  TARGET_HIT: { bg: 'bg-accent-green/10', text: 'text-accent-green', label: '목표달성' },
  STOP_HIT: { bg: 'bg-accent-red/10', text: 'text-accent-red', label: '손절' },
  EXPIRED: { bg: 'bg-slate-700/50', text: 'text-slate-400', label: '만료' },
}

export default function RecommendationTable({ data }: { data: Recommendation[] }) {
  if (!data.length) {
    return <div className="text-center text-slate-500 py-8">추천 종목 데이터가 없습니다</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700 text-slate-400">
            <th className="text-left py-3 px-2">종목</th>
            <th className="text-left py-3 px-2">시장</th>
            <th className="text-center py-3 px-2">방향</th>
            <th className="text-right py-3 px-2">진입가</th>
            <th className="text-right py-3 px-2">목표가</th>
            <th className="text-right py-3 px-2">손절가</th>
            <th className="text-right py-3 px-2">현재가</th>
            <th className="text-right py-3 px-2">손익</th>
            <th className="text-center py-3 px-2">상태</th>
          </tr>
        </thead>
        <tbody>
          {data.map((rec) => {
            const badge = statusBadge[rec.status] || statusBadge.OPEN
            return (
              <tr key={rec.id} className="border-b border-slate-800 hover:bg-bg-hover/50">
                <td className="py-3 px-2">
                  <div className="font-medium text-white">{rec.name}</div>
                  <div className="text-xs text-slate-500">{rec.ticker}</div>
                </td>
                <td className="py-3 px-2 text-slate-400">{rec.market}</td>
                <td className="py-3 px-2 text-center">
                  {rec.direction === 'LONG' ? (
                    <span className="inline-flex items-center gap-1 text-accent-green">
                      <ArrowUpRight size={14} /> 매수
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-accent-red">
                      <ArrowDownRight size={14} /> 매도
                    </span>
                  )}
                </td>
                <td className="py-3 px-2 text-right text-slate-300">
                  {rec.entry_price.toLocaleString()}
                </td>
                <td className="py-3 px-2 text-right text-accent-green">
                  {rec.target_price.toLocaleString()}
                </td>
                <td className="py-3 px-2 text-right text-accent-red">
                  {rec.stop_loss.toLocaleString()}
                </td>
                <td className="py-3 px-2 text-right text-slate-300">
                  {rec.current_price ? rec.current_price.toLocaleString() : '-'}
                </td>
                <td
                  className={`py-3 px-2 text-right font-medium ${
                    (rec.pnl_percent ?? 0) >= 0 ? 'text-accent-green' : 'text-accent-red'
                  }`}
                >
                  {rec.pnl_percent != null ? `${rec.pnl_percent >= 0 ? '+' : ''}${rec.pnl_percent.toFixed(1)}%` : '-'}
                </td>
                <td className="py-3 px-2 text-center">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${badge.bg} ${badge.text}`}>
                    {badge.label}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
