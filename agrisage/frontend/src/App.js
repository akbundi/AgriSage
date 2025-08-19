import React, { useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [context, setContext] = useState({
    location: "",
    district: "",
    crop: "",
    stage: ""
  });
  const [resp, setResp] = useState(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const payload = {
        query,
        context: {
          location: context.location || undefined,
          district: context.district || undefined,
          crop: context.crop || undefined,
          stage: context.stage || undefined
        }
      };
      const r = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const json = await r.json();
      setResp(json);
    } catch (e) {
      setResp({
        answer: "⚠️ Network error or backend not available (offline?).",
        explain: {}
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        padding: 20,
        fontFamily: "Arial, sans-serif",
        maxWidth: 800,
        margin: "auto"
      }}
    >
      <h1>AgriSage</h1>
      <p>Ask a farm question (voice or text) — demo PWA</p>

      <textarea
        rows={3}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="When should I irrigate my wheat next week in Jaipur?"
        style={{ width: "100%", padding: 10, fontSize: 16 }}
      />

      <div style={{ marginTop: 8 }}>
        <label>Location: </label>
        <input
          value={context.location}
          placeholder="e.g. Jaipur, Rajasthan"
          onChange={(e) => setContext({ ...context, location: e.target.value })}
        />

        <label style={{ marginLeft: 10 }}>District: </label>
        <input
          value={context.district}
          placeholder="e.g. Jaipur"
          onChange={(e) => setContext({ ...context, district: e.target.value })}
        />

        <label style={{ marginLeft: 10 }}>Crop: </label>
        <input
          value={context.crop}
          placeholder="e.g. wheat"
          onChange={(e) => setContext({ ...context, crop: e.target.value })}
        />

        <label style={{ marginLeft: 10 }}>Stage: </label>
        <input
          value={context.stage}
          placeholder="e.g. flowering"
          onChange={(e) => setContext({ ...context, stage: e.target.value })}
        />
      </div>

      <div style={{ marginTop: 10 }}>
        <button
          onClick={ask}
          disabled={loading || !query}
          style={{ padding: "8px 16px", fontSize: 16 }}
        >
          {loading ? "Thinking…" : "Ask AgriSage"}
        </button>
      </div>

      {resp && (
        <div
          style={{
            marginTop: 20,
            background: "#f7fff7",
            padding: 12,
            borderRadius: 8
          }}
        >
          <h3>Answer</h3>
          <div style={{ whiteSpace: "pre-wrap" }}>{resp.answer}</div>

          <h4 style={{ marginTop: 10 }}>Explain</h4>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(resp.explain, null, 2)}
          </pre>

          <h4>Citations</h4>
          <ul>
            {(resp.citations || []).map((c) => (
              <li key={c.id}>
                {c.title} — {c.source}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
