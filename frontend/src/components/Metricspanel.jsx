function MetricRow({ name, value, valueClass = "" }) {
  return (
    <div className="metric-row">
      <span className="metric-name">{name}</span>
      <span className={`metric-value ${valueClass}`}>{value}</span>
    </div>
  );
}

function SectionLabel({ label }) {
  return <div className="metric-section-label">{label}</div>;
}

export default function MetricsPanel({ metrics }) {
  const { meta_title, meta_description, word_count, headings, cta_count, links, images } = metrics;

  const altPct = images.missing_alt_pct;
  const altClass = altPct === 0 ? "good" : altPct > 50 ? "poor" : "warn";

  const metaTitleVal = meta_title || "—";
  const metaDescVal = meta_description
    ? meta_description.length > 40
      ? meta_description.slice(0, 40) + "…"
      : meta_description
    : "—";

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">⊞</span>
        <span className="panel-title">Factual Metrics</span>
      </div>
      <div className="metrics-body">
        <SectionLabel label="Meta" />
        <MetricRow
          name="Title"
          value={metaTitleVal}
          valueClass={!meta_title ? "poor" : ""}
        />
        <MetricRow
          name="Description"
          value={metaDescVal}
          valueClass={!meta_description ? "poor" : ""}
        />

        <SectionLabel label="Content" />
        <MetricRow name="Word Count" value={word_count.toLocaleString()} valueClass="amber" />
        <MetricRow name="H1 Tags" value={headings.h1} valueClass={headings.h1 === 1 ? "good" : headings.h1 === 0 ? "poor" : "warn"} />
        <MetricRow name="H2 Tags" value={headings.h2} />
        <MetricRow name="H3 Tags" value={headings.h3} />

        <SectionLabel label="Engagement" />
        <MetricRow name="CTA Count" value={cta_count} valueClass={cta_count === 0 ? "poor" : cta_count >= 3 ? "amber" : ""} />
        <MetricRow name="Internal Links" value={links.internal} />
        <MetricRow name="External Links" value={links.external} />

        <SectionLabel label="Images" />
        <MetricRow name="Total Images" value={images.total} />
        <MetricRow name="Missing Alt Text" value={`${images.missing_alt} (${altPct}%)`} valueClass={altClass} />
      </div>
    </div>
  );
}