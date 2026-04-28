import React from "react";

interface VelocityDataPoint {
  sprint_name: string;
  estimated: number;
  actual: number;
}

interface VelocityChartProps {
  data: VelocityDataPoint[];
}

export function VelocityChart({ data }: VelocityChartProps) {
  // TODO: implement — bar chart (recharts or visx) showing estimated vs actual per sprint
  return <div className="velocity-chart">TODO: VelocityChart ({data.length} sprints)</div>;
}
