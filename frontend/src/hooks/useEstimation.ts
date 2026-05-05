import type { Estimation, EstimateRequest } from "../types/estimation";

interface UseEstimationReturn {
  estimation: Estimation | null;
  isLoading: boolean;
  error: string | null;
  estimate: (request: EstimateRequest) => Promise<void>;
  reset: () => void;
}

export function useEstimation(): UseEstimationReturn {
  // TODO: implement
  throw new Error("Not implemented");
}
