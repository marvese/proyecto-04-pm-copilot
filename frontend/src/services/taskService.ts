import type { Task, CreateTaskRequest, PatchTaskRequest, TaskStatus } from "../types/task";

export const taskService = {
  async list(projectId: string, filters?: { status?: TaskStatus; sprint_id?: string }): Promise<Task[]> {
    // TODO: implement — GET /api/v1/tasks?project_id=...
    throw new Error("Not implemented");
  },

  async get(taskId: string): Promise<Task> {
    // TODO: implement — GET /api/v1/tasks/{taskId}
    throw new Error("Not implemented");
  },

  async create(request: CreateTaskRequest): Promise<Task> {
    // TODO: implement — POST /api/v1/tasks
    throw new Error("Not implemented");
  },

  async patch(taskId: string, updates: PatchTaskRequest): Promise<Task> {
    // TODO: implement — PATCH /api/v1/tasks/{taskId}
    throw new Error("Not implemented");
  },

  async delete(taskId: string): Promise<void> {
    // TODO: implement — DELETE /api/v1/tasks/{taskId}
    throw new Error("Not implemented");
  },

  async syncToJira(taskId: string): Promise<void> {
    // TODO: implement — POST /api/v1/tasks/{taskId}/sync-jira
    throw new Error("Not implemented");
  },
};
