import type { Estimation, EstimateRequest, BreakdownEpicResponse } from "../types/estimation";

export const estimationService = {
  async estimate(request: EstimateRequest): Promise<Estimation> {
    // TODO: implement — POST /api/v1/estimate
    throw new Error("Not implemented");
  },

  async breakdownEpic(
    projectId: string,
    epicTitle: string,
    description: string,
    context?: string
  ): Promise<BreakdownEpicResponse> {
    // TODO: implement — POST /api/v1/estimate/breakdown
    throw new Error("Not implemented");
  },
};
