const INSIGHT_LABELS = {
  seo_structure: "SEO Structure",
  messaging_clarity: "Messaging Clarity",
  cta_usage: "CTA Usage",
  content_depth: "Content Depth",
  ux_concerns: "UX Concerns",
};

function scoreBadgeClass(score) {
  if (!score) return "";
  if (score === "Good") return "Good";
  if (score === "Needs Work") return "Needs-Work";
  if (score === "Poor") return "Poor";
  return "";
}

export default function InsightsPanel({ insights }) {
  const keys = Object.keys(INSIGHT_LABELS);

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">◎</span>
        <span className="panel-title">AI Insights</span>
      </div>
      <div className="insights-body">
        {keys.map((key) => {
          const insight = insights[key];
          if (!insight) return null;
          return (
            <div className="insight-card" key={key}>
              <div className="insight-card-header">
                <span className="insight-card-title">{INSIGHT_LABELS[key]}</span>
                {insight.score && (
                  <span className={`score-badge ${scoreBadgeClass(insight.score)}`}>
                    {insight.score}
                  </span>
                )}
              </div>
              <p className="insight-summary">{insight.summary}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}