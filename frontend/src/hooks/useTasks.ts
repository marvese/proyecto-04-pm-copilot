import { useState, useEffect, useCallback, useRef } from "react";
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
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  const load = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await taskService.list(projectId, filtersRef.current);
      setTasks(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error cargando tareas");
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  const createTask = useCallback(async (request: CreateTaskRequest): Promise<Task> => {
    const task = await taskService.create(request);
    setTasks((prev) => [task, ...prev]);
    return task;
  }, []);

  const updateTask = useCallback(async (taskId: string, updates: PatchTaskRequest): Promise<Task> => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, ...updates } : t))
    );
    try {
      const updated = await taskService.patch(taskId, updates);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      return updated;
    } catch (e) {
      await load();
      throw e;
    }
  }, [load]);

  const deleteTask = useCallback(async (taskId: string): Promise<void> => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    try {
      await taskService.delete(taskId);
    } catch (e) {
      await load();
      throw e;
    }
  }, [load]);

  return { tasks, isLoading, error, createTask, updateTask, deleteTask, refresh: load };
}
