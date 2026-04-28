import { useState, useEffect } from "react";
import type { Task, CreateTaskRequest, PatchTaskRequest, TaskStatus } from "../types/task";
import { taskService } from "../services/taskService";

interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  createTask: (request: CreateTaskRequest) => Promise<Task>;
  updateTask: (taskId: string, updates: PatchTaskRequest) => Promise<Task>;
  deleteTask: (taskId: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useTasks(
  projectId: string,
  filters?: { status?: TaskStatus; sprint_id?: string }
): UseTasksReturn {
  // TODO: implement
  // - Fetch tasks on mount and when projectId/filters change
  // - Optimistic updates for create/update/delete
  throw new Error("Not implemented");
}
