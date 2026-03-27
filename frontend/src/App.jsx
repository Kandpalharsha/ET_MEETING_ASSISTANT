import { useState, useCallback } from "react";
import AuditStream from "./components/AuditStream";
import TaskBoard from "./components/TaskBoard";
import { useWebSocket } from "./hooks/useWebSocket";

const API = "http://localhost:8000";

const ET_TRANSCRIPT = `Editorial Planning Meeting — Economic Times Digital
Date: March 23, 2026 | 10:00 AM IST
Attendees: Rakesh Sharma (Senior Editor), Priya Nair (Bureau Chief),
           Arjun Mehta (Correspondent), Vikram Iyer (Tech Lead),
           Sunita Rao (Legal/Compliance), Meera Joshi (Events),
           Ravi Krishnan (Finance)

Rakesh: Let's start. Top priority this week is the Union Budget impact analysis.
We've decided it goes live Tuesday, April 1st — that is locked in.
Arjun, you are on ground reporting. Can you file the first draft by March 29?

Arjun: Yes, I will have it ready. Should I include the MSME sector angle?

Rakesh: Absolutely, make it the lead angle. Priya, once Arjun files,
editorial review needs to be done by March 30th. Can you own that?

Priya: Sure. I will pull in the Mumbai bureau for regional data points too.

Rakesh: Good. Now Sunita, the fintech regulatory piece we are running on Friday.
Legal needs to clear it before publish. There are some RBI circular references
from February that need fact-checking against the actual text.

Sunita: I will handle the compliance review. I need until March 28th.
The February RBI circular on payment aggregators I will flag anything
that looks like a misquote.

Rakesh: Perfect. Vikram, there was an outage on the ET Markets live feed
yesterday during the Sensex rally. That websocket reconnection bug cannot
happen during Budget day coverage, we will have 10x normal traffic.

Vikram: Understood. My team will have the websocket fix patched and tested
by March 27th. I will also set up the load monitoring dashboards for Budget day
by April 1st.

Meera: Quick flag. Registration confirmation emails for the ET Wealth Summit
are bouncing. About 200 registrations have not gotten their confirmation.
The email delivery pipeline needs a fix.

Vikram: That is on the tech side. I will look at it, should be sorted by March 26th.

Rakesh: Ravi, we need finance sign-off on the Budget special supplement
sponsorship packages. There are three advertisers waiting on confirmed rates.

Ravi: I will get the approval done by March 25th and send the confirmed
rate cards to the sales team.

Priya: One more thing. TRAI announced a new AI content disclosure policy last week.
Our editorial style guide needs updating before we publish any AI-assisted content.

Sunita: That is on me too. I will draft the updated disclosure guidelines
and circulate for team review by March 31st.

Rakesh: That covers everything. Budget coverage is the critical path.`;

// ── Escalation notification popup ────────────────────────────────────
function EscalationAlert({ alert, onDismiss }) {
  if (!alert) return null;
  return (
    <div className="fixed top-4 right-4 z-50 w-80 bg-[#1a0a0a] border border-red-500/40 rounded-xl p-4 shadow-xl animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-semibold text-red-400 font-mono uppercase tracking-wider">
            Escalation triggered
          </span>
        </div>
        <button
          onClick={onDismiss}
          className="text-gray-600 hover:text-gray-400 text-lg leading-none"
        >
          ×
        </button>
      </div>
      <p className="text-xs text-gray-300 font-medium mb-1 leading-relaxed">
        {alert.task_title}
      </p>
      <p className="text-[11px] text-gray-500 mb-3 leading-relaxed">
        {alert.message}
      </p>
      <div className="flex items-center justify-between border-t border-red-500/20 pt-3">
        <div>
          <p className="text-[10px] text-gray-600">Notified manager</p>
          <p className="text-xs text-white font-medium">{alert.manager}</p>
        </div>
        <div className="text-right">
          <p className="text-[10px] text-gray-600">Stalled owner</p>
          <p className="text-xs text-gray-400">{alert.owner}</p>
        </div>
      </div>
    </div>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────
function StatCard({ label, value, accent }) {
  const colors = {
    green: "text-emerald-400",
    red: "text-red-400",
    purple: "text-purple-400",
    blue: "text-blue-400",
    white: "text-white",
  };
  return (
    <div className="bg-[#111] border border-[#1E1E1E] rounded-xl px-4 py-3 flex flex-col gap-1">
      <span className="text-[10px] text-gray-600 uppercase tracking-widest font-mono">
        {label}
      </span>
      <span
        className={`text-xl font-semibold ${colors[accent] || "text-white"}`}
      >
        {value}
      </span>
    </div>
  );
}

// ── Header ────────────────────────────────────────────────────────────
function Header({ running, connected }) {
  return (
    <div className="flex items-center justify-between mb-5">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-[#E8001D] rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white text-xs font-bold">ET</span>
        </div>
        <div>
          <h1 className="text-sm font-semibold text-white leading-tight">
            Editorial Workflow Agent
          </h1>
          <p className="text-[11px] text-gray-600 font-mono">
            PS 2 · Meeting Intelligence · Groq + Llama 3.3 70B · LangGraph
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {running && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#E8001D]/30 bg-[#E8001D]/5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#E8001D] animate-pulse" />
            <span className="text-xs text-[#E8001D] font-mono">
              agents running
            </span>
          </div>
        )}
        <div className="flex items-center gap-1.5">
          <div
            className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-500" : "bg-red-500"}`}
          />
          <span className="text-[11px] text-gray-600 font-mono">
            {connected ? "connected" : "disconnected"}
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Upload panel ──────────────────────────────────────────────────────
function UploadPanel({ onSubmit, running }) {
  const [text, setText] = useState(ET_TRANSCRIPT);
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="bg-[#111] border border-[#1E1E1E] rounded-xl p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-white">
          Meeting transcript
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setText(ET_TRANSCRIPT)}
            className="text-[11px] text-gray-600 hover:text-gray-400 font-mono border border-[#1E1E1E] hover:border-gray-700 px-2 py-1 rounded transition-colors"
          >
            load ET demo
          </button>
          <button
            onClick={() => setText("")}
            className="text-[11px] text-gray-600 hover:text-gray-400 font-mono border border-[#1E1E1E] hover:border-gray-700 px-2 py-1 rounded transition-colors"
          >
            clear
          </button>
        </div>
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
        placeholder="Paste any meeting transcript here…"
        className="w-full bg-[#0A0A0A] border border-[#1E1E1E] rounded-lg px-3 py-2.5
                   text-xs text-gray-300 font-mono resize-none focus:outline-none
                   focus:border-gray-700 placeholder-gray-700 leading-relaxed"
      />
      <div className="flex items-center justify-between mt-3">
        <p className="text-[11px] text-gray-700 font-mono">{wordCount} words</p>
        <button
          disabled={running || !text.trim()}
          onClick={() => onSubmit(text.trim())}
          className="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium
                     bg-[#E8001D] hover:bg-red-600 text-white transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {running ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              Running…
            </>
          ) : (
            "Run workflow →"
          )}
        </button>
      </div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────
export default function App() {
  const [auditLog, setAuditLog] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [running, setRunning] = useState(false);
  const [connected, setConnected] = useState(false);
  const [result, setResult] = useState(null);
  const [escalAlert, setEscalAlert] = useState(null);

  const handleMessage = useCallback((msg) => {
    if (msg.type === "audit") {
      setAuditLog((prev) => {
        const exists = prev.some((e) => e.id === msg.data.id);
        return exists ? prev : [...prev, msg.data];
      });
    } else if (msg.type === "tasks_full") {
      setTasks(msg.data);
    } else if (msg.type === "workflow_complete") {
      setResult(msg.data);
      setRunning(false);
    } else if (msg.type === "escalation_notification") {
      setEscalAlert(msg.data);
    } else if (msg.type === "connected") {
      setConnected(true);
    }
  }, []);

  const wsRef = useWebSocket(handleMessage);

  // Also track WS connection state
  const handleConnect = useCallback(() => setConnected(true), []);
  const handleDisconnect = useCallback(() => setConnected(false), []);

  const runWorkflow = async (transcript) => {
    setRunning(true);
    setAuditLog([]);
    setTasks([]);
    setResult(null);
    setEscalAlert(null);
    try {
      await fetch(`${API}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });
    } catch (err) {
      console.error("Workflow error:", err);
      setRunning(false);
    }
  };

  const injectStall = async (taskId) => {
    await fetch(`${API}/api/demo/stall/${taskId}`, { method: "POST" });
  };

  // Autonomy score for display
  const autonomyScore = result
    ? Math.round(
        ((result.audit_count - result.escalations) /
          Math.max(result.audit_count, 1)) *
          100,
      )
    : null;

  return (
    <div className="min-h-screen bg-[#0A0A0A] p-4 md:p-5">
      <div className="max-w-7xl mx-auto">
        <Header running={running} connected={connected} />

        <UploadPanel onSubmit={runWorkflow} running={running} />

        {/* Stats row */}
        {result && (
          <div className="grid grid-cols-6 gap-2 mb-4 animate-fade-in">
            <StatCard
              label="Workflow ID"
              value={result.workflow_id}
              accent="white"
            />
            <StatCard
              label="Tasks created"
              value={result.tasks_created}
              accent="green"
            />
            <StatCard
              label="Audit entries"
              value={result.audit_count}
              accent="blue"
            />
            <StatCard
              label="Escalations"
              value={result.escalations}
              accent="purple"
            />
            <StatCard
              label="Autonomy"
              value={`${autonomyScore}%`}
              accent="green"
            />
            <StatCard
              label="Status"
              value={result.status}
              accent={result.status === "completed" ? "green" : "red"}
            />
          </div>
        )}

        {/* ET context banner */}
        {result?.et_context && (
          <div className="mb-4 px-4 py-2.5 bg-[#111] border border-[#1E1E1E] rounded-xl flex items-start gap-3 animate-fade-in">
            <span className="text-[#E8001D] text-xs font-mono mt-0.5 flex-shrink-0">
              ET
            </span>
            <p className="text-xs text-gray-500 leading-relaxed">
              {result.et_context}
            </p>
          </div>
        )}

        {/* Main panels */}
        <div className="grid grid-cols-2 gap-4 h-[580px]">
          <AuditStream entries={auditLog} running={running} />
          <TaskBoard tasks={tasks} onStall={injectStall} />
        </div>

        {/* Decisions panel */}
        {result?.decisions?.length > 0 && (
          <div className="mt-4 bg-[#111] border border-[#1E1E1E] rounded-xl p-4 animate-fade-in">
            <p className="text-[10px] font-medium text-gray-600 uppercase tracking-widest font-mono mb-3">
              Decisions extracted from meeting
            </p>
            <div className="grid grid-cols-2 gap-2">
              {result.decisions.map((d, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 bg-[#0A0A0A] rounded-lg px-3 py-2.5"
                >
                  <span className="text-[10px] text-gray-700 font-mono mt-0.5 flex-shrink-0">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <p className="text-xs text-gray-400 leading-relaxed">{d}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Escalation notification popup */}
      <EscalationAlert
        alert={escalAlert}
        onDismiss={() => setEscalAlert(null)}
      />
    </div>
  );
}
