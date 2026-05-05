import React from "react";
import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { ChatPage } from "./pages/ChatPage";
import { TasksPage } from "./pages/TasksPage";
import { ReportsPage } from "./pages/ReportsPage";
import { useProjectContext } from "./hooks/useProjectContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/tasks", label: "Tareas" },
  { to: "/chat", label: "Chat IA" },
  { to: "/reports", label: "Informes" },
];

function AppLayout() {
  const { project, projects, isLoading, selectProject } = useProjectContext();

  return (
    <div style={styles.root}>
      <nav style={styles.nav}>
        <div style={styles.navBrand}>PM Copilot</div>

        <div style={styles.navLinks}>
          {NAV_ITEMS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              {label}
            </NavLink>
          ))}
        </div>

        <div style={styles.navRight}>
          {isLoading ? (
            <span style={styles.projectLoading}>Cargando…</span>
          ) : (
            <select
              value={project?.id ?? ""}
              onChange={(e) => e.target.value && selectProject(e.target.value)}
              style={styles.projectSelect}
            >
              <option value="" disabled>
                {projects.length === 0 ? "Sin proyectos" : "Selecciona proyecto"}
              </option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          )}
        </div>
      </nav>

      <main style={styles.main}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    minHeight: "100vh",
    background: "#0d1b2a",
    display: "flex",
    flexDirection: "column",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  nav: {
    background: "#1a1a2e",
    borderBottom: "1px solid #2d3f55",
    display: "flex",
    alignItems: "center",
    padding: "0 24px",
    height: 56,
    gap: 24,
    position: "sticky",
    top: 0,
    zIndex: 100,
  },
  navBrand: {
    color: "#e94560",
    fontWeight: 800,
    fontSize: 18,
    letterSpacing: "-0.02em",
    flexShrink: 0,
  },
  navLinks: { display: "flex", gap: 4, flex: 1 },
  navLink: {
    color: "#a0a0b0",
    textDecoration: "none",
    fontSize: 14,
    fontWeight: 500,
    padding: "6px 12px",
    borderRadius: 6,
    transition: "color 0.15s, background 0.15s",
  },
  navLinkActive: {
    color: "#eaeaea",
    background: "#16213e",
  },
  navRight: { marginLeft: "auto", flexShrink: 0 },
  projectSelect: {
    background: "#16213e",
    border: "1px solid #2d3f55",
    borderRadius: 6,
    color: "#eaeaea",
    fontSize: 13,
    padding: "6px 10px",
    cursor: "pointer",
    maxWidth: 220,
  },
  projectLoading: { color: "#7a8a9a", fontSize: 13 },
  main: { flex: 1 },
};
