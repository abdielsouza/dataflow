import { useCallback, useEffect, useState, type ComponentType } from "react";
import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import {
  ArrowLeft,
  CheckCircle2,
  CirclePlay,
  Database,
  FileJson,
  GitBranch,
  LoaderCircle,
  Plus,
  Save,
  Settings2,
  X,
  Zap,
} from "lucide-react";

import "@xyflow/react/dist/style.css";

import type {
  OperationType,
  PipelineNodeData,
} from "./types";
import { serializePipeline } from "./serializePipeline";
import { useUpdateAnalysis } from "./analysisQueries";
import { executeAnalysis } from "./executeAnalysis";
import { ApiError, api, getAccessToken, type AnalysisDefinition, type DatasetPreview } from "../../lib/api";

interface WorkflowEditorProps {
  analysisId: string;
  analysisName: string;
  initialDefinition?: AnalysisDefinition;
  onBack: () => void;
}

interface OperationOption {
  type: OperationType;
  label: string;
  description: string;
  icon: ComponentType<{ size?: number }>; 
  parameters: Record<string, unknown>;
}

function FilterIcon({ size = 18 }: { size?: number }) {
  return <GitBranch size={size} />;
}

const operationOptions: OperationOption[] = [
  {
    type: "filter",
    label: "Filter rows",
    description: "Filter records using a condition",
    icon: FilterIcon,
    parameters: {
      column: "",
      operator: "eq",
      value: "",
    },
  },
  {
    type: "group_by",
    label: "Group by",
    description: "Group rows and calculate aggregations",
    icon: GitBranch,
    parameters: {
      columns: [],
      aggregations: {},
    },
  },
  {
    type: "sort",
    label: "Sort",
    description: "Sort rows by one or more columns",
    icon: GitBranch,
    parameters: {
      columns: [],
      descending: false,
    },
  },
  {
    type: "concat",
    label: "Concatenate",
    description: "Combine compatible datasets",
    icon: GitBranch,
    parameters: {},
  },
  {
    type: "create_chart",
    label: "Create chart",
    description: "Generate a chart from the dataset",
    icon: GitBranch,
    parameters: {
      chart: {
        type: "bar",
        x: "",
        y: "",
        title: "",
      },
    },
  },
];

const initialNodes: Node<PipelineNodeData>[] = [
  {
    id: "source",
    type: "input",
    position: { x: 80, y: 180 },
    data: {
      label: "Dataset",
      operationType: "concat",
      parameters: {},
    },
    deletable: false,
    style: {
      width: 180,
      borderRadius: 12,
      border: "1px solid #cbd5e1",
      background: "#f8fafc",
      padding: 12,
      fontWeight: 600,
    },
  },
];

const initialEdges: Edge[] = [];

export default function WorkflowEditor({
  analysisId,
  analysisName,
  initialDefinition,
  onBack,
}: WorkflowEditorProps) {
  const [nodes, setNodes, onNodesChange] =
    useNodesState<Node<PipelineNodeData>>(initialNodes);

  const [edges, setEdges, onEdgesChange] =
    useEdgesState<Edge>(initialEdges);

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(
    null,
  );
  const [showOperations, setShowOperations] = useState(true);
  const [showSettings, setShowSettings] = useState(true);
  const [datasetName, setDatasetName] = useState("My dataset");
  const [datasetSource, setDatasetSource] = useState("");
  const [datasetPreview, setDatasetPreview] = useState<DatasetPreview | null>(null);
  const [isUploadingDataset, setIsUploadingDataset] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [notice, setNotice] = useState("");
  const [executionResult, setExecutionResult] = useState<Awaited<
    ReturnType<typeof executeAnalysis>
  > | null>(null);
  const updateAnalysisMutation = useUpdateAnalysis();

  useEffect(() => {
    if (!initialDefinition) return;

    const operationNodes: Node<PipelineNodeData>[] = initialDefinition.operations.map(
      (operation, index) => {
        const option = operationOptions.find((item) => item.type === operation.type);
        return {
          id: operation.id,
          type: "default",
          position: { x: 260 + (index % 3) * 220, y: 100 + Math.floor(index / 3) * 150 },
          data: {
            label: option?.label ?? operation.type,
            operationType: operation.type as OperationType,
            parameters: operation.parameters,
          },
          style: {
            width: 190, borderRadius: 12, border: "1px solid #cbd5e1",
            background: "#ffffff", padding: 12, fontWeight: 500,
          },
        };
      },
    );
    const incoming = new Set(initialDefinition.edges.map((edge) => edge.target));
    const restoredEdges: Edge[] = [
      ...initialDefinition.edges.map((edge) => ({
        id: `${edge.source}-${edge.target}`, source: edge.source, target: edge.target,
        animated: true, style: { stroke: "#64748b", strokeWidth: 1.5 },
      })),
      ...initialDefinition.operations
        .filter((operation) => !incoming.has(operation.id))
        .map((operation) => ({
          id: `source-${operation.id}`, source: "source", target: operation.id,
          animated: true, style: { stroke: "#64748b", strokeWidth: 1.5 },
        })),
    ];

    setNodes([...initialNodes, ...operationNodes]);
    setEdges(restoredEdges);
    setDatasetName(initialDefinition.dataset.name);
    setDatasetSource(
      initialDefinition.dataset.source === "manual"
        ? ""
        : initialDefinition.dataset.source,
    );
    setSelectedNodeId(null);
    setExecutionResult(null);
    setNotice("");
  }, [analysisId, initialDefinition, setEdges, setNodes]);

  useEffect(() => {
    if (!datasetSource || datasetSource === "manual") {
      setDatasetPreview(null);
      return;
    }

    let cancelled = false;
    api.previewDataset(datasetSource)
      .then((preview) => { if (!cancelled) setDatasetPreview(preview); })
      .catch(() => { if (!cancelled) setDatasetPreview(null); });
    return () => { cancelled = true; };
  }, [datasetSource]);

  async function handleDatasetUpload(file?: File) {
    if (!file) return;
    setIsUploadingDataset(true);
    setNotice("");
    try {
      const uploaded = await api.uploadDataset(file);
      if (!uploaded.source) throw new Error("The API did not return a dataset source.");
      setDatasetName(file.name.replace(/\.(csv|parquet)$/i, ""));
      setDatasetSource(uploaded.source);
      setDatasetPreview(uploaded);
      setNotice(`Dataset uploaded: ${uploaded.name} (${(uploaded.size_bytes ?? file.size).toLocaleString()} bytes).`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to upload dataset.");
    } finally {
      setIsUploadingDataset(false);
    }
  }

  const selectedNode =
    nodes.find((node) => node.id === selectedNodeId) ?? null;

  const connectNodes = useCallback(
    (connection: Connection) => {
      setEdges((currentEdges) =>
        addEdge(
          {
            ...connection,
            animated: true,
            style: { stroke: "#64748b", strokeWidth: 1.5 },
          },
          currentEdges,
        ),
      );
    },
    [setEdges],
  );

  function addOperation(option: OperationOption) {
    const operationNumber =
      nodes.filter((node) => node.id !== "source").length + 1;

    const nodeId = crypto.randomUUID();

    const newNode: Node<PipelineNodeData> = {
      id: nodeId,
      type: "default",
      position: {
        x: 260 + (operationNumber - 1) % 3 * 40,
        y: 100 + (operationNumber - 1) * 110,
      },
      data: {
        label: option.label,
        operationType: option.type,
        parameters: structuredClone(option.parameters),
      },
      style: {
        width: 190,
        borderRadius: 12,
        border: "1px solid #cbd5e1",
        background: "#ffffff",
        padding: 12,
        fontWeight: 500,
      },
    };

    setNodes((currentNodes) => [...currentNodes, newNode]);
    setSelectedNodeId(nodeId);
    setShowSettings(true);
    setNotice("");
    setExecutionResult(null);
  }

  function updateSelectedParameters(rawValue: string) {
    if (!selectedNode) return;

    try {
      const parameters = JSON.parse(rawValue) as Record<string, unknown>;

      setNodes((currentNodes) =>
        currentNodes.map((node) =>
          node.id === selectedNode.id
            ? {
                ...node,
                data: {
                  ...node.data,
                  parameters,
                },
              }
            : node,
        ),
      );

      setNotice("");
    } catch {
      setNotice("Invalid JSON. Fix the parameters before running.");
    }
  }

  function validatePipeline(): boolean {
    const operationNodes = nodes.filter(
      (node) => node.id !== "source",
    );

    if (!datasetName.trim()) {
      setNotice("Enter a dataset name.");
      setShowSettings(true);
      return false;
    }

    if (!datasetSource.trim()) {
      setNotice("Enter the dataset source.");
      setShowSettings(true);
      return false;
    }

    if (operationNodes.length === 0) {
      setNotice("Add at least one operation to the pipeline.");
      return false;
    }

    const operationIds = new Set(
      operationNodes.map((node) => node.id),
    );

    const operationEdges = edges.filter(
      (edge) =>
        operationIds.has(edge.source) &&
        operationIds.has(edge.target),
    );

    const adjacency = new Map<string, string[]>();
    operationNodes.forEach((node) => adjacency.set(node.id, []));
    operationEdges.forEach((edge) => {
      adjacency.get(edge.source)?.push(edge.target);
    });

    const sourceTargets = edges
      .filter((edge) => edge.source === "source" && operationIds.has(edge.target))
      .map((edge) => edge.target);
    const visited = new Set<string>();
    const queue = [...sourceTargets];
    while (queue.length) {
      const current = queue.shift()!;
      if (visited.has(current)) continue;
      visited.add(current);
      queue.push(...(adjacency.get(current) ?? []));
    }

    if (visited.size !== operationNodes.length) {
      setNotice("Connect every operation to the Dataset node. Remove isolated nodes before running.");
      return false;
    }

    const indegree = new Map(operationNodes.map((node) => [node.id, 0]));
    operationEdges.forEach((edge) => indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1));
    const ready = [...indegree.entries()].filter(([, degree]) => degree === 0).map(([id]) => id);
    let visitedCount = 0;
    while (ready.length) {
      const current = ready.shift()!;
      visitedCount += 1;
      for (const target of adjacency.get(current) ?? []) {
        const degree = (indegree.get(target) ?? 0) - 1;
        indegree.set(target, degree);
        if (degree === 0) ready.push(target);
      }
    }
    if (visitedCount !== operationNodes.length) {
      setNotice("The pipeline contains a cycle. Remove a connection before running.");
      return false;
    }

    setNotice("Pipeline validation passed.");
    return true;
  }

  async function handleSaveDraft() {
    const analysis = serializePipeline(
      analysisName,
      {
        name: datasetName.trim(),
        source: datasetSource.trim(),
      },
      nodes,
      edges,
    );

    try {
      const saved = await updateAnalysisMutation.mutateAsync({
        id: analysisId,
        definition: analysis,
      });
      setNotice(`Analysis saved successfully: ${saved.name}`);
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "Unable to save the draft.",
      );
    }
  }

  async function handleRun() {
    setNotice("");
    setExecutionResult(null);

    if (!validatePipeline()) return;

    if (!getAccessToken()) {
      setNotice("Please log in before executing an analysis.");
      return;
    }

    setIsExecuting(true);

    try {
      const analysis = serializePipeline(
        analysisName,
        {
          name: datasetName.trim(),
          source: datasetSource.trim(),
        },
        nodes,
        edges,
      );

      const result = await executeAnalysis(analysis);

      setExecutionResult(result);
      setNotice(
        `Execution response received: ${result.status ?? "status unavailable"}.`,
      );
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setNotice(
          "Your session is missing or expired. Please log in again.",
        );
      } else {
        setNotice(
          error instanceof Error
            ? error.message
            : "Failed to execute the analysis.",
        );
      }
    } finally {
      setIsExecuting(false);
    }
  }

  return (
    <div className="flex h-screen min-h-[600px] flex-col bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="z-10 flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            aria-label="Back to analyses"
          >
            <ArrowLeft size={18} />
          </button>

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
            <Zap size={18} />
          </div>

          <div className="min-w-0">
            <div className="truncate text-sm font-semibold">
              {analysisName}
            </div>
            <div className="text-xs text-slate-500">
              Pipeline editor · Draft
            </div>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => setShowOperations((visible) => !visible)}
            className="hidden items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50 md:flex"
          >
            <Plus size={16} />
            Operations
          </button>

          <button
            type="button"
            onClick={() => setShowSettings((visible) => !visible)}
            className="hidden items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50 md:flex"
          >
            <Settings2 size={16} />
            Parameters
          </button>

          <button
            type="button"
            onClick={handleSaveDraft}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50"
          >
            <Save size={16} />
            <span className="hidden sm:inline">Save draft</span>
          </button>

          <button
            type="button"
            onClick={validatePipeline}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50"
          >
            <CheckCircle2 size={16} />
            <span className="hidden sm:inline">Validate</span>
          </button>

          <button
            type="button"
            onClick={handleRun}
            disabled={isExecuting}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isExecuting ? (
              <LoaderCircle size={16} className="animate-spin" />
            ) : (
              <CirclePlay size={16} />
            )}
            {isExecuting ? "Running..." : "Run"}
          </button>
        </div>
      </header>

      {/* Workspace */}
      <div className="flex min-h-0 flex-1">
        {/* Operations panel */}
        {showOperations && (
          <aside className="z-10 hidden w-64 shrink-0 overflow-y-auto border-r border-slate-200 bg-white md:block">
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-4">
              <div>
                <h2 className="text-sm font-semibold">Operations</h2>
                <p className="mt-1 text-xs text-slate-500">
                  Add a step to your pipeline
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowOperations(false)}
                className="rounded-md p-1 text-slate-400 hover:bg-slate-100"
                aria-label="Close operations panel"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-2 p-3">
              {operationOptions.map((option) => {
                const Icon = option.icon;

                return (
                  <button
                    key={option.type}
                    type="button"
                    onClick={() => addOperation(option)}
                    className="flex w-full items-start gap-3 rounded-xl border border-slate-200 p-3 text-left transition hover:border-indigo-300 hover:bg-indigo-50/50"
                  >
                    <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                      <Icon size={17} />
                    </span>

                    <span className="min-w-0">
                      <span className="block text-sm font-medium">
                        {option.label}
                      </span>
                      <span className="mt-1 block text-xs leading-5 text-slate-500">
                        {option.description}
                      </span>
                    </span>
                  </button>
                );
              })}
            </div>
          </aside>
        )}

        {/* Flow canvas */}
        <main className="relative min-w-0 flex-1">
          <div className="absolute left-4 top-4 z-10 rounded-lg border border-slate-200 bg-white/95 px-3 py-2 shadow-sm">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
              <GitBranch size={15} />
              {nodes.length - 1} operation
              {nodes.length - 1 === 1 ? "" : "s"}
              <span className="text-slate-300">·</span>
              {edges.length} connection
              {edges.length === 1 ? "" : "s"}
            </div>
          </div>

          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={connectNodes}
            onNodeClick={(_, node) => {
              setSelectedNodeId(node.id);
              setShowSettings(true);
            }}
            onPaneClick={() => setSelectedNodeId(null)}
            fitView
            fitViewOptions={{ padding: 0.25 }}
            deleteKeyCode={["Backspace", "Delete"]}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#cbd5e1" gap={20} />
            <Controls />
            <MiniMap
              nodeStrokeWidth={3}
              zoomable
              pannable
            />
          </ReactFlow>

          {notice && (
            <div className="absolute bottom-4 left-4 right-4 z-20 flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-3 text-sm shadow-lg md:right-auto md:max-w-xl">
              <div className="min-w-0 flex-1 text-slate-700">
                {notice}
              </div>
              <button
                type="button"
                onClick={() => setNotice("")}
                className="shrink-0 rounded p-0.5 text-slate-400 hover:bg-slate-100"
                aria-label="Dismiss notification"
              >
                <X size={16} />
              </button>
            </div>
          )}

          {executionResult && (
            <section className="absolute bottom-20 right-4 z-20 max-h-72 w-[min(24rem,calc(100%-2rem))] overflow-auto rounded-xl border border-slate-200 bg-white shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-emerald-600" />
                  <h3 className="text-sm font-semibold">
                    Execution response
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setExecutionResult(null)}
                  className="rounded p-1 text-slate-400 hover:bg-slate-100"
                  aria-label="Close execution result"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-3 p-4">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="text-slate-500">Status</span>
                  <span className="font-medium">
                    {executionResult.status ?? "Unknown"}
                  </span>
                </div>

                {executionResult.id && (
                  <div className="text-xs text-slate-500">
                    Execution ID: {executionResult.id}
                  </div>
                )}

                {executionResult.error && (
                  <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    {executionResult.error}
                  </p>
                )}

                <details>
                  <summary className="flex cursor-pointer items-center gap-2 text-xs font-medium text-slate-600">
                    <FileJson size={14} />
                    Raw response
                  </summary>
                  <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-100">
                    {JSON.stringify(executionResult, null, 2)}
                  </pre>
                </details>
              </div>
            </section>
          )}
        </main>

        {/* Parameters panel */}
        {showSettings && (
          <aside className="z-10 hidden w-80 shrink-0 overflow-y-auto border-l border-slate-200 bg-white lg:block">
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-4">
              <div>
                <h2 className="text-sm font-semibold">Parameters</h2>
                <p className="mt-1 text-xs text-slate-500">
                  Configure the dataset and selected operation
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowSettings(false)}
                className="rounded-md p-1 text-slate-400 hover:bg-slate-100"
                aria-label="Close parameters panel"
              >
                <X size={16} />
              </button>
            </div>

            {/* Dataset settings */}
            <section className="space-y-3 border-b border-slate-100 p-4">
              <div className="flex items-center gap-2">
                <Database size={16} className="text-indigo-600" />
                <h3 className="text-sm font-semibold">Dataset</h3>
              </div>

              <div>
                <label
                  htmlFor="dataset-name"
                  className="mb-1.5 block text-xs font-medium text-slate-600"
                >
                  Name
                </label>
                <input
                  id="dataset-name"
                  value={datasetName}
                  onChange={(event) => setDatasetName(event.target.value)}
                  placeholder="My dataset"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="dataset-file" className="block text-xs font-medium text-slate-600">
                  Import a dataset
                </label>
                <input
                  id="dataset-file"
                  type="file"
                  accept=".csv,.parquet,text/csv,application/vnd.apache.parquet"
                  disabled={isUploadingDataset}
                  onChange={(event) => {
                    void handleDatasetUpload(event.target.files?.[0]);
                    event.currentTarget.value = "";
                  }}
                  className="block w-full text-xs text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-xs file:font-semibold file:text-indigo-700 hover:file:bg-indigo-100 disabled:opacity-60"
                />
                <p className="text-xs leading-5 text-slate-500">
                  CSV or Parquet · maximum 20 MB. The file is stored by the Dataflow API.
                </p>
                {isUploadingDataset && <p className="text-xs text-indigo-600">Uploading and checking file…</p>}
                {datasetPreview && (
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
                      <CheckCircle2 size={14} className="text-emerald-600" />
                      {datasetPreview.name}
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      {datasetPreview.columns.length} columns · {datasetPreview.preview_row_count} preview rows
                    </p>
                    <div className="mt-2 max-h-40 overflow-auto rounded border border-slate-200 bg-white">
                      <table className="min-w-full text-left text-[11px]">
                        <thead className="sticky top-0 bg-slate-100">
                          <tr>{datasetPreview.columns.map((column) => <th key={column.name} className="whitespace-nowrap px-2 py-1.5 font-semibold">{column.name}<span className="ml-1 font-normal text-slate-500">{column.dtype}</span></th>)}</tr>
                        </thead>
                        <tbody>
                          {datasetPreview.rows.slice(0, 5).map((row, index) => (
                            <tr key={index} className="border-t border-slate-100">
                              {datasetPreview.columns.map((column) => <td key={column.name} className="max-w-32 truncate whitespace-nowrap px-2 py-1.5">{String(row[column.name] ?? "—")}</td>)}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                {!datasetPreview && datasetSource && datasetSource !== "manual" && (
                  <p className="text-xs text-amber-700">Dataset preview unavailable. Re-import the file if it was moved or deleted.</p>
                )}
              </div>
            </section>

            {/* Selected operation settings */}
            <section className="space-y-3 p-4">
              <div>
                <h3 className="text-sm font-semibold">
                  {selectedNode?.data.label ?? "No operation selected"}
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  {selectedNode
                    ? `Type: ${selectedNode.data.operationType}`
                    : "Select a node on the canvas to edit its parameters."}
                </p>
              </div>

              {selectedNode && selectedNode.id !== "source" && (
                <>
                  <label
                    htmlFor="node-parameters"
                    className="block text-xs font-medium text-slate-600"
                  >
                    Parameters (JSON)
                  </label>

                  <textarea
                    id="node-parameters"
                    key={selectedNode.id}
                    defaultValue={JSON.stringify(
                      selectedNode.data.parameters,
                      null,
                      2,
                    )}
                    onBlur={(event) =>
                      updateSelectedParameters(event.target.value)
                    }
                    spellCheck={false}
                    rows={14}
                    className="w-full resize-y rounded-lg border border-slate-200 bg-slate-50 p-3 font-mono text-xs leading-5 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  />

                  <p className="text-xs leading-5 text-slate-500">
                    Edit the JSON and move focus away from the field to apply
                    changes. Parameter names must match the backend operation
                    schema.
                  </p>

                  <button
                    type="button"
                    onClick={() => {
                      setNodes((currentNodes) =>
                        currentNodes.filter(
                          (node) => node.id !== selectedNode.id,
                        ),
                      );
                      setEdges((currentEdges) =>
                        currentEdges.filter(
                          (edge) =>
                            edge.source !== selectedNode.id &&
                            edge.target !== selectedNode.id,
                        ),
                      );
                      setSelectedNodeId(null);
                      setNotice("Operation removed.");
                    }}
                    className="w-full rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
                  >
                    Remove operation
                  </button>
                </>
              )}
            </section>
          </aside>
        )}
      </div>

      {/* Mobile helper */}
      <div className="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-2 text-xs text-slate-500 md:hidden">
        <span>Pipeline editor</span>
        <button
          type="button"
          onClick={() => setShowOperations((visible) => !visible)}
          className="flex items-center gap-1.5 rounded-md px-2 py-1.5 font-medium text-indigo-600 hover:bg-indigo-50"
        >
          <Plus size={14} />
          Operations
        </button>
      </div>

      {showOperations && (
        <div className="fixed inset-x-0 bottom-12 z-30 max-h-[55vh] overflow-y-auto border-t border-slate-200 bg-white shadow-2xl md:hidden">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <h2 className="text-sm font-semibold">Add operation</h2>
            <button
              type="button"
              onClick={() => setShowOperations(false)}
              className="rounded-md p-1 text-slate-400 hover:bg-slate-100"
              aria-label="Close operations menu"
            >
              <X size={16} />
            </button>
          </div>
          <div className="grid grid-cols-1 gap-2 p-3 sm:grid-cols-2">
            {operationOptions.map((option) => {
              const Icon = option.icon;

              return (
                <button
                  key={option.type}
                  type="button"
                  onClick={() => {
                    addOperation(option);
                    setShowOperations(false);
                  }}
                  className="flex items-start gap-3 rounded-xl border border-slate-200 p-3 text-left hover:border-indigo-300 hover:bg-indigo-50/50"
                >
                  <Icon size={17} />
                  <span>
                    <span className="block text-sm font-medium">
                      {option.label}
                    </span>
                    <span className="mt-1 block text-xs text-slate-500">
                      {option.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}