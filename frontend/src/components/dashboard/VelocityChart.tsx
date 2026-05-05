import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface VelocityDataPoint {
  sprint_name: string;
  estimated: number;
  actual: number;
}

interface VelocityChartProps {
  data: VelocityDataPoint[];
}

export function VelocityChart({ data }: VelocityChartProps) {
  if (data.length === 0) {
    return (
      <div style={styles.empty}>
        <p style={styles.emptyText}>Sin datos de velocidad aún</p>
      </div>
    );
  }

  return (
    <div style={styles.wrapper}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 16, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3f55" />
          <XAxis dataKey="sprint_name" tick={{ fill: "#a0a0b0", fontSize: 12 }} />
          <YAxis tick={{ fill: "#a0a0b0", fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: "#16213e", border: "1px solid #2d3f55", borderRadius: 8 }}
            labelStyle={{ color: "#eaeaea" }}
            itemStyle={{ color: "#eaeaea" }}
          />
          <Legend wrapperStyle={{ color: "#a0a0b0", fontSize: 12 }} />
          <Bar dataKey="estimated" name="Estimado" fill="#0f3460" radius={[4, 4, 0, 0]} />
          <Bar dataKey="actual" name="Real" fill="#e94560" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: { width: "100%", padding: "4px 0" },
  empty: {
    height: 120,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  emptyText: { color: "#a0a0b0", margin: 0 },
};
