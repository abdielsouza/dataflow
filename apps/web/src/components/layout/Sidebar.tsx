import {
  Activity,
  ChartNoAxesCombined,
  ChevronDown,
  Database,
  FolderKanban,
  LayoutDashboard,
  Settings,
  Workflow,
} from "lucide-react";

interface SidebarProps {
  activeItem: string;
  onNavigate: (item: string) => void;
}

const navigation = [
  {
    title: "WORKSPACE",
    items: [
      { label: "Overview", icon: LayoutDashboard },
      { label: "Analyses", icon: Workflow },
      { label: "Datasets", icon: Database },
    ],
  },
  {
    title: "MONITORING",
    items: [
      { label: "Executions", icon: Activity },
      { label: "Insights", icon: ChartNoAxesCombined },
    ],
  },
];

export function Sidebar({ activeItem, onNavigate }: SidebarProps) {
  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-white/10 bg-[#111318] text-slate-300">
      <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-white">
          <Workflow size={21} strokeWidth={2.2} />
        </div>

        <div>
          <p className="text-base font-semibold tracking-tight text-white">
            Dataflow
          </p>
          <p className="text-[11px] text-slate-500">Analytics platform</p>
        </div>
      </div>

      <button
        type="button"
        className="mx-3 mt-5 flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 p-3 text-left transition hover:bg-white/10"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-violet-500/15 text-violet-300">
          <FolderKanban size={17} />
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-white">
            My Workspace
          </p>
          <p className="text-xs text-slate-500">Personal workspace</p>
        </div>

        <ChevronDown size={15} className="text-slate-500" />
      </button>

      <nav className="flex-1 space-y-7 overflow-y-auto px-3 py-7">
        {navigation.map((group) => (
          <div key={group.title}>
            <p className="mb-2 px-3 text-[10px] font-semibold tracking-[0.16em] text-slate-500">
              {group.title}
            </p>

            <div className="space-y-1">
              {group.items.map(({ label, icon: Icon }) => {
                const active = activeItem === label;

                return (
                  <button
                    key={label}
                    type="button"
                    onClick={() => onNavigate(label)}
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                      active
                        ? "bg-blue-500/15 font-medium text-blue-300"
                        : "text-slate-400 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <Icon size={18} />
                    <span>{label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-white/10 p-3">
        <button
          type="button"
          onClick={() => onNavigate("Settings")}
          className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
            activeItem === "Settings"
              ? "bg-blue-500/15 text-blue-300"
              : "text-slate-400 hover:bg-white/5 hover:text-white"
          }`}
        >
          <Settings size={18} />
          Settings
        </button>

        <div className="mt-3 flex items-center gap-3 rounded-lg p-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-violet-500 text-xs font-bold text-white">
            DF
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-white">
              Dataflow User
            </p>
            <p className="truncate text-xs text-slate-500">
              Personal account
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}