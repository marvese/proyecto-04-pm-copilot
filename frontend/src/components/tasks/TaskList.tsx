import React from "react";
import type { Task } from "../../types/task";
import { TaskCard } from "./TaskCard";
import { LoadingSpinner } from "../ui/LoadingSpinner";

type Column = { key: Task["status"]; label: string };

const COLUMNS: Column[] = [
  { key: "backlog", label: "Backlog" },
  { key: "todo", label: "Por hacer" },
  { key: "in_progress", label: "En progreso" },
  { key: "in_review", label: "En revisión" },
  { key: "done", label: "Hecho" },
];

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  error?: string | null;
  onStatusChange?: (taskId: string, status: Task["status"]) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskList({ tasks, isLoading, error, onStatusChange, onDelete }: TaskListProps) {
  if (isLoading) {
    return (
      <div style={styles.centered}>
        <LoadingSpinner label="Cargando tareas..." />
      </div>
    );
  }

  if (error) {
    return <div style={styles.errorBox}>{error}</div>;
  }

  const byStatus = (status: Task["status"]) => tasks.filter((t) => t.status === status);

  return (
    <div style={styles.board}>
      {COLUMNS.map(({ key, label }) => {
        const col = byStatus(key);
        return (
          <div key={key} style={styles.column}>
            <div style={styles.columnHeader}>
              <span style={styles.columnLabel}>{label}</span>
              <span style={styles.columnCount}>{col.length}</span>
            </div>
            <div style={styles.cards}>
              {col.length === 0 ? (
                <div style={styles.empty}>Vacío</div>
              ) : (
                col.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onStatusChange={onStatusChange}
                    onDelete={onDelete}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  board: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: 12,
    alignItems: "start",
    overflowX: "auto",
    minWidth: 800,
  },
  column: {
    background: "#16213e",
    borderRadius: 10,
    padding: 12,
    minHeight: 200,
  },
  columnHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  columnLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: "#c0c8d8",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  columnCount: {
    background: "#2d3f55",
    borderRadius: 10,
    padding: "2px 8px",
    fontSize: 12,
    color: "#a0a0b0",
  },
  cards: { display: "flex", flexDirection: "column", gap: 8 },
  empty: { color: "#7a8a9a", fontSize: 13, textAlign: "center", padding: "20px 0" },
  centered: { display: "flex", justifyContent: "center", padding: "40px 0" },
  errorBox: {
    background: "#2a1a1a",
    border: "1px solid #f44336",
    borderRadius: 8,
    padding: "12px 16px",
    color: "#f44336",
    fontSize: 14,
  },
};
