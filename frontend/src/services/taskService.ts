import type { Task, CreateTaskRequest, PatchTaskRequest, TaskStatus } from "../types/task";

const BASE = "/api/v1/tasks";

async function checkOk(res: Response, label: string): Promise<void> {
  if (!res.ok) throw new Error(`${label}: ${res.status} ${res.statusText}`);
}

export const taskService = {
  async list(projectId: string, filters?: { status?: TaskStatus; sprint_id?: string }): Promise<Task[]> {
    const params = new URLSearchParams({ project_id: projectId });
    if (filters?.status) params.set("status", filters.status);
    if (filters?.sprint_id) params.set("sprint_id", filters.sprint_id);
    const res = await fetch(`${BASE}?${params}`);
    await checkOk(res, "list tasks");
    return res.json();
  },

  async get(taskId: string): Promise<Task> {
    const res = await fetch(`${BASE}/${taskId}`);
    await checkOk(res, "get task");
    return res.json();
  },

  async create(request: CreateTaskRequest): Promise<Task> {
    const res = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    await checkOk(res, "create task");
    return res.json();
  },

  async patch(taskId: string, updates: PatchTaskRequest): Promise<Task> {
    const res = await fetch(`${BASE}/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    await checkOk(res, "patch task");
    return res.json();
  },

  async delete(taskId: string): Promise<void> {
    const res = await fetch(`${BASE}/${taskId}`, { method: "DELETE" });
    await checkOk(res, "delete task");
  },

  async syncToJira(taskId: string): Promise<void> {
    const res = await fetch(`${BASE}/${taskId}/sync-jira`, { method: "POST" });
    await checkOk(res, "sync task to jira");
  },
};
