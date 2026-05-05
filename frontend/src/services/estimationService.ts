import type { Estimation, EstimateRequest, BreakdownEpicResponse } from "../types/estimation";

export const estimationService = {
  async estimate(_request: EstimateRequest): Promise<Estimation> {
    // TODO: implement — POST /api/v1/estimate
    throw new Error("Not implemented");
  },

  async breakdownEpic(
    _projectId: string,
    _epicTitle: string,
    _description: string,
    _context?: string
  ): Promise<BreakdownEpicResponse> {
    // TODO: implement — POST /api/v1/estimate/breakdown
    throw new Error("Not implemented");
  },
};
