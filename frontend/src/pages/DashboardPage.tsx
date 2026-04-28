import React from "react";
import { SprintOverview } from "../components/dashboard/SprintOverview";
import { VelocityChart } from "../components/dashboard/VelocityChart";
import { useProjectContext } from "../hooks/useProjectContext";

export function DashboardPage() {
  // TODO: implement
  // - useProjectContext() to get active project and sprint
  // - Fetch sprint metrics from /api/v1/sprints/active and task status counts
  // - Render SprintOverview + VelocityChart + activity feed
  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>
      <p>TODO: implement DashboardPage</p>
    </div>
  );
}
