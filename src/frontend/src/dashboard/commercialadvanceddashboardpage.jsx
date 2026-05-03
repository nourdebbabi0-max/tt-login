import PowerBIFrame from "../components/common/powerbiframe.jsx";
import { POWERBI_REPORT_URL } from "../utils/powerbiconfig.js";

export default function CommercialAdvancedDashboardPage() {
  return (
    <div className="powerbi-page">
      <div className="card dashboard-card powerbi-page-header">
        <div>
          <h2>Suivi des avances</h2>
          <p>
            Visualisation Power BI des avances : montant, nombre d’utilisateurs
            et suivi par heure.
          </p>
        </div>

        <div className="powerbi-help-box">
          Utilise les boutons internes Power BI pour changer la visualisation.
        </div>
      </div>

      <PowerBIFrame
        title="Suivi des avances Power BI"
        src={POWERBI_REPORT_URL}
      />
    </div>
  );
}