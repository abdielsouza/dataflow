export type OperationType =
  | "filter"
  | "group_by"
  | "sort"
  | "concat"
  | "create_chart";

export type OperationParameters = Record<string, unknown>;

export interface PipelineNodeData extends Record<string, unknown> {
  label: string;
  operationType: OperationType;
  parameters: OperationParameters;
}

export interface PipelineDraft {
  id: string;
  name: string;
  dataset: {
    name: string;
    source: string;
  };
}