import { useState, useCallback } from "react";
import type { Project, Sprint } from "../types/project";

interface UseProjectContextReturn {
  project: Project | null;
  activeSprint: Sprint | null;
  projects: Project[];
  isLoading: boolean;
  selectProject: (projectId: string) => void;
}

export function useProjectContext(): UseProjectContextReturn {
  const [projects] = useState<Project[]>([]);
  const [project] = useState<Project | null>(null);
  const [activeSprint] = useState<Sprint | null>(null);
  const [isLoading] = useState(false);

  // TODO PMCP-27: load projects from projectService, persist selectedProjectId in localStorage
  const selectProject = useCallback((_projectId: string) => {}, []);

  return { project, activeSprint, projects, isLoading, selectProject };
}
