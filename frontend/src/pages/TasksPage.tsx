import React from "react";
import { TaskList } from "../components/tasks/TaskList";
import { useTasks } from "../hooks/useTasks";
import { useProjectContext } from "../hooks/useProjectContext";

export function TasksPage() {
  // TODO: implement
  // - useTasks(project.id) to load tasks
  // - Filters: status, sprint_id
  // - Create task button
  return (
    <div className="tasks-page">
      <h1>Tasks</h1>
      <p>TODO: implement TasksPage</p>
    </div>
  );
}
