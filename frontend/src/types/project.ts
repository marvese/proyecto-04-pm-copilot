export type SprintStatus = "planned" | "active" | "completed";

export interface Project {
  id: string;
  name: string;
  description: string;
  jira_project_key: string | null;
  confluence_space_key: string | null;
  github_repo: string | null;
}

export interface Sprint {
  id: string;
  project_id: string;
  name: string;
  goal: string | null;
  status: SprintStatus;
  capacity_points: number | null;
  start_date: string | null;
  end_date: string | null;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
  jira_project_key?: string;
  confluence_space_key?: string;
  github_repo?: string;
}

export interface ProjectStatusResult {
  active_sprint_name: string | null;
  completed_points: number;
  remaining_points: number;
  total_points: number;
  days_remaining: number | null;
  blocked_task_count: number;
}
