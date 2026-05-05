import React from "react";
import type { ProjectStatusResult } from "../../types/project";

interface SprintOverviewProps {
  status: ProjectStatusResult | null;
}

export function SprintOverview({ status }: SprintOverviewProps) {
  if (!status) {
    return (
      <div style={styles.card}>
        <p style={styles.noData}>Sin sprint activo</p>
      </div>
    );
  }

  const pct = status.total_points > 0
    ? Math.round((status.completed_points / status.total_points) * 100)
    : 0;

  return (
    <div style={styles.card}>
      <h3 style={styles.sprintName}>{status.active_sprint_name ?? "Sprint activo"}</h3>

      <div style={styles.progressContainer}>
        <div style={styles.progressBar}>
          <div style={{ ...styles.progressFill, width: `${pct}%` }} />
        </div>
        <span style={styles.pctLabel}>{pct}%</span>
      </div>

      <div style={styles.metrics}>
        <Metric label="Completados" value={status.completed_points} unit="pts" color="#4caf50" />
        <Metric label="Restantes" value={status.remaining_points} unit="pts" color="#ff9800" />
        <Metric
          label="Días restantes"
          value={status.days_remaining ?? "--"}
          unit={status.days_remaining !== null ? "días" : ""}
          color="#2196f3"
        />
        <Metric label="Bloqueadas" value={status.blocked_task_count} unit="tareas" color="#f44336" />
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  unit,
  color,
}: {
  label: string;
  value: number | string;
  unit: string;
  color: string;
}) {
  return (
    <div style={styles.metricBox}>
      <span style={{ ...styles.metricValue, color }}>{value}</span>
      <span style={styles.metricUnit}>{unit}</span>
      <span style={styles.metricLabel}>{label}</span>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#1e2a3a",
    borderRadius: 12,
    padding: "20px 24px",
    border: "1px solid #2d3f55",
  },
  sprintName: { margin: "0 0 16px", color: "#eaeaea", fontSize: 16, fontWeight: 600 },
  noData: { color: "#a0a0b0", margin: 0, textAlign: "center", padding: "16px 0" },
  progressContainer: { display: "flex", alignItems: "center", gap: 12, marginBottom: 20 },
  progressBar: {
    flex: 1,
    height: 8,
    background: "#2d3f55",
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #0f3460, #e94560)",
    borderRadius: 4,
    transition: "width 0.6s ease",
  },
  pctLabel: { color: "#eaeaea", fontWeight: 700, minWidth: 38, textAlign: "right" },
  metrics: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 12 },
  metricBox: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    background: "#16213e",
    borderRadius: 8,
    padding: "10px 8px",
  },
  metricValue: { fontSize: 22, fontWeight: 700 },
  metricUnit: { fontSize: 11, color: "#a0a0b0", marginBottom: 2 },
  metricLabel: { fontSize: 11, color: "#7a8a9a", textAlign: "center" },
};
