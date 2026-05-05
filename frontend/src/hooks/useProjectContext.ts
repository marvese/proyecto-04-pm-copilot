import { useState, useEffect, useCallback } from "react";
import type { Project } from "../types/project";
import { projectService } from "../services/projectService";

const STORAGE_KEY = "pmcp_selected_project_id";

interface UseProjectContextReturn {
  project: Project | null;
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  selectProject: (projectId: string) => void;
}

export function useProjectContext(): UseProjectContextReturn {
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    projectService
      .list()
      .then((data) => {
        setProjects(data);
        const storedId = localStorage.getItem(STORAGE_KEY);
        if (storedId) {
          const found = data.find((p) => p.id === storedId) ?? null;
          setProject(found);
        }
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setIsLoading(false));
  }, []);

  const selectProject = useCallback(
    (projectId: string) => {
      localStorage.setItem(STORAGE_KEY, projectId);
      const found = projects.find((p) => p.id === projectId) ?? null;
      setProject(found);
    },
    [projects]
  );

  return { project, projects, isLoading, error, selectProject };
}
