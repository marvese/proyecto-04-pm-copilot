import React, { useState } from "react";
import { TaskList } from "../components/tasks/TaskList";
import { useTasks } from "../hooks/useTasks";
import { useProjectContext } from "../hooks/useProjectContext";
import type { CreateTaskRequest, TaskPriority, TaskType } from "../types/task";

const INITIAL_FORM: CreateTaskRequest = {
  project_id: "",
  title: "",
  description: "",
  type: "task",
  priority: "medium",
};

export function TasksPage() {
  const { project } = useProjectContext();
  const projectId = project?.id ?? "";
  const { tasks, isLoading, error, createTask, updateTask, deleteTask } = useTasks(projectId);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<CreateTaskRequest>({ ...INITIAL_FORM, project_id: projectId });
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  if (!project) {
    return (
      <div style={styles.centered}>
        <p style={styles.noProject}>Selecciona un proyecto para ver las tareas.</p>
      </div>
    );
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setFormError(null);
    try {
      await createTask({ ...form, project_id: project.id });
      setForm({ ...INITIAL_FORM, project_id: project.id });
      setShowForm(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Error creando tarea");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>Tareas — {project.name}</h1>
        <button style={styles.addBtn} onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "+ Nueva tarea"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} style={styles.form}>
          <div style={styles.formRow}>
            <input
              required
              placeholder="Título"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              style={styles.input}
            />
            <select
              value={form.type}
              onChange={(e) => setForm((f) => ({ ...f, type: e.target.value as TaskType }))}
              style={styles.select}
            >
              {(["story", "task", "bug", "epic"] as TaskType[]).map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <select
              value={form.priority}
              onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value as TaskPriority }))}
              style={styles.select}
            >
              {(["low", "medium", "high", "critical"] as TaskPriority[]).map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            <button type="submit" disabled={creating} style={styles.submitBtn}>
              {creating ? "Creando…" : "Crear"}
            </button>
          </div>
          <textarea
            placeholder="Descripción (opcional)"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            style={styles.textarea}
            rows={2}
          />
          {formError && <p style={styles.formError}>{formError}</p>}
        </form>
      )}

      <div style={styles.boardWrapper}>
        <TaskList
          tasks={tasks}
          isLoading={isLoading}
          error={error}
          onStatusChange={(id, status) => updateTask(id, { status })}
          onDelete={deleteTask}
        />
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { padding: "24px 32px", maxWidth: 1400, margin: "0 auto" },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  title: { margin: 0, color: "#eaeaea", fontSize: 24, fontWeight: 700 },
  addBtn: {
    background: "#e94560",
    border: "none",
    borderRadius: 8,
    color: "#fff",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
    padding: "8px 18px",
  },
  form: {
    background: "#16213e",
    border: "1px solid #2d3f55",
    borderRadius: 10,
    padding: "16px 20px",
    marginBottom: 20,
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  formRow: { display: "flex", gap: 10, alignItems: "center" },
  input: {
    flex: 1,
    background: "#0d1b2a",
    border: "1px solid #2d3f55",
    borderRadius: 6,
    color: "#eaeaea",
    fontSize: 14,
    padding: "8px 12px",
  },
  select: {
    background: "#0d1b2a",
    border: "1px solid #2d3f55",
    borderRadius: 6,
    color: "#eaeaea",
    fontSize: 13,
    padding: "8px 10px",
    cursor: "pointer",
  },
  textarea: {
    background: "#0d1b2a",
    border: "1px solid #2d3f55",
    borderRadius: 6,
    color: "#eaeaea",
    fontSize: 14,
    padding: "8px 12px",
    resize: "vertical",
    fontFamily: "inherit",
  },
  submitBtn: {
    background: "#0f3460",
    border: "none",
    borderRadius: 6,
    color: "#fff",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
    padding: "8px 18px",
  },
  formError: { color: "#f44336", margin: 0, fontSize: 13 },
  boardWrapper: { overflowX: "auto" },
  centered: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: 300,
  },
  noProject: { color: "#a0a0b0", fontSize: 16 },
};
