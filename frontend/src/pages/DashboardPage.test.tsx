import { render, screen } from "@testing-library/react";
import { DashboardPage } from "./DashboardPage";

vi.mock("../hooks/useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));
vi.mock("../services/projectService", () => ({
  projectService: { getStatus: vi.fn().mockResolvedValue(null) },
}));

import { useProjectContext } from "../hooks/useProjectContext";

const mockUseProjectContext = vi.mocked(useProjectContext);

describe("DashboardPage", () => {
  it("shows loading spinner while projects load", () => {
    mockUseProjectContext.mockReturnValue({
      project: null,
      projects: [],
      isLoading: true,
      error: null,
      selectProject: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByLabelText(/cargando/i)).toBeInTheDocument();
  });

  it("shows welcome message when no project is selected", () => {
    mockUseProjectContext.mockReturnValue({
      project: null,
      projects: [],
      isLoading: false,
      error: null,
      selectProject: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText("Bienvenido a PM Copilot")).toBeInTheDocument();
  });

  it("shows project dashboard when a project is selected", () => {
    mockUseProjectContext.mockReturnValue({
      project: {
        id: "proj-1",
        name: "Mi Proyecto",
        description: "",
        jira_project_key: null,
        confluence_space_key: null,
        github_repo: null,
      },
      projects: [],
      isLoading: false,
      error: null,
      selectProject: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText(/Mi Proyecto/)).toBeInTheDocument();
  });
});
