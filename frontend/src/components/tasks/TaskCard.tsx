import React, { useState } from "react";
import type { Task } from "../../types/task";

const PRIORITY_COLORS: Record<Task["priority"], string> = {
  critical: "#f44336",
  high: "#ff9800",
  medium: "#ffeb3b",
  low: "#4caf50",
};

const STATUS_LABELS: Record<Task["status"], string> = {
  backlog: "Backlog",
  todo: "Por hacer",
  in_progress: "En progreso",
  in_review: "En revisión",
  done: "Hecho",
};

interface TaskCardProps {
  task: Task;
  onStatusChange?: (taskId: string, status: Task["status"]) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskCard({ task, onStatusChange, onDelete }: TaskCardProps) {
  const [isChangingStatus, setIsChangingStatus] = useState(false);

  const handleStatusChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStatus = e.target.value as Task["status"];
    setIsChangingStatus(true);
    try {
      await onStatusChange?.(task.id, newStatus);
    } finally {
      setIsChangingStatus(false);
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span
          style={{
            ...styles.priorityDot,
            background: PRIORITY_COLORS[task.priority],
          }}
          title={`Prioridad: ${task.priority}`}
        />
        <span style={styles.type}>{task.type}</span>
        {task.estimated_points != null && (
          <span style={styles.points}>{task.estimated_points} pts</span>
        )}
      </div>

      <p style={styles.title}>{task.title}</p>

      {task.jira_key && (
        <a
          href={`#jira-${task.jira_key}`}
          style={styles.jiraLink}
          title="Ver en Jira"
        >
          {task.jira_key}
        </a>
      )}

      <div style={styles.footer}>
        <select
          value={task.status}
          onChange={handleStatusChange}
          disabled={isChangingStatus}
          style={styles.statusSelect}
        >
          {(Object.keys(STATUS_LABELS) as Task["status"][]).map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>

        {onDelete && (
          <button
            onClick={() => onDelete(task.id)}
            style={styles.deleteBtn}
            title="Eliminar tarea"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#1e2a3a",
    border: "1px solid #2d3f55",
    borderRadius: 10,
    padding: "12px 14px",
    display: "flex",
    flexDirection: "column",
    gap: 8,
    cursor: "default",
    transition: "border-color 0.15s",
  },
  header: { display: "flex", alignItems: "center", gap: 8 },
  priorityDot: {
    width: 10,
    height: 10,
    borderRadius: "50%",
    flexShrink: 0,
  },
  type: {
    fontSize: 11,
    color: "#a0a0b0",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    fontWeight: 600,
    flex: 1,
  },
  points: {
    fontSize: 11,
    color: "#7a8a9a",
    background: "#16213e",
    borderRadius: 4,
    padding: "2px 6px",
  },
  title: { margin: 0, color: "#eaeaea", fontSize: 14, lineHeight: 1.45 },
  jiraLink: {
    fontSize: 11,
    color: "#0080ff",
    textDecoration: "none",
    display: "inline-block",
  },
  footer: { display: "flex", alignItems: "center", gap: 8 },
  statusSelect: {
    flex: 1,
    background: "#16213e",
    border: "1px solid #2d3f55",
    borderRadius: 6,
    color: "#c0c8d8",
    fontSize: 12,
    padding: "4px 8px",
    cursor: "pointer",
  },
  deleteBtn: {
    background: "transparent",
    border: "none",
    color: "#7a8a9a",
    fontSize: 18,
    cursor: "pointer",
    lineHeight: 1,
    padding: "0 4px",
  },
};
