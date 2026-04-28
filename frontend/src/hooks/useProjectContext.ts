import { useState, useEffect } from "react";
import type { Project, Sprint } from "../types/project";
import { projectService } from "../services/projectService";

interface UseProjectContextReturn {
  project: Project | null;
  activeSprint: Sprint | null;
  projects: Project[];
  isLoading: boolean;
  selectProject: (projectId: string) => void;
}

export function useProjectContext(): UseProjectContextReturn {
  // TODO: implement
  // - Load projects on mount
  // - selectedProjectId persisted in localStorage
  // - Fetch active sprint when project changes
  throw new Error("Not implemented");
}
