import { useState } from "react";

export default function App() {
  const [text, setText] = useState("");

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

      <button style={{ marginTop: 10 }}>Run Workflow</button>
    </div>
  );
}
