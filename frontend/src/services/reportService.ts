export interface ReportResponse {
  id: string;
  type: string;
  title: string;
  content: string;
  sprint_id: string | null;
  confluence_page_id: string | null;
}

const BASE = "/api/v1/reports";

async function checkOk(res: Response, label: string): Promise<void> {
  if (!res.ok) throw new Error(`${label}: ${res.status} ${res.statusText}`);
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  await checkOk(res, path);
  return res.json();
}

export const reportService = {
  async sprintReport(projectId: string, sprintId?: string): Promise<ReportResponse> {
    return post("/sprint", { project_id: projectId, sprint_id: sprintId ?? null });
  },

  async statusReport(projectId: string): Promise<ReportResponse> {
    return post("/status", { project_id: projectId });
  },

  async meetingNotes(projectId: string, rawNotes: string): Promise<ReportResponse> {
    return post("/meeting-notes", { project_id: projectId, raw_notes: rawNotes });
  },

  downloadUrl(reportId: string): string {
    return `/api/v1/reports/${reportId}/download`;
  },
};
