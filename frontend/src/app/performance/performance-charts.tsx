"use client";

import PerformanceChart from "@/components/features/performance-chart";

interface PerformanceChartsProps {
  dates: string[];
  winRates: number[];
  cumulativeReturns: number[];
}

export default function PerformanceCharts({
  dates,
  winRates,
  cumulativeReturns,
}: PerformanceChartsProps) {
  return (
    <PerformanceChart
      dates={dates}
      winRates={winRates}
      cumulativeReturns={cumulativeReturns}
    />
  );
}
