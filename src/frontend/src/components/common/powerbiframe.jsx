export default function PowerBIFrame({ title = "Dashboard Power BI", src }) {
  if (!src) {
    return (
      <section className="powerbi-section">
        <div className="powerbi-empty">Lien Power BI manquant.</div>
      </section>
    );
  }

  return (
    <section className="powerbi-section">
      <iframe
        title={title}
        src={src}
        className="powerbi-iframe"
        allowFullScreen
      />
    </section>
  );
}