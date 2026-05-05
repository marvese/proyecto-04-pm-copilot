import type { Project, CreateProjectRequest, ProjectStatusResult } from "../types/project";

const BASE = "/api/v1/projects";

async function checkOk(res: Response, label: string): Promise<void> {
  if (!res.ok) throw new Error(`${label}: ${res.status} ${res.statusText}`);
}

export const projectService = {
  async list(): Promise<Project[]> {
    const res = await fetch(BASE);
    await checkOk(res, "list projects");
    return res.json();
  },

  async get(projectId: string): Promise<Project> {
    const res = await fetch(`${BASE}/${projectId}`);
    await checkOk(res, "get project");
    return res.json();
  },

  async create(request: CreateProjectRequest): Promise<Project> {
    const res = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    await checkOk(res, "create project");
    return res.json();
  },

  async getStatus(projectId: string): Promise<ProjectStatusResult> {
    const res = await fetch(`${BASE}/${projectId}/status`);
    await checkOk(res, "get project status");
    return res.json();
  },
};
