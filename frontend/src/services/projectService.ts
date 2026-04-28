import type { Project, CreateProjectRequest } from "../types/project";

export const projectService = {
  async list(): Promise<Project[]> {
    // TODO: implement — GET /api/v1/projects
    throw new Error("Not implemented");
  },

  async get(projectId: string): Promise<Project> {
    // TODO: implement — GET /api/v1/projects/{projectId}
    throw new Error("Not implemented");
  },

  async create(request: CreateProjectRequest): Promise<Project> {
    // TODO: implement — POST /api/v1/projects
    throw new Error("Not implemented");
  },
};
