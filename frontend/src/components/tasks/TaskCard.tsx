import React from "react";
import type { Task } from "../../types/task";

interface TaskCardProps {
  task: Task;
  onStatusChange?: (taskId: string, status: Task["status"]) => void;
  onEdit?: (task: Task) => void;
}

export function TaskCard({ task, onStatusChange, onEdit }: TaskCardProps) {
  // TODO: implement
  // - Show title, type badge, priority indicator, points, jira_sync_status
  // - Click to edit
  return <div className="task-card">{task.title}</div>;
}
