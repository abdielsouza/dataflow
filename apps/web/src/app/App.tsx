import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Bell,
  CheckCircle2,
  Clock3,
  Database,
  FilePlus2,
  MoreHorizontal,
  Plus,
  Search,
  Workflow,
  X,
} from "lucide-react";

import { Sidebar } from "../components/layout/Sidebar";
import {
  type Analysis,
  type AnalysisStatus,
} from "../data/analyses";
import WorkflowEditor from "../features/analyses/WorkflowEditor";
import {
  useAnalyses,
  useAnalysis,
  useCreateAnalysis,
} from "../features/analyses/analysisQueries";
import { clearAccessToken, getAccessToken, type AnalysisListItem } from "../lib/api";
import { LoginForm } from "../features/auth/LoginForm";

const statusConfig: Record<
  AnalysisStatus,
  { label: string; className: string }
> = {
  success: {
    label: "Successful",
    className: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  },
  running: {
    label: "Running",
    className: "bg-blue-50 text-blue-700 ring-blue-600/20",
  },
  draft: {
    label: "Draft",
    className: "bg-slate-100 text-slate-600 ring-slate-500/20",
  },
};

function mapRemoteAnalysis(item: AnalysisListItem): Analysis {
  return {
    id: item.id,
    name: item.name,
    description: item.dataset?.name ?? "Dataset do backend",
    updatedAt: new Date(item.updated_at).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }),
    status: "draft",
    operationsCount: 0,
  };
}

export default function App() {
  // --- Estado de autenticação e sessão da UI ---
  const [activeItem, setActiveItem] = useState("Overview");
  const [search, setSearch] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAnalysisName, setNewAnalysisName] = useState("");
  const [openedAnalysis, setOpenedAnalysis] = useState<Analysis | null>(null);
  const [authenticated, setAuthenticated] = useState(() => Boolean(getAccessToken()));

  const { data: analysesFromApi = [], isLoading, isError, error } = useAnalyses();
  const createAnalysisMutation = useCreateAnalysis();
  const { data: openedAnalysisDetail, isLoading: isOpenedAnalysisLoading, error: openedAnalysisError } =
    useAnalysis(openedAnalysis?.id);

  const analyses = analysesFromApi.map(mapRemoteAnalysis);

  useEffect(() => {
    const syncAuthState = () => setAuthenticated(Boolean(getAccessToken()));

    window.addEventListener("storage", syncAuthState);
    return () => window.removeEventListener("storage", syncAuthState);
  }, []);

  const filteredAnalyses = useMemo(() => {
    const query = search.trim().toLowerCase();

    return analyses.filter(
      (analysis) =>
        analysis.name.toLowerCase().includes(query) ||
        analysis.description.toLowerCase().includes(query),
    );
  }, [analyses, search]);

  function createAnalysis() {
    const name = newAnalysisName.trim();

    if (!name) return;

    createAnalysisMutation.mutate(
      {
        name,
        dataset: {
          name,
          source: "",
        },
        operations: [],
        edges: [],
      },
      {
        onSuccess: (saved) => {
          setNewAnalysisName("");
          setShowCreateModal(false);
          setActiveItem("Analyses");
          setOpenedAnalysis(mapRemoteAnalysis(saved));
        },
      },
    );
  }

  const successfulCount = analyses.filter(
    (analysis) => analysis.status === "success",
  ).length;

  const operationsCount = analyses.reduce(
    (total, analysis) => total + analysis.operationsCount,
    0,
  );

  function handleLogout() {
    clearAccessToken();
    setAuthenticated(false);
    setOpenedAnalysis(null);
  }

  if (!authenticated) {
    return <LoginForm onSuccess={() => setAuthenticated(true)} />;
  }

  // --- Editor de análise em tela cheia ---
  if (openedAnalysis) {
    if (isOpenedAnalysisLoading) {
      return (
        <div className="flex h-screen items-center justify-center bg-slate-50 text-sm text-slate-600">
          Loading saved analysis…
        </div>
      );
    }

    if (!openedAnalysisDetail) {
      return (
        <div className="flex h-screen flex-col items-center justify-center gap-3 bg-slate-50 px-6 text-center">
          <p className="text-sm text-red-600">
            {openedAnalysisError instanceof Error ? openedAnalysisError.message : "Could not load this analysis."}
          </p>
          <button
            type="button"
            onClick={() => setOpenedAnalysis(null)}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
          >
            Back to analyses
          </button>
        </div>
      );
    }

    return (
      <WorkflowEditor
        key={openedAnalysis.id}
        analysisId={openedAnalysis.id}
        analysisName={openedAnalysis.name}
        initialDefinition={openedAnalysisDetail.definition}
        onBack={() => setOpenedAnalysis(null)}
      />
    );
  }

  return (
    <div className="flex h-screen min-w-0 overflow-hidden bg-[#f7f8fa] text-slate-900">
      <Sidebar activeItem={activeItem} onNavigate={setActiveItem} />

      {/* Layout principal do workspace: cabeçalho, conteúdo e ações globais. */}
      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5 sm:px-8">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span>Workspace</span>
            <span>/</span>
            <span className="font-medium text-slate-800">{activeItem}</span>
          </div>

          <div className="flex items-center gap-3">
            <label className="hidden h-9 w-60 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 md:flex">
              <Search size={16} className="text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search analyses..."
                className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
              />
              {search && (
                <button
                  type="button"
                  onClick={() => setSearch("")}
                  aria-label="Clear search"
                >
                  <X size={14} className="text-slate-400" />
                </button>
              )}
            </label>

            <button
              type="button"
              aria-label="Notifications"
              className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-50"
            >
              <Bell size={17} />
              <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-blue-500" />
            </button>

            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-360 px-5 py-8 sm:px-8 lg:px-10">
            {activeItem === "Overview" || activeItem === "Analyses" ? (
              <>
                <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
                      Data workspace
                    </p>
                    <h1 className="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
                      {activeItem === "Overview"
                        ? "Good to see you."
                        : "Your analyses"}
                    </h1>
                    <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">
                      Build data pipelines, transform datasets, and turn your
                      data into insights.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => setShowCreateModal(true)}
                    className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
                  >
                    <Plus size={17} />
                    New analysis
                  </button>
                </section>

                <section className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <MetricCard
                    label="Total analyses"
                    value={analyses.length.toString()}
                    detail="In your workspace"
                    icon={Workflow}
                    iconClass="bg-blue-50 text-blue-600"
                  />
                  <MetricCard
                    label="Successful analyses"
                    value={successfulCount.toString()}
                    detail="Ready to use"
                    icon={CheckCircle2}
                    iconClass="bg-emerald-50 text-emerald-600"
                  />
                  <MetricCard
                    label="Operations configured"
                    value={operationsCount.toString()}
                    detail="Across all analyses"
                    icon={Activity}
                    iconClass="bg-violet-50 text-violet-600"
                  />
                  <MetricCard
                    label="Datasets"
                    value="—"
                    detail="Connect your first dataset"
                    icon={Database}
                    iconClass="bg-amber-50 text-amber-600"
                  />
                </section>

                <section className="mt-9">
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-base font-semibold text-slate-900">
                        Recent analyses
                      </h2>
                      <p className="mt-1 text-sm text-slate-500">
                        Pick up where you left off.
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => setActiveItem("Analyses")}
                      className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700"
                    >
                      View all
                      <ArrowRight size={15} />
                    </button>
                  </div>

                  <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm shadow-slate-900/2">
                    <div className="hidden grid-cols-[minmax(0,2fr)_minmax(120px,0.8fr)_minmax(120px,0.8fr)_40px] gap-4 border-b border-slate-100 bg-slate-50/70 px-5 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 md:grid">
                      <span>Analysis</span>
                      <span>Status</span>
                      <span>Last updated</span>
                      <span />
                    </div>

                    {isLoading ? (
                      <div className="px-5 py-12 text-center text-sm text-slate-500">
                        Loading analyses from the API...
                      </div>
                    ) : isError ? (
                      <div className="px-5 py-12 text-center text-sm text-red-600">
                        {error instanceof Error ? error.message : "Failed to load analyses."}
                      </div>
                    ) : filteredAnalyses.length > 0 ? (
                      filteredAnalyses.map((analysis) => (
                        <AnalysisRow
                          key={analysis.id}
                          analysis={analysis}
                          onOpen={() => {
                            setOpenedAnalysis(analysis);
                          }}
                        />
                      ))
                    ) : (
                      <div className="px-5 py-12 text-center">
                        <Search
                          size={24}
                          className="mx-auto mb-3 text-slate-300"
                        />
                        <p className="text-sm font-medium text-slate-700">
                          No analyses found
                        </p>
                        <p className="mt-1 text-sm text-slate-500">
                          Try a different search or create a new analysis.
                        </p>
                      </div>
                    )}
                  </div>
                </section>

                <section className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-2">
                  <div className="rounded-xl border border-slate-200 bg-white p-5">
                    <div className="flex items-start gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                        <Workflow size={20} />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-slate-900">
                          Build your first pipeline
                        </h3>
                        <p className="mt-1 text-sm leading-6 text-slate-500">
                          Connect operations into a workflow to transform and
                          analyze your data.
                        </p>
                        <button
                          type="button"
                          onClick={() => setShowCreateModal(true)}
                          className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
                        >
                          Create an analysis
                          <ArrowRight size={15} />
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-white p-5">
                    <div className="flex items-start gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                        <Database size={20} />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-slate-900">
                          Get your data ready
                        </h3>
                        <p className="mt-1 text-sm leading-6 text-slate-500">
                          Organize your data sources before connecting them to
                          your analyses.
                        </p>
                        <button
                          type="button"
                          onClick={() => setActiveItem("Datasets")}
                          className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
                        >
                          Explore datasets
                          <ArrowRight size={15} />
                        </button>
                      </div>
                    </div>
                  </div>
                </section>
              </>
            ) : (
              <section className="flex min-h-[60vh] flex-col items-center justify-center text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-500 shadow-sm">
                  {activeItem === "Datasets" ? (
                    <Database size={25} />
                  ) : activeItem === "Executions" ? (
                    <Activity size={25} />
                  ) : activeItem === "Insights" ? (
                    <ArrowUpRight size={25} />
                  ) : (
                    <MoreHorizontal size={25} />
                  )}
                </div>
                <h1 className="mt-5 text-xl font-semibold text-slate-900">
                  {activeItem}
                </h1>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                  This workspace is ready to be implemented. We will connect
                  this section to the Dataflow API as we build the feature.
                </p>
                {activeItem === "Datasets" && (
                  <button
                    type="button"
                    onClick={() => setActiveItem("Overview")}
                    className="mt-5 text-sm font-medium text-blue-600 hover:text-blue-700"
                  >
                    Back to overview
                  </button>
                )}
              </section>
            )}

            <footer className="mt-10 flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 py-5 text-xs text-slate-400">
              <span>Dataflow · Data analytics workspace</span>
              <span>Early access</span>
            </footer>
          </div>
        </div>
      </main>

      {showCreateModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-[2px]"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShowCreateModal(false);
            }
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-analysis-title"
            className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl"
          >
            <div className="flex items-start justify-between">
              <div>
                <h2
                  id="create-analysis-title"
                  className="text-lg font-semibold text-slate-950"
                >
                  Create an analysis
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Give your new analysis a name to get started.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                aria-label="Close dialog"
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              >
                <X size={18} />
              </button>
            </div>

            <form
              className="mt-6"
              onSubmit={(event) => {
                event.preventDefault();
                createAnalysis();
              }}
            >
              <label
                htmlFor="analysis-name"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Analysis name
              </label>
              <input
                id="analysis-name"
                autoFocus
                required
                maxLength={100}
                value={newAnalysisName}
                onChange={(event) => setNewAnalysisName(event.target.value)}
                placeholder="e.g. Customer churn analysis"
                className="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
              />

              <div className="mt-6 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="h-10 rounded-lg border border-slate-200 px-4 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="h-10 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition hover:bg-blue-700"
                >
                  Create analysis
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  iconClass,
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Workflow;
  iconClass: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/2">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{label}</p>
        <div
          className={`flex h-9 w-9 items-center justify-center rounded-lg ${iconClass}`}
        >
          <Icon size={18} />
        </div>
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <p className="text-2xl font-semibold tracking-tight text-slate-950">
          {value}
        </p>
        {label === "Successful analyses" && successfulCountLabel(value) && (
          <ArrowUpRight size={15} className="text-emerald-600" />
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400">{detail}</p>
    </div>
  );
}

function successfulCountLabel(value: string) {
  return Number(value) > 0;
}

function AnalysisRow({
  analysis,
  onOpen,
}: {
  analysis: Analysis;
  onOpen: () => void;
}) {
  const status = statusConfig[analysis.status];

  return (
    <div className="grid grid-cols-1 gap-3 border-b border-slate-100 px-5 py-4 transition last:border-b-0 hover:bg-slate-50/70 md:grid-cols-[minmax(0,2fr)_minmax(120px,0.8fr)_minmax(120px,0.8fr)_40px] md:items-center md:gap-4">
      <button
        type="button"
        onClick={onOpen}
        className="flex min-w-0 items-center gap-3 text-left"
      >
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500">
          <FilePlus2 size={19} />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-slate-800">
            {analysis.name}
          </p>
          <p className="mt-1 truncate text-xs text-slate-400">
            {analysis.description}
          </p>
        </div>
      </button>

      <div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${status.className}`}
        >
          {analysis.status === "success" ? (
            <CheckCircle2 size={12} />
          ) : analysis.status === "running" ? (
            <Activity size={12} />
          ) : (
            <span className="h-1.5 w-1.5 rounded-full bg-current opacity-60" />
          )}
          {status.label}
        </span>
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Clock3 size={14} className="text-slate-400" />
        {analysis.updatedAt}
      </div>

      <div className="flex items-center justify-between gap-3 md:justify-end">
        <span className="text-xs text-slate-400 md:hidden">
          {analysis.operationsCount} operations
        </span>
        <button
          type="button"
          onClick={onOpen}
          aria-label={`Open ${analysis.name}`}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
        >
          <MoreHorizontal size={18} />
        </button>
      </div>
    </div>
  );
}