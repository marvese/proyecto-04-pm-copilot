import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskCard } from "./TaskCard";
import type { Task } from "../../types/task";

const baseTask: Task = {
  id: "task-1",
  project_id: "proj-1",
  title: "Implementar autenticación JWT",
  description: "Añadir JWT al backend",
  type: "story",
  status: "todo",
  priority: "high",
  estimated_points: 5,
  actual_points: null,
  sprint_id: null,
  jira_key: "PMCP-42",
  jira_sync_status: "synced",
  tags: [],
  created_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
};

describe("TaskCard", () => {
  it("renders task title and type", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.getByText("Implementar autenticación JWT")).toBeInTheDocument();
    expect(screen.getByText("story")).toBeInTheDocument();
  });

  it("renders estimated points", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.getByText("5 pts")).toBeInTheDocument();
  });

  it("renders jira key as link", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.getByText("PMCP-42")).toBeInTheDocument();
  });

  it("does not render jira key when null", () => {
    render(<TaskCard task={{ ...baseTask, jira_key: null }} />);
    expect(screen.queryByText("PMCP-42")).not.toBeInTheDocument();
  });

  it("renders delete button when onDelete is provided", () => {
    const onDelete = vi.fn();
    render(<TaskCard task={baseTask} onDelete={onDelete} />);
    expect(screen.getByTitle("Eliminar tarea")).toBeInTheDocument();
  });

  it("calls onDelete with task id when delete button clicked", async () => {
    const onDelete = vi.fn();
    render(<TaskCard task={baseTask} onDelete={onDelete} />);
    await userEvent.click(screen.getByTitle("Eliminar tarea"));
    expect(onDelete).toHaveBeenCalledWith("task-1");
  });

  it("calls onStatusChange when status select changes", async () => {
    const onStatusChange = vi.fn().mockResolvedValue(undefined);
    render(<TaskCard task={baseTask} onStatusChange={onStatusChange} />);
    await userEvent.selectOptions(screen.getByRole("combobox"), "done");
    expect(onStatusChange).toHaveBeenCalledWith("task-1", "done");
  });

  it("does not render delete button when onDelete is not provided", () => {
    render(<TaskCard task={baseTask} />);
    expect(screen.queryByTitle("Eliminar tarea")).not.toBeInTheDocument();
  });
});
