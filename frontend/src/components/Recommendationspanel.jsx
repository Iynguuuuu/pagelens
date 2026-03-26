export default function RecommendationsPanel({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;

  const sorted = [...recommendations].sort((a, b) => a.priority - b.priority);

  return (
    <div className="recs-panel">
      <div className="panel-header">
        <span className="panel-icon">▲</span>
        <span className="panel-title">Prioritized Recommendations</span>
      </div>
      <div className="recs-body">
        {sorted.map((rec) => (
          <div className="rec-card" key={rec.priority}>
            <div className="rec-priority">#{rec.priority}</div>
            <div>
              <div className="rec-title">{rec.title}</div>
              <p className="rec-reasoning">{rec.reasoning}</p>
              <div className="rec-action-label">Action</div>
              <p className="rec-action">{rec.action}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}