import { render, screen } from "@testing-library/react";
import { SprintOverview } from "./SprintOverview";
import type { ProjectStatusResult } from "../../types/project";

const activeStatus: ProjectStatusResult = {
  active_sprint_name: "Sprint 3",
  completed_points: 20,
  remaining_points: 10,
  total_points: 30,
  days_remaining: 5,
  blocked_task_count: 2,
};

describe("SprintOverview", () => {
  it("shows 'Sin sprint activo' when status is null", () => {
    render(<SprintOverview status={null} />);
    expect(screen.getByText("Sin sprint activo")).toBeInTheDocument();
  });

  it("renders sprint name", () => {
    render(<SprintOverview status={activeStatus} />);
    expect(screen.getByText("Sprint 3")).toBeInTheDocument();
  });

  it("renders completed and remaining points", () => {
    render(<SprintOverview status={activeStatus} />);
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });

  it("renders days remaining", () => {
    render(<SprintOverview status={activeStatus} />);
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("renders blocked task count", () => {
    render(<SprintOverview status={activeStatus} />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("shows -- for days remaining when null", () => {
    render(<SprintOverview status={{ ...activeStatus, days_remaining: null }} />);
    expect(screen.getByText("--")).toBeInTheDocument();
  });

  it("calculates progress percentage correctly", () => {
    render(<SprintOverview status={activeStatus} />);
    expect(screen.getByText("67%")).toBeInTheDocument();
  });

  it("shows 0% when total_points is 0", () => {
    render(<SprintOverview status={{ ...activeStatus, total_points: 0 }} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});
