import { useState } from "react";
import AuditForm from "./components/AuditForm";
import MetricsPanel from "./components/MetricsPanel";
import InsightsPanel from "./components/InsightsPanel";
import RecommendationsPanel from "./components/RecommendationsPanel";
import Loader from "./components/Loader";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function App() {
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleAudit(url) {
    setStatus("loading");
    setResult(null);
    setErrorMsg("");
    try {
      const res = await fetch(`${API_BASE}/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Audit failed");
      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">◈</span>
            <span className="logo-text">PageLens</span>
          </div>
          <p className="tagline">AI-powered website audit in seconds</p>
        </div>
      </header>

      <main className="main">
        <AuditForm onSubmit={handleAudit} loading={status === "loading"} />

        {status === "loading" && <Loader />}

        {status === "error" && (
          <div className="error-card">
            <span className="error-icon">⚠</span>
            <p>{errorMsg}</p>
          </div>
        )}

        {status === "success" && result && (
          <div className="results">
            <div className="results-header">
              <div className="results-url">
                <span className="results-label">Audited</span>
                <a href={result.url} target="_blank" rel="noreferrer" className="results-link">
                  {result.url}
                </a>
              </div>
              <div className="log-badge">
                Log ID: <code>{result.log_id}</code>
              </div>
            </div>

            <div className="panels-grid">
              <MetricsPanel metrics={result.metrics} />
              <InsightsPanel insights={result.insights} />
            </div>

            <RecommendationsPanel recommendations={result.recommendations} />
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built for Eight25Media · Prompt logs at <code>/logs</code></p>
      </footer>
    </div>
  );
}