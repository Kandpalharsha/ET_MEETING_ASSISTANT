import { useState, useCallback } from "react";
import TaskBoard from "./components/TaskBoard";
import AuditStream from "./components/AuditStream";
import { useWebSocket } from "./hooks/useWebSocket";

const API = "http://localhost:8000";

export default function App() {
  const [text, setText] = useState("");
  const [tasks, setTasks] = useState([]);
  const [audit, setAudit] = useState([]);
  const [running, setRunning] = useState(false);

  // 🔥 Handle incoming WS messages
  const handleMessage = useCallback((msg) => {
    if (msg.type === "audit") {
      setAudit((prev) => {
        const exists = prev.some((e) => e.id === msg.data.id);
        return exists ? prev : [...prev, msg.data];
      });
    } else if (msg.type === "tasks_full") {
      setTasks(msg.data);
    } else if (msg.type === "workflow_complete") {
      setRunning(false);
    }
  }, []);

  // 🔥 Connect WebSocket
  useWebSocket(handleMessage);

  const runWorkflow = async () => {
    if (!text.trim()) return;

    setRunning(true);
    setTasks([]);
    setAudit([]);

    try {
      await fetch(`${API}/api/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ transcript: text }),
      });
    } catch (err) {
      console.error(err);
      setRunning(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>ET Workflow Agent</h2>

      <textarea
        rows={6}
        style={{ width: "100%", marginTop: 10 }}
        placeholder="Paste meeting transcript..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        onClick={runWorkflow}
        disabled={running}
        style={{ marginTop: 10 }}
      >
        {running ? "Running..." : "Run Workflow"}
      </button>

      <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
        <div style={{ flex: 1 }}>
          <TaskBoard tasks={tasks} />
        </div>

        <div style={{ flex: 1 }}>
          <AuditStream entries={audit} running={running} />
        </div>
      </div>
    </div>
  );
}
