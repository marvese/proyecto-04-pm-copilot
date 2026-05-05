import React, { useEffect, useState } from "react";
import { SprintOverview } from "../components/dashboard/SprintOverview";
import { VelocityChart } from "../components/dashboard/VelocityChart";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { useProjectContext } from "../hooks/useProjectContext";
import { projectService } from "../services/projectService";
import type { ProjectStatusResult } from "../types/project";

export function DashboardPage() {
  const { project, isLoading: projectLoading } = useProjectContext();
  const [status, setStatus] = useState<ProjectStatusResult | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    if (!project) return;
    setStatusLoading(true);
    setStatusError(null);
    projectService
      .getStatus(project.id)
      .then(setStatus)
      .catch((e: Error) => setStatusError(e.message))
      .finally(() => setStatusLoading(false));
  }, [project]);

  if (projectLoading) {
    return (
      <div style={styles.centered}>
        <LoadingSpinner size="lg" label="Cargando proyectos..." />
      </div>
    );
  }

  if (!project) {
    return (
      <div style={styles.centered}>
        <div style={styles.emptyState}>
          <h2 style={styles.emptyTitle}>Bienvenido a PM Copilot</h2>
          <p style={styles.emptyText}>
            Selecciona un proyecto en el menú superior para ver el dashboard.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>{project.name}</h1>
        <p style={styles.subtitle}>{project.description}</p>
      </div>

      <div style={styles.grid}>
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Sprint activo</h2>
          {statusLoading ? (
            <div style={styles.centered}>
              <LoadingSpinner label="Cargando métricas..." />
            </div>
          ) : statusError ? (
            <div style={styles.errorBox}>{statusError}</div>
          ) : (
            <SprintOverview status={status} />
          )}
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Velocidad por sprint</h2>
          <div style={styles.card}>
            <VelocityChart data={[]} />
          </div>
        </section>
      </div>

      {project.jira_project_key && (
        <div style={styles.badges}>
          <Badge label="Jira" value={project.jira_project_key} />
          {project.confluence_space_key && (
            <Badge label="Confluence" value={project.confluence_space_key} />
          )}
          {project.github_repo && <Badge label="GitHub" value={project.github_repo} />}
        </div>
      )}
    </div>
  );
}

function Badge({ label, value }: { label: string; value: string }) {
  return (
    <div style={styles.badge}>
      <span style={styles.badgeLabel}>{label}</span>
      <span style={styles.badgeValue}>{value}</span>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { padding: "24px 32px", maxWidth: 1100, margin: "0 auto" },
  header: { marginBottom: 28 },
  title: { margin: "0 0 6px", color: "#eaeaea", fontSize: 26, fontWeight: 700 },
  subtitle: { margin: 0, color: "#a0a0b0", fontSize: 15 },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 },
  section: {},
  sectionTitle: {
    margin: "0 0 12px",
    color: "#c0c8d8",
    fontSize: 14,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  card: {
    background: "#1e2a3a",
    borderRadius: 12,
    padding: "20px 24px",
    border: "1px solid #2d3f55",
  },
  centered: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: 200,
  },
  emptyState: {
    textAlign: "center",
    padding: "48px 24px",
    maxWidth: 420,
  },
  emptyTitle: { margin: "0 0 12px", color: "#eaeaea" },
  emptyText: { margin: 0, color: "#a0a0b0", lineHeight: 1.6 },
  errorBox: {
    background: "#2a1a1a",
    border: "1px solid #f44336",
    borderRadius: 8,
    padding: "12px 16px",
    color: "#f44336",
    fontSize: 14,
  },
  badges: { display: "flex", gap: 12, flexWrap: "wrap" },
  badge: {
    display: "flex",
    gap: 6,
    alignItems: "center",
    background: "#16213e",
    borderRadius: 6,
    padding: "6px 12px",
    fontSize: 13,
  },
  badgeLabel: { color: "#a0a0b0", fontWeight: 500 },
  badgeValue: { color: "#eaeaea" },
};
