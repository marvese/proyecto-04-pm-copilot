export type FibonacciPoints = 1 | 2 | 3 | 5 | 8 | 13 | 21;

export interface PointsBreakdown {
  frontend: number;
  backend: number;
  testing: number;
}

export interface SimilarTask {
  id: string;
  title: string;
  estimated: number;
  actual: number | null;
}

export interface Estimation {
  points: FibonacciPoints;
  confidence: number;
  breakdown: PointsBreakdown;
  rationale: string;
  similar_tasks: SimilarTask[];
  risks: string[];
}

export interface EstimateRequest {
  project_id: string;
  title: string;
  description: string;
  acceptance_criteria?: string;
  component_tags?: string[];
}

export interface StoryItem {
  title: string;
  description: string;
  estimated_points: FibonacciPoints | null;
}

export interface BreakdownEpicResponse {
  stories: StoryItem[];
}
