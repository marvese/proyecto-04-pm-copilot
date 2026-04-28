import React from "react";
import type { Sprint } from "../../types/project";

interface SprintOverviewProps {
  sprint: Sprint | null;
  completedPoints: number;
  totalPoints: number;
  daysRemaining: number | null;
}

export function SprintOverview({ sprint, completedPoints, totalPoints, daysRemaining }: SprintOverviewProps) {
  // TODO: implement
  // - Sprint name and goal
  // - Progress bar (completedPoints / totalPoints)
  // - Days remaining badge
  return <div className="sprint-overview">TODO: SprintOverview</div>;
}
