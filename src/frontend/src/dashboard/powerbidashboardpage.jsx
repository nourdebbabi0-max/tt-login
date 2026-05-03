import PowerBIFrame from "../components/common/powerbiframe.jsx";
import {
  getPowerBiPageUrl,
  POWERBI_PAGE_NAMES
} from "../utils/powerbiconfig.js";

const PAGE_META = {
  home: {
    title: "Home dashboard",
    description: "Accueil du dashboard Power BI.",
    pageName: POWERBI_PAGE_NAMES.home
  },
  avances: {
    title: "Suivi des avances",
    description: "Dashboard des avances.",
    pageName: POWERBI_PAGE_NAMES.avances
  },
  avancesHeure: {
    title: "Suivi par heure ADV",
    description: "Analyse horaire des avances.",
    pageName: POWERBI_PAGE_NAMES.avancesHeure
  },
  remboursement: {
    title: "Suivi des remboursements",
    description: "Dashboard des remboursements.",
    pageName: POWERBI_PAGE_NAMES.remboursement
  },
  remboursementHeure: {
    title: "Suivi par heure REV",
    description: "Analyse horaire des remboursements.",
    pageName: POWERBI_PAGE_NAMES.remboursementHeure
  },
  service: {
    title: "Suivi des services",
    description: "Dashboard des services.",
    pageName: POWERBI_PAGE_NAMES.service
  },
  aideDecision: {
    title: "Aide à la décision",
    description: "Système d’aide à la décision et insights.",
    pageName: POWERBI_PAGE_NAMES.aideDecision
  }
};

export default function PowerBIDashboardPage({ pageKey }) {
  const page = PAGE_META[pageKey] || PAGE_META.home;
  const iframeUrl = getPowerBiPageUrl(page.pageName);

  return (
    <div className="powerbi-page">
      <div className="card dashboard-card powerbi-page-header">
        <div>
          <h2>{page.title}</h2>
          <p>{page.description}</p>
        </div>

        <div className="powerbi-help-box">
          Les visualisations sont affichées depuis Power BI Service.
        </div>
      </div>

      <PowerBIFrame title={page.title} src={iframeUrl} />
    </div>
  );
}