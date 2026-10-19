import { apiRequest } from "../../lib/api";
import type { AnalysisRequest } from "./serializePipeline";

export interface ExecutionResponse {
  id?: string;
  analysis_id?: string;
  status?: string;
  error?: string | null;
  artifacts?: unknown[];
  [key: string]: unknown;
}

export async function executeAnalysis(
  analysis: AnalysisRequest,
): Promise<ExecutionResponse> {
  return apiRequest<ExecutionResponse>("/executions", {
    method: "POST",
    body: JSON.stringify({ analysis }),
  });
}