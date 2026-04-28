import React from "react";
import type { Task } from "../../types/task";
import { TaskCard } from "./TaskCard";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onStatusChange?: (taskId: string, status: Task["status"]) => void;
  onEdit?: (task: Task) => void;
}

export function TaskList({ tasks, isLoading, onStatusChange, onEdit }: TaskListProps) {
  // TODO: implement — render list with loading skeleton
  return (
    <div className="task-list">
      {tasks.map((t) => (
        <TaskCard key={t.id} task={t} onStatusChange={onStatusChange} onEdit={onEdit} />
      ))}
    </div>
  );
}
