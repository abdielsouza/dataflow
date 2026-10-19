import type { Edge, Node } from "@xyflow/react";
import type { PipelineNodeData } from "./types";

export interface AnalysisRequest {
  name: string;
  dataset: {
    name: string;
    source: string;
  };
  operations: Array<{
    id: string;
    type: string;
    parameters: Record<string, unknown>;
  }>;
  edges: Array<{
    source: string;
    target: string;
  }>;
}

export function serializePipeline(
  name: string,
  dataset: AnalysisRequest["dataset"],
  nodes: Node<PipelineNodeData>[],
  edges: Edge[],
): AnalysisRequest {
  const operations = nodes
    .filter((node) => node.id !== "source")
    .map((node) => ({
      id: node.id,
      type: node.data.operationType,
      parameters: node.data.parameters,
    }));

  const operationIds = new Set(operations.map((operation) => operation.id));

  return {
    name,
    dataset,
    operations,
    edges: edges
      .filter(
        (edge) =>
          operationIds.has(edge.source) &&
          operationIds.has(edge.target),
      )
      .map((edge) => ({
        source: edge.source,
        target: edge.target,
      })),
  };
}