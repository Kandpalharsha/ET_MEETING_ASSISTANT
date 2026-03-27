import { useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runWorkflow = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${API}/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ transcript: text }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
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
        style={{ marginTop: 10 }}
        disabled={loading}
      >
        {loading ? "Running..." : "Run Workflow"}
      </button>

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Output</h3>
          <pre style={{ background: "#111", color: "#0f0", padding: 10 }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
