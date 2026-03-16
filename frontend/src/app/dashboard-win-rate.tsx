"use client";

import WinRateGauge from "@/components/ui/win-rate-gauge";

interface DashboardWinRateProps {
  value: number;
}

export default function DashboardWinRate({ value }: DashboardWinRateProps) {
  return (
    <div className="relative">
      <WinRateGauge value={value} size={180} />
    </div>
  );
}
