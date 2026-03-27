const PRIORITY_STYLES = {
  high: "bg-red-500/10   text-red-400   border-red-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  low: "bg-gray-500/10  text-gray-400  border-gray-500/20",
};

const STATUS_STYLES = {
  pending: "text-gray-400",
  in_progress: "text-blue-400",
  stalled: "text-red-400",
  done: "text-emerald-400",
  escalated: "text-purple-400",
};

const CATEGORY_ICON = {
  editorial: "✦",
  compliance: "⚖",
  technical: "⚙",
  finance: "₹",
  events: "◈",
};

function TaskCard({ task, onStall }) {
  const daysLeft = task.deadline
    ? Math.ceil((new Date(task.deadline) - new Date()) / 86400000)
    : null;

  const isStalled = task.status === "stalled";
  const isEscalated = task.status === "escalated";

  return (
    <div
      className={`rounded-lg border p-3 transition-colors
      ${
        isStalled
          ? "border-red-500/40 bg-red-500/5"
          : isEscalated
            ? "border-purple-500/40 bg-purple-500/5"
            : "border-et-border bg-et-card hover:border-gray-600"
      }`}
    >
      {/* top row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-gray-600 text-xs">
            {CATEGORY_ICON[task.category] || "·"}
          </span>
          <span
            className={`text-[10px] font-mono capitalize ${STATUS_STYLES[task.status] || "text-gray-400"}`}
          >
            {task.status}
          </span>
        </div>
        <span
          className={`text-[10px] px-2 py-0.5 rounded-full border font-medium
                          ${PRIORITY_STYLES[task.priority] || PRIORITY_STYLES.medium}`}
        >
          {task.priority}
        </span>
      </div>

      {/* title */}
      <p className="text-xs text-gray-200 leading-relaxed mb-2 font-medium line-clamp-2">
        {task.title}
      </p>

      {/* meta */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* owner avatar */}
          <div className="w-5 h-5 rounded-full bg-et-muted flex items-center justify-center">
            <span className="text-[9px] text-gray-400 font-medium">
              {task.owner
                ? task.owner
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .slice(0, 2)
                : "?"}
            </span>
          </div>
          <span className="text-[11px] text-gray-500 truncate max-w-[90px]">
            {task.owner || "Unassigned"}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {task.nudge_sent && (
            <span className="text-[9px] text-amber-500 font-mono">nudged</span>
          )}
          {daysLeft !== null && (
            <span
              className={`text-[10px] font-mono
              ${
                daysLeft <= 2
                  ? "text-red-400"
                  : daysLeft <= 5
                    ? "text-amber-400"
                    : "text-gray-600"
              }`}
            >
              {daysLeft <= 0 ? "overdue" : `${daysLeft}d`}
            </span>
          )}
        </div>
      </div>

      {/* stall button — demo only */}
      {task.status === "pending" && (
        <button
          onClick={() => onStall(task.id)}
          className="mt-2 w-full text-[10px] text-gray-700 hover:text-red-400
                     border border-et-border hover:border-red-500/30
                     rounded px-2 py-1 transition-colors font-mono"
        >
          simulate stall →
        </button>
      )}
      {task.status !== "done" && (
        <button
          onClick={() =>
            fetch(`http://localhost:8000/api/tasks/${task.id}/done`, {
              method: "POST",
            })
          }
          className="mt-2 w-full text-[10px] text-gray-700 hover:text-emerald-400
               border border-et-border hover:border-emerald-500/30
               rounded px-2 py-1 transition-colors font-mono"
        >
          mark done ✓
        </button>
      )}
    </div>
  );
}

export default function TaskBoard({ tasks, onStall }) {
  const byStatus = {
    pending: tasks.filter((t) => t.status === "pending"),
    in_progress: tasks.filter((t) => t.status === "in_progress"),
    stalled: tasks.filter((t) => t.status === "stalled"),
    escalated: tasks.filter((t) => t.status === "escalated"),
    done: tasks.filter((t) => t.status === "done"),
  };

  const categories = [...new Set(tasks.map((t) => t.category))].filter(Boolean);

  return (
    <div className="flex flex-col h-full bg-et-card border border-et-border rounded-xl overflow-hidden">
      {/* header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-et-border flex-shrink-0">
        <span className="text-sm font-medium text-white">Task board</span>
        <div className="flex items-center gap-3">
          {tasks.length > 0 && (
            <div className="flex gap-1.5">
              {categories.map((cat) => (
                <span
                  key={cat}
                  className="text-[10px] text-gray-600 bg-et-muted px-2 py-0.5 rounded font-mono"
                >
                  {cat}
                </span>
              ))}
            </div>
          )}
          <span className="text-xs text-gray-600 font-mono">
            {tasks.length} tasks
          </span>
        </div>
      </div>

      {/* stats row */}
      {tasks.length > 0 && (
        <div className="grid grid-cols-4 border-b border-et-border flex-shrink-0">
          {[
            {
              label: "Pending",
              count: byStatus.pending.length,
              color: "text-gray-400",
            },
            {
              label: "Stalled",
              count: byStatus.stalled.length,
              color: "text-red-400",
            },
            {
              label: "Escalated",
              count: byStatus.escalated.length,
              color: "text-purple-400",
            },
            {
              label: "Done",
              count: byStatus.done.length,
              color: "text-emerald-400",
            },
          ].map((s) => (
            <div
              key={s.label}
              className="flex flex-col items-center py-2 border-r border-et-border last:border-0"
            >
              <span className={`text-lg font-semibold ${s.color}`}>
                {s.count}
              </span>
              <span className="text-[10px] text-gray-700">{s.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* tasks */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <div className="w-10 h-10 rounded border border-et-border flex items-center justify-center">
              <span className="text-gray-700 text-lg">✦</span>
            </div>
            <p className="text-sm text-gray-600">Tasks will appear here</p>
            <p className="text-xs text-gray-700">after the workflow runs</p>
          </div>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} onStall={onStall} />
          ))
        )}
      </div>
    </div>
  );
}
