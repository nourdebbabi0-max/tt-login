import PowerBIFrame from "../components/common/powerbiframe.jsx";
import { POWERBI_REPORT_URL } from "../utils/powerbiconfig.js";

export default function CommercialServicePage() {
  return (
    <div className="powerbi-page">
      <div className="card dashboard-card powerbi-page-header">
        <div>
          <h2>Service</h2>
          <p>
            Visualisation Power BI de l’évolution des services par date et par
            service.
          </p>
        </div>

        <div className="powerbi-help-box">
          Utilise les boutons internes “Par date” et “Par service” dans le
          rapport Power BI.
        </div>
      </div>

      <PowerBIFrame
        title="Services Power BI"
        src={POWERBI_REPORT_URL}
      />
    </div>
  );
}