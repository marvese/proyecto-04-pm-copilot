export type TaskType = "story" | "bug" | "task" | "epic";
export type TaskStatus = "backlog" | "todo" | "in_progress" | "in_review" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";
export type JiraSyncStatus = "pending" | "synced" | "failed" | "local_only";

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string;
  type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  estimated_points: number | null;
  actual_points: number | null;
  sprint_id: string | null;
  jira_key: string | null;
  jira_sync_status: JiraSyncStatus;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  project_id: string;
  title: string;
  description: string;
  type?: TaskType;
  priority?: TaskPriority;
  estimated_points?: number;
  sprint_id?: string;
  tags?: string[];
}

export interface PatchTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  estimated_points?: number;
  actual_points?: number;
  sprint_id?: string;
  tags?: string[];
}
