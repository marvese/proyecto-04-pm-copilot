export type ReportFormat = "markdown" | "docx" | "confluence";

export interface ReportResponse {
  id: string;
  type: string;
  title: string;
  content: string;
  confluence_page_id: string | null;
}

export const reportService = {
  async sprintReport(
    projectId: string,
    sprintId?: string,
    format: ReportFormat = "markdown"
  ): Promise<ReportResponse> {
    // TODO: implement — POST /api/v1/reports/sprint
    throw new Error("Not implemented");
  },

  async statusReport(projectId: string, format: ReportFormat = "markdown"): Promise<ReportResponse> {
    // TODO: implement — POST /api/v1/reports/status
    throw new Error("Not implemented");
  },

  async meetingNotes(
    projectId: string,
    rawNotes: string,
    format: ReportFormat = "markdown"
  ): Promise<ReportResponse> {
    // TODO: implement — POST /api/v1/reports/meeting-notes
    throw new Error("Not implemented");
  },

  downloadUrl(reportId: string, format: ReportFormat): string {
    return `/api/v1/reports/${reportId}/download/${format}`;
  },
};
