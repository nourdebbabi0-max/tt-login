import PowerBIFrame from "../components/common/powerbiframe.jsx";
import { POWERBI_REPORT_URL } from "../utils/powerbiconfig.js";

export default function CommercialRemboursementPage() {
  return (
    <div className="powerbi-page">
      <div className="card dashboard-card powerbi-page-header">
        <div>
          <h2>Dashboard remboursement</h2>
          <p>
            Visualisation Power BI des remboursements : frais, nombre de
            personnes, montant, crédit et suivi par heure.
          </p>
        </div>

        <div className="powerbi-help-box">
          Les boutons “Par frais”, “Par nombre de personnes”, “Par montant” et
          “Par crédit” restent gérés directement dans Power BI.
        </div>
      </div>

      <PowerBIFrame
        title="Remboursements Power BI"
        src={POWERBI_REPORT_URL}
      />
    </div>
  );
}