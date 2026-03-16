"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface PerformanceChartProps {
  dates: string[];
  /** Already percentage values (e.g. 65.3 = 65.3%) */
  winRates: number[];
  /** Already percentage values */
  cumulativeReturns: number[];
}

export default function PerformanceChart({
  dates,
  winRates,
  cumulativeReturns,
}: PerformanceChartProps) {
  const data = dates.map((date, i) => ({
    date: new Date(date).toLocaleDateString("en-US", {
      month: "2-digit",
      day: "2-digit",
    }),
    winRate: Math.round(winRates[i]),
    cumulativeReturn: Math.round(cumulativeReturns[i] * 10) / 10,
  }));

  return (
    <div className="h-[350px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
          />
          <YAxis
            yAxisId="left"
            stroke="#94a3b8"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            tickFormatter={(v: number) => `${v}%`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#94a3b8"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            tickFormatter={(v: number) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "0.5rem",
              color: "#e2e8f0",
            }}
          />
          <Legend
            wrapperStyle={{ color: "#94a3b8" }}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="winRate"
            name="Win Rate (%)"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cumulativeReturn"
            name="Cumulative Return (%)"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
