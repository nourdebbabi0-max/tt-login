import { useEffect, useState } from "react";
import {
  getFinalReportsRequest,
  previewFinalReportRequest
} from "../api/reports.api";

function formatDate(timestamp) {
  if (!timestamp) return "-";

  return new Date(timestamp * 1000).toLocaleString("fr-FR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function formatSize(bytes) {
  if (!bytes && bytes !== 0) return "-";

  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;

  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
}

export default function AnalyseRapportsFinauxPage() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportRows, setReportRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadReports() {
    setLoading(true);
    setError("");

    try {
      const data = await getFinalReportsRequest();
      setReports(Array.isArray(data) ? data : []);
    } catch {
      setError("Impossible de charger les rapports finaux.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePreview(filename) {
    setPreviewLoading(true);
    setError("");

    try {
      const data = await previewFinalReportRequest(filename);

      setSelectedReport(data.filename);
      setReportRows(Array.isArray(data.rows) ? data.rows : []);
    } catch {
      setError("Impossible d’afficher le contenu du rapport.");
    } finally {
      setPreviewLoading(false);
    }
  }

  useEffect(() => {
    loadReports();
  }, []);

  const columns = reportRows.length > 0 ? Object.keys(reportRows[0]) : [];

  return (
    <div className="card dashboard-card">
      <div className="reports-header">
        <div>
          <h2>Rapports finaux ELT</h2>
          <p>
            Liste des fichiers CSV générés automatiquement par le pipeline ELT.
          </p>
        </div>

        <button className="reports-refresh-btn" type="button" onClick={loadReports}>
          Actualiser
        </button>
      </div>

      {loading ? (
        <p>Chargement des rapports...</p>
      ) : error ? (
        <p className="reports-error">{error}</p>
      ) : reports.length === 0 ? (
        <p>Aucun rapport CSV trouvé pour le moment.</p>
      ) : (
        <div className="reports-table-wrap">
          <table className="reports-table">
            <thead>
              <tr>
                <th>Nom du fichier</th>
                <th>Taille</th>
                <th>Dernière modification</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {reports.map((report) => (
                <tr key={report.filename}>
                  <td>{report.filename}</td>
                  <td>{formatSize(report.size)}</td>
                  <td>{formatDate(report.modified_at)}</td>
                  <td>
                    <button
                      className="reports-view-btn"
                      type="button"
                      onClick={() => handlePreview(report.filename)}
                    >
                      Voir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {previewLoading ? (
        <p className="reports-preview-loading">Chargement du contenu...</p>
      ) : selectedReport ? (
        <div className="reports-preview">
          <h3>Contenu du rapport : {selectedReport}</h3>

          {reportRows.length === 0 ? (
            <p>Ce rapport ne contient aucune ligne.</p>
          ) : (
            <div className="reports-table-wrap">
              <table className="reports-table reports-preview-table">
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {reportRows.map((row, index) => (
                    <tr key={index}>
                      {columns.map((column) => (
                        <td key={column}>{row[column] || "-"}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}