import { render, screen } from "@testing-library/react";
import { TasksPage } from "./TasksPage";

vi.mock("../hooks/useProjectContext", () => ({
  useProjectContext: vi.fn(),
}));
vi.mock("../hooks/useTasks", () => ({
  useTasks: vi.fn(),
}));

import { useProjectContext } from "../hooks/useProjectContext";
import { useTasks } from "../hooks/useTasks";

const mockUseProjectContext = vi.mocked(useProjectContext);
const mockUseTasks = vi.mocked(useTasks);

const noTasksReturn = {
  tasks: [],
  isLoading: false,
  error: null,
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  refresh: vi.fn(),
};

describe("TasksPage", () => {
  beforeEach(() => {
    mockUseTasks.mockReturnValue(noTasksReturn);
  });

  it("shows message when no project is selected", () => {
    mockUseProjectContext.mockReturnValue({
      project: null,
      projects: [],
      isLoading: false,
      error: null,
      selectProject: vi.fn(),
    });
    render(<TasksPage />);
    expect(screen.getByText(/Selecciona un proyecto/)).toBeInTheDocument();
  });

  it("renders task list when project is selected", () => {
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
    render(<TasksPage />);
    expect(screen.getByText(/Mi Proyecto/)).toBeInTheDocument();
  });

  it("shows create task button when project is selected", () => {
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
    render(<TasksPage />);
    expect(screen.getByText("+ Nueva tarea")).toBeInTheDocument();
  });
});
