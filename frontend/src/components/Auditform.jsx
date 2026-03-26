import { useState } from "react";

export default function AuditForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return;
    onSubmit(url.trim());
  }

  return (
    <div className="audit-form">
      <label className="form-label">Enter a URL to audit</label>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <input
            className="url-input"
            type="text"
            placeholder="https://example.com/landing-page"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            autoFocus
          />
          <button className="audit-btn" type="submit" disabled={loading || !url.trim()}>
            {loading ? "Analyzing..." : "Run Audit →"}
          </button>
        </div>
      </form>
    </div>
  );
}