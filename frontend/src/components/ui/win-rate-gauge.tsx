"use client";

interface WinRateGaugeProps {
  /** Percentage value, e.g. 65.3 means 65.3% */
  value: number;
  size?: number;
}

export default function WinRateGauge({
  value,
  size = 160,
}: WinRateGaugeProps) {
  const percentage = Math.round(value);
  const fraction = value / 100;
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - fraction * circumference;
  const center = size / 2;

  // Color based on value
  let color: string;
  if (percentage >= 60) {
    color = "#10b981"; // green
  } else if (percentage >= 40) {
    color = "#eab308"; // yellow
  } else {
    color = "#ef4444"; // red
  }

  return (
    <div className="relative flex flex-col items-center gap-2">
      <svg width={size} height={size} className="-rotate-90">
        {/* Background circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#334155"
          strokeWidth="10"
        />
        {/* Progress circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: "stroke-dashoffset 0.5s ease" }}
        />
      </svg>
      <div
        className="absolute flex flex-col items-center justify-center"
        style={{ width: size, height: size }}
      >
        <span className="text-3xl font-bold" style={{ color }}>
          {percentage}%
        </span>
        <span className="text-xs text-[var(--text-secondary)]">Win Rate</span>
      </div>
    </div>
  );
}
