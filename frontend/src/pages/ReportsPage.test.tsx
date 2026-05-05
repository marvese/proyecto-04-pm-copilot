import { render, screen } from "@testing-library/react";
import { ReportsPage } from "./ReportsPage";

vi.mock("../hooks/useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));

import { useProjectContext } from "../hooks/useProjectContext";

const mockUseProjectContext = vi.mocked(useProjectContext);

describe("ReportsPage", () => {
  it("shows message when no project is selected", () => {
    mockUseProjectContext.mockReturnValue({
      project: null,
      projects: [],
      isLoading: false,
      error: null,
      selectProject: vi.fn(),
    });
    render(<ReportsPage />);
    expect(screen.getByText(/Selecciona un proyecto/)).toBeInTheDocument();
  });

  it("renders report action buttons when project is selected", () => {
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
    render(<ReportsPage />);
    expect(screen.getByText("Informe de sprint")).toBeInTheDocument();
    expect(screen.getByText("Estado del proyecto")).toBeInTheDocument();
    expect(screen.getByText("Transcribir notas")).toBeInTheDocument();
  });

  it("renders meeting notes textarea", () => {
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
    render(<ReportsPage />);
    expect(screen.getByPlaceholderText(/transcripción/i)).toBeInTheDocument();
  });
});
