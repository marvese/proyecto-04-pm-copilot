import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { useProjectContext } from "../hooks/useProjectContext";
import { reportService, type ReportResponse } from "../services/reportService";

type ReportKey = "sprint" | "status" | "meeting";

export function ReportsPage() {
  const { project } = useProjectContext();
  const [activeReport, setActiveReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState<ReportKey | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [meetingNotes, setMeetingNotes] = useState("");

  if (!project) {
    return (
      <div style={styles.centered}>
        <p style={styles.noProject}>Selecciona un proyecto para generar informes.</p>
      </div>
    );
  }

  const run = async (key: ReportKey, fn: () => Promise<ReportResponse>) => {
    setLoading(key);
    setError(null);
    setActiveReport(null);
    try {
      const report = await fn();
      setActiveReport(report);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error generando informe");
    } finally {
      setLoading(null);
    }
  };

  const handleDownload = () => {
    if (!activeReport) return;
    const blob = new Blob([activeReport.content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeReport.type}-report.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>Informes — {project.name}</h1>

      <div style={styles.actions}>
        <ReportButton
          label="Informe de sprint"
          loading={loading === "sprint"}
          onClick={() =>
            run("sprint", () => reportService.sprintReport(project.id))
          }
        />
        <ReportButton
          label="Estado del proyecto"
          loading={loading === "status"}
          onClick={() =>
            run("status", () => reportService.statusReport(project.id))
          }
        />
      </div>

      <div style={styles.meetingSection}>
        <h2 style={styles.sectionTitle}>Notas de reunión</h2>
        <textarea
          placeholder="Pega aquí la transcripción o notas brutas de la reunión..."
          value={meetingNotes}
          onChange={(e) => setMeetingNotes(e.target.value)}
          style={styles.textarea}
          rows={6}
        />
        <button
          style={styles.meetingBtn}
          disabled={!meetingNotes.trim() || loading === "meeting"}
          onClick={() =>
            run("meeting", () => reportService.meetingNotes(project.id, meetingNotes))
          }
        >
          {loading === "meeting" ? (
            <LoadingSpinner size="sm" label="Generando…" />
          ) : (
            "Transcribir notas"
          )}
        </button>
      </div>

      {error && <div style={styles.errorBox}>{error}</div>}

      {loading && loading !== "meeting" && (
        <div style={styles.loadingBox}>
          <LoadingSpinner size="md" label="Generando informe..." />
        </div>
      )}

      {activeReport && (
        <div style={styles.result}>
          <div style={styles.resultHeader}>
            <h2 style={styles.resultTitle}>{activeReport.title}</h2>
            <button style={styles.downloadBtn} onClick={handleDownload}>
              Descargar .md
            </button>
          </div>
          <div style={styles.markdown}>
            <ReactMarkdown>{activeReport.content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

function ReportButton({
  label,
  loading,
  onClick,
}: {
  label: string;
  loading: boolean;
  onClick: () => void;
}) {
  return (
    <button style={styles.reportBtn} disabled={loading} onClick={onClick}>
      {loading ? <LoadingSpinner size="sm" label="Generando…" /> : label}
    </button>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { padding: "24px 32px", maxWidth: 900, margin: "0 auto" },
  title: { margin: "0 0 24px", color: "#eaeaea", fontSize: 24, fontWeight: 700 },
  actions: { display: "flex", gap: 12, marginBottom: 28, flexWrap: "wrap" },
  reportBtn: {
    background: "#0f3460",
    border: "none",
    borderRadius: 8,
    color: "#fff",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
    padding: "12px 24px",
    minWidth: 160,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  meetingSection: { marginBottom: 28 },
  sectionTitle: {
    margin: "0 0 10px",
    color: "#c0c8d8",
    fontSize: 14,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  textarea: {
    width: "100%",
    background: "#16213e",
    border: "1px solid #2d3f55",
    borderRadius: 8,
    color: "#eaeaea",
    fontSize: 14,
    lineHeight: 1.6,
    padding: "12px 14px",
    resize: "vertical",
    fontFamily: "inherit",
    boxSizing: "border-box",
    marginBottom: 10,
  },
  meetingBtn: {
    background: "#e94560",
    border: "none",
    borderRadius: 8,
    color: "#fff",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
    padding: "10px 22px",
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  errorBox: {
    background: "#2a1a1a",
    border: "1px solid #f44336",
    borderRadius: 8,
    padding: "12px 16px",
    color: "#f44336",
    fontSize: 14,
    marginBottom: 20,
  },
  loadingBox: {
    display: "flex",
    justifyContent: "center",
    padding: "32px 0",
  },
  result: {
    background: "#16213e",
    border: "1px solid #2d3f55",
    borderRadius: 12,
    padding: "20px 24px",
  },
  resultHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 16,
  },
  resultTitle: { margin: 0, color: "#eaeaea", fontSize: 18 },
  downloadBtn: {
    background: "#0f3460",
    border: "none",
    borderRadius: 6,
    color: "#fff",
    cursor: "pointer",
    fontSize: 13,
    fontWeight: 600,
    padding: "6px 14px",
  },
  markdown: {
    color: "#c8d0e0",
    lineHeight: 1.7,
    fontSize: 15,
  },
  centered: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: 300,
  },
  noProject: { color: "#a0a0b0", fontSize: 16 },
};
