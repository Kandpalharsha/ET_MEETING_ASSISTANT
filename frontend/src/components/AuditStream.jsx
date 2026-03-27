import { useEffect, useRef } from "react";

const AGENT_LABEL = {
  extraction_agent: "Extraction",
  escalation_agent: "Escalation",
  task_creation_agent: "Task Creation",
  tracker_agent: "Tracker",
  demo_control: "Demo",
};

const STATUS_STYLES = {
  success: {
    bar: "bg-emerald-500",
    badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  recovery: {
    bar: "bg-amber-500",
    badge: "bg-amber-500/10  text-amber-400  border-amber-500/20",
  },
  failure: {
    bar: "bg-red-500",
    badge: "bg-red-500/10    text-red-400    border-red-500/20",
  },
  escalated: {
    bar: "bg-purple-500",
    badge: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  },
};

function AuditCard({ entry, isNew }) {
  const s = STATUS_STYLES[entry.status] || STATUS_STYLES.success;
  const time = new Date(entry.timestamp).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div
      className={`relative flex gap-3 p-3 rounded-lg border border-et-border bg-et-card
                     ${isNew ? "animate-slide-in" : ""}`}
    >
      {/* status bar */}
      <div className={`w-0.5 rounded-full flex-shrink-0 ${s.bar}`} />

      <div className="flex-1 min-w-0">
        {/* header row */}
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <span className="text-xs font-semibold text-white font-mono">
            {AGENT_LABEL[entry.agent] || entry.agent} Agent
          </span>
          <span className="text-xs text-gray-600">·</span>
          <span className="text-xs text-gray-400 font-mono">
            {entry.action}
          </span>
          <span
            className={`ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full border
                        ${s.badge}`}
          >
            {entry.status}
          </span>
        </div>

        {/* output */}
        <p className="text-xs text-gray-300 mb-1 leading-relaxed">
          {entry.output_summary}
        </p>

        {/* reasoning */}
        <p className="text-[11px] text-gray-600 leading-relaxed italic">
          {entry.reasoning}
        </p>

        {/* timestamp */}
        <p className="text-[10px] text-gray-700 mt-1 font-mono">{time}</p>
      </div>
    </div>
  );
}

export default function AuditStream({ entries, running }) {
  const bottomRef = useRef(null);
  const prevLen = useRef(0);

  useEffect(() => {
    if (entries.length > prevLen.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    prevLen.current = entries.length;
  }, [entries.length]);

  return (
    <div className="flex flex-col h-full bg-et-card border border-et-border rounded-xl overflow-hidden">
      {/* header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-et-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${running ? "bg-et-red animate-pulse-dot" : "bg-gray-700"}`}
          />
          <span className="text-sm font-medium text-white">Audit trail</span>
        </div>
        <div className="flex items-center gap-3">
          {running && (
            <span className="text-xs text-gray-500 font-mono">
              agents running…
            </span>
          )}
          <span className="text-xs text-gray-600 font-mono">
            {entries.length} entries
          </span>
        </div>
      </div>

      {/* legend */}
      <div className="flex gap-3 px-4 py-2 border-b border-et-border bg-et-dark flex-shrink-0">
        {Object.entries(STATUS_STYLES).map(([key, s]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${s.bar}`} />
            <span className="text-[10px] text-gray-600 capitalize">{key}</span>
          </div>
        ))}
      </div>

      {/* entries */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {entries.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
            <div className="w-10 h-10 rounded-full border border-et-border flex items-center justify-center">
              <div className="w-3 h-3 border-2 border-gray-700 rounded-full" />
            </div>
            <p className="text-sm text-gray-600">
              Paste a meeting transcript to start
            </p>
            <p className="text-xs text-gray-700">
              Agents will log every decision here in real time
            </p>
          </div>
        ) : (
          entries.map((e, i) => (
            <AuditCard key={e.id} entry={e} isNew={i >= entries.length - 3} />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
